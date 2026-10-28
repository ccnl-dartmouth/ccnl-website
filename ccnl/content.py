"""Load and validate everything under content/.

Every problem is reported with the file name and a plain-language fix. Problems are
collected (not raised one by one) so a member sees all of them in a single build.
"""

import datetime
import difflib
import re
import unicodedata
from pathlib import Path

import bibtexparser
import markdown
import yaml
from bibtexparser.bparser import BibTexParser
from bibtexparser.latexenc import latex_to_unicode

from .images import IMAGE_EXTS

ROLES = ("pi", "postdoc", "grad", "undergrad", "collaborator")
ROLE_LABELS = {
    "pi": "Principal Investigator",
    "postdoc": "Postdoctoral Scholar",
    "grad": "Graduate Student",
    "undergrad": "Undergraduate Student",
    "collaborator": "Collaborator",
}
ROLE_GROUP_TITLES = {
    "pi": "Principal Investigator",
    "postdoc": "Postdoctoral Scholars",
    "grad": "Graduate Students",
    "undergrad": "Undergraduate Students",
    "collaborator": "Collaborators",
}
PAGES = ("home", "about", "research", "people", "publications", "resources", "contact")
STALE_DAYS = 365

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONT_MATTER = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n(.*))?\Z", re.S)
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ORCID = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
MONTH = re.compile(r"^(\d{4})-(\d{2})(?:-(\d{2}))?$")

_markdown = markdown.Markdown(extensions=["extra", "sane_lists", "smarty"])


def render_markdown(text):
    _markdown.reset()
    return _markdown.convert(text or "")


# --------------------------------------------------------------------------- helpers


def where_of(path, root):
    try:
        return str(Path(path).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return str(path)


def read_front_matter(path, where, problems):
    """Return (meta dict, body text), or (None, None) after recording an error."""
    try:
        text = Path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        problems.error(where, f"could not read the file ({exc}). Save it as plain UTF-8 text.")
        return None, None
    text = text.replace("\r\n", "\n")
    match = FRONT_MATTER.match(text)
    if not match:
        return {}, text
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        problems.error(
            where,
            "the header between the two '---' lines is not valid YAML "
            f"({str(exc).splitlines()[-1] if str(exc) else exc.__class__.__name__}). "
            "A common cause is a colon inside a value: put the value in quotes.",
        )
        return None, None
    if not isinstance(meta, dict):
        problems.error(where, "the header between the two '---' lines must be a list of 'name: value' lines.")
        return None, None
    return meta, match.group(2) or ""


def check_slug(path, where, problems):
    if not SLUG.match(Path(path).stem):
        problems.error(
            where,
            "the file name must use only lowercase letters, digits and hyphens, e.g. 'jane-doe.md'. Rename the file.",
        )
        return False
    return True


def check_url(value, where, field, problems):
    if isinstance(value, str) and re.match(r"^https?://\S+\.\S+", value.strip()):
        return value.strip()
    problems.error(where, f"'{field}' must be a full web address starting with http:// or https:// (got {value!r}).")
    return None


def normalize_month(value):
    """Accept 'YYYY-MM', 'YYYY-MM-DD' or a YAML date; return a date or None."""
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    m = MONTH.match(str(value).strip())
    if not m:
        return None
    year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3) or 1)
    try:
        return datetime.date(year, month, day)
    except ValueError:
        return None


def check_meta(meta, where, spec, problems):
    """Validate front matter against `spec`; return a cleaned dict (missing optional keys -> None)."""
    clean = {}
    for key in meta:
        if key not in spec:
            close = difflib.get_close_matches(str(key), spec, n=1)
            hint = f" (did you mean '{close[0]}'?)" if close else f". Allowed fields: {', '.join(spec)}"
            problems.error(where, f"unknown field '{key}'{hint}")
    for key, rule in spec.items():
        value = meta.get(key)
        if value is None or value == "":
            if rule.get("required"):
                problems.error(where, f"missing required field '{key}'. Add a line like `{key}: {rule.get('example', '...')}`")
            clean[key] = None
            continue
        kind = rule.get("type", "str")
        if kind == "str":
            if isinstance(value, (list, dict)):
                problems.error(where, f"'{key}' must be text, not a list.")
                value = None
            else:
                value = str(value)
        elif kind == "year":
            try:
                value = int(value)
                if not 1900 <= value <= 2100:
                    raise ValueError
            except (TypeError, ValueError):
                problems.error(where, f"'{key}' must be a four-digit year like 2024 (got {value!r}).")
                value = None
        elif kind == "bool":
            if not isinstance(value, bool):
                problems.error(where, f"'{key}' must be true or false (got {value!r}).")
                value = None
        elif kind == "int":
            if isinstance(value, bool) or not isinstance(value, int):
                problems.error(where, f"'{key}' must be a whole number (got {value!r}).")
                value = None
        elif kind == "list":
            if not isinstance(value, list):
                problems.error(where, f"'{key}' must be a list (each item on its own line starting with '- ').")
                value = None
        elif kind == "dict":
            if not isinstance(value, dict):
                problems.error(where, f"'{key}' must be a set of 'name: value' lines indented under '{key}:'.")
                value = None
        elif kind == "month":
            parsed = normalize_month(value)
            if parsed is None:
                problems.error(where, f"'{key}' must look like 2026-10 (year-month) (got {value!r}).")
            value = parsed
        choices = rule.get("choices")
        if value is not None and choices and value not in choices:
            close = difflib.get_close_matches(str(value), choices, n=1)
            hint = f" Did you mean '{close[0]}'?" if close else ""
            problems.error(where, f"'{key}' must be one of: {', '.join(choices)} (got {value!r}).{hint}")
            value = None
        clean[key] = value
    return clean


