from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

try:
    from bs4 import BeautifulSoup  # type: ignore
except ImportError as exc:
    raise SystemExit(
        "BeautifulSoup4 is niet geïnstalleerd. Installeer eerst: pip install beautifulsoup4"
    ) from exc


@dataclass
class DiyArticle:
    source_path: Path
    output_href: str
    title: str
    description: str
    lead: str
    category: str
    platform: str
    hardware: str
    image_src: str
    image_alt: str
    eyebrow: str
    sort_key: str


SKIP_FILES = {
    "index.html",
    "reviews.html",
    "review.html",
    "diy.html",
    "tutorials.html",
    "homey.html",
    "privacy.html",
    "over-ons.html",
    "over.html",
    "over-mij.html",
    "contact.html",
    "404.html",
    "header.html",
    "footer.html",
}

SKIP_NAME_PATTERNS = (
    "review-",
    "sjabloon-",
)

START_MARKER = "<!-- AUTO-GENERATED-DIY-CARDS:START -->"
END_MARKER = "<!-- AUTO-GENERATED-DIY-CARDS:END -->"


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def strip_site_suffix(title: str) -> str:
    return re.sub(r"\s*\|\s*huisvanvandaag\.nl\s*$", "", title, flags=re.IGNORECASE).strip()


def get_text(el) -> str:
    if not el:
        return ""
    return normalize_whitespace(el.get_text(" ", strip=True))


def find_meta_content(soup: BeautifulSoup, name: str) -> str:
    tag = soup.find("meta", attrs={"name": name})
    return normalize_whitespace(tag.get("content", "")) if tag else ""


def extract_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1:
        return get_text(h1)
    if soup.title and soup.title.string:
        return strip_site_suffix(normalize_whitespace(soup.title.string))
    return "Zonder titel"


def extract_lead(soup: BeautifulSoup) -> str:
    selectors = [
        "p.lead.muted",
        "p.lead",
        ".article-hero .lead",
        "main article p.lead",
    ]
    for selector in selectors:
        el = soup.select_one(selector)
        text = get_text(el)
        if text:
            return text
    return ""


def extract_category_meta(soup: BeautifulSoup) -> tuple[str, str, str]:
    pills = [get_text(p) for p in soup.select(".meta-list .meta-pill")]
    category = platform = hardware = ""
    for pill in pills:
        if ":" not in pill:
            continue
        key, value = [normalize_whitespace(part) for part in pill.split(":", 1)]
        key_l = key.lower()
        if key_l == "categorie":
            category = value
        elif key_l == "platform":
            platform = value
        elif key_l == "hardware":
            hardware = value
    return category, platform, hardware


def extract_hero_image(soup: BeautifulSoup) -> tuple[str, str]:
    selectors = [
        ".project-hero-media img",
        ".article-hero img",
        "main img",
    ]
    for selector in selectors:
        img = soup.select_one(selector)
        if img and img.get("src"):
            return normalize_whitespace(img.get("src", "")), normalize_whitespace(img.get("alt", ""))
    return "", ""


def extract_eyebrow(soup: BeautifulSoup) -> str:
    return get_text(soup.select_one(".eyebrow"))


def is_excluded_file(path: Path) -> bool:
    name = path.name.lower()
    if name in SKIP_FILES:
        return True
    return any(name.startswith(prefix) for prefix in SKIP_NAME_PATTERNS)


def has_diy_breadcrumb(soup: BeautifulSoup) -> bool:
    breadcrumbs = soup.select_one(".breadcrumbs")
    if not breadcrumbs:
        return False

    text = get_text(breadcrumbs).lower()
    if "diy" in text:
        return True

    for link in breadcrumbs.find_all("a", href=True):
        if re.search(r"(^|/)?diy\.html$", link["href"], flags=re.IGNORECASE):
            return True

    return False


