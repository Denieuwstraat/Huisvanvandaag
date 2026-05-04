from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

HTML_FILES_GLOB = ("*.html", "*.htm")

SECTION_HEADING_PATTERN = re.compile(
    r"<h([1-6])\b[^>]*>(.*?)</h\1>",
    re.IGNORECASE | re.DOTALL,
)

TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")

MARKER_START = "<!-- AFFILIATE_AUTO_BLOCK_START -->"
MARKER_END = "<!-- AFFILIATE_AUTO_BLOCK_END -->"

SCRIPT_TAG_PATTERN = re.compile(
    r'<script\b[^>]*\bsrc=["\']affiliate-products\.js["\'][^>]*>\s*</script>',
    re.IGNORECASE,
)

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


@dataclass
class InjectionResult:
    file: str
    relative_path: str
    article_type: str
    matched_product_keys: list[str]
    status: str
    reason: str | None = None
    inserted_count: int = 0
    wrote_file: bool = False


def strip_html(value: str) -> str:
    text = TAG_PATTERN.sub(" ", value)
    text = WHITESPACE_PATTERN.sub(" ", text)
    return text.strip()


def normalize_text(value: str) -> str:
    value = strip_html(value).lower()
    value = value.replace("₂", "2")
    value = value.replace("–", "-").replace("—", "-")
    value = WHITESPACE_PATTERN.sub(" ", value)
    return value.strip()


def is_review_page(html: str, relative_path: str, article_type_from_report: str | None = None) -> bool:
    if article_type_from_report == "review":
        return True

    normalized_html = normalize_text(html)
    normalized_path = relative_path.lower().replace("\\", "/")

    if "reviews.html" in html.lower() or "reviews/" in normalized_path:
        return True
    if "review" in Path(relative_path).stem.lower():
        return True
    return any(hint in normalized_html for hint in REVIEW_HINTS)


def is_in_excluded_dir(path: Path, excluded_dir_names: set[str]) -> bool:
    return any(part.lower() in excluded_dir_names for part in path.parts)


def is_probable_draft_file(path: Path, draft_patterns: list[re.Pattern[str]]) -> bool:
    return any(pattern.search(path.stem) for pattern in draft_patterns)


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

            relative = path.relative_to(root)

            if is_in_excluded_dir(relative, excluded_dir_names):
                continue

            if not include_drafts and is_probable_draft_file(path, draft_patterns):
                continue

            seen.add(path)
            yield path


def parse_excluded_dirs(raw_values: list[str] | None) -> set[str]:
    excluded = {name.lower() for name in DEFAULT_EXCLUDED_DIR_NAMES}
    if raw_values:
        excluded.update(value.strip().lower() for value in raw_values if value.strip())
    return excluded


def load_report(path: Path) -> dict[str, dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, dict) and "scanned_articles" in data:
        articles = data["scanned_articles"]
    elif isinstance(data, list):
        articles = data
    else:
        raise ValueError("Onbekend report-formaat. Verwacht een lijst of een object met 'scanned_articles'.")

    result: dict[str, dict[str, object]] = {}

    for item in articles:
        if not isinstance(item, dict):
            continue

        relative_path = item.get("relative_path") or item.get("file")
        matched_product_keys = item.get("matched_product_keys") or []
        article_type = item.get("article_type") or "unknown"

        if isinstance(relative_path, str) and isinstance(matched_product_keys, list):
            result[relative_path.replace("\\", "/")] = {
                "matched_product_keys": [str(key) for key in matched_product_keys if isinstance(key, str)],
                "article_type": str(article_type),
            }

    return result


def ensure_affiliate_script_tag(html: str) -> tuple[str, bool]:
    if SCRIPT_TAG_PATTERN.search(html):
        return html, False

    script_tag = '\n<script src="affiliate-products.js"></script>\n'
    body_close = re.search(r"</body\s*>", html, re.IGNORECASE)

    if body_close:
        new_html = html[:body_close.start()] + script_tag + html[body_close.start():]
        return new_html, True

    return html + script_tag, True


def remove_existing_auto_block(html: str) -> tuple[str, bool]:
    pattern = re.compile(
        re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
        re.DOTALL,
    )
    new_html, count = pattern.subn("", html)
    return new_html, count > 0


def build_affiliate_block(product_keys: list[str], block_id_base: str, article_type: str) -> str:
    placeholders = "\n".join(
        f'  <div id="{block_id_base}-{index + 1}"></div>'
        for index, _ in enumerate(product_keys)
    )

    render_calls = "\n".join(
        f'  renderAffiliateProduct("{block_id_base}-{index + 1}", "{key}");'
        for index, key in enumerate(product_keys)
    )

    if article_type == "review":
        heading = "Bekijk actuele prijs en beschikbaarheid"
        intro = "Dit zijn passende links bij het product uit deze review."
        aria_label = "Affiliate links bij deze review"
    else:
        heading = "Handige links bij dit project"
        intro = "Dit zijn producten die aansluiten op de benodigdheden in dit artikel."
        aria_label = "Aanbevolen producten"

    return (
        f"\n{MARKER_START}\n"
        f'<section class="affiliate-auto-block" aria-label="{aria_label}">\n'
        f"  <h3>{heading}</h3>\n"
        f"  <p>{intro}</p>\n"
        f"{placeholders}\n"
        f"</section>\n"
        f"<script>\n{render_calls}\n</script>\n"
        f"{MARKER_END}\n"
    )