def check_stale(updated, where, today, problems):
    if updated and (today - updated).days > STALE_DAYS:
        problems.warn(
            where,
            f"last updated {updated:%Y-%m}, over a year ago. If it is still correct, change `updated:` to the current month.",
        )


def split_email(address, where, problems):
    if not EMAIL.match(address.strip()):
        problems.error(where, f"'{address}' does not look like an email address.")
        return None
    user, domain = address.strip().rsplit("@", 1)
    return {"user": user, "domain": domain}


def list_md(directory, where_of_dir, problems, extra_ok=()):
    """Markdown files in a collection folder (sorted); warns about files that will be ignored (images go in content/images/)."""
    files = []
    for path in sorted(Path(directory).iterdir()):
        if path.name.startswith((".", "_")) or path.name.lower() == "readme.md" or path.is_dir():
            continue
        suffix = path.suffix.lower()
        if suffix == ".md":
            files.append(path)
        elif suffix in IMAGE_EXTS:
            problems.warn(
                f"{where_of_dir}/{path.name}",
                "images do not go in this folder, so this one is not used. Move it to content/images/.",
            )
        elif suffix in extra_ok:
            continue
        else:
            problems.warn(
                f"{where_of_dir}/{path.name}", "this file type is ignored by the site. Use a .md file here."
            )
    return files


def scan_images(content_dir):
    """All pictures directly in content/images/: stem -> [paths]. Pictures are paired with pages and papers by name."""
    found = {}
    folder = Path(content_dir) / "images"
    if folder.is_dir():
        for path in sorted(folder.iterdir()):
            if path.is_file() and path.suffix.lower() in IMAGE_EXTS and not path.name.startswith("."):
                found.setdefault(path.stem, []).append(path)
    return found


def own_image(images, stem):
    """The picture named like `stem`, if there is exactly one (problems are reported by check_images)."""
    paths = images.get(stem, [])
    return paths[0] if len(paths) == 1 else None


def check_images(images, root, content_dir, slugs_by_kind, referenced, problems):
    """Report images that cannot be paired: ambiguous names, wrong capitals, duplicates and unused pictures.

    `slugs_by_kind` maps 'person' / 'paper' / 'research theme' to the names of their files; `referenced` holds image
    file names used explicitly (logos in lab.yaml, the hero in home.md, `image:` lines).
    """
    where_dir = where_of(Path(content_dir) / "images", root)
    owners = {}
    for kind, slugs in slugs_by_kind.items():
        for slug in slugs:
            owners.setdefault(slug, []).append(kind)
    for stem, paths in sorted(images.items()):
        kinds = owners.get(stem, [])
        for index, path in enumerate(paths):
            where = f"{where_dir}/{path.name}"
            if len(kinds) > 1:
                problems.error(
                    where,
                    f"the name '{stem}' belongs to both a {kinds[0]} and a {kinds[1]}, so this image cannot be paired. "
                    "Rename one of the two files.",
                )
            elif kinds:
                if index > 0:
                    problems.error(where, f"there are two images named '{stem}'. Keep one and delete the other.")
            elif path.name in referenced:
                continue
            elif stem.lower() in owners:
                problems.error(
                    where,
                    f"rename the image to '{stem.lower()}{path.suffix.lower()}' (lowercase, same name as the page or paper it belongs to). "
                    "GitHub is case-sensitive, so 'Photo.JPG' and 'photo.jpg' are different files.",
                )
            else:
                problems.warn(
                    where,
                    "this image doesn't match any person, paper or research theme, and isn't used in lab.yaml or home.md, "
                    "so it isn't shown. Rename it to match the page or paper it belongs to.",
                )


def resolve_field_image(directory, filename, where, problems, hint="content/images/"):
    directory = Path(directory)
    path = directory / str(filename)
    if path.is_file():
        return path
    for other in (directory.iterdir() if directory.is_dir() else ()):
        if other.name.lower() == str(filename).lower():
            problems.error(where, f"'image: {filename}' must match the file name exactly; the file is called '{other.name}'.")
            return None
    problems.error(where, f"image '{filename}' was not found in {hint}. Upload it there, or fix the name.")
    return None


# --------------------------------------------------------------------------- loaders

