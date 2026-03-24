from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from html import unescape
from pathlib import Path
from typing import Iterable

SECTION_HEADING_PATTERN = re.compile(
    r"<h([1-6])[^>]*>(.*?)</h\1>",
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


@dataclass
class ArticleInventory:
    file: str
    relative_path: str
    title: str | None
    benodigdheden_heading: str | None
    benodigdheden: list[str]
    matched_product_keys: list[str]


def strip_html(value: str) -> str:
    text = TAG_PATTERN.sub(" ", value)
    text = unescape(text)
    text = WHITESPACE_PATTERN.sub(" ", text)
    return text.strip()


def normalize_for_match(value: str) -> str:
    value = strip_html(value).lower()
    value = value.replace("₂", "2")
    value = value.replace("–", "-").replace("—", "-")
    return value


def extract_title(html: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    title = strip_html(match.group(1))
    return title or None


def find_benodigdheden_section(html: str) -> tuple[str | None, list[str]]:
    headings = list(SECTION_HEADING_PATTERN.finditer(html))
    for index, match in enumerate(headings):
        heading_text = strip_html(match.group(2)).lower()
        if "benodigdheden" not in heading_text:
            continue

        section_start = match.end()
        section_end = headings[index + 1].start() if index + 1 < len(headings) else len(html)
        section_html = html[section_start:section_end]

        items = [strip_html(item) for item in LIST_ITEM_PATTERN.findall(section_html)]
        items = [item for item in items if item]
        return strip_html(match.group(2)), items

    return None, []


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
            deduped.append(alias)

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


def match_products(benodigdheden: Iterable[str], product_map: dict[str, list[str]]) -> list[str]:
    matched: list[str] = []
    normalized_items = [normalize_for_match(item) for item in benodigdheden]

    for product_key, aliases in product_map.items():
        for alias in aliases:
            alias_normalized = normalize_for_match(alias)
            if any(alias_normalized in item for item in normalized_items):
                matched.append(product_key)
                break

    return sorted(set(matched))


def scan_html_file(path: Path, root: Path, product_map: dict[str, list[str]]) -> ArticleInventory:
    html = path.read_text(encoding="utf-8", errors="ignore")
    heading, benodigdheden = find_benodigdheden_section(html)

    return ArticleInventory(
        file=path.name,
        relative_path=path.relative_to(root).as_posix(),
        title=extract_title(html),
        benodigdheden_heading=heading,
        benodigdheden=benodigdheden,
        matched_product_keys=match_products(benodigdheden, product_map),
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan HTML-artikelen op een 'Benodigdheden'-sectie en match producten via affiliate-products.json."
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
        help="Schrijf de scan ook naar JSON.",
    )
    parser.add_argument(
        "--md-out",
        dest="md_out",
        type=Path,
        help="Schrijf de scan ook naar Markdown.",
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

    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.json_out:
        args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.md_out:
        args.md_out.write_text(build_markdown_report(results), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
