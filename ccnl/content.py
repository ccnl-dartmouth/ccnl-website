"""Load and validate everything under content/.

Every problem is reported with the file name and a plain-language fix. Problems are
collected (not raised one by one) so a member sees all of them in a single build.
"""

import datetime
import difflib
import re
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
PAGES = ("home", "about", "research", "people", "publications", "join", "resources", "teaching", "contact")
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
    """Markdown files in a collection folder (sorted); warns about files that will be ignored."""
    files = []
    for path in sorted(Path(directory).iterdir()):
        if path.name.startswith((".", "_")) or path.name.lower() == "readme.md" or path.is_dir():
            continue
        suffix = path.suffix.lower()
        if suffix == ".md":
            files.append(path)
        elif suffix in IMAGE_EXTS or suffix in extra_ok:
            continue
        else:
            problems.warn(
                f"{where_of_dir}/{path.name}", "this file type is ignored by the site. Use a .md file (or an image) here."
            )
    return files


def find_same_name_images(directory, slugs, where_of_dir, problems):
    """Map slug -> image path for images named like the slug (case mismatches are errors)."""
    found = {}
    for path in sorted(Path(directory).iterdir()):
        if path.suffix.lower() not in IMAGE_EXTS or path.name.startswith("."):
            continue
        stem = path.stem
        if stem in slugs:
            if stem in found:
                problems.error(
                    f"{where_of_dir}/{path.name}",
                    f"there are two images named '{stem}'. Keep one and delete the other.",
                )
            else:
                found[stem] = path
        elif stem.lower() in slugs:
            problems.error(
                f"{where_of_dir}/{path.name}",
                f"rename the image to '{stem.lower()}{path.suffix.lower()}' (lowercase, same name as the .md file). "
                "GitHub is case-sensitive, so 'Photo.JPG' and 'photo.jpg' are different files.",
            )
        else:
            problems.warn(f"{where_of_dir}/{path.name}", "this image has no matching .md file with the same name, so it is not used.")
    return found


def resolve_field_image(directory, filename, where, problems):
    path = Path(directory) / str(filename)
    if path.is_file():
        return path
    for other in Path(directory).iterdir():
        if other.name.lower() == str(filename).lower():
            problems.error(where, f"'image: {filename}' must match the file name exactly; the file is called '{other.name}'.")
            return None
    problems.error(where, f"image '{filename}' was not found next to this file. Upload it to the same folder, or fix the name.")
    return None


# --------------------------------------------------------------------------- loaders

LAB_SPEC = {
    "name": {"required": True, "example": "Computational & Cognitive Neuroscience Lab"},
    "short_name": {"required": True, "example": "CCNL"},
    "tagline": {},
    "department": {},
    "institution": {},
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


def load_research(content_dir, root, problems):
    folder = Path(content_dir) / "research"
    themes = []
    if not folder.is_dir():
        return themes
    where_dir = where_of(folder, root)
    for path in list_md(folder, where_dir, problems):
        where = where_of(path, root)
        check_slug(path, where, problems)
        meta, body = read_front_matter(path, where, problems)
        if meta is None:
            continue
        clean = check_meta(meta, where, RESEARCH_SPEC, problems)
        image_src = resolve_field_image(folder, clean["image"], where, problems) if clean["image"] else None
        if clean["image"] and not clean["image_alt"]:
            problems.warn(where, "add `image_alt:` describing the figure in a sentence, for people who use screen readers.")
        themes.append(
            {
                "slug": path.stem,
                "title": clean["title"] or path.stem,
                "order": clean["order"] if clean["order"] is not None else 1000,
                "html": render_markdown(body),
                "image_src": image_src,
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


def load_people(content_dir, root, problems):
    folder = Path(content_dir) / "people"
    people = []
    if not folder.is_dir():
        return people
    where_dir = where_of(folder, root)
    files = list_md(folder, where_dir, problems)
    slugs = {p.stem for p in files}
    photos = find_same_name_images(folder, slugs, where_dir, problems)
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
        # Current lab members always get a profile page to fill in. Alumni and collaborators get one only if
        # their file has a bio. `profile: true/false` overrides either way.
        if clean["profile"] is not None:
            has_profile = clean["profile"]
        elif clean["status"] == "current" and clean["role"] != "collaborator":
            has_profile = True
        else:
            has_profile = bool(body.strip())
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
                "photo_src": photos.get(path.stem),
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

PUB_EXTRA_SPEC_FIELDS = ("pdf", "si", "data", "code", "url", "cofirst", "corresponding", "status", "selected", "note", "image")
VENUE_FIELDS = ("journal", "booktitle", "howpublished", "publisher", "school", "institution")
LINK_LABELS = (("pdf", "PDF"), ("si", "SI"), ("data", "Data"), ("code", "Code"), ("url", "Link"))


def clean_bib_text(value):
    value = latex_to_unicode(str(value))
    return re.sub(r"\s+", " ", value.replace("{", "").replace("}", "")).strip()


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
        initials = "".join(tok[0] for tok in re.split(r"[\s.\-]+", first) if tok)
        names.append({"last": last, "initials": initials.upper(), "etal": False})
    return names


def name_list(value):
    return [n.strip() for n in re.split(r"\s*[;,]\s*|\s+and\s+", clean_bib_text(value)) if n.strip()]


def load_publications(content_dir, root, problems):
    folder = Path(content_dir) / "publications"
    pubs, seen_keys = [], {}
    if not folder.is_dir():
        return pubs
    where_dir = where_of(folder, root)
    for path in sorted(folder.iterdir()):
        if path.name.startswith((".", "_")) or path.is_dir() or path.suffix.lower() in IMAGE_EXTS:
            continue
        where = where_of(path, root)
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
        if entry.get("doi"):
            doi = entry["doi"].strip()
            links.insert(0, {"label": "DOI", "url": doi if doi.startswith("http") else f"https://doi.org/{doi}"})

        image_src = resolve_field_image(folder, entry["image"].strip(), where, problems) if entry.get("image") else None
        selected_raw = entry.get("selected", "").strip().lower()
        if selected_raw not in ("", "true", "false", "yes", "no"):
            problems.error(where, f"entry '{key}': `selected` must be true or false (got '{selected_raw}').")
        pubs.append(
            {
                "key": key,
                "title": clean_bib_text(entry["title"]),
                "authors": authors,
                "year": int(year_text),
                "venue": venue,
                "volume": clean_bib_text(entry.get("volume", "")),
                "number": clean_bib_text(entry.get("number", "")),
                "pages": clean_bib_text(entry.get("pages", "")).replace("--", "–"),
                "links": links,
                "note": clean_bib_text(entry.get("note", "")),
                "abstract": clean_bib_text(entry.get("abstract", "")),
                "preprint": preprint,
                "selected": selected_raw in ("true", "yes"),
                "image_src": image_src,
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
    join = load_text_page(content_dir, root, "join", problems, "join" in nav_pages, today, allowed=("recruiting", "updated"))

    research = load_research(content_dir, root, problems)
    people = load_people(content_dir, root, problems)
    publications = load_publications(content_dir, root, problems)
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
        "publications": publications,
        "has_cofirst": any(a.get("cofirst") for p in publications for a in p["authors"]),
        "has_corresponding": any(a.get("corresponding") for p in publications for a in p["authors"]),
        "resources": resources,
        "teaching": teaching,
        "today": today,
    }