LAB_SPEC = {
    "name": {"required": True, "example": "Computational & Cognitive Neuroscience Lab"},
    "short_name": {"required": True, "example": "CCNL"},
    "tagline": {},
    "department": {},
    "institution": {},
    "institution_logo": {"example": "dartmouth-logo.svg"},
    "institution_url": {"example": "https://www.dartmouth.edu"},
    "credit": {"example": "Logo: Wikimedia Commons, CC BY-SA 4.0"},
    "address": {"type": "list"},
    "email": {},
    "funders": {"type": "list"},
    "social": {"type": "dict"},
}
SOCIAL_KEYS = ("github", "bluesky", "scholar", "twitter", "linkedin", "youtube")


def load_yaml(path, where, problems):
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8-sig")) or {}
    except (OSError, yaml.YAMLError) as exc:
        problems.error(where, f"could not read this file as YAML ({exc}).")
        return None
    if not isinstance(data, dict):
        problems.error(where, "must be a set of 'name: value' lines.")
        return None
    return data


def load_lab(content_dir, root, problems):
    path = Path(content_dir) / "lab.yaml"
    where = where_of(path, root)
    if not path.is_file():
        problems.error(where, "this file is missing. It holds the lab name, address and contact details.")
        return {}
    data = load_yaml(path, where, problems)
    if data is None:
        return {}
    lab = check_meta(data, where, LAB_SPEC, problems)
    lab["address"] = [str(line) for line in (lab["address"] or [])]
    if lab["email"]:
        lab["email"] = split_email(lab["email"], where, problems)
    if lab["institution_url"]:
        lab["institution_url"] = check_url(lab["institution_url"], where, "institution_url", problems)
    if lab["institution_logo"] and not (Path(content_dir) / "images" / lab["institution_logo"]).is_file():
        problems.error(where, f"institution_logo '{lab['institution_logo']}' was not found in content/images/.")
        lab["institution_logo"] = None
    funders = []
    for i, item in enumerate(lab["funders"] or [], 1):
        if not isinstance(item, dict) or not item.get("name"):
            problems.error(where, f"funders item {i} needs at least a 'name:' line.")
            continue
        unknown = set(item) - {"name", "logo", "url"}
        if unknown:
            problems.error(where, f"funders item {i} has unknown field(s): {', '.join(sorted(unknown))}. Allowed: name, logo, url.")
        funder = {"name": str(item["name"]), "logo": item.get("logo"), "url": None}
        if item.get("url"):
            funder["url"] = check_url(item["url"], where, f"funders item {i} url", problems)
        if funder["logo"] and not (Path(content_dir) / "images" / str(funder["logo"])).is_file():
            problems.error(where, f"funders item {i}: logo '{funder['logo']}' was not found in content/images/.")
            funder["logo"] = None
        funders.append(funder)
    lab["funders"] = funders
    social = []
    for key, value in (lab["social"] or {}).items():
        if key not in SOCIAL_KEYS:
            problems.error(where, f"social: unknown site '{key}'. Allowed: {', '.join(SOCIAL_KEYS)}.")
            continue
        url = check_url(value, where, f"social {key}", problems)
        if url:
            social.append({"label": key.capitalize() if key != "github" else "GitHub", "url": url})
    lab["social"] = social
    return lab


def load_nav(content_dir, root, problems):
    path = Path(content_dir) / "site.yaml"
    where = where_of(path, root)
    if not path.is_file():
        problems.error(where, "this file is missing. It lists the pages in the top menu.")
        return []
    data = load_yaml(path, where, problems)
    if data is None:
        return []
    unknown = set(data) - {"nav"}
    if unknown:
        problems.error(where, f"unknown field(s): {', '.join(sorted(unknown))}. Only 'nav' is allowed.")
    nav = []
    for i, item in enumerate(data.get("nav") or [], 1):
        if not isinstance(item, dict) or "page" not in item or "label" not in item:
            problems.error(where, f"nav item {i} must look like: - {{label: People, page: people}}")
            continue
        if item["page"] not in PAGES:
            close = difflib.get_close_matches(str(item["page"]), PAGES, n=1)
            hint = f" Did you mean '{close[0]}'?" if close else ""
            problems.error(where, f"nav item {i}: unknown page '{item['page']}'. Pages: {', '.join(PAGES)}.{hint}")
            continue
        nav.append({"label": str(item["label"]), "page": item["page"]})
    if not nav:
        problems.error(where, "the menu is empty. Add at least a 'home' entry.")
    return nav


TEXT_PAGE_SPEC = {
    "headline": {"example": "How does the brain learn flexibly?"},
    "hero_image": {"example": "lab-group.jpg"},
    "hero_alt": {"example": "Lab members around a table at the 2026 retreat"},
    "recruiting": {"choices": ("open", "closed"), "example": "closed"},
    "updated": {"type": "month", "example": "2026-10"},
}


