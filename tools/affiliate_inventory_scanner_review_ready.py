from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from html import unescape
from pathlib import Path
from typing import Iterable

SECTION_HEADING_PATTERN = re.compile(
    r"<h([1-6])\b[^>]*>(.*?)</h\1>",
    re.IGNORECASE | re.DOTALL,
)
LIST_ITEM_PATTERN = re.compile(r"<li\b[^>]*>(.*?)</li>", re.IGNORECASE | re.DOTALL)
TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")
HTML_FILES_GLOB = ("*.html", "*.htm")

DEFAULT_EXCLUDED_DIR_NAMES = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "tools",
}

DEFAULT_DRAFT_FILENAME_PATTERNS = [
    re.compile(r"^#", re.IGNORECASE),
    re.compile(r"\bkopie\b", re.IGNORECASE),
    re.compile(r"\bcopy\b", re.IGNORECASE),
    re.compile(r"\brs\b", re.IGNORECASE),
    re.compile(r"\bdefinitief\b", re.IGNORECASE),
    re.compile(r"\bv\d+\b", re.IGNORECASE),
]

REVIEW_HINTS = (
    "review-score-panel",
    "in deze review",
    "kort oordeel",
    "eindoordeel",
    "voor wie is dit een goede keuze",
)

REVIEW_MATCH_SECTION_HEADINGS = (
    "wat is het",
    "eerste indruk",
    "gebruikservaring",
    "integratie",
    "compatibiliteit",
)


@dataclass
class ArticleInventory:
    file: str
    relative_path: str
    title: str | None
    article_type: str
    match_source: str
    benodigdheden_heading: str | None
    benodigdheden: list[str]
    matched_product_keys: list[str]


def clean_text(value: str) -> str:
    """Maak tekst compact, éénregelig en veilig voor JSON-output."""
    return " ".join(value.split()).strip()


def strip_html(value: str) -> str:
    text = TAG_PATTERN.sub(" ", value)
    text = unescape(text)
    text = WHITESPACE_PATTERN.sub(" ", text)
    return text.strip()


def normalize_for_match(value: str) -> str:
    value = strip_html(value).lower()
    value = value.replace("₂", "2")
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"[^a-z0-9à-ÿ\s\-_/+.]", " ", value)
    value = WHITESPACE_PATTERN.sub(" ", value)
    return value.strip()


