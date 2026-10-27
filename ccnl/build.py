"""Turn the loaded content into a static site in an output folder."""

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .content import load_site, where_of
from .images import IMAGE_EXTS, process_image
from .problems import BuildFailed, Problems

PAGE_TEMPLATES = {
    "home": "home.html",
    "about": "about.html",
    "research": "research.html",
    "people": "people.html",
    "publications": "publications.html",
    "join": "join.html",
    "resources": "resources.html",
    "teaching": "teaching.html",
    "contact": "contact.html",
}


def process_site_images(site, out_dir, root, problems):
    """Resize/clean every image and record the output file names on the content."""
    images_out = Path(out_dir) / "images"

    for person in site["people"]:
        if person["photo_src"]:
            person["photo"] = process_image(
                person["photo_src"], images_out / "people", person["slug"], 700, person["where"], problems
            )
            if person["photo"]:
                person["photo"] = f"people/{person['photo']}"
    for theme in site["research"]:
        if theme["image_src"]:
            name = process_image(theme["image_src"], images_out / "research", theme["slug"], 1400, theme["where"], problems)
            theme["image"] = f"research/{name}" if name else None
    for pub in site["publications"]:
        if pub["image_src"]:
            name = process_image(pub["image_src"], images_out / "publications", pub["key"], 500, pub["where"], problems)
            pub["image"] = f"publications/{name}" if name else None

    # site-wide images (logos, banners): keep their names so lab.yaml can refer to them
    site_images = Path(site["content_dir"]) / "images"
    logo_stems = {Path(f["logo"]).stem for f in site["lab"].get("funders", []) if f["logo"]}
    if site_images.is_dir():
        for path in sorted(site_images.iterdir()):
            if path.suffix.lower() in IMAGE_EXTS and not path.name.startswith("."):
                max_px = 480 if path.stem in logo_stems else 2000  # logos are shown about 48px tall
                process_image(path, images_out / "site", path.stem, max_px, where_of(path, root), problems)
    hero = site["home"].get("hero_image") if site["home"] else None
    if hero:
        produced = list((images_out / "site").glob(f"{Path(hero).stem}.*"))
        site["home"]["hero"] = f"site/{produced[0].name}" if produced else None
    for funder in site["lab"].get("funders", []):
        if funder["logo"]:
            stem = Path(funder["logo"]).stem
            produced = list((images_out / "site").glob(f"{stem}.*"))
            funder["logo"] = f"site/{produced[0].name}" if produced else None


def make_environment(templates_dir, base_path, site):
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    base = base_path.rstrip("/")

    def url(path=""):
        return f"{base}/{path.lstrip('/')}" if path else f"{base}/"

    env.globals.update(
        url=url,
        lab=site["lab"],
        nav=site["nav"],
        year=site["today"].year,
        base_path=base,
    )
    return env


def write_page(env, out_dir, rel_dir, template, **context):
    target = Path(out_dir) / rel_dir
    target.mkdir(parents=True, exist_ok=True)
    html = env.get_template(template).render(**context)
    (target / "index.html").write_text(html, encoding="utf-8")


def render_site(site, out_dir, templates_dir, static_dir, base_path):
    env = make_environment(templates_dir, base_path, site)
    selected = [p for p in site["publications"] if p["selected"]]
    built_pages = {item["page"] for item in site["nav"]} | {"home"}
    env.globals["pages"] = built_pages  # templates link to optional pages (e.g. join) only if they exist

    for page, template in PAGE_TEMPLATES.items():
        if page not in built_pages:
            continue
        rel = "" if page == "home" else f"{page}/"
        write_page(
            env,
            out_dir,
            rel,
            template,
            page=page,
            site=site,
            selected_publications=selected,
        )
    for person in site["people"]:
        if person["profile"]:
            write_page(env, out_dir, f"people/{person['slug']}/", "person.html", page="people", person=person, site=site)

    (Path(out_dir) / "404.html").write_text(
        env.get_template("404.html").render(page="404", site=site), encoding="utf-8"
    )
    (Path(out_dir) / ".nojekyll").write_text("", encoding="utf-8")  # tell GitHub Pages not to run Jekyll
    if Path(static_dir).is_dir():
        shutil.copytree(static_dir, Path(out_dir) / "static")


def build(content_dir, out_dir, templates_dir, static_dir, base_path="", root=".", today=None, problems=None):
    """Build the site. Raises BuildFailed (after recording errors in `problems`) if anything is wrong.

    The output folder is only replaced when the whole build succeeds.
    """
    problems = problems or Problems()
    site = load_site(content_dir, root, problems, today)
    problems.raise_if_errors()

    out_dir = Path(out_dir)
    tmp_dir = out_dir.with_name(out_dir.name + ".tmp")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)
    try:
        process_site_images(site, tmp_dir, root, problems)
        problems.raise_if_errors()
        render_site(site, tmp_dir, templates_dir, static_dir, base_path)
    except BuildFailed:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    if out_dir.exists():
        shutil.rmtree(out_dir)
    tmp_dir.rename(out_dir)
    return site