def load_text_page(content_dir, root, name, problems, required, today, allowed=("headline", "recruiting", "updated")):
    """Load content/<name>.md: front matter limited to `allowed` fields, plus the Markdown body as HTML."""
    path = Path(content_dir) / f"{name}.md"
    where = where_of(path, root)
    if not path.is_file():
        if required:
            problems.error(where, "this file is missing but the page is used by the site.")
        return None
    meta, body = read_front_matter(path, where, problems)
    if meta is None:
        return None
    spec = {k: v for k, v in TEXT_PAGE_SPEC.items() if k in allowed}
    clean = check_meta(meta, where, spec, problems)
    check_stale(clean.get("updated"), where, today, problems)
    if clean.get("hero_image"):
        if not (Path(content_dir) / "images" / clean["hero_image"]).is_file():
            problems.error(where, f"hero_image '{clean['hero_image']}' was not found in content/images/. Upload it there, or remove the line to use the default picture.")
            clean["hero_image"] = None
        elif not clean.get("hero_alt"):
            problems.warn(where, "add `hero_alt:` describing the photo in a sentence, for people who use screen readers.")
    return {**clean, "html": render_markdown(body), "where": where, "hero": None}


RESEARCH_SPEC = {
    "title": {"required": True, "example": "Adaptive learning and decision making"},
    "order": {"type": "int", "example": "1"},
    "image": {"example": "figure.png"},
    "image_alt": {"example": "Diagram of a neuron whose firing rate depends on recent rewards"},
}


def load_research(content_dir, root, problems, images):
    folder = Path(content_dir) / "research"
    themes = []
    if not folder.is_dir():
        return themes
    where_dir = where_of(folder, root)
    files = list_md(folder, where_dir, problems)
    for path in files:
        where = where_of(path, root)
        check_slug(path, where, problems)
        meta, body = read_front_matter(path, where, problems)
        if meta is None:
            continue
        clean = check_meta(meta, where, RESEARCH_SPEC, problems)
        # the figure is content/images/<same name as the theme file>.jpg, or the file named in `image:`
        if clean["image"]:
            image_src = resolve_field_image(Path(content_dir) / "images", clean["image"], where, problems)
        else:
            image_src = own_image(images, path.stem)
        if image_src and not clean["image_alt"]:
            problems.warn(where, "add `image_alt:` describing the figure in a sentence, for people who use screen readers.")
        themes.append(
            {
                "slug": path.stem,
                "title": clean["title"] or path.stem,
                "order": clean["order"] if clean["order"] is not None else 1000,
                "html": render_markdown(body),
                "image_src": image_src,
                "image_name": clean["image"],
                "image": None,
                "image_alt": clean["image_alt"] or "",
                "where": where,
            }
        )
    themes.sort(key=lambda t: (t["order"], t["title"]))
    return themes


PEOPLE_SPEC = {
    "name": {"required": True, "example": "Jane Doe"},
    "role": {"required": True, "choices": ROLES, "example": "grad"},
    "status": {"required": True, "choices": ("current", "alumni"), "example": "current"},
    "start": {"type": "year", "example": "2022"},
    "end": {"type": "year"},
    "degrees": {},
    "current_position": {},
    "profile": {"type": "bool"},
    "links": {"type": "dict"},
}
LINK_KEYS = ("scholar", "orcid", "github", "website", "cv", "linkedin", "bluesky", "email")


def build_person_links(links, where, problems):
    """Return (list of {label,url}, email dict or None)."""
    out, email = [], None
    for key, value in (links or {}).items():
        if key not in LINK_KEYS:
            close = difflib.get_close_matches(str(key), LINK_KEYS, n=1)
            hint = f" Did you mean '{close[0]}'?" if close else f" Allowed: {', '.join(LINK_KEYS)}."
            problems.error(where, f"links: unknown entry '{key}'.{hint}")
            continue
        value = str(value).strip()
        if key == "email":
            email = split_email(value, where, problems)
        elif key == "orcid":
            if ORCID.match(value):
                out.append({"label": "ORCID", "url": f"https://orcid.org/{value}"})
            else:
                url = check_url(value, where, "links orcid", problems)
                if url:
                    out.append({"label": "ORCID", "url": url})
        elif key == "github":
            if re.match(r"^[A-Za-z0-9-]+$", value):
                out.append({"label": "GitHub", "url": f"https://github.com/{value}"})
            else:
                url = check_url(value, where, "links github", problems)
                if url:
                    out.append({"label": "GitHub", "url": url})
        else:
            url = check_url(value, where, f"links {key}", problems)
            if url:
                labels = {"scholar": "Google Scholar", "website": "Website", "cv": "CV", "linkedin": "LinkedIn", "bluesky": "Bluesky"}
                out.append({"label": labels[key], "url": url})
    return out, email


