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

DEFAULT_PRODUCT_MAP = {
    "wemos_d1_mini": [
        "wemos d1 mini",
        "wemos d1 mini pro",
        "nodemcu",
        "esp8266",
    ],
    "mh_z19b": [
        "mh-z19b",
        "mh z19b",
        "mh-z19c",
        "mh z19c",
        "co₂ sensor",
        "co2 sensor",
        "infrared carbon dioxide sensor",
    ],
}

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


def load_product_map(path: Path | None) -> dict[str, list[str]]:
    if path is None:
        return DEFAULT_PRODUCT_MAP

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Productmap JSON moet een object/dictionary zijn.")

    validated: dict[str, list[str]] = {}
    for key, aliases in data.items():
        if not isinstance(key, str):
            raise ValueError("Alle productkeys moeten strings zijn.")
        if not isinstance(aliases, list) or not all(isinstance(alias, str) for alias in aliases):
            raise ValueError(f"Product '{key}' moet een lijst met string-aliassen hebben.")
        validated[key] = aliases

    return validated


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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan HTML-artikelen op een 'Benodigdheden'-sectie en maak een inventory voor affiliate mapping."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Map waarin HTML-bestanden gescand moeten worden. Standaard: huidige map.",
    )
    parser.add_argument(
        "--product-map",
        dest="product_map",
        type=Path,
        help="Pad naar JSON-bestand met product aliases. Laat leeg om de standaardmap te gebruiken.",
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

    product_map = load_product_map(args.product_map)
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

    payload = [asdict(item) for item in results]
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.json_out:
        args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.md_out:
        args.md_out.write_text(build_markdown_report(results), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
