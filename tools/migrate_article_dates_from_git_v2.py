#!/usr/bin/env python3
"""
HuisvanVandaag - artikeldata controleren en migreren via Git.

Doel:
- Controleer in één run alle artikel-HTML-bestanden.
- Bepaal de vermoedelijke eerste publicatiedatum via de oudste Git-commit.
- Lees de nieuwste Git-commit als controlesignaal.
- Gebruik standaard NIET automatisch de nieuwste Git-commit als modified_date.
- Vergelijk bestaande publish_date / modified_date met de Git-historie.
- Schrijf standaard niets weg.
- Pas datums alleen toe met --apply.
- Bestaande publish_date wordt standaard NIET overschreven.
- Gebruik --force om bestaande datums te vervangen door Git-data.

Belangrijk:
Git kent de datum waarop een bestand voor het eerst in de repository verscheen.
Dat is meestal een goede benadering van de oorspronkelijke publicatiedatum,
maar het is niet gegarandeerd hetzelfde als de echte publicatiedatum wanneer
oude bestanden pas later aan Git zijn toegevoegd.

Gebruik:
    python tools/migrate_article_dates_from_git.py .
    python tools/migrate_article_dates_from_git.py . --csv datum-rapport.csv
    python tools/migrate_article_dates_from_git.py . --apply --backup
    python tools/migrate_article_dates_from_git.py . --apply --backup --csv datum-rapport.csv

Optioneel:
    --force
        Overschrijf bestaande publish_date / modified_date met Git-datums.

    --all-html
        Scan alle HTML-bestanden i.p.v. alleen artikelachtige pagina's.
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable


SKIP_FILENAMES = {
    "index.html",
    "404.html",
    "reviews.html",
    "tutorials.html",
    "diy.html",
    "homey.html",
    "privacy.html",
    "privacy-disclaimer.html",
    "contact.html",
    "over.html",
    "informatief.html",
}

EXCLUDED_DIRS = {
    ".git",
    ".github",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "backup",
    "backups",
}


@dataclass
class DateResult:
    file: Path
    title: str = ""
    existing_publish: str = ""
    existing_modified: str = ""
    git_first: str = ""
    git_last: str = ""
    proposed_publish: str = ""
    proposed_modified: str = ""
    status: str = ""
    notes: list[str] = field(default_factory=list)
    applied: list[str] = field(default_factory=list)


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def ensure_git_repo(root: Path) -> None:
    proc = run_git(root, ["rev-parse", "--show-toplevel"])
    if proc.returncode != 0:
        raise RuntimeError(
            "De opgegeven map is geen Git-repository of Git is niet beschikbaar."
        )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def strip_tags(value: str) -> str:
    value = re.sub(r"<script\b.*?</script>", "", value, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", "", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def get_title(text: str) -> str:
    h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", text, re.I | re.S)
    if h1:
        return strip_tags(h1.group(1)).strip()

    title = re.search(r"<title\b[^>]*>(.*?)</title>", text, re.I | re.S)
    if title:
        value = strip_tags(title.group(1)).strip()
        value = re.sub(
            r"\s*\|\s*huisvanvandaag\.nl\s*$",
            "",
            value,
            flags=re.I,
        )
        return value.strip()

    return ""


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


def valid_date(value: str) -> bool:
    if not value:
        return False

    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def article_like(text: str, path: Path) -> bool:
    if path.name.lower() in SKIP_FILENAMES:
        return False

    lower = text.lower()

    return (
        "<h1" in lower
        and (
            "<article" in lower
            or "article-hero" in lower
            or "project-article" in lower
            or get_meta(text, "hv-schema-type")
        )
    )


def find_html_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.html")):
        rel_parts = path.relative_to(root).parts[:-1]

        if any(part.lower() in EXCLUDED_DIRS for part in rel_parts):
            continue

        yield path


def git_dates_for_file(root: Path, path: Path) -> tuple[str, str, list[str]]:
    """
    Retourneert:
    - oudste commitdatum
    - nieuwste commitdatum
    - notities

    --follow wordt gebruikt om eenvoudige renames te volgen.
    """
    notes: list[str] = []
    rel = path.relative_to(root).as_posix()

    proc = run_git(
        root,
        [
            "log",
            "--follow",
            "--format=%ad",
            "--date=short",
            "--",
            rel,
        ],
    )

    if proc.returncode != 0:
        notes.append("Git-log kon niet worden gelezen")
        return "", "", notes

    dates = [
        line.strip()
        for line in proc.stdout.splitlines()
        if valid_date(line.strip())
    ]

    if not dates:
        notes.append("geen Git-historie voor dit bestand gevonden")
        return "", "", notes

    newest = dates[0]
    oldest = dates[-1]

    if oldest == newest:
        notes.append("bestand komt slechts in één Git-commit voor")

    return oldest, newest, notes


def replace_or_add_meta(
    text: str,
    name: str,
    value: str,
    *,
    overwrite: bool,
) -> tuple[str, bool]:
    """
    Vervangt een bestaande meta-tag indien overwrite=True.
    Voegt anders een ontbrekende meta-tag toe.
    """
    patterns = [
        re.compile(
            rf'(<meta\b[^>]*\bname=["\']{re.escape(name)}["\'][^>]*\bcontent=["\'])([^"\']*)(["\'][^>]*>)',
            re.I | re.S,
        ),
        re.compile(
            rf'(<meta\b[^>]*\bcontent=["\'])([^"\']*)(["\'][^>]*\bname=["\']{re.escape(name)}["\'][^>]*>)',
            re.I | re.S,
        ),
    ]

    for pattern in patterns:
        match = pattern.search(text)

        if match:
            if not overwrite:
                return text, False

            new_text = (
                text[:match.start()]
                + match.group(1)
                + value
                + match.group(3)
                + text[match.end():]
            )
            return new_text, new_text != text

    snippet = f'  <meta name="{name}" content="{value}">\n'

    viewport = re.search(
        r'<meta\b[^>]*\bname=["\']viewport["\'][^>]*>',
        text,
        re.I | re.S,
    )

    if viewport:
        return (
            text[:viewport.end()]
            + "\n"
            + snippet
            + text[viewport.end():],
            True,
        )

    charset = re.search(
        r'<meta\b[^>]*\bcharset=["\'][^"\']+["\'][^>]*>',
        text,
        re.I | re.S,
    )

    if charset:
        return (
            text[:charset.end()]
            + "\n"
            + snippet
            + text[charset.end():],
            True,
        )

    head_close = re.search(r"</head\s*>", text, re.I)
    if head_close:
        return (
            text[:head_close.start()]
            + snippet
            + text[head_close.start():],
            True,
        )

    return text, False


def analyze_file(
    root: Path,
    path: Path,
    text: str,
) -> DateResult:
    result = DateResult(file=path)
    result.title = get_title(text)
    result.existing_publish = get_meta(text, "publish_date")
    result.existing_modified = get_meta(text, "modified_date")

    git_first, git_last, notes = git_dates_for_file(root, path)
    result.git_first = git_first
    result.git_last = git_last
    result.notes.extend(notes)

    # Voorgestelde publish date:
    if valid_date(result.existing_publish):
        result.proposed_publish = result.existing_publish
    elif git_first:
        result.proposed_publish = git_first

    # Voorgestelde modified date:
    # Veilig uitgangspunt: een ontbrekende modified_date wordt gelijk aan publish_date.
    # De nieuwste Git-commit is alleen een controlesignaal, omdat brede template-
    # of technische wijzigingen anders ten onrechte als inhoudelijke update gelden.
    if valid_date(result.existing_modified):
        result.proposed_modified = result.existing_modified
    elif result.proposed_publish:
        result.proposed_modified = result.proposed_publish

    # Analyse / waarschuwingen
    if result.existing_publish and not valid_date(result.existing_publish):
        result.notes.append("bestaande publish_date heeft ongeldig formaat")

    if result.existing_modified and not valid_date(result.existing_modified):
        result.notes.append("bestaande modified_date heeft ongeldig formaat")

    if (
        valid_date(result.existing_publish)
        and git_first
        and result.existing_publish != git_first
    ):
        result.notes.append(
            f"publish_date wijkt af van oudste Git-datum ({git_first})"
        )

    if (
        valid_date(result.existing_modified)
        and git_last
        and result.existing_modified != git_last
    ):
        result.notes.append(
            f"modified_date wijkt af van laatste Git-datum ({git_last})"
        )

    if result.proposed_publish and result.proposed_modified:
        if result.proposed_modified < result.proposed_publish:
            result.notes.append(
                "modified_date ligt vóór publish_date; handmatige controle nodig"
            )

    # Status
    if not result.proposed_publish:
        result.status = "HANDMATIG"
    elif not result.existing_publish or not result.existing_modified:
        result.status = "AANVULLEN"
    elif result.notes:
        result.status = "CONTROLEREN"
    else:
        result.status = "GOED"

    return result


def apply_dates(
    path: Path,
    text: str,
    result: DateResult,
    *,
    force: bool,
    use_git_modified: bool,
) -> str:
    """
    Standaard:
    - bestaande publish_date niet overschrijven
    - bestaande modified_date niet overschrijven
    - alleen ontbrekende waarden invullen

    Met --force:
    - gebruik Git first als publish_date

    Standaard:
    - ontbrekende modified_date = publish_date

    Met --use-git-modified:
    - gebruik bewust Git last als modified_date
    """
    publish_value = (
        result.git_first
        if force and result.git_first
        else result.proposed_publish
    )

    if use_git_modified and result.git_last:
        modified_value = result.git_last
    else:
        modified_value = result.proposed_modified

    if publish_value:
        overwrite_publish = force or not valid_date(result.existing_publish)
        text, changed = replace_or_add_meta(
            text,
            "publish_date",
            publish_value,
            overwrite=overwrite_publish,
        )
        if changed:
            result.applied.append(f"publish_date={publish_value}")

    if modified_value:
        overwrite_modified = force or not valid_date(result.existing_modified)
        text, changed = replace_or_add_meta(
            text,
            "modified_date",
            modified_value,
            overwrite=overwrite_modified,
        )
        if changed:
            result.applied.append(f"modified_date={modified_value}")

    return text


def print_report(results: list[DateResult], root: Path) -> None:
    print()
    print("=" * 92)
    print(" HUISVANVANDAAG - GIT ARTIKELDATUM RAPPORT")
    print("=" * 92)

    totals: dict[str, int] = {}

    for result in results:
        totals[result.status] = totals.get(result.status, 0) + 1

        rel = result.file.relative_to(root)

        print()
        print(f"[{result.status}] {rel}")
        print(f"  Titel              : {result.title or '(geen titel gevonden)'}")
        print(f"  Bestaand publish   : {result.existing_publish or '-'}")
        print(f"  Bestaand modified  : {result.existing_modified or '-'}")
        print(f"  Oudste Git-datum   : {result.git_first or '-'}")
        print(f"  Laatste Git-datum  : {result.git_last or '-'}")
        print(f"  Voorstel publish   : {result.proposed_publish or '-'}")
        print(f"  Voorstel modified  : {result.proposed_modified or '-'}")

        for note in result.notes:
            print(f"  ~ {note}")

        for applied in result.applied:
            print(f"  ✓ {applied}")

    print()
    print("-" * 92)
    print(f"Totaal artikelen: {len(results)}")
    for status in sorted(totals):
        print(f"{status:12}: {totals[status]}")
    print("-" * 92)


def write_csv(
    results: list[DateResult],
    root: Path,
    target: Path,
) -> None:
    with target.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")

        writer.writerow(
            [
                "bestand",
                "status",
                "titel",
                "bestaande_publish_date",
                "bestaande_modified_date",
                "git_eerste_datum",
                "git_laatste_datum",
                "voorgestelde_publish_date",
                "voorgestelde_modified_date",
                "notities",
                "toegepast",
            ]
        )

        for r in results:
            writer.writerow(
                [
                    r.file.relative_to(root).as_posix(),
                    r.status,
                    r.title,
                    r.existing_publish,
                    r.existing_modified,
                    r.git_first,
                    r.git_last,
                    r.proposed_publish,
                    r.proposed_modified,
                    " | ".join(r.notes),
                    " | ".join(r.applied),
                ]
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Controleer en migreer HuisvanVandaag artikeldata "
            "op basis van Git-historie."
        )
    )

    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Rootmap van de website/repository.",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Schrijf voorgestelde datums naar de HTML.",
    )

    parser.add_argument(
        "--backup",
        action="store_true",
        help="Maak .bak-bestanden van gewijzigde HTML-bestanden.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overschrijf bestaande datums met Git first/last dates. "
            "Gebruik alleen na controle van het rapport."
        ),
    )

    parser.add_argument(
        "--use-git-modified",
        action="store_true",
        help=(
            "Gebruik de nieuwste Git-commit als modified_date. "
            "Standaard wordt een ontbrekende modified_date gelijk aan publish_date."
        ),
    )

    parser.add_argument(
        "--csv",
        type=Path,
        help="Schrijf een CSV-rapport.",
    )

    parser.add_argument(
        "--all-html",
        action="store_true",
        help="Scan alle HTML-bestanden in plaats van alleen artikelpagina's.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    if not root.exists() or not root.is_dir():
        print(f"FOUT: map bestaat niet: {root}", file=sys.stderr)
        return 2

    try:
        ensure_git_repo(root)
    except RuntimeError as exc:
        print(f"FOUT: {exc}", file=sys.stderr)
        return 2

    results: list[DateResult] = []

    for path in find_html_files(root):
        original = read_text(path)

        if not args.all_html and not article_like(original, path):
            continue

        result = analyze_file(root, path, original)

        if args.apply:
            updated = apply_dates(
                path,
                original,
                result,
                force=args.force,
                use_git_modified=args.use_git_modified,
            )

            if updated != original:
                if args.backup:
                    backup_path = path.with_suffix(path.suffix + ".bak")
                    shutil.copy2(path, backup_path)

                write_text(path, updated)

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