def find_insertion_index_after_heading_section(html: str, heading_keywords: tuple[str, ...]) -> int | None:
    headings = list(SECTION_HEADING_PATTERN.finditer(html))

    for index, match in enumerate(headings):
        heading_text = strip_html(match.group(2)).lower()
        if not any(keyword in heading_text for keyword in heading_keywords):
            continue

        section_start = match.end()
        section_end = headings[index + 1].start() if index + 1 < len(headings) else len(html)
        section_html = html[section_start:section_end]

        list_matches = list(re.finditer(r"</(?:ul|ol)\s*>", section_html, re.IGNORECASE))
        if list_matches:
            return section_start + list_matches[-1].end()

        paragraph_matches = list(re.finditer(r"</p\s*>", section_html, re.IGNORECASE))
        if paragraph_matches:
            return section_start + paragraph_matches[-1].end()

        return section_end

    return None


def find_insertion_index_after_benodigdheden_list(html: str) -> int | None:
    return find_insertion_index_after_heading_section(html, ("benodigdheden", "wat heb je nodig"))


def find_insertion_index_after_review_score(html: str) -> int | None:
    start = re.search(r'<div\b[^>]*\bclass=["\'][^"\']*review-score-panel[^"\']*["\'][^>]*>', html, re.IGNORECASE)
    if not start:
        return None

    # Zoek de bijbehorende sluitende </div>, ook als er binnen het scoreblok nog een div staat
    # zoals <div class="review-score-value">.
    div_token_pattern = re.compile(r"<div\b[^>]*>|</div\s*>", re.IGNORECASE)
    depth = 1

    for token in div_token_pattern.finditer(html, start.end()):
        token_text = token.group(0).lower()
        if token_text.startswith("<div"):
            depth += 1
        else:
            depth -= 1

        if depth == 0:
            return token.end()

    return None


def find_review_insertion_index(html: str) -> int | None:
    # Voorkeur: direct onder het eindoordeel, omdat dit commercieel logisch is zonder de review te onderbreken.
    insertion_index = find_insertion_index_after_review_score(html)
    if insertion_index is not None:
        return insertion_index

    # Fallback: na de productuitleg.
    insertion_index = find_insertion_index_after_heading_section(html, ("wat is het",))
    if insertion_index is not None:
        return insertion_index

    # Tweede fallback: na de eerste alinea in het artikel.
    article_match = re.search(r'<article\b[^>]*>', html, re.IGNORECASE)
    if article_match:
        paragraph_match = re.search(r"</p\s*>", html[article_match.end():], re.IGNORECASE)
        if paragraph_match:
            return article_match.end() + paragraph_match.end()

    return None


def inject_into_html(
    html: str,
    product_keys: list[str],
    relative_path: str,
    *,
    article_type_from_report: str | None = None,
) -> tuple[str, str, int, str]:
    if not product_keys:
        return html, "skipped", 0, "unknown"

    article_type = "review" if is_review_page(html, relative_path, article_type_from_report) else "article"

    html, _ = remove_existing_auto_block(html)
    html, _ = ensure_affiliate_script_tag(html)

    if article_type == "review":
        insertion_index = find_review_insertion_index(html)
        missing_reason = "geen geschikt review-invoegpunt gevonden"
    else:
        insertion_index = find_insertion_index_after_benodigdheden_list(html)
        missing_reason = "geen Benodigdheden-sectie gevonden"

    if insertion_index is None:
        return html, "no_insertion_point", 0, article_type

    block_id_base = re.sub(r"[^a-z0-9]+", "-", relative_path.lower()).strip("-")
    if not block_id_base:
        block_id_base = "affiliate-auto"

    block = build_affiliate_block(product_keys, f"affiliate-auto-{block_id_base}", article_type)
    new_html = html[:insertion_index] + block + html[insertion_index:]

    return new_html, "ready", len(product_keys), article_type