def load_people(content_dir, root, problems, images):
    folder = Path(content_dir) / "people"
    people = []
    if not folder.is_dir():
        return people
    where_dir = where_of(folder, root)
    files = list_md(folder, where_dir, problems)
    for path in files:
        where = where_of(path, root)
        check_slug(path, where, problems)
        meta, body = read_front_matter(path, where, problems)
        if meta is None:
            continue
        clean = check_meta(meta, where, PEOPLE_SPEC, problems)
        if clean["status"] == "current" and clean["end"]:
            problems.error(where, "`end:` is set but `status` is current. Set `status: alumni` or remove `end:`.")
        if clean["start"] and clean["end"] and clean["end"] < clean["start"]:
            problems.error(where, f"`end: {clean['end']}` is before `start: {clean['start']}`.")
        links, email = build_person_links(clean["links"], where, problems)
        # Everyone except collaborators gets a profile page (minimal until they add a bio).
        # Collaborators are only listed, with their links. `profile: true/false` overrides either way.
        has_profile = clean["profile"] if clean["profile"] is not None else clean["role"] != "collaborator"
        people.append(
            {
                "slug": path.stem,
                "name": clean["name"] or path.stem,
                "role": clean["role"],
                "role_label": ROLE_LABELS.get(clean["role"], ""),
                "status": clean["status"],
                "start": clean["start"],
                "end": clean["end"],
                "years": years_label(clean["start"], clean["end"], clean["status"]),
                "degrees": clean["degrees"],
                "current_position": clean["current_position"],
                "profile": has_profile,
                "links": links,
                "email": email,
                "html": render_markdown(body),
                "photo_src": own_image(images, path.stem),  # content/images/<same name as the profile file>.jpg
                "photo": None,
                "where": where,
            }
        )
    return people


def years_label(start, end, status):
    """Text like '2022\u2013present', '2014\u20132019', '2019' or 'until 2020' ('' if no years are known)."""
    if start and end:
        return f"{start}" if start == end else f"{start}\u2013{end}"
    if start:
        return f"{start}\u2013present" if status == "current" else f"{start}"
    if end:
        return f"until {end}"
    return ""


def group_alumni(alumni):
    """Alumni (already newest first) split into subsections by role, in the same order as the current groups."""
    groups = []
    for role in ROLES:
        members = [p for p in alumni if p["role"] == role]
        if members:
            groups.append({"role": role, "title": ROLE_GROUP_TITLES[role], "people": members})
    return groups


def group_people(people):
    """Current people grouped by role in a fixed order; alumni as one list, newest first."""
    groups = []
    for role in ROLES:
        members = [p for p in people if p["status"] == "current" and p["role"] == role]
        members.sort(key=lambda p: (p["start"] or 9999, p["name"].lower()))
        if members:
            groups.append({"role": role, "title": ROLE_GROUP_TITLES[role], "people": members})
    alumni = [p for p in people if p["status"] == "alumni"]
    alumni.sort(key=lambda p: (-(p["end"] or 0), p["name"].lower()))
    return groups, alumni


# ----- publications

VENUE_FIELDS = ("journal", "booktitle", "howpublished", "publisher", "school", "institution")
LINK_LABELS = (("pdf", "PDF"), ("preprint", "Preprint"), ("si", "SI"), ("data", "Data"), ("code", "Code"),
               ("video", "Video"), ("slides", "Slides"), ("poster", "Poster"), ("url", "Link"))
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def clean_bib_text(value):
    value = latex_to_unicode(str(value))
    return re.sub(r"\s+", " ", value.replace("{", "").replace("}", "").replace("--", "\u2013")).strip()


def parse_authors(raw):
    names = []
    for part in re.split(r"\s+and\s+", re.sub(r"\s+", " ", raw)):
        part = clean_bib_text(part)
        if not part:
            continue
        if part.lower() == "others":
            names.append({"last": "", "initials": "", "etal": True})
            continue
        if "," in part:
            last, first = [p.strip() for p in part.split(",", 1)]
        else:
            tokens = part.split()
            last, first = tokens[-1], " ".join(tokens[:-1])
        # "MC" is already initials (keep both letters); "Xiao-Jing" and "Jane Q." give one letter per name part
        initials = "".join(tok if (tok.isupper() and len(tok) > 1) else tok[0] for tok in re.split(r"[\s.\-]+", first) if tok)
        names.append({"last": last, "initials": initials.upper(), "etal": False})
    return names


def month_label(value, year, where, key, problems):
    """'Nov 2026' from `month = {11}` / `{nov}` / `{November}`; just the year when there is no month."""
    text = clean_bib_text(value or "")
    if not text:
        return str(year)
    number = int(text) if text.isdigit() else next((i for i, m in enumerate(MONTHS, 1) if text.lower().startswith(m.lower())), 0)
    if not 1 <= number <= 12:
        problems.error(where, f"entry '{key}': `month` must be a number from 1 to 12 or a month name like `nov` (got '{text}').")
        return str(year)
    return f"{MONTHS[number - 1]} {year}"


def clean_bibtex(text):
    """The entry as shown on the paper's page: no comments before it and no blank `field = {}` lines."""
    start = re.search(r"^\s*@", text, re.M)
    raw = text[start.start():] if start else text
    return "\n".join(l for l in raw.strip().splitlines() if not re.match(r"\s*\w+\s*=\s*\{\s*\}\s*,?\s*$", l))


def split_keywords(value):
    """`keywords = {learning, decision making; reward}` -> ['learning', 'decision making', 'reward'] (no repeats)."""
    text = clean_bib_text(value or "")
    seen, out = set(), []
    for word in (w.strip() for w in re.split(r";" if ";" in text else ",", text)):
        if word and word.lower() not in seen:
            seen.add(word.lower())
            out.append(word)
    return out


