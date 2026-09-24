#!/usr/bin/env python3
"""
HuisvanVandaag HTML migratie- en controlescript.

Doel:
- Scan bestaande HTML-artikelen.
- Detecteer artikeltype.
- Controleer SEO/AI/schema-vereisten.
- Rapporteer ontbrekende onderdelen.
- Pas optioneel alleen veilige technische fixes toe.

Veilige automatische fixes:
- dubbele <body>-openingen verwijderen
- dubbele </body>-sluitingen verwijderen
- dubbele script.js includes verwijderen
- canonical toevoegen als die ontbreekt
- author-meta toevoegen als die ontbreekt
- modified_date toevoegen op basis van publish_date
- robots-meta toevoegen als die ontbreekt
- hv-schema-type proberen te bepalen en toevoegen als die ontbreekt
- hv-product-name bij reviews proberen af te leiden uit H1
- defer toevoegen aan affiliate-products.js als defer/async ontbreekt
- loading="lazy" en decoding="async" toevoegen aan niet-hero afbeeldingen
- fetchpriority="high" en decoding="async" toevoegen aan hero-afbeelding

NIET automatisch:
- publiceren/veranderen van inhoudelijke tekst
- Kort antwoord genereren
- FAQ genereren
- bronnen verzinnen
- testcontext verzinnen
- affiliate-links verzinnen
- interne links verzinnen

Gebruik:
    python tools/migrate_existing_articles.py .
    python tools/migrate_existing_articles.py . --apply
    python tools/migrate_existing_articles.py . --apply --backup
    python tools/migrate_existing_articles.py . --csv migratie-rapport.csv

Standaard worden bekende index-/overzichtspagina's overgeslagen.
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin


SITE_URL = "https://www.huisvanvandaag.nl/"
DEFAULT_AUTHOR = "Mike Mulders"

SKIP_FILENAMES = {
    "index.html",
    "404.html",
    "reviews.html",
    "tutorials.html",
    "diy.html",
    "homey.html",
    "privacy.html",
    "contact.html",
    "over.html",
    "privacy-disclaimer.html",
    "informatief.html",
}

ARTICLE_TYPES = {"howto", "techarticle", "review"}


@dataclass
class CheckResult:
    file: Path
    article_type: str = ""
    title: str = ""
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    fixes_applied: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.issues:
            return "AANDACHT"
        if self.suggestions:
            return "GOED + REDACTIONEEL"
        return "GOED"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def get_meta(text: str, name: str) -> str:
    patterns = [
        rf'<meta\b[^>]*\bname=["\']{re.escape(name)}["\'][^>]*\bcontent=["\']([^"\']*)["\'][^>]*>',
        rf'<meta\b[^>]*\bcontent=["\']([^"\']*)["\'][^>]*\bname=["\']{re.escape(name)}["\'][^>]*>',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return html.unescape(match.group(1).strip())
    return ""


def get_title(text: str) -> str:
    h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", text, re.I | re.S)
    if h1:
        return strip_tags(h1.group(1)).strip()

    title = re.search(r"<title\b[^>]*>(.*?)</title>", text, re.I | re.S)
    if title:
        value = strip_tags(title.group(1)).strip()
        value = re.sub(r"\s*\|\s*huisvanvandaag\.nl\s*$", "", value, flags=re.I)
        return value.strip()

    return ""


def strip_tags(value: str) -> str:
    value = re.sub(r"<script\b.*?</script>", "", value, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", "", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def canonical_for(path: Path, root: Path) -> str:
    rel = path.relative_to(root).as_posix()
    return urljoin(SITE_URL, rel)


def has_canonical(text: str) -> bool:
    return bool(re.search(r'<link\b[^>]*\brel=["\']canonical["\']', text, re.I))


def get_canonical(text: str) -> str:
    patterns = [
        r'<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=["\']([^"\']+)["\']',
        r'<link\b[^>]*\bhref=["\']([^"\']+)["\'][^>]*\brel=["\']canonical["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return match.group(1).strip()
    return ""


def detect_article_type(text: str, path: Path) -> str:
    existing = get_meta(text, "hv-schema-type").lower()
    if existing in ARTICLE_TYPES:
        return existing

    lower = text.lower()
    name = path.name.lower()

    if name in {
        "gemini-voor-home.html",
        "homey-bridge.html",
    }:
        return "techarticle"

    review_signals = [
        'href="reviews.html"',
        'id="pluspunten"',
        'id="minpunten"',
        "eindoordeel",
        "kort oordeel",
        "review-score",
    ]
    if any(signal in lower for signal in review_signals) or "review" in name:
        return "review"

    tutorial_signals = [
        'href="tutorials.html"',
        "veelgemaakte fouten",
        "wat leer je",
        "stap-voor-stap",
        "tutorial",
    ]
    if any(signal in lower for signal in tutorial_signals) or "tutorial" in name:
        return "howto"

    diy_signals = [
        'href="diy.html"',
        "wat ga je bouwen",
        "benodigdheden",
        "diy",
    ]
    if any(signal in lower for signal in diy_signals):
        return "howto"

    info_signals = [
    "kennisbank",
    'href="homey.html"',
    "kort samengevat",
    "informatief",
    "maak kennis met",
    "wat is ",
    "wat doet ",
]
    if any(signal in lower for signal in info_signals):
        return "techarticle"

    # Alleen classificeren als het duidelijk op een artikel lijkt.
    if "<article" in lower and "<h1" in lower:
        return "techarticle"

    return ""


def article_like(text: str, path: Path) -> bool:
    if path.name.lower() in SKIP_FILENAMES:
        return False
    lower = text.lower()
    return "<h1" in lower and ("<article" in lower or "article-hero" in lower or "project-article" in lower)


def count_open_body(text: str) -> int:
    return len(re.findall(r"<body\b[^>]*>", text, re.I))


def count_close_body(text: str) -> int:
    return len(re.findall(r"</body\s*>", text, re.I))


def count_script_js(text: str) -> int:
    return len(re.findall(r'<script\b[^>]*\bsrc=["\'][^"\']*script\.js(?:\?[^"\']*)?["\'][^>]*>\s*</script>', text, re.I))


def has_robots(text: str) -> bool:
    return bool(get_meta(text, "robots"))


def has_author(text: str) -> bool:
    return bool(get_meta(text, "author"))


def has_publish_date(text: str) -> bool:
    return bool(get_meta(text, "publish_date"))


def has_modified_date(text: str) -> bool:
    return bool(get_meta(text, "modified_date"))


def has_open_graph(text: str) -> bool:
    return bool(re.search(r'<meta\b[^>]*\bproperty=["\']og:title["\']', text, re.I))


def has_visible_author(text: str) -> bool:
    return bool(
        re.search(r'rel=["\']author["\']', text, re.I)
        or re.search(r"\bDoor\s+Mike\s+Mulders\b", strip_tags(text), re.I)
    )


def has_kort_answer(text: str, article_type: str) -> bool:
    if article_type == "review":
        return bool(re.search(r'id=["\']kort-oordeel["\']', text, re.I))
    return bool(re.search(r'id=["\']kort-antwoord["\']', text, re.I))


def has_sources(text: str) -> bool:
    return bool(re.search(r'id=["\']bronnen["\']', text, re.I))


def has_test_context(text: str) -> bool:
    return bool(re.search(r'id=["\']wat-is-getest["\']', text, re.I))


def has_review_product_name(text: str) -> bool:
    return bool(get_meta(text, "hv-product-name"))


def has_internal_links(text: str) -> bool:
    hrefs = re.findall(r'<a\b[^>]*\bhref=["\']([^"\']+)["\']', text, re.I)
    article_links = [
        href for href in hrefs
        if href
        and not href.startswith(("#", "mailto:", "tel:", "http://", "https://"))
        and href.lower().endswith((".html", "/"))
    ]
    return len(article_links) >= 2


def has_affiliate_script(text: str) -> bool:
    return "affiliate-products.js" in text


def affiliate_script_deferred(text: str) -> bool:
    match = re.search(
        r'<script\b([^>]*)\bsrc=["\'][^"\']*affiliate-products\.js["\']([^>]*)>',
        text,
        re.I | re.S,
    )
    if not match:
        return True
    attrs = f"{match.group(1)} {match.group(2)}".lower()
    return " defer" in f" {attrs}" or " async" in f" {attrs}"


def audit(path: Path, root: Path, text: str) -> CheckResult:
    result = CheckResult(file=path)
    result.article_type = detect_article_type(text, path)
    result.title = get_title(text)

    if count_open_body(text) != 1:
        result.issues.append(f"{count_open_body(text)} openende <body>-tags")
    if count_close_body(text) != 1:
        result.issues.append(f"{count_close_body(text)} sluitende </body>-tags")
    if count_script_js(text) > 1:
        result.issues.append(f"script.js wordt {count_script_js(text)}× geladen")

    if not has_canonical(text):
        result.issues.append("canonical ontbreekt")
    else:
        canonical = get_canonical(text)
        if canonical and canonical.startswith("https://huisvanvandaag.nl"):
            result.issues.append("canonical gebruikt non-www domein")

    if not get_meta(text, "hv-schema-type"):
        result.issues.append("hv-schema-type ontbreekt")
    if not has_publish_date(text):
        result.issues.append("publish_date ontbreekt")
    if not has_modified_date(text):
        result.issues.append("modified_date ontbreekt")
    if not has_author(text):
        result.issues.append("author-meta ontbreekt")
    if not has_robots(text):
        result.issues.append("robots-meta ontbreekt")
    if not has_open_graph(text):
        result.suggestions.append("Open Graph metadata ontbreekt")
    if not has_visible_author(text):
        result.suggestions.append("zichtbare auteur/datum ontbreekt")

    if result.article_type and not has_kort_answer(text, result.article_type):
        if result.article_type == "review":
            result.suggestions.append("Kort oordeel ontbreekt")
        else:
            result.suggestions.append("Kort antwoord ontbreekt")

    if result.article_type == "techarticle" and not has_sources(text):
        result.suggestions.append("bronnenblok ontbreekt")
    if result.article_type == "review":
        if not has_test_context(text):
            result.suggestions.append("testcontext ontbreekt")
        if not has_review_product_name(text):
            result.issues.append("hv-product-name ontbreekt")
    if not has_internal_links(text):
        result.suggestions.append("weinig/geen interne artikel-links")

    if has_affiliate_script(text) and not affiliate_script_deferred(text):
        result.issues.append("affiliate-products.js mist defer/async")

    return result


def insert_before_head_close(text: str, snippet: str) -> str:
    match = re.search(r"</head\s*>", text, re.I)
    if not match:
        return text
    return text[:match.start()] + snippet.rstrip() + "\n" + text[match.start():]


def insert_after_viewport(text: str, snippet: str) -> str:
    viewport = re.search(
        r'<meta\b[^>]*\bname=["\']viewport["\'][^>]*>',
        text,
        re.I | re.S,
    )
    if viewport:
        return text[:viewport.end()] + "\n" + snippet.rstrip() + text[viewport.end():]

    charset = re.search(r'<meta\b[^>]*\bcharset=["\'][^"\']+["\'][^>]*>', text, re.I | re.S)
    if charset:
        return text[:charset.end()] + "\n" + snippet.rstrip() + text[charset.end():]

    return insert_before_head_close(text, snippet)


def add_meta_if_missing(text: str, name: str, content: str) -> tuple[str, bool]:
    if get_meta(text, name):
        return text, False

    escaped = html.escape(content, quote=True)
    snippet = f'  <meta name="{name}" content="{escaped}">\n'
    return insert_after_viewport(text, snippet), True


def add_canonical_if_missing(text: str, canonical: str) -> tuple[str, bool]:
    if has_canonical(text):
        return text, False

    snippet = f'  <link rel="canonical" href="{html.escape(canonical, quote=True)}">\n'
    return insert_before_head_close(text, snippet), True


def normalize_canonical_www(text: str) -> tuple[str, bool]:
    old = text
    text = re.sub(
        r'(rel=["\']canonical["\'][^>]*href=["\'])https://huisvanvandaag\.nl',
        r'\1https://www.huisvanvandaag.nl',
        text,
        flags=re.I,
    )
    text = re.sub(
        r'(href=["\'])https://huisvanvandaag\.nl([^"\']*["\'][^>]*rel=["\']canonical["\'])',
        r'\1https://www.huisvanvandaag.nl\2',
        text,
        flags=re.I,
    )
    return text, text != old


def remove_duplicate_body_tags(text: str) -> tuple[str, bool]:
    changed = False

    body_matches = list(re.finditer(r"<body\b[^>]*>", text, re.I))
    if len(body_matches) > 1:
        keep = body_matches[0]
        parts = []
        last = 0
        for idx, m in enumerate(body_matches):
            parts.append(text[last:m.start()])
            if idx == 0:
                parts.append(m.group(0))
            else:
                changed = True
            last = m.end()
        parts.append(text[last:])
        text = "".join(parts)

    close_matches = list(re.finditer(r"</body\s*>", text, re.I))
    if len(close_matches) > 1:
        # Bewaar alleen de laatste sluitende body-tag.
        keep_idx = len(close_matches) - 1
        parts = []
        last = 0
        for idx, m in enumerate(close_matches):
            parts.append(text[last:m.start()])
            if idx == keep_idx:
                parts.append(m.group(0))
            else:
                changed = True
            last = m.end()
        parts.append(text[last:])
        text = "".join(parts)

    return text, changed


def remove_duplicate_script_js(text: str) -> tuple[str, bool]:
    pattern = re.compile(
        r'<script\b[^>]*\bsrc=["\'][^"\']*script\.js(?:\?[^"\']*)?["\'][^>]*>\s*</script>',
        re.I,
    )
    matches = list(pattern.finditer(text))
    if len(matches) <= 1:
        return text, False

    result = []
    last = 0
    for idx, m in enumerate(matches):
        result.append(text[last:m.start()])
        if idx == 0:
            result.append(m.group(0))
        last = m.end()
    result.append(text[last:])
    return "".join(result), True


def add_defer_to_affiliate_script(text: str) -> tuple[str, bool]:
    pattern = re.compile(
        r'<script\b(?P<before>[^>]*)\bsrc=(?P<quote>["\'])'
        r'(?P<src>[^"\']*affiliate-products\.js)'
        r'(?P=quote)(?P<after>[^>]*)>',
        re.I | re.S,
    )

    def repl(match: re.Match[str]) -> str:
        attrs = f"{match.group('before')} {match.group('after')}".lower()
        if re.search(r"\b(?:defer|async)\b", attrs):
            return match.group(0)

        before = match.group("before").rstrip()
        after = match.group("after")
        return (
            f'<script{before} src={match.group("quote")}'
            f'{match.group("src")}{match.group("quote")} defer{after}>'
        )

    new_text, count = pattern.subn(repl, text)
    return new_text, count > 0 and new_text != text


def add_image_loading_attributes(text: str) -> tuple[str, list[str]]:
    fixes = []

    hero_pattern = re.compile(
        r'(<div\b[^>]*class=["\'][^"\']*project-hero-media[^"\']*["\'][^>]*>.*?<img\b)([^>]*)(>)',
        re.I | re.S,
    )

    def hero_repl(match: re.Match[str]) -> str:
        attrs = match.group(2)
        additions = ""
        if not re.search(r"\bfetchpriority\s*=", attrs, re.I):
            additions += ' fetchpriority="high"'
        if not re.search(r"\bdecoding\s*=", attrs, re.I):
            additions += ' decoding="async"'
        return match.group(1) + attrs + additions + match.group(3)

    new_text, hero_count = hero_pattern.subn(hero_repl, text, count=1)
    if new_text != text:
        fixes.append("hero-afbeelding attributen")
    text = new_text

    # Alle overige afbeeldingen: geen logo/header/footer aannames aanpassen,
    # alleen afbeeldingen binnen project/article content.
    img_pattern = re.compile(
        r'(<(?:article|div)\b[^>]*(?:project-article|article-body)[^>]*>.*?)(</(?:article|div)>)',
        re.I | re.S,
    )
    block = img_pattern.search(text)
    if block:
        content = block.group(1)

        def img_repl(match: re.Match[str]) -> str:
            tag = match.group(0)
            if "project-hero-media" in tag:
                return tag
            if not re.search(r"\bloading\s*=", tag, re.I):
                tag = tag[:-1] + ' loading="lazy">'
            if not re.search(r"\bdecoding\s*=", tag, re.I):
                tag = tag[:-1] + ' decoding="async">'
            return tag

        updated = re.sub(r"<img\b[^>]*>", img_repl, content, flags=re.I)
        if updated != content:
            text = text[:block.start(1)] + updated + text[block.end(1):]
            fixes.append("lazy loading contentafbeeldingen")

    return text, fixes


def apply_safe_fixes(path: Path, root: Path, text: str, result: CheckResult) -> str:
    article_type = result.article_type or detect_article_type(text, path)

    text, changed = remove_duplicate_body_tags(text)
    if changed:
        result.fixes_applied.append("dubbele body-tags verwijderd")

    text, changed = remove_duplicate_script_js(text)
    if changed:
        result.fixes_applied.append("dubbele script.js include verwijderd")

    text, changed = add_canonical_if_missing(text, canonical_for(path, root))
    if changed:
        result.fixes_applied.append("canonical toegevoegd")

    text, changed = normalize_canonical_www(text)
    if changed:
        result.fixes_applied.append("canonical naar www genormaliseerd")

    if article_type:
        text, changed = add_meta_if_missing(text, "hv-schema-type", article_type)
        if changed:
            result.fixes_applied.append(f"hv-schema-type={article_type} toegevoegd")

    publish_date = get_meta(text, "publish_date")
    if publish_date:
        text, changed = add_meta_if_missing(text, "modified_date", publish_date)
        if changed:
            result.fixes_applied.append("modified_date uit publish_date toegevoegd")

    text, changed = add_meta_if_missing(text, "author", DEFAULT_AUTHOR)
    if changed:
        result.fixes_applied.append("author-meta toegevoegd")

    text, changed = add_meta_if_missing(
        text,
        "robots",
        "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1",
    )
    if changed:
        result.fixes_applied.append("robots-meta toegevoegd")

    if article_type == "review" and not get_meta(text, "hv-product-name"):
        title = result.title or get_title(text)
        product_name = re.sub(r"\breview\b.*$", "", title, flags=re.I).strip(" :-–—|")
        product_name = product_name or title
        if product_name:
            text, changed = add_meta_if_missing(text, "hv-product-name", product_name)
            if changed:
                result.fixes_applied.append(
                    f'hv-product-name toegevoegd als "{product_name}"'
                )

    text, changed = add_defer_to_affiliate_script(text)
    if changed:
        result.fixes_applied.append("defer aan affiliate-products.js toegevoegd")

    text, image_fixes = add_image_loading_attributes(text)
    result.fixes_applied.extend(image_fixes)

    return text


def find_html_files(root: Path) -> Iterable[Path]:
    excluded_dirs = {
        ".git",
        ".github",
        "node_modules",
        "vendor",
        "dist",
        "build",
        "backup",
        "backups",
    }

    for path in sorted(root.rglob("*.html")):
        if any(part.lower() in excluded_dirs for part in path.relative_to(root).parts[:-1]):
            continue
        yield path


def print_report(results: list[CheckResult], root: Path) -> None:
    print()
    print("=" * 80)
    print(" HUISVANVANDAAG - BESTAANDE ARTIKELEN MIGRATIERAPPORT")
    print("=" * 80)

    counts = {"GOED": 0, "GOED + REDACTIONEEL": 0, "AANDACHT": 0}

    for result in results:
        counts[result.status] += 1
        rel = result.file.relative_to(root)
        print()
        print(f"[{result.status}] {rel}")
        print(f"  Type : {result.article_type or 'onbekend'}")
        print(f"  Titel: {result.title or '(geen titel gevonden)'}")

        for issue in result.issues:
            print(f"  ! {issue}")

        for suggestion in result.suggestions:
            print(f"  ~ {suggestion}")

        for fix in result.fixes_applied:
            print(f"  ✓ FIX: {fix}")

    print()
    print("-" * 80)
    print(f"Totaal artikelen       : {len(results)}")
    print(f"Technisch goed         : {counts['GOED']}")
    print(f"Goed, redactie gewenst : {counts['GOED + REDACTIONEEL']}")
    print(f"Technische aandacht    : {counts['AANDACHT']}")
    print("-" * 80)


def write_csv(results: list[CheckResult], root: Path, target: Path) -> None:
    with target.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(
            [
                "bestand",
                "status",
                "artikeltype",
                "titel",
                "technische_punten",
                "redactionele_punten",
                "fixes_toegepast",
            ]
        )

        for r in results:
            writer.writerow(
                [
                    r.file.relative_to(root).as_posix(),
                    r.status,
                    r.article_type,
                    r.title,
                    " | ".join(r.issues),
                    " | ".join(r.suggestions),
                    " | ".join(r.fixes_applied),
                ]
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan en migreer bestaande HuisvanVandaag HTML-artikelen."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Rootmap van de website/repository (standaard: huidige map).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Pas veilige technische fixes toe.",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Maak voor gewijzigde bestanden een .bak kopie. Alleen relevant met --apply.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="Schrijf daarnaast een CSV-rapport.",
    )
    parser.add_argument(
        "--all-html",
        action="store_true",
        help="Scan ook HTML die niet automatisch als artikel wordt herkend.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    if not root.exists() or not root.is_dir():
        print(f"FOUT: map bestaat niet: {root}", file=sys.stderr)
        return 2

    results: list[CheckResult] = []

    for path in find_html_files(root):
        original = read_text(path)

        if not args.all_html and not article_like(original, path):
            continue

        result = audit(path, root, original)

        if args.apply:
            updated = apply_safe_fixes(path, root, original, result)

            if updated != original:
                if args.backup:
                    backup = path.with_suffix(path.suffix + ".bak")
                    shutil.copy2(path, backup)

                write_text(path, updated)

                # Na migratie opnieuw auditen zodat het rapport de actuele staat toont.
                fixes = list(result.fixes_applied)
                result = audit(path, root, updated)
                result.fixes_applied = fixes

        results.append(result)

    print_report(results, root)

    if args.csv:
        target = args.csv
        if not target.is_absolute():
            target = Path.cwd() / target
        write_csv(results, root, target)
        print(f"\nCSV-rapport geschreven naar: {target}")

    if not results:
        print("\nGeen artikelpagina's gevonden.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
