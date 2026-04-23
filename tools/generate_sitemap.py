from pathlib import Path
import datetime

ROOT_URL = "https://www.huisvanvandaag.nl"

SKIP_FILES = {
    "header.html",
    "footer.html",
}

SKIP_PREFIXES = (
    "sjabloon-",
)

def should_skip(path: Path):
    name = path.name.lower()
    if name in SKIP_FILES:
        return True
    if any(name.startswith(p) for p in SKIP_PREFIXES):
        return True
    return False


def generate_sitemap(root: Path):
    urls = []

    for path in root.rglob("*.html"):
        if should_skip(path):
            continue

        rel = path.relative_to(root).as_posix()

        # homepage netjes houden
        if rel == "index.html":
            url = ROOT_URL + "/"
        else:
            url = f"{ROOT_URL}/{rel}"

        urls.append(url)

    urls = sorted(set(urls))

    today = datetime.date.today().isoformat()

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url in urls:
        xml.append("  <url>")
        xml.append(f"    <loc>{url}</loc>")
        xml.append(f"    <lastmod>{today}</lastmod>")
        xml.append("  </url>")

    xml.append("</urlset>")

    return "\n".join(xml)


def main():
    root = Path(".").resolve()
    sitemap = generate_sitemap(root)

    output = root / "sitemap.xml"
    output.write_text(sitemap, encoding="utf-8")

    print(f"[OK] sitemap.xml gegenereerd ({len(sitemap)} regels)")


if __name__ == "__main__":
    main()