def format_citation(authors, year, title, venue, volume, number, pages, doi_url):
    """One plain-text reference in a fixed APA-like style, built from the BibTeX fields."""
    names = ["et al." if a.get("etal") else f"{a['last']}, {'. '.join(a['initials'])}." for a in authors]
    if len(names) > 1 and not authors[-1].get("etal"):
        names[-1] = "& " + names[-1]
    text = f"{', '.join(names)} ({year}). {title}"
    text += "" if title[-1] in ".?!" else "."
    where = venue + (f", {volume}" if volume else "") + (f"({number})" if volume and number else "") + (f", {pages}" if pages else "")
    return f"{text} {where}." + (f" {doi_url}" if doi_url else "")


def name_list(value):
    return [n.strip() for n in re.split(r"\s*[;,]\s*|\s+and\s+", clean_bib_text(value)) if n.strip()]


def load_publications(content_dir, root, problems, images):
    folder = Path(content_dir) / "publications"
    pubs, seen_keys = [], {}
    if not folder.is_dir():
        return pubs
    where_dir = where_of(folder, root)
    for path in sorted(folder.iterdir()):
        if path.name.startswith((".", "_")) or path.is_dir():
            continue
        where = where_of(path, root)
        if path.suffix.lower() in IMAGE_EXTS:
            problems.warn(where, "images do not go in this folder, so this one is not used. Move it to content/images/.")
            continue
        if path.suffix.lower() != ".bib":
            problems.warn(where, "this file type is ignored by the site. Publications must be .bib files.")
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as exc:
            problems.error(where, f"could not read the file ({exc}). Save it as plain UTF-8 text.")
            continue
        parser = BibTexParser(common_strings=True, ignore_nonstandard_types=False)
        try:
            db = bibtexparser.loads(text, parser)
        except Exception as exc:  # the parser is lenient but can still raise on garbage
            problems.error(where, f"could not parse this BibTeX ({exc.__class__.__name__}). Check that braces {{ }} and commas are balanced.")
            continue
        if len(db.entries) == 0:
            problems.error(
                where,
                "no valid BibTeX entry found. It should look like `@article{smith2024, author = {...}, title = {...}, "
                "journal = {...}, year = {2024}}`. Check that braces { } and commas are balanced.",
            )
            continue
        if len(db.entries) > 1:
            problems.error(where, f"contains {len(db.entries)} entries. Use one .bib file per paper.")
            continue
        entry = {k.lower(): v for k, v in db.entries[0].items()}
        key = entry.get("id", path.stem)
        if key in seen_keys:
            problems.error(where, f"BibTeX key '{key}' is also used in {seen_keys[key]}. Keys must be unique.")
            continue
        seen_keys[key] = where_of(path, root)

        missing = [f for f in ("author", "title", "year") if not entry.get(f)]
        if missing:
            problems.error(where, f"entry '{key}' is missing: {', '.join(missing)}. Add a line like `{missing[0]} = {{...}},`.")
            continue
        venue = next((clean_bib_text(entry[f]) for f in VENUE_FIELDS if entry.get(f)), None)
        status = entry.get("status", "").strip().lower()
        preprint = status == "preprint" or entry.get("entrytype") == "unpublished"
        if not venue and entry.get("eprint"):
            venue = clean_bib_text(entry.get("archiveprefix") or "preprint")
        if not venue:
            problems.error(where, f"entry '{key}' needs a journal (or booktitle, howpublished, publisher). Add `journal = {{...}},`.")
            continue
        if status and status != "preprint":
            problems.error(where, f"entry '{key}': `status` must be `preprint` (or left out for a published paper), got '{status}'.")
        year_text = clean_bib_text(entry["year"])
        if not re.fullmatch(r"\d{4}", year_text):
            problems.error(where, f"entry '{key}': year must be four digits like 2024 (got '{year_text}').")
            continue

        authors = parse_authors(entry["author"])
        if not authors:
            problems.error(where, f"entry '{key}': the author field is empty.")
            continue
        lasts = {a["last"].lower() for a in authors}
        for field in ("cofirst", "corresponding"):
            marked = {n.lower() for n in name_list(entry.get(field, ""))}
            unmatched = marked - lasts
            if unmatched:
                problems.error(
                    where,
                    f"entry '{key}': `{field}` lists {', '.join(sorted(unmatched))}, who is not among the authors "
                    f"({', '.join(a['last'] for a in authors if a['last'])}). Use last names exactly as they appear in the author field.",
                )
            for a in authors:
                a[field] = a["last"].lower() in marked

        links = []
        for field, label in LINK_LABELS:
            if entry.get(field):
                url = check_url(entry[field].strip(), where, field, problems)
                if url:
                    links.append({"label": label, "url": url})
        doi_url = None
        if entry.get("doi"):
            doi = entry["doi"].strip()
            doi_url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
            links.insert(0, {"label": "DOI", "url": doi_url})
        pmid = clean_bib_text(entry.get("pmid", ""))
        if pmid and not pmid.isdigit():
            problems.error(where, f"entry '{key}': `pmid` must be just the number, like `pmid = {{12345678}}` (got '{pmid}').")
            pmid = ""
        if pmid:
            links.append({"label": "PubMed", "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"})
        if not SLUG.match(path.stem):
            problems.error(where, "the file name must use only lowercase letters, digits and hyphens, e.g. '2026-doe-learning.bib'. It becomes the web address of the paper's page. Rename the file.")
            continue
        volume, number = clean_bib_text(entry.get("volume", "")), clean_bib_text(entry.get("number", ""))
        pages = clean_bib_text(entry.get("pages", "")).replace("--", "–")

        # the thumbnail is content/images/<same name as the .bib file>.jpg, or the file named in `image =`
        if entry.get("image"):
            image_src = resolve_field_image(Path(content_dir) / "images", entry["image"].strip(), where, problems)
        else:
            image_src = own_image(images, path.stem)
        pubs.append(
            {
                "key": key,
                "slug": path.stem,  # the paper's page is publications/<file name>/
                "title": clean_bib_text(entry["title"]),
                "authors": authors,
                "year": int(year_text),
                "date": month_label(entry.get("month"), year_text, where, key, problems),
                "venue": venue,
                "volume": volume,
                "number": number,
                "pages": pages,
                "keywords": split_keywords(entry.get("keywords") or entry.get("keyword")),
                "doi": doi_url,
                "pmid": pmid,
                "citation": format_citation(authors, year_text, clean_bib_text(entry["title"]), venue, volume, number, pages, doi_url),
                "bibtex": clean_bibtex(text),
                "links": links,
                "note": clean_bib_text(entry.get("note", "")),
                "abstract": clean_bib_text(entry.get("abstract", "")),
                "related": [],
                "preprint": preprint,
                "search": " ".join(clean_bib_text(v) for k, v in entry.items() if k not in ("image", "id", "entrytype") and v),  # every BibTeX field, for the search box
                "image_src": image_src,
                "image_name": entry["image"].strip() if entry.get("image") else None,
                "image": None,
                "where": where,
            }
        )
    pubs.sort(key=lambda p: (-p["year"], p["key"]))
    return pubs


