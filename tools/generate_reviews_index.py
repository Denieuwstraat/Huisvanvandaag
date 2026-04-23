#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


DEFAULT_OUTPUT = "reviews-index.js"
DEFAULT_OVERRIDES = "data/reviews-overrides.json"
EXCLUDED_FILES = {"reviews.html"}
EXCLUDED_DIRS = {"node_modules", ".git", ".github", "dist", "build", "venv", ".venv", "__pycache__"}
REVIEW_THRESHOLD = 6


@dataclass
class ReviewItem:
    slug: str
    title: str = ""
    excerpt: str = ""
    category: str = ""
    platform: str = ""
    productType: str = ""
    score: str = ""
    featured: bool = False
    image: str = ""
    imageAlt: str = ""

    def as_public_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "title": self.title,
            "excerpt": self.excerpt,
            "category": self.category,
            "platform": self.platform,
            "productType": self.productType,
            "score": self.score,
            "featured": self.featured,
            "image": self.image,
            "imageAlt": self.imageAlt,
        }


@dataclass
class ScanResult:
    file: str
    is_review: bool
    score_value: int
    matched_signals: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    item: dict[str, Any] | None = None


class ReviewIndexGeneratorError(Exception):
    pass


META_PILL_LABEL_RE = re.compile(r"^\s*([^:]+):\s*(.*?)\s*$")
WHITESPACE_RE = re.compile(r"\s+")


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return WHITESPACE_RE.sub(" ", value).strip()


