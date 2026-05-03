from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

try:
    from bs4 import BeautifulSoup  # type: ignore
except ImportError:
    raise SystemExit("Installeer eerst: pip install beautifulsoup4")


@dataclass
class InfoArticle:
    source_path: Path
    output_href: str
    title: str
    description: str
    lead: str
    category: str
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
    "informatief.html",
    "contact.html",
    "header.html",
    "footer.html",
}

SKIP_PREFIXES = (
    "review-",
    "sjabloon-",
)

START = "<!-- AUTO-GENERATED-INFORMATIEF-CARDS:START -->"
END = "<!-- AUTO-GENERATED-INFORMATIEF-CARDS:END -->"


def text(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)) if el else ""


def extract_title(soup):
    if soup.find("h1"):
        return text(soup.find("h1"))
    if soup.title:
        return re.sub(r"\s*\|.*", "", soup.title.string or "")
    return "Zonder titel"


def extract_lead(soup):
    for sel in ["p.lead", ".lead", ".article-hero p"]:
        el = soup.select_one(sel)
        if el:
            return text(el)
    return ""


def extract_meta(soup):
    meta = soup.find("meta", attrs={"name": "description"})
    return meta["content"].strip() if meta and meta.get("content") else ""


def extract_image(soup):
    img = soup.select_one(".project-hero-media img, main img")
    if img:
        return img.get("src", ""), img.get("alt", "")
    return "", ""


def extract_eyebrow(soup):
    return text(soup.select_one(".eyebrow")) or "Informatief"


def is_excluded(path):
    name = path.name.lower()
    if name in SKIP_FILES:
        return True
    return any(name.startswith(p) for p in SKIP_PREFIXES)


def is_informational(soup, path):
    if is_excluded(path):
        return False

    title = extract_title(soup).lower()
    eyebrow = extract_eyebrow(soup).lower()
    full = text(soup).lower()

    # uitsluiten
    if any(x in title for x in ["review", "bouw je eigen", "tutorial"]):
        return False

    score = 0

    if "wat is" in title:
        score += 3

    if "hoe werkt" in title:
        score += 3

    if "verschil tussen" in title:
        score += 3

    if eyebrow in {"informatief", "uitleg", "achtergrond"}:
        score += 3

    if "wat betekent" in full:
        score += 2

    if "wanneer gebruik je" in full:
        score += 2

    if "in dit artikel" in full:
        score += 1

    return score >= 4


def parse(path, root):
    raw = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(raw, "html.parser")

    if not is_informational(soup, path):
        return None

    title = extract_title(soup)
    desc = extract_meta(soup)
    lead = extract_lead(soup)
    img, alt = extract_image(soup)
    eyebrow = extract_eyebrow(soup)

    return InfoArticle(
        path,
        path.relative_to(root).as_posix(),
        title,
        desc,
        lead,
        "Informatief",
        img,
        alt or title,
        eyebrow,
        title.lower(),
    )


def render(articles):
    html_blocks = []

    for a in articles:
        image = ""
        if a.image_src:
            image = f'''
<a class="article-card-image" href="{a.output_href}">
  <img src="{a.image_src}" alt="{a.image_alt}" loading="lazy">
</a>
'''

        desc = html.escape(a.lead or a.description)

        html_blocks.append(f'''
<article class="article-card">
{image}
  <div class="article-card-body">
    <span class="eyebrow">{a.eyebrow}</span>
    <h2><a href="{a.output_href}">{a.title}</a></h2>
    <p class="muted">{desc}</p>
    <a class="button-secondary" href="{a.output_href}">Lees artikel</a>
  </div>
</article>
''')

    return "\n".join(html_blocks)

def replace(content: str, cards: str) -> str:
    pattern = re.compile(
        r"(<!-- AUTO-GENERATED-INFORMATIEF-CARDS:START -->)(.*?)(<!-- AUTO-GENERATED-INFORMATIEF-CARDS:END -->)",
        re.DOTALL,
    )

    def safe_replace(match: re.Match) -> str:
        return f"{match.group(1)}\n{cards}\n{match.group(3)}"

    return pattern.sub(safe_replace, content, count=1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = root / "informatief.html"

    articles = []

    for path in root.rglob("*.html"):
        art = parse(path, root)
        if art:
            articles.append(art)

    articles.sort(key=lambda x: x.sort_key)

    template = output.read_text(encoding="utf-8")
    cards = render(articles)
    final = replace(template, cards)

    if args.write:
        output.write_text(final, encoding="utf-8")
        print(f"[OK] Informatief overzicht bijgewerkt")
    else:
        print(final)

    print(f"[INFO] Gevonden artikelen: {len(articles)}")


if __name__ == "__main__":
    main()