def is_diy_article(soup: BeautifulSoup, path: Path) -> bool:
    if is_excluded_file(path):
        return False

    title = extract_title(soup).lower()
    eyebrow = extract_eyebrow(soup).lower()
    category, platform, hardware = extract_category_meta(soup)
    category_l = category.lower()
    platform_l = platform.lower()
    hardware_l = hardware.lower()
    full_text = normalize_whitespace(soup.get_text(" ", strip=True)).lower()

    negative_markers = (
        "review",
        "kennisbank",
        "informatief",
    )
    if any(marker in title for marker in negative_markers):
        return False

    if path.name.lower() in {"homey copy.html"}:
        return False

    score = 0

    if has_diy_breadcrumb(soup):
        score += 4

    if eyebrow in {"diy", "diy & homeyduino", "homeyduino"}:
        score += 3

    if category_l == "diy":
        score += 4

    if any(phrase in title for phrase in ("bouw je eigen", "maak je eigen")):
        score += 3

    if soup.select_one(".project-content-layout"):
        score += 1

    if "wat ga je bouwen?" in full_text:
        score += 3

    if "benodigdheden" in full_text and "stap-voor-stap uitleg" in full_text:
        score += 2

    if "integratie met homey" in full_text:
        score += 1

    if platform_l in {"homeyduino", "esp8266", "esp32", "arduino"}:
        score += 1

    if hardware_l not in {"", "niet opgegeven"}:
        score += 1

    has_strong_anchor = any(
        (
            has_diy_breadcrumb(soup),
            category_l == "diy",
            eyebrow in {"diy", "diy & homeyduino", "homeyduino"},
            any(phrase in title for phrase in ("bouw je eigen", "maak je eigen")),
            "wat ga je bouwen?" in full_text,
        )
    )

    return has_strong_anchor and score >= 5


def parse_article(path: Path, root: Path) -> Optional[DiyArticle]:
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="utf-8", errors="ignore")

    soup = BeautifulSoup(raw, "html.parser")
    if not is_diy_article(soup, path):
        return None

    title = extract_title(soup)
    description = find_meta_content(soup, "description")
    lead = extract_lead(soup)
    category, platform, hardware = extract_category_meta(soup)
    image_src, image_alt = extract_hero_image(soup)
    eyebrow = extract_eyebrow(soup)

    rel = path.relative_to(root).as_posix()

    return DiyArticle(
        source_path=path,
        output_href=rel,
        title=title,
        description=description,
        lead=lead,
        category=category or "DIY",
        platform=platform or "Onbekend",
        hardware=hardware or "Niet opgegeven",
        image_src=image_src,
        image_alt=image_alt or title,
        eyebrow=eyebrow or "DIY",
        sort_key=title.casefold(),
    )


def iter_html_files(root: Path, include_drafts: bool = False) -> Iterable[Path]:
    excluded_dirs = {
        ".git",
        "node_modules",
        "venv",
        ".venv",
        "__pycache__",
        "dist",
        "build",
    }
    if not include_drafts:
        excluded_dirs.update({"drafts", "_drafts"})

    for path in root.rglob("*.html"):
        if any(part.lower() in excluded_dirs for part in path.parts):
            continue
        yield path


def choose_icon(article: DiyArticle) -> str:
    combined = f"{article.title} {article.description} {article.lead} {article.hardware} {article.category}".lower()
    mapping = [
        (("co2", "co₂", "luchtkwaliteit", "mh-z19"), "🌬️"),
        (("licht", "ldr", "schemer"), "💡"),
        (("temperatuur", "dht", "luchtvochtigheid"), "🌡️"),
        (("deur", "raam", "contact", "reed"), "🚪"),
        (("clapper", "geluid", "klap"), "👏"),
        (("relay", "relais", "schakel", "switch"), "🔌"),
        (("beweg", "pir", "motion"), "👣"),
        (("rook", "brand"), "🔥"),
        (("water", "lek"), "💧"),
        (("nfc", "rc522", "tag"), "🏷️"),
    ]
    for keywords, icon in mapping:
        if any(keyword in combined for keyword in keywords):
            return icon
    return "🛠️"