# ----- resources and teaching

RESOURCE_SPEC = {
    "title": {"required": True, "example": "Salience-driven value construction"},
    "paper": {"example": "smith2024"},
    "links": {"type": "list"},
}


def load_resources(content_dir, root, problems):
    folder = Path(content_dir) / "resources"
    items = []
    if not folder.is_dir():
        return items
    where_dir = where_of(folder, root)
    for path in list_md(folder, where_dir, problems):
        where = where_of(path, root)
        check_slug(path, where, problems)
        meta, body = read_front_matter(path, where, problems)
        if meta is None:
            continue
        clean = check_meta(meta, where, RESOURCE_SPEC, problems)
        links = []
        for i, link in enumerate(clean["links"] or [], 1):
            if not isinstance(link, dict) or not link.get("label") or not link.get("url"):
                problems.error(where, f"links item {i} must have both a label and a url, e.g. `- {{label: Code, url: https://...}}`.")
                continue
            url = check_url(link["url"], where, f"links item {i} url", problems)
            if url:
                links.append({"label": str(link["label"]), "url": url})
        items.append(
            {
                "slug": path.stem,
                "title": clean["title"] or path.stem,
                "paper": clean["paper"],
                "paper_pub": None,
                "links": links,
                "html": render_markdown(body),
                "where": where,
            }
        )
    items.sort(key=lambda i: i["title"].lower())
    return items


TEACHING_SPEC = {
    "code": {"required": True, "example": "PSYC 50.02"},
    "title": {"required": True, "example": "Decision making"},
    "next_offering": {"example": "Winter 2027"},
    "updated": {"type": "month", "example": "2026-10"},
}


def load_teaching(content_dir, root, problems, today):
    folder = Path(content_dir) / "teaching"
    courses = []
    if not folder.is_dir():
        return courses
    where_dir = where_of(folder, root)
    for path in list_md(folder, where_dir, problems):
        where = where_of(path, root)
        check_slug(path, where, problems)
        meta, body = read_front_matter(path, where, problems)
        if meta is None:
            continue
        clean = check_meta(meta, where, TEACHING_SPEC, problems)
        check_stale(clean["updated"], where, today, problems)
        courses.append(
            {
                "slug": path.stem,
                "code": clean["code"] or "",
                "title": clean["title"] or path.stem,
                "next_offering": clean["next_offering"],
                "html": render_markdown(body),
                "where": where,
            }
        )
    courses.sort(key=lambda c: c["code"])
    return courses


# --------------------------------------------------------------------------- everything


def ascii_key(text):
    return re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower())


def person_key(name):
    """'last|initial' for a person's name, the form bibliographies use ('Michael (Chong) Wang' -> 'wang|m')."""
    tokens = [t for t in name.split() if ascii_key(t)]
    return f"{ascii_key(tokens[-1])}|{ascii_key(tokens[0])[0]}" if len(tokens) >= 2 else None


def member_keys(people):
    """Keys for everyone listed on the People page."""
    return {key for key in (person_key(p["name"]) for p in people) if key}


