#!/usr/bin/env python3
"""
internal_linker_v2.py

Scant HTML-artikelen en vult de bestaande "Gerelateerd"-sectie in de rechterkolom
automatisch met relevante interne links.

Ontworpen voor huisvanvandaag.nl en vergelijkbare statische sites.

Belangrijkste eigenschappen:
- matcht artikelen op basis van titel, headings, bestandsnaam en hoofdtekst
- houdt rekening met artikeltype (DIY / tutorial / review / informatief)
- werkt primair in de rechterkolom binnen .sidebar-card > .footer-links
- laat de inhoud van het artikel zelf ongemoeid
- vervangt placeholders zoals [[GERELATEERD_LINK_1]] automatisch
- kan een ontbrekende Gerelateerd-kaart aanmaken in <aside class="side-stack">
- slaat pagina's als index/contact/over/privacy/disclaimer standaard over
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from bs4 import BeautifulSoup, Tag

STOPWORDS_NL = {
    "aan", "af", "al", "als", "bij", "dan", "dat", "de", "der", "deze", "die",
    "dit", "doen", "door", "een", "en", "er", "geen", "had", "heb", "heeft",
    "hem", "het", "hier", "hoe", "hun", "iemand", "iets", "ik", "in", "is",
    "je", "kan", "kun", "maar", "me", "meer", "met", "mij", "mijn", "moet",
    "na", "naar", "niet", "nog", "nu", "of", "om", "ons", "ook", "op", "over",
    "te", "tot", "uit", "van", "veel", "voor", "want", "was", "we", "wel",
    "werd", "wie", "wij", "wil", "worden", "zal", "ze", "zei", "zelf", "zich",
    "zij", "zijn", "zo", "zonder", "zou", "smart", "home", "huis", "vandaag",
}

SKIP_FILENAMES = {
    "index.html",
    "over.html",
    "contact.html",
    "privacy.html",
    "privacy-disclaimer.html",
    "disclaimer.html",
    "404.html",
    "diy.html",
    "tutorials.html",
    "reviews.html",
    "homey.html",
}

TYPE_RULES = {
    "informatief": {"diy", "tutorial", "review", "informatief"},
    "tutorial": {"diy", "review", "informatief", "tutorial"},
    "diy": {"tutorial", "review", "informatief", "diy"},
    "review": {"tutorial", "informatief", "diy", "review"},
    "unknown": {"diy", "tutorial", "review", "informatief", "unknown"},
}


@dataclass
class Article:
    path: Path
    url: str
    title: str
    article_type: str
    headings: list[str] = field(default_factory=list)
    body_text: str = ""
    keywords: list[str] = field(default_factory=list)
    summary_terms: list[str] = field(default_factory=list)
    score_terms: Counter = field(default_factory=Counter)


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return text.lower()


def slug_to_words(filename: str) -> str:
    stem = Path(filename).stem
    return stem.replace("-", " ").replace("_", " ")


def tokenize(text: str) -> list[str]:
    text = normalize_text(text)
    raw = re.findall(r"[a-z0-9][a-z0-9\+\#\-]{1,}", text)
    tokens = []
    for token in raw:
        token = token.strip("-")
        if len(token) < 3:
            continue
        if token in STOPWORDS_NL:
            continue
        tokens.append(token)
    return tokens


def weighted_terms(title: str, headings: Iterable[str], body_text: str, filename: str) -> Counter:
    counter: Counter = Counter()

    for token in tokenize(title):
        counter[token] += 6

    for heading in headings:
        for token in tokenize(heading):
            counter[token] += 4

    for token in tokenize(slug_to_words(filename)):
        counter[token] += 5

    body_tokens = tokenize(body_text)
    body_counts = Counter(body_tokens)
    for token, count in body_counts.items():
        counter[token] += min(count, 6)

    return counter


def extract_article_type(path: Path, soup: BeautifulSoup) -> str:
    path_posix = path.as_posix().lower()
    parent_name = path.parent.name.lower()
    file_name = path.name.lower()

    if "/diy/" in path_posix or parent_name == "diy":
        return "diy"
    if "/tutorial" in path_posix or "tutorial" in parent_name:
        return "tutorial"
    if "/review" in path_posix or "review" in parent_name:
        return "review"

    active_nav = soup.select_one("nav a.active")
    if active_nav:
        active_text = active_nav.get_text(" ", strip=True).lower()
        if "diy" in active_text:
            return "diy"
        if "tutorial" in active_text:
            return "tutorial"
        if "review" in active_text:
            return "review"

    eyebrow = soup.select_one(".eyebrow")
    if eyebrow:
        text = eyebrow.get_text(" ", strip=True).lower()
        if "diy" in text:
            return "diy"
        if "tutorial" in text:
            return "tutorial"
        if "review" in text:
            return "review"
        if "informat" in text or "kennisbank" in text:
            return "informatief"

    breadcrumbs = " ".join(x.get_text(" ", strip=True).lower() for x in soup.select(".breadcrumbs a, .breadcrumbs span"))
    if "diy" in breadcrumbs:
        return "diy"
    if "tutorial" in breadcrumbs:
        return "tutorial"
    if "review" in breadcrumbs:
        return "review"
    if "kennisbank" in breadcrumbs or "homey" in breadcrumbs:
        return "informatief"

    if any(term in file_name for term in ("review", "test", "ervaring")):
        return "review"
    if any(term in file_name for term in ("tutorial", "handleiding", "uitleg")):
        return "tutorial"
    if any(term in file_name for term in ("bouw", "maak", "diy")):
        return "diy"

    return "informatief"


def extract_text_without_noise(soup: BeautifulSoup) -> tuple[str, list[str]]:
    article = soup.select_one("article") or soup.select_one("main") or soup.body or soup

    headings: list[str] = []
    for heading in article.find_all(["h1", "h2", "h3"]):
        text = heading.get_text(" ", strip=True)
        if text:
            headings.append(text)

    soup_copy = BeautifulSoup(str(article), "html.parser")

    for tag in soup_copy.find_all(["script", "style", "nav", "footer", "pre", "code"]):
        tag.decompose()

    for tag in soup_copy.select(".toc, .sidebar-card, .footer-links, .internal-links-block"):
        tag.decompose()

    body_text = soup_copy.get_text(" ", strip=True)
    body_text = re.sub(r"\s+", " ", body_text).strip()
    return body_text, headings


def parse_article(path: Path, root: Path) -> Optional[Article]:
    if path.name.lower() in SKIP_FILENAMES:
        return None

    text = path.read_text(encoding="utf-8")
    if "internal-linker:ignore" in text.lower():
        return None

    soup = BeautifulSoup(text, "html.parser")
    title_tag = soup.find("h1") or soup.find("title")
    title = title_tag.get_text(" ", strip=True) if title_tag else path.stem.replace("-", " ").title()

    body_text, headings = extract_text_without_noise(soup)
    if len(body_text) < 120:
        return None

    article_type = extract_article_type(path, soup)
    terms = weighted_terms(title, headings, body_text, path.name)
    keywords = [token for token, _ in terms.most_common(20)]
    summary_terms = [token for token, _ in terms.most_common(6)]

    return Article(
        path=path,
        url=path.relative_to(root).as_posix(),
        title=title,
        article_type=article_type,
        headings=headings,
        body_text=body_text,
        keywords=keywords,
        summary_terms=summary_terms,
        score_terms=terms,
    )


def collect_articles(root: Path, include_drafts: bool = False) -> list[Article]:
    html_files = sorted(root.rglob("*.html"))
    articles: list[Article] = []

    for path in html_files:
        parts_lower = {part.lower() for part in path.parts}
        if not include_drafts and parts_lower.intersection({"draft", "concept", "tmp", "snippets"}):
            continue
        article = parse_article(path, root)
        if article:
            articles.append(article)
    return articles


def similarity_score(a: Article, b: Article) -> float:
    if a.path == b.path:
        return 0.0

    allowed = TYPE_RULES.get(a.article_type, TYPE_RULES["unknown"])
    if b.article_type not in allowed:
        return 0.0

    set_a = set(a.keywords[:18])
    set_b = set(b.keywords[:18])
    overlap = set_a & set_b
    if not overlap:
        return 0.0

    weighted_overlap = sum(min(a.score_terms[t], b.score_terms[t]) for t in overlap)
    same_type_bonus = 1.5 if a.article_type == b.article_type else 3.0
    title_overlap = len(set(tokenize(a.title)) & set(tokenize(b.title))) * 2.0

    return weighted_overlap + same_type_bonus + title_overlap


def pick_related(article: Article, pool: list[Article], limit: int = 3) -> list[Article]:
    scored: list[tuple[float, Article]] = []

    for candidate in pool:
        score = similarity_score(article, candidate)
        if score <= 0:
            continue
        scored.append((score, candidate))

    scored.sort(key=lambda x: (-x[0], x[1].title.lower()))

    picked: list[Article] = []
    used_titles: set[str] = set()

    for score, candidate in scored:
        normalized_title = normalize_text(candidate.title)
        if normalized_title in used_titles:
            continue
        if len(set(article.keywords[:8]) & set(candidate.keywords[:8])) == 0 and score < 8:
            continue
        picked.append(candidate)
        used_titles.add(normalized_title)
        if len(picked) >= limit:
            break

    return picked


def sidebar_links_match_existing(existing_links: list[Tag], related: list[Article]) -> bool:
    existing = [(link.get("href", "").strip(), link.get_text(" ", strip=True)) for link in existing_links]
    target = [(item.url.strip(), item.title.strip()) for item in related]
    return existing == target


def ensure_sidebar_footer_links(soup: BeautifulSoup) -> tuple[Optional[Tag], str]:
    # 1. Prefer a sidebar card already labelled "Gerelateerd"
    for card in soup.select(".sidebar-card"):
        heading = card.find(["h2", "h3", "strong"])
        heading_text = heading.get_text(" ", strip=True).lower() if heading else ""
        if heading_text == "gerelateerd":
            footer_links = card.select_one(".footer-links")
            if footer_links is None:
                footer_links = soup.new_tag("div", attrs={"class": "footer-links"})
                card.append(footer_links)
                return footer_links, "sidebar_created_footer_links"
            return footer_links, "sidebar_found"

    # 2. Fallback: first sidebar card
    first_card = soup.select_one(".side-stack .sidebar-card")
    if first_card:
        heading = first_card.find(["h2", "h3", "strong"])
        if heading is None:
            heading = soup.new_tag("h3")
            heading.string = "Gerelateerd"
            first_card.insert(0, heading)
        else:
            heading.clear()
            heading.append("Gerelateerd")

        footer_links = first_card.select_one(".footer-links")
        if footer_links is None:
            footer_links = soup.new_tag("div", attrs={"class": "footer-links"})
            first_card.append(footer_links)
        return footer_links, "sidebar_reused_existing_card"

    # 3. Create full card inside aside.side-stack
    aside = soup.select_one("aside.side-stack")
    if aside is None:
        return None, "no_sidebar_found"

    card = soup.new_tag("div", attrs={"class": "sidebar-card"})
    heading = soup.new_tag("h3")
    heading.string = "Gerelateerd"
    card.append(heading)

    footer_links = soup.new_tag("div", attrs={"class": "footer-links"})
    card.append(footer_links)
    aside.append(card)
    return footer_links, "sidebar_card_created"


def inject_sidebar_links(html: str, related: list[Article]) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    footer_links, status = ensure_sidebar_footer_links(soup)
    if footer_links is None:
        return html, status

    existing_links = footer_links.find_all("a", recursive=False)
    if sidebar_links_match_existing(existing_links, related):
        return html, "sidebar_already_up_to_date"

    footer_links.clear()

    for rel in related:
        a = soup.new_tag("a", href=rel.url)
        a.string = rel.title
        footer_links.append(a)

    return str(soup), status


def process_articles(
    root: Path,
    write: bool,
    limit: int,
    min_score_hint: int,
    include_drafts: bool,
) -> list[dict]:
    articles = collect_articles(root, include_drafts=include_drafts)
    results: list[dict] = []

    for article in articles:
        related = pick_related(article, articles, limit=limit)
        filtered = [rel for rel in related if similarity_score(article, rel) >= min_score_hint]

        if not filtered:
            results.append({
                "file": article.url,
                "status": "skipped_no_matches",
                "article_type": article.article_type,
                "links_added": 0,
            })
            continue

        original_html = article.path.read_text(encoding="utf-8")
        updated_html, placement = inject_sidebar_links(original_html, filtered)

        status = "updated"
        links_added = len(filtered)

        if placement == "sidebar_already_up_to_date":
            status = "skipped_existing_sidebar_links"
            links_added = 0
        elif placement == "no_sidebar_found":
            status = "skipped_no_sidebar"
            links_added = 0
        elif updated_html == original_html:
            status = "skipped_no_change"
            links_added = 0
        elif write:
            article.path.write_text(updated_html, encoding="utf-8")

        results.append({
            "file": article.url,
            "status": status if write or status.startswith("skipped") else "preview",
            "article_type": article.article_type,
            "links_added": links_added,
            "placement": placement,
            "related": [
                {
                    "title": item.title,
                    "url": item.url,
                    "type": item.article_type,
                    "score_terms": item.summary_terms,
                }
                for item in filtered
            ],
        })

    return results


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Vul de Gerelateerd-sectie in de sidebar automatisch met relevante interne links."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Rootmap van de site / repository.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Schrijf wijzigingen terug naar de HTML-bestanden.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Maximaal aantal interne links per artikel.",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=8,
        help="Minimale matchscore om een artikel te linken.",
    )
    parser.add_argument(
        "--include-drafts",
        action="store_true",
        help="Neem ook draft/concept-mappen mee.",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="",
        help="Pad voor JSON-rapport.",
    )
    parser.add_argument(
        "--md-out",
        type=str,
        default="",
        help="Pad voor Markdown-rapport.",
    )
    return parser


def write_json_report(path: Path, results: list[dict]) -> None:
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


def write_md_report(path: Path, results: list[dict]) -> None:
    lines = [
        "# Internal linker v2 rapport",
        "",
        "| Bestand | Status | Type | Links | Plaatsing |",
        "|---|---|---:|---:|---|",
    ]

    for row in results:
        lines.append(
            f"| {row.get('file', '')} | {row.get('status', '')} | "
            f"{row.get('article_type', '')} | {row.get('links_added', 0)} | "
            f"{row.get('placement', '')} |"
        )

        related = row.get("related", [])
        if related:
            for rel in related:
                lines.append(
                    f"| ↳ {rel.get('title', '')} | {rel.get('type', '')} |  |  | {rel.get('url', '')} |"
                )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        print(f"Fout: map bestaat niet of is geen directory: {root}", file=sys.stderr)
        return 1

    results = process_articles(
        root=root,
        write=args.write,
        limit=max(1, args.limit),
        min_score_hint=max(1, args.min_score),
        include_drafts=args.include_drafts,
    )

    if args.json_out:
        write_json_report(Path(args.json_out), results)
    if args.md_out:
        write_md_report(Path(args.md_out), results)

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