def extract_title(html: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    title = strip_html(match.group(1))
    return title or None


def extract_h1(html: str) -> str | None:
    match = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    value = strip_html(match.group(1))
    return value or None


def extract_meta_description(html: str) -> str | None:
    patterns = [
        r'<meta\b[^>]*\bname=["\']description["\'][^>]*\bcontent=["\'](.*?)["\'][^>]*>',
        r'<meta\b[^>]*\bcontent=["\'](.*?)["\'][^>]*\bname=["\']description["\'][^>]*>',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if match:
            value = strip_html(match.group(1))
            if value:
                return value
    return None


def find_section_items_by_heading_keyword(html: str, heading_keywords: tuple[str, ...]) -> tuple[str | None, list[str]]:
    headings = list(SECTION_HEADING_PATTERN.finditer(html))
    for index, match in enumerate(headings):
        heading_text = strip_html(match.group(2)).lower()
        if not any(keyword in heading_text for keyword in heading_keywords):
            continue

        section_start = match.end()
        section_end = headings[index + 1].start() if index + 1 < len(headings) else len(html)
        section_html = html[section_start:section_end]

        items = [strip_html(item) for item in LIST_ITEM_PATTERN.findall(section_html)]
        items = [clean_text(item) for item in items if clean_text(item)]
        return strip_html(match.group(2)), items

    return None, []


def find_benodigdheden_section(html: str) -> tuple[str | None, list[str]]:
    return find_section_items_by_heading_keyword(html, ("benodigdheden", "wat heb je nodig"))


def extract_section_text_by_heading_keywords(html: str, heading_keywords: tuple[str, ...]) -> list[str]:
    headings = list(SECTION_HEADING_PATTERN.finditer(html))
    sections: list[str] = []

    for index, match in enumerate(headings):
        heading_text = strip_html(match.group(2)).lower()
        if not any(keyword in heading_text for keyword in heading_keywords):
            continue

        section_start = match.start()
        section_end = headings[index + 1].start() if index + 1 < len(headings) else len(html)
        section_text = strip_html(html[section_start:section_end])
        if section_text:
            sections.append(section_text)

    return sections


def is_review_page(html: str, relative_path: str) -> bool:
    normalized_html = normalize_for_match(html)
    normalized_path = relative_path.lower().replace("\\", "/")

    if "reviews.html" in html.lower() or "reviews/" in normalized_path:
        return True
    if "review" in Path(relative_path).stem.lower():
        return True
    return any(hint in normalized_html for hint in REVIEW_HINTS)


def detect_article_type(html: str, relative_path: str) -> str:
    if is_review_page(html, relative_path):
        return "review"

    normalized_html = normalize_for_match(html)
    normalized_path = relative_path.lower().replace("\\", "/")

    if "diy.html" in html.lower() or "diy/" in normalized_path:
        return "diy"
    if "tutorials.html" in html.lower() or "tutorial" in normalized_path:
        return "tutorial"
    return "article"


def extract_review_match_candidates(html: str) -> list[str]:
    candidates: list[str] = []

    for value in (extract_title(html), extract_h1(html), extract_meta_description(html)):
        if value:
            candidates.append(value)

    candidates.extend(extract_section_text_by_heading_keywords(html, REVIEW_MATCH_SECTION_HEADINGS))

    # Reviewpagina's hebben vaak productinformatie in korte oordelen of kenmerken.
    candidates.extend(extract_section_text_by_heading_keywords(html, ("pluspunten", "minpunten", "aandachtspunten")))

    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        normalized = normalize_for_match(candidate)
        if normalized and normalized not in seen:
            seen.add(normalized)
            deduped.append(clean_text(candidate))

    return deduped


def extract_aliases_from_product_data(product_data: dict[str, object], product_key: str) -> list[str]:
    aliases_raw = product_data.get("aliases", [])
    aliases: list[str] = []

    if isinstance(aliases_raw, list):
        aliases.extend(alias for alias in aliases_raw if isinstance(alias, str))

    name = product_data.get("name")
    if isinstance(name, str) and name.strip():
        aliases.append(name.strip())

    aliases.append(product_key)

    deduped: list[str] = []
    seen: set[str] = set()

    for alias in aliases:
        normalized = normalize_for_match(alias)
        if normalized and normalized not in seen:
            seen.add(normalized)
            deduped.append(clean_text(alias))

    return deduped


def build_product_map_from_affiliate_json(path: Path) -> dict[str, list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("affiliate-products.json moet een object/dictionary op rootniveau zijn.")

    product_map: dict[str, list[str]] = {}

    for product_key, product_data in data.items():
        if not isinstance(product_key, str):
            raise ValueError("Alle productkeys in affiliate-products.json moeten strings zijn.")
        if not isinstance(product_data, dict):
            raise ValueError(f"Product '{product_key}' moet een object zijn.")

        aliases = extract_aliases_from_product_data(product_data, product_key)
        if not aliases:
            raise ValueError(f"Product '{product_key}' heeft geen bruikbare aliases of naam.")

        product_map[product_key] = aliases

    return product_map


def alias_matches_candidate(alias_normalized: str, candidate: str) -> bool:
    if not alias_normalized or len(alias_normalized) < 2:
        return False

    # Korte aliases zoals "co2" of "pir" geven snel false positives in reviewteksten.
    if len(alias_normalized) <= 3:
        return re.search(rf"(?<![a-z0-9]){re.escape(alias_normalized)}(?![a-z0-9])", candidate) is not None

    return alias_normalized in candidate


def match_products(candidates: Iterable[str], product_map: dict[str, list[str]]) -> list[str]:
    matched: list[str] = []
    normalized_candidates = [normalize_for_match(item) for item in candidates if normalize_for_match(item)]

    for product_key, aliases in product_map.items():
        for alias in aliases:
            alias_normalized = normalize_for_match(alias)
            if any(alias_matches_candidate(alias_normalized, candidate) for candidate in normalized_candidates):
                matched.append(product_key)
                break

    return sorted(set(matched))


def scan_html_file(path: Path, root: Path, product_map: dict[str, list[str]]) -> ArticleInventory:
    html = path.read_text(encoding="utf-8", errors="ignore")
    relative_path = path.relative_to(root).as_posix()
    article_type = detect_article_type(html, relative_path)
    heading, benodigdheden = find_benodigdheden_section(html)

    if article_type == "review":
        candidates = extract_review_match_candidates(html)
        match_source = "review_metadata_and_sections"
    elif benodigdheden:
        candidates = benodigdheden
        match_source = "benodigdheden"
    else:
        candidates = [value for value in (extract_title(html), extract_h1(html), extract_meta_description(html)) if value]
        match_source = "metadata_fallback"

    return ArticleInventory(
        file=path.name,
        relative_path=relative_path,
        title=extract_title(html),
        article_type=article_type,
        match_source=match_source,
        benodigdheden_heading=heading,
        benodigdheden=benodigdheden,
        matched_product_keys=match_products(candidates, product_map),
    )


def is_in_excluded_dir(path: Path, excluded_dir_names: set[str]) -> bool:
    return any(part.lower() in excluded_dir_names for part in path.parts)


def is_probable_draft_file(path: Path, draft_patterns: list[re.Pattern[str]]) -> bool:
    stem = path.stem
    return any(pattern.search(stem) for pattern in draft_patterns)


def iter_html_files(
    root: Path,
    *,
    include_drafts: bool,
    excluded_dir_names: set[str],
    draft_patterns: list[re.Pattern[str]],
) -> Iterable[Path]:
    seen: set[Path] = set()

    for pattern in HTML_FILES_GLOB:
        for path in root.rglob(pattern):
            if not path.is_file():
                continue
            if path in seen:
                continue
            if is_in_excluded_dir(path.relative_to(root), excluded_dir_names):
                continue
            if not include_drafts and is_probable_draft_file(path, draft_patterns):
                continue

            seen.add(path)
            yield path


def build_markdown_report(items: list[ArticleInventory]) -> str:
    lines = [
        "# Affiliate inventory scan",
        "",
        f"Totaal gescande artikelen: {len(items)}",
        "",
    ]

    for item in items:
        lines.append(f"## {item.relative_path}")
        if item.title:
            lines.append(f"- Titel: {item.title}")
        lines.append(f"- Artikeltype: {item.article_type}")
        lines.append(f"- Matchbron: {item.match_source}")
        lines.append(f"- Benodigdheden-sectie gevonden: {'ja' if item.benodigdheden_heading else 'nee'}")

        if item.benodigdheden_heading:
            lines.append(f"- Heading: {item.benodigdheden_heading}")

        if item.benodigdheden:
            lines.append("- Benodigdheden:")
            for benodigdheid in item.benodigdheden:
                lines.append(f"  - {benodigdheid}")
        else:
            lines.append("- Benodigdheden: geen lijst gevonden")

        if item.matched_product_keys:
            lines.append("- Herkende productkeys:")
            for key in item.matched_product_keys:
                lines.append(f"  - {key}")
        else:
            lines.append("- Herkende productkeys: geen")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_excluded_dirs(raw_values: list[str] | None) -> set[str]:
    excluded = {name.lower() for name in DEFAULT_EXCLUDED_DIR_NAMES}
    if raw_values:
        excluded.update(value.strip().lower() for value in raw_values if value.strip())
    return excluded


def resolve_affiliate_products_path(root: Path, provided_path: Path | None) -> Path:
    if provided_path is not None:
        resolved = provided_path if provided_path.is_absolute() else (Path.cwd() / provided_path).resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"affiliate-products.json niet gevonden: {resolved}")
        return resolved

    candidates = [
        root / "affiliate-products.json",
        root / "data" / "affiliate-products.json",
        root / "config" / "affiliate-products.json",
        root / "tools" / "affiliate-products.json",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    raise FileNotFoundError(
        "Geen affiliate-products.json gevonden. Verwacht op rootniveau of geef expliciet --affiliate-products op."
    )


def resolve_output_path(root: Path, output_path: Path) -> Path:
    """Maak relatieve outputpaden standaard relatief aan de rootmap."""
    if output_path.is_absolute():
        return output_path
    return (root / output_path).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Scan HTML-artikelen op passende affiliate producten. "
            "DIY/tutorials worden primair via Benodigdheden gematcht; reviews via titel, H1, meta en reviewsecties."
        )
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Map waarin HTML-bestanden gescand moeten worden. Standaard: huidige map.",
    )
    parser.add_argument(
        "--affiliate-products",
        dest="affiliate_products",
        type=Path,
        help="Pad naar affiliate-products.json. Laat leeg om automatisch te zoeken.",
    )
    parser.add_argument(
        "--json-out",
        dest="json_out",
        type=Path,
        default=Path("affiliate_report.json"),
        help="Schrijf de scan naar JSON. Standaard: affiliate_report.json",
    )
    parser.add_argument(
        "--md-out",
        dest="md_out",
        type=Path,
        default=Path("affiliate_report.md"),
        help="Schrijf de scan naar Markdown. Standaard: affiliate_report.md",
    )
    parser.add_argument(
        "--include-drafts",
        action="store_true",
        help="Neem ook concept-, kopie- en RS-bestanden mee in de scan.",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Extra mapnaam om uit te sluiten. Kan meerdere keren gebruikt worden.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Map bestaat niet: {root}")

    affiliate_products_path = resolve_affiliate_products_path(root, args.affiliate_products)
    product_map = build_product_map_from_affiliate_json(affiliate_products_path)
    excluded_dir_names = parse_excluded_dirs(args.exclude_dir)

    results = [
        scan_html_file(path, root, product_map)
        for path in sorted(
            iter_html_files(
                root,
                include_drafts=args.include_drafts,
                excluded_dir_names=excluded_dir_names,
                draft_patterns=DEFAULT_DRAFT_FILENAME_PATTERNS,
            )
        )
    ]

    payload = {
        "affiliate_products_source": affiliate_products_path.as_posix(),
        "scanned_articles": [asdict(item) for item in results],
    }

    json_out_path = resolve_output_path(root, args.json_out)
    md_out_path = resolve_output_path(root, args.md_out)

    json_out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md_out_path.write_text(
        build_markdown_report(results),
        encoding="utf-8",
    )

    matched_article_count = sum(1 for item in results if item.matched_product_keys)
    review_match_count = sum(1 for item in results if item.article_type == "review" and item.matched_product_keys)
    total_matches = sum(len(item.matched_product_keys) for item in results)

    print("Affiliate inventory scan voltooid.")
    print(f"Gescande HTML-bestanden: {len(results)}")
    print(f"Artikelen met matches: {matched_article_count}")
    print(f"Reviewpagina's met matches: {review_match_count}")
    print(f"Totaal gevonden productmatches: {total_matches}")
    print(f"JSON report saved to: {json_out_path}")
    print(f"Markdown report saved to: {md_out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