def build_summary(results: list[InjectionResult]) -> str:
    total = len(results)
    updated = sum(1 for result in results if result.status == "updated")
    would_update = sum(1 for result in results if result.status == "would_update")
    skipped = total - updated - would_update

    lines = [
        "# Affiliate injector rapport",
        "",
        f"- Totaal beoordeeld: {total}",
        f"- Aangepast: {updated}",
        f"- Zou aangepast worden (dry-run): {would_update}",
        f"- Overgeslagen / niet aangepast: {skipped}",
        "",
    ]

    for result in results:
        lines.append(f"## {result.relative_path}")
        lines.append(f"- Artikeltype: {result.article_type}")
        lines.append(f"- Status: {result.status}")

        if result.reason:
            lines.append(f"- Reden: {result.reason}")

        if result.matched_product_keys:
            lines.append(f"- Productkeys: {', '.join(result.matched_product_keys)}")
        else:
            lines.append("- Productkeys: geen")

        lines.append(f"- Aantal inserts: {result.inserted_count}")
        lines.append(f"- Bestand geschreven: {'ja' if result.wrote_file else 'nee'}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Injecteer automatisch affiliate blocks in HTML-bestanden op basis van affiliate_report.json."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Projectmap waarin HTML-bestanden staan. Standaard: huidige map.",
    )
    parser.add_argument(
        "--report",
        required=True,
        type=Path,
        help="Pad naar affiliate_report.json.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Schrijf wijzigingen daadwerkelijk weg. Zonder deze vlag draait het script als dry-run.",
    )
    parser.add_argument(
        "--report-out",
        dest="report_out",
        type=Path,
        help="Schrijf een injector-rapport weg als JSON.",
    )
    parser.add_argument(
        "--md-out",
        dest="md_out",
        type=Path,
        help="Schrijf een injector-rapport weg als Markdown.",
    )
    parser.add_argument(
        "--include-drafts",
        action="store_true",
        help="Neem ook concept-, kopie- en RS-bestanden mee.",
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

    report_path = args.report if args.report.is_absolute() else (Path.cwd() / args.report).resolve()
    if not report_path.exists():
        raise SystemExit(f"Report niet gevonden: {report_path}")

    report_map = load_report(report_path)
    excluded_dir_names = parse_excluded_dirs(args.exclude_dir)

    results: list[InjectionResult] = []

    for path in sorted(
        iter_html_files(
            root,
            include_drafts=args.include_drafts,
            excluded_dir_names=excluded_dir_names,
            draft_patterns=DEFAULT_DRAFT_FILENAME_PATTERNS,
        )
    ):
        relative_path = path.relative_to(root).as_posix()
        report_item = report_map.get(relative_path, {})
        matched_product_keys = report_item.get("matched_product_keys", [])
        article_type_from_report = report_item.get("article_type")

        if not isinstance(matched_product_keys, list):
            matched_product_keys = []

        if not matched_product_keys:
            results.append(
                InjectionResult(
                    file=path.name,
                    relative_path=relative_path,
                    article_type=str(article_type_from_report or "unknown"),
                    matched_product_keys=[],
                    status="skipped",
                    reason="geen matched_product_keys in report",
                )
            )
            continue

        original_html = path.read_text(encoding="utf-8", errors="ignore")
        new_html, inject_status, inserted_count, detected_article_type = inject_into_html(
            original_html,
            [str(key) for key in matched_product_keys],
            relative_path,
            article_type_from_report=str(article_type_from_report) if article_type_from_report else None,
        )

        if inject_status == "no_insertion_point":
            reason = (
                "geen geschikt review-invoegpunt gevonden"
                if detected_article_type == "review"
                else "geen Benodigdheden-sectie gevonden"
            )
            results.append(
                InjectionResult(
                    file=path.name,
                    relative_path=relative_path,
                    article_type=detected_article_type,
                    matched_product_keys=[str(key) for key in matched_product_keys],
                    status="skipped",
                    reason=reason,
                    inserted_count=0,
                )
            )
            continue

        if new_html == original_html:
            results.append(
                InjectionResult(
                    file=path.name,
                    relative_path=relative_path,
                    article_type=detected_article_type,
                    matched_product_keys=[str(key) for key in matched_product_keys],
                    status="unchanged",
                    reason="geen wijziging nodig",
                    inserted_count=inserted_count,
                    wrote_file=False,
                )
            )
            continue

        if args.write:
            path.write_text(new_html, encoding="utf-8")
            results.append(
                InjectionResult(
                    file=path.name,
                    relative_path=relative_path,
                    article_type=detected_article_type,
                    matched_product_keys=[str(key) for key in matched_product_keys],
                    status="updated",
                    inserted_count=inserted_count,
                    wrote_file=True,
                )
            )
        else:
            results.append(
                InjectionResult(
                    file=path.name,
                    relative_path=relative_path,
                    article_type=detected_article_type,
                    matched_product_keys=[str(key) for key in matched_product_keys],
                    status="would_update",
                    reason="dry-run",
                    inserted_count=inserted_count,
                    wrote_file=False,
                )
            )

    payload = {
        "mode": "write" if args.write else "dry-run",
        "results": [asdict(result) for result in results],
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.report_out:
        args.report_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.md_out:
        args.md_out.write_text(build_summary(results), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
