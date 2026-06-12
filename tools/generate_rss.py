#!/usr/bin/env python3
from __future__ import annotations

import argparse
import email.utils
import html
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from bs4 import BeautifulSoup

ROOT_URL = "https://www.huisvanvandaag.nl"
DEFAULT_OUTPUT = "rss.xml"
DEFAULT_LIMIT = 25

SKIP_FILES = {
    "index.html",
    "reviews.html",
    "review.html",
    "diy.html",
    "tutorials.html",
    "informatief.html",
    "homey.html",
    "contact.html",
    "over.html",
    "over-ons.html",
    "over-mij.html",
    "privacy.html",
    "privacy-disclaimer.html",
    "404.html",
    "header.html",
    "footer.html",
}

SKIP_PREFIXES = (
    "sjabloon-",
)

EXCLUDED_DIRS = {
    ".git",
    ".github",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "drafts",
    "_drafts",
}

WHITESPACE_RE = re.compile(r"\s+")
SITE_SUFFIX_RE = re.compile(r"\s*\|\s*huisvanvandaag\.nl\s*$", re.IGNORECASE)


@dataclass
class RssArticle:
    source_path: Path
    url: str
    title: str
    description: str
    publish_date: date
    image_url: str = ""


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return WHITESPACE_RE.sub(" ", value).strip()


def should_skip(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    name = path.name.lower()

    if name in SKIP_FILES:
        return True

    if any(name.startswith(prefix) for prefix in SKIP_PREFIXES):
        return True

    if any(part.lower() in EXCLUDED_DIRS for part in rel.parts):
        return True

    return False


def read_html(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def get_meta(soup: BeautifulSoup, name: str) -> str:
    tag = soup.find("meta", attrs={"name": name})
    if tag and tag.get("content"):
        return clean_text(str(tag["content"]))
    return ""


def get_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1:
        return clean_text(h1.get_text(" ", strip=True))

    title_tag = soup.find("title")
    if title_tag:
        return SITE_SUFFIX_RE.sub("", clean_text(title_tag.get_text(" ", strip=True)))

    return "Zonder titel"


def get_description(soup: BeautifulSoup) -> str:
    meta_description = get_meta(soup, "description")
    if meta_description:
        return meta_description

    lead = soup.select_one("p.lead.muted") or soup.select_one("p.lead") or soup.select_one(".article-hero .lead")
    if lead:
        return clean_text(lead.get_text(" ", strip=True))

    article = soup.select_one("article")
    if article:
        first_p = article.find("p")
        if first_p:
            return clean_text(first_p.get_text(" ", strip=True))

    return ""


def parse_publish_date(value: str) -> Optional[date]:
    value = clean_text(value)
    if not value or value == "[[PUBLISH_DATE]]":
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def get_image_url(soup: BeautifulSoup, article_url: str) -> str:
    img = soup.select_one(".project-hero-media img") or soup.select_one(".article-hero img") or soup.select_one("main img")
    if not img or not img.get("src"):
        return ""

    src = clean_text(str(img.get("src")))
    if src.startswith(("http://", "https://")):
        return src

    if src.startswith("/"):
        return f"{ROOT_URL}{src}"

    # Relatief aan root van de site. De huidige site gebruikt meestal assets/... vanaf root.
    return f"{ROOT_URL}/{quote(src)}"


def make_url(path: Path, root: Path) -> str:
    rel = path.relative_to(root).as_posix()
    if rel == "index.html":
        return f"{ROOT_URL}/"
    return f"{ROOT_URL}/{quote(rel)}"


def parse_article(path: Path, root: Path) -> Optional[RssArticle]:
    if should_skip(path, root):
        return None

    soup = BeautifulSoup(read_html(path), "html.parser")
    publish_date = parse_publish_date(get_meta(soup, "publish_date"))

    # Alleen echte artikelen met een geldige publish_date komen in de RSS-feed.
    if publish_date is None:
        return None

    url = make_url(path, root)
    title = get_title(soup)
    description = get_description(soup)
    image_url = get_image_url(soup, url)

    return RssArticle(
        source_path=path,
        url=url,
        title=title,
        description=description,
        publish_date=publish_date,
        image_url=image_url,
    )


def rfc2822_date(value: date) -> str:
    dt = datetime.combine(value, time(hour=12, minute=0), tzinfo=timezone.utc)
    return email.utils.format_datetime(dt, usegmt=True)


def build_item(article: RssArticle) -> str:
    title = html.escape(article.title)
    link = html.escape(article.url)
    guid = html.escape(article.url)
    description = html.escape(article.description)
    pub_date = rfc2822_date(article.publish_date)

    lines = [
        "  <item>",
        f"    <title>{title}</title>",
        f"    <link>{link}</link>",
        f"    <guid isPermaLink=\"true\">{guid}</guid>",
        f"    <description>{description}</description>",
        f"    <pubDate>{pub_date}</pubDate>",
    ]

    if article.image_url:
        image_url = html.escape(article.image_url)
        lines.append(f"    <enclosure url=\"{image_url}\" type=\"image/jpeg\" />")

    lines.append("  </item>")
    return "\n".join(lines)


def build_rss(articles: list[RssArticle]) -> str:
    last_build_date = email.utils.format_datetime(datetime.now(timezone.utc), usegmt=True)

    lines = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        "<rss version=\"2.0\" xmlns:atom=\"http://www.w3.org/2005/Atom\">",
        "<channel>",
        "  <title>Huis van Vandaag</title>",
        f"  <link>{ROOT_URL}/</link>",
        "  <description>De nieuwste Homey-tips, slimme automatiseringen en DIY-projecten van Huis van Vandaag.</description>",
        "  <language>nl-nl</language>",
        f"  <lastBuildDate>{last_build_date}</lastBuildDate>",
        f"  <atom:link href=\"{ROOT_URL}/rss.xml\" rel=\"self\" type=\"application/rss+xml\" />",
        "",
    ]

    for article in articles:
        lines.append(build_item(article))
        lines.append("")

    lines.extend([
        "</channel>",
        "</rss>",
    ])

    return "\n".join(lines)


def collect_articles(root: Path, limit: int) -> list[RssArticle]:
    articles: list[RssArticle] = []

    for path in root.rglob("*.html"):
        article = parse_article(path, root)
        if article:
            articles.append(article)

    articles.sort(key=lambda item: (item.publish_date, item.title.casefold()), reverse=True)
    return articles[:limit]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genereer rss.xml voor huisvanvandaag.nl op basis van HTML-artikelen.")
    parser.add_argument("root", nargs="?", default=".", help="Rootmap van de website/repository.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help=f"Outputbestand. Default: {DEFAULT_OUTPUT}")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help=f"Aantal artikelen in de feed. Default: {DEFAULT_LIMIT}")
    parser.add_argument("--write", action="store_true", help="Schrijf rss.xml weg. Zonder --write wordt de RSS naar stdout geprint.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output

    articles = collect_articles(root, args.limit)
    rss = build_rss(articles)

    if args.write:
        output.write_text(rss, encoding="utf-8")
        print(f"[OK] RSS-feed gegenereerd: {output}")
    else:
        print(rss)

    print(f"[INFO] Artikelen in RSS-feed: {len(articles)}")
    for article in articles:
        print(f" - {article.publish_date.isoformat()} | {article.title} | {article.url}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