def build_card_description(article: DiyArticle) -> str:
    text = article.lead or article.description
    if text:
        return text
    return f"DIY-project met {article.hardware.lower()} op {article.platform.lower()}."


def render_cards(articles: list[DiyArticle]) -> str:
    lines: list[str] = []
    for article in articles:
        description = html.escape(build_card_description(article))
        title = html.escape(article.title)
        href = html.escape(article.output_href)
        icon = choose_icon(article)

        # 👉 NIEUW: check of er een afbeelding is
        image_html = ""
        if article.image_src:
            image_html = f'''
            <a class="article-card-image" href="{href}">
              <img src="{html.escape(article.image_src)}" alt="{html.escape(article.image_alt)}" loading="lazy">
            </a>
            '''

        card = f'''
          <article class="article-card">
            {image_html}
            <div class="article-card-body">
              <span class="eyebrow">{html.escape(article.eyebrow)}</span>
              <h2><a href="{href}">{title}</a></h2>
              <p class="muted">{description}</p>
              <div class="meta-list">
                <span class="meta-pill">Categorie: {html.escape(article.category)}</span>
                <span class="meta-pill">Platform: {html.escape(article.platform)}</span>
                <span class="meta-pill">Hardware: {html.escape(article.hardware)}</span>
              </div>
              <a class="button-secondary" href="{href}">Bekijk project</a>
            </div>
          </article>
        '''
        lines.append(card.strip())

    return "\n".join(lines)
    lines: list[str] = []
    for article in articles:
        description = html.escape(build_card_description(article))
        title = html.escape(article.title)
        href = html.escape(article.output_href)
        icon = choose_icon(article)
        card = (
            '          <article class="card">\n'
            f'            <div class="card-icon">{icon}</div>\n'
            f'            <h3>{title}</h3>\n'
            f'            <p class="muted">{description}</p><a class="link" href="{href}">Lees artikel →</a>\n'
            '          </article>'
        )
        lines.append(card)
    return "\n".join(lines)


def replace_between_markers(content: str, replacement: str) -> str:
    pattern = re.compile(
        rf"({re.escape(START_MARKER)})(.*)({re.escape(END_MARKER)})",
        flags=re.DOTALL,
    )
    if not pattern.search(content):
        raise ValueError(
            "Markers niet gevonden in diy.html. Voeg deze toe:\n"
            f"{START_MARKER}\n"
            f"{END_MARKER}"
        )
    return pattern.sub(rf"\1\n{replacement}\n          \3", content, count=1)


def build_index(root: Path, output: Path, write: bool, include_drafts: bool) -> int:
    articles: list[DiyArticle] = []

    for path in iter_html_files(root, include_drafts=include_drafts):
        article = parse_article(path, root)
        if article:
            articles.append(article)

    articles.sort(key=lambda item: item.sort_key)

    template = output.read_text(encoding="utf-8")
    cards_html = render_cards(articles)
    final_html = replace_between_markers(template, cards_html)

    if write:
        output.write_text(final_html, encoding="utf-8")
        print(f"[OK] DIY-overzicht bijgewerkt: {output}")
    else:
        print(final_html)

    print(f"[INFO] Gevonden DIY-artikelen: {len(articles)}")
    for article in articles:
        print(f" - {article.output_href} -> {article.title}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Werk de kaartjes in diy.html automatisch bij op basis van bestaande DIY-artikelen."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Rootmap van de website / repository",
    )
    parser.add_argument(
        "--output",
        default="diy.html",
        help="Doelbestand met markers waarin de DIY-kaarten worden bijgewerkt",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Schrijf de output terug naar bestand in plaats van printen naar stdout",
    )
    parser.add_argument(
        "--include-drafts",
        action="store_true",
        help="Neem ook conceptmappen zoals drafts of _drafts mee",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = (root / output).resolve()

    if not output.exists():
        raise SystemExit(f"Doelbestand niet gevonden: {output}")

    return build_index(root=root, output=output, write=args.write, include_drafts=args.include_drafts)


if __name__ == "__main__":
    raise SystemExit(main())