def style_authors(publications, people):
    """Flag authors who are listed in People and prepare their CSS classes and screen-reader text."""
    keys = member_keys(people)
    profile_slugs = {}
    for person in people:
        if person.get("profile"):
            profile_slugs.setdefault(person_key(person["name"]), person["slug"])
    for pub in publications:
        for a in pub["authors"]:
            if a.get("etal"):
                continue
            a["key"] = f"{ascii_key(a['last'])}|{a['initials'][0].lower()}" if a["initials"] else None
            a["member"] = a["key"] in keys
            a["slug"] = profile_slugs.get(a["key"])  # lets a paper's page link the author to their profile
            roles = [(a["member"], "member", "lab member"), (a.get("cofirst"), "cofirst", "co-first author"),
                     (a.get("corresponding"), "corr", "corresponding author")]
            a["classes"] = " ".join(f"au-{css}" for on, css, _ in roles if on)
            a["role_text"] = ", ".join(text for on, _, text in roles if on)


def author_roles(publications):
    """Which author styles occur, for the legend on the Publications page."""
    authors = [a for p in publications for a in p["authors"] if not a.get("etal")]
    return {"member": any(a["member"] for a in authors), "cofirst": any(a.get("cofirst") for a in authors),
            "corresponding": any(a.get("corresponding") for a in authors)}


def load_site(content_dir, root, problems, today=None):
    today = today or datetime.date.today()
    content_dir = Path(content_dir)
    if not content_dir.is_dir():
        problems.error(str(content_dir), "the content folder does not exist.")
        return {}

    lab = load_lab(content_dir, root, problems)
    nav = load_nav(content_dir, root, problems)
    nav_pages = {item["page"] for item in nav}

    home = load_text_page(content_dir, root, "home", problems, True, today, allowed=("headline", "hero_image", "hero_alt"))
    about = load_text_page(content_dir, root, "about", problems, "about" in nav_pages, today, allowed=())
    join = load_text_page(content_dir, root, "join", problems, False, today, allowed=("recruiting", "updated"))  # shown on the Contact page

    images = scan_images(content_dir)
    research = load_research(content_dir, root, problems, images)
    people = load_people(content_dir, root, problems, images)
    for person in people:  # shown on the cards: where they are now, or the lab's institution for current members
        person["affiliation"] = person["current_position"] or (
            (lab.get("institution") or "") if person["status"] == "current" and person["role"] != "collaborator" else "")
    publications = load_publications(content_dir, root, problems, images)
    resources = load_resources(content_dir, root, problems)
    teaching = load_teaching(content_dir, root, problems, today)

    by_key = {p["key"]: p for p in publications}
    for item in resources:
        if item["paper"]:
            if item["paper"] in by_key:
                item["paper_pub"] = by_key[item["paper"]]
            else:
                problems.error(
                    item["where"],
                    f"`paper: {item['paper']}` does not match any publication. Use the BibTeX key (the text after `@article{{` in the .bib file).",
                )

    # Pictures used by name elsewhere (logos, hero, `image:` lines) are exempt from the "unused picture" warning
    site_image_names = {f["logo"] for f in lab.get("funders", []) if f.get("logo")}
    for name in (lab.get("institution_logo"), (home or {}).get("hero_image")):
        if name:
            site_image_names.add(name)
    bib_stems = {p.stem for p in (content_dir / "publications").glob("*.bib") if not p.name.startswith((".", "_"))} if (content_dir / "publications").is_dir() else set()
    check_images(
        images,
        root,
        content_dir,
        {"person": {p["slug"] for p in people}, "paper": bib_stems, "research theme": {t["slug"] for t in research}},
        site_image_names | {x["image_name"] for x in research + publications if x.get("image_name")},
        problems,
    )

    style_authors(publications, people)
    for pub in publications:  # up to four other papers that share keywords with this one (most shared first, then newest)
        mine = {k.lower() for k in pub["keywords"]}
        scored = [(len(mine & {k.lower() for k in o["keywords"]}), o) for o in publications if o is not pub and mine]
        ranked = sorted((x for x in scored if x[0]), key=lambda x: (-x[0], -x[1]["year"], x[1]["key"]))
        pub["related"] = [{k: o[k] for k in ("slug", "title", "year", "venue")} for _, o in ranked[:4]]
    for person in people:  # each profile page lists the person's own papers (newest first, as loaded)
        person["author_key"] = person_key(person["name"])
        person["publications"] = [
            pub for pub in publications if person["author_key"] and any(a.get("key") == person["author_key"] for a in pub["authors"])
        ]
    people_groups, alumni = group_people(people)
    return {
        "content_dir": content_dir,
        "lab": lab,
        "nav": nav,
        "home": home,
        "about": about,
        "join": join,
        "research": research,
        "people": people,
        "people_groups": people_groups,
        "alumni": alumni,
        "alumni_groups": group_alumni(alumni),
        "publications": publications,
        "author_roles": author_roles(publications),
        "resources": resources,
        "teaching": teaching,
        "site_image_names": sorted(site_image_names),
        "today": today,
    }