def normalize_path_for_web(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def safe_read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ReviewIndexGeneratorError(f"Kon bestand niet lezen met ondersteunde encodings: {path}")


def should_skip_path(path: Path) -> bool:
    if path.name in EXCLUDED_FILES:
        return True
    return any(part in EXCLUDED_DIRS for part in path.parts)


def find_html_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.html"):
        rel = path.relative_to(root)
        if should_skip_path(rel):
            continue
        files.append(path)
    return sorted(files)


def parse_html(path: Path) -> BeautifulSoup:
    return BeautifulSoup(safe_read_text(path), "html.parser")


def get_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1:
        return clean_text(h1.get_text(" ", strip=True))

    title_tag = soup.find("title")
    if title_tag:
        title = clean_text(title_tag.get_text(" ", strip=True))
        title = re.sub(r"\s*\|\s*huisvanvandaag\.nl\s*$", "", title, flags=re.I)
        return title
    return ""


def get_excerpt(soup: BeautifulSoup) -> str:
    lead = soup.select_one("p.lead.muted") or soup.select_one("p.lead")
    if lead:
        return clean_text(lead.get_text(" ", strip=True))

    article = soup.select_one("article")
    if article:
        first_p = article.find("p")
        if first_p:
            return clean_text(first_p.get_text(" ", strip=True))
    return ""


def get_meta_pills(soup: BeautifulSoup) -> dict[str, str]:
    result: dict[str, str] = {}
    for pill in soup.select(".meta-list .meta-pill"):
        text = clean_text(pill.get_text(" ", strip=True))
        match = META_PILL_LABEL_RE.match(text)
        if match:
            label = match.group(1).strip().lower()
            value = match.group(2).strip()
            result[label] = value
    return result


def get_score(soup: BeautifulSoup) -> str:
    score_node = soup.select_one(".review-score-value")
    if score_node:
        return clean_text(score_node.get_text(" ", strip=True))
    return ""


def get_hero_image(soup: BeautifulSoup) -> tuple[str, str]:
    hero_img = soup.select_one(".project-hero-media img")
    if hero_img:
        return clean_text(hero_img.get("src")), clean_text(hero_img.get("alt"))

    first_img = soup.find("img")
    if first_img:
        return clean_text(first_img.get("src")), clean_text(first_img.get("alt"))
    return "", ""


def has_review_sidebar(soup: BeautifulSoup) -> bool:
    headings = [clean_text(h.get_text(" ", strip=True)).lower() for h in soup.select(".toc h3")]
    return any("in deze review" in heading for heading in headings)


def has_breadcrumb_to_reviews(soup: BeautifulSoup) -> bool:
    for link in soup.select(".breadcrumbs a"):
        href = clean_text(link.get("href"))
        if href.lower().endswith("reviews.html"):
            return True
    return False


def has_section_heading(soup: BeautifulSoup, needle: str) -> bool:
    needle = needle.lower()
    for heading in soup.find_all(["h1", "h2", "h3"]):
        text = clean_text(heading.get_text(" ", strip=True)).lower()
        if needle in text:
            return True
    return False


def detect_review_signals(soup: BeautifulSoup, filename: str) -> tuple[int, list[str]]:
    score = 0
    signals: list[str] = []

    if filename.lower() in EXCLUDED_FILES:
        return 0, signals

    if has_breadcrumb_to_reviews(soup):
        score += 3
        signals.append("breadcrumb -> reviews.html")

    if has_review_sidebar(soup):
        score += 3
        signals.append("sidebar: In deze review")

    if has_section_heading(soup, "eindoordeel"):
        score += 2
        signals.append("sectie: Eindoordeel")

    if soup.select_one(".review-score-value"):
        score += 2
        signals.append("review-score-value")

    if has_section_heading(soup, "pluspunten"):
        score += 1
        signals.append("sectie: Pluspunten")

    if has_section_heading(soup, "minpunten"):
        score += 1
        signals.append("sectie: Minpunten")

    if has_section_heading(soup, "integratie en compatibiliteit"):
        score += 1
        signals.append("sectie: Integratie en compatibiliteit")

    if has_section_heading(soup, "wat is het"):
        score += 1
        signals.append("sectie: Wat is het")

    return score, signals


def extract_review_metadata(soup: BeautifulSoup, rel_path: Path) -> ReviewItem:
    meta = get_meta_pills(soup)
    image, image_alt = get_hero_image(soup)
    return ReviewItem(
        slug=normalize_path_for_web(rel_path),
        title=get_title(soup),
        excerpt=get_excerpt(soup),
        category=meta.get("categorie", ""),
        platform=meta.get("platform", ""),
        productType=meta.get("type", "") or meta.get("producttype", ""),
        score=get_score(soup),
        featured=False,
        image=image,
        imageAlt=image_alt,
    )


def validate_item(item: ReviewItem) -> list[str]:
    missing: list[str] = []
    for field_name in ("title", "excerpt", "category", "platform", "productType", "score", "image"):
        if not getattr(item, field_name):
            missing.append(field_name)
    if item.image and not item.imageAlt:
        missing.append("imageAlt")
    return missing


def load_overrides(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReviewIndexGeneratorError(f"Ongeldige JSON in overrides-bestand {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ReviewIndexGeneratorError("Overrides-bestand moet een JSON-object bevatten met slugs als keys.")
    return {str(k): v for k, v in data.items() if isinstance(v, dict)}


def apply_overrides(item: ReviewItem, overrides: dict[str, Any]) -> ReviewItem:
    allowed_fields = set(item.as_public_dict().keys())
    for key, value in overrides.items():
        if key in allowed_fields:
            setattr(item, key, value)
    return item


def sort_items(items: list[ReviewItem]) -> list[ReviewItem]:
    return sorted(items, key=lambda x: (not bool(x.featured), x.title.lower(), x.slug.lower()))


def to_javascript(items: list[ReviewItem]) -> str:
    public_items = [item.as_public_dict() for item in items]
    json_payload = json.dumps(public_items, ensure_ascii=False, indent=2)
    return f"window.HVV_REVIEWS = {json_payload};\n"


def to_markdown_report(results: list[ScanResult]) -> str:
    review_results = [r for r in results if r.is_review]
    non_review_results = [r for r in results if not r.is_review]

    lines = [
        "# Review index scan report",
        "",
        f"- Gevonden reviewpagina's: **{len(review_results)}**",
        f"- Overgeslagen HTML-bestanden: **{len(non_review_results)}**",
        "",
        "## Reviews",
        "",
    ]

    if not review_results:
        lines.append("Geen reviewpagina's gevonden.")
    else:
        for result in review_results:
            lines.append(f"### {result.file}")
            lines.append("")
            lines.append(f"- Detectiescore: **{result.score_value}**")
            lines.append(f"- Signalen: {', '.join(result.matched_signals) if result.matched_signals else 'geen'}")
            if result.missing_fields:
                lines.append(f"- Ontbrekende velden: {', '.join(result.missing_fields)}")
            else:
                lines.append("- Ontbrekende velden: geen")
            if result.item:
                lines.append(f"- Titel: {result.item.get('title', '')}")
                lines.append(f"- Slug: `{result.item.get('slug', '')}`")
            lines.append("")

    lines.extend([
        "## Overgeslagen bestanden",
        "",
    ])

    if not non_review_results:
        lines.append("Geen overgeslagen bestanden.")
    else:
        for result in non_review_results:
            lines.append(f"- `{result.file}` (score: {result.score_value})")

    lines.append("")
    return "\n".join(lines)


def scan_reviews(root: Path, overrides: dict[str, dict[str, Any]]) -> tuple[list[ReviewItem], list[ScanResult]]:
    items: list[ReviewItem] = []
    results: list[ScanResult] = []

    for path in find_html_files(root):
        rel_path = path.relative_to(root)
        soup = parse_html(path)
        detect_score, signals = detect_review_signals(soup, path.name)
        is_review = detect_score >= REVIEW_THRESHOLD

        if not is_review:
            results.append(
                ScanResult(
                    file=normalize_path_for_web(rel_path),
                    is_review=False,
                    score_value=detect_score,
                    matched_signals=signals,
                )
            )
            continue

        item = extract_review_metadata(soup, rel_path)
        item = apply_overrides(item, overrides.get(item.slug, {}))
        missing_fields = validate_item(item)
        items.append(item)
        results.append(
            ScanResult(
                file=normalize_path_for_web(rel_path),
                is_review=True,
                score_value=detect_score,
                matched_signals=signals,
                missing_fields=missing_fields,
                item=item.as_public_dict(),
            )
        )

    return sort_items(items), results


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genereer automatisch reviews-index.js op basis van review-HTML-pagina's."
    )
    parser.add_argument("root", nargs="?", default=".", help="Projectroot om te scannen (default: huidige map).")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help=f"Outputbestand (default: {DEFAULT_OUTPUT}).")
    parser.add_argument(
        "--overrides",
        default=DEFAULT_OVERRIDES,
        help=f"Optioneel overrides-bestand in JSON-formaat (default: {DEFAULT_OVERRIDES}).",
    )
    parser.add_argument("--write", action="store_true", help="Schrijf reviews-index.js weg.")
    parser.add_argument("--json-out", help="Schrijf een JSON-rapport met scanresultaten weg.")
    parser.add_argument("--md-out", help="Schrijf een Markdown-rapport met scanresultaten weg.")
    parser.add_argument("--fail-on-missing", action="store_true", help="Eindig met exitcode 1 als reviewvelden ontbreken.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output_path = root / args.output
    overrides_path = root / args.overrides

    overrides = load_overrides(overrides_path)
    items, results = scan_reviews(root, overrides)

    js_payload = to_javascript(items)
    missing_total = sum(1 for result in results if result.is_review and result.missing_fields)

    print(f"Reviewpagina's gevonden: {len(items)}")
    print(f"Reviews met ontbrekende velden: {missing_total}")

    for result in results:
        if result.is_review:
            missing_info = f" | ontbrekend: {', '.join(result.missing_fields)}" if result.missing_fields else ""
            print(f"[REVIEW] {result.file} (score {result.score_value}){missing_info}")
        else:
            print(f"[SKIP]   {result.file} (score {result.score_value})")

    if args.write:
        write_text(output_path, js_payload)
        print(f"Geschreven: {output_path}")
    else:
        print("Dry run: gebruik --write om reviews-index.js daadwerkelijk weg te schrijven.")

    if args.json_out:
        json_path = root / args.json_out
        json_payload = [asdict(result) for result in results]
        write_text(json_path, json.dumps(json_payload, ensure_ascii=False, indent=2))
        print(f"JSON-rapport geschreven: {json_path}")

    if args.md_out:
        md_path = root / args.md_out
        write_text(md_path, to_markdown_report(results))
        print(f"Markdown-rapport geschreven: {md_path}")

    if args.fail_on_missing and missing_total:
        print("Fout: er zijn reviewpagina's met ontbrekende verplichte velden.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
