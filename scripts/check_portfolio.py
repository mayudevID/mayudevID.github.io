#!/usr/bin/env python3
"""Offline, dependency-free checks against the built bilingual Jekyll site.

Usage:
    bundle exec jekyll build
    python3 scripts/check_portfolio.py --site _site

External application/store links are only checked for preservation, NOT probed
over the network: some storefronts may block automated clients or change URLs.
"""
from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
import sys
import xml.etree.ElementTree as ET

ORIGIN = "https://mydv.my.id"
LANGUAGES = {"en": "/", "id": "/id/"}
EXPECTED_STORE_URL = "https://apps.apple.com/us/app/holy-smart/id6789028854"
EXPECTED_SECTIONS = ("projects", "experience", "skills", "contact")
EXPECTED_PROJECTS = ("Holy Smart", "Holy World", "Ar-Rauda", "Bloom", "Cling!", "KBBI Daring")


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.images = []
        self.metadata = []
        self.alternates = {}
        self.canonicals = []
        self.html_lang = None
        self.h1_count = 0
        self.lang_switches = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "html":
            self.html_lang = attrs.get("lang")
        if tag == "h1":
            self.h1_count += 1
        if tag == "img":
            self.images.append(attrs)
            self.links.append(("image", attrs.get("src", "")))
        if tag == "script" and attrs.get("src"):
            self.links.append(("script", attrs["src"]))
        if tag == "a" and attrs.get("href"):
            self.links.append(("link", attrs["href"]))
            if attrs.get("hreflang") in LANGUAGES:
                self.lang_switches.append((attrs["hreflang"], attrs["href"]))
        if tag == "link":
            rel = set((attrs.get("rel") or "").split())
            if attrs.get("href") and ("stylesheet" in rel or "icon" in rel):
                self.links.append(("asset", attrs["href"]))
            if "canonical" in rel:
                self.canonicals.append(attrs.get("href"))
            if "alternate" in rel and attrs.get("hreflang"):
                self.alternates[attrs["hreflang"]] = attrs.get("href")
        if tag == "meta":
            self.metadata.append(attrs)


def check_page(site: Path, lang: str, page_path: str) -> list[str]:
    errors = []
    page = site / page_path.lstrip("/") / "index.html"
    if not page.is_file():
        return [f"{lang}: expected generated file not found: {page}"]
    html = page.read_text(encoding="utf-8")
    parser = Document()
    parser.feed(html)
    prefix = f"{lang} ({page_path})"

    if "{%" in html or "{{" in html:
        errors.append(f"{prefix}: unrendered Liquid template tokens found")
    if parser.html_lang != lang:
        errors.append(f"{prefix}: html lang expected {lang!r}, got {parser.html_lang!r}")
    if parser.h1_count != 1:
        errors.append(f"{prefix}: expected exactly one H1, got {parser.h1_count}")
    repeated = [value for value, count in Counter(parser.ids).items() if count > 1]
    if repeated:
        errors.append(f"{prefix}: duplicate IDs: {repeated}")
    if parser.canonicals != [ORIGIN + page_path]:
        errors.append(f"{prefix}: incorrect canonical: {parser.canonicals}")

    for alt_lang, href in LANGUAGES.items():
        expected_url = ORIGIN + href
        if parser.alternates.get(alt_lang) != expected_url:
            errors.append(f"{prefix}: hreflang {alt_lang} missing/incorrect")
        if (alt_lang, href) not in parser.lang_switches:
            errors.append(f"{prefix}: language switch missing /{alt_lang} URL")
    if parser.alternates.get("x-default") != ORIGIN + "/":
        errors.append(f"{prefix}: incorrect x-default hreflang")
    current = [v for v in parser.metadata if v.get("property") == "og:url"]
    if [m.get("content") for m in current] != [ORIGIN + page_path]:
        errors.append(f"{prefix}: og:url does not match canonical")
    if not any(m.get("name") == "description" and m.get("content") for m in parser.metadata):
        errors.append(f"{prefix}: missing meta description")

    for section in EXPECTED_SECTIONS:
        if f"{section}-{lang}" not in parser.ids:
            errors.append(f"{prefix}: section anchor missing: {section}-{lang}")
    if html.count(EXPECTED_STORE_URL) != 1:
        errors.append(f"{prefix}: Holy Smart App Store URL was modified or duplicated")
    for name in EXPECTED_PROJECTS:
        if name not in html:
            errors.append(f"{prefix}: project missing: {name}")
    if not parser.images:
        errors.append(f"{prefix}: no images found")
    for attrs in parser.images:
        if not attrs.get("alt"):
            errors.append(f"{prefix}: image has no descriptive alt: {attrs.get('src')}")
        if attrs.get("src", "").startswith("/assets/") and attrs.get("loading") != "lazy":
            # Featured-project and screenshot content is below the primary hero.
            errors.append(f"{prefix}: screenshot should be lazy-loaded: {attrs.get('src')}")

    local_ids = set(parser.ids)
    for kind, link in parser.links:
        parsed = urlparse(urljoin(ORIGIN + page_path, link))
        if parsed.scheme not in ("http", "https") or parsed.netloc != urlparse(ORIGIN).netloc:
            continue
        target = unquote(parsed.path)
        target_file = site / target.lstrip("/")
        if not target or target.endswith("/"):
            target_file = target_file / "index.html"
        if not target_file.is_file():
            errors.append(f"{prefix}: broken local {kind}: {link} -> {target_file}")
        if kind == "link" and parsed.fragment and parsed.path == page_path:
            if unquote(parsed.fragment) not in local_ids:
                errors.append(f"{prefix}: broken in-page anchor: {link}")
    return errors


def check_source() -> list[str]:
    errors = []
    for relative in ("portfolio/portfolio-en.md", "portfolio/portfolio.md"):
        source = Path(relative)
        if not source.is_file():
            errors.append(f"missing source: {source}")
            continue
        content = source.read_text(encoding="utf-8")
        if content.count("<!-- PORTFOLIO:SECTION -->") != 12:
            errors.append(f"{relative}: expected 12 Jekyll section markers")
        if EXPECTED_STORE_URL not in content:
            errors.append(f"{relative}: canonical Holy Smart store link unexpectedly changed")
        if 'src="./assets/' in content:
            errors.append(f"{relative}: relative assets break on /id/; use /assets/")
    return errors


def check_sitemap(site: Path) -> list[str]:
    path = site / "sitemap.xml"
    if not path.is_file():
        return ["missing generated sitemap.xml"]
    try:
        document = ET.parse(path)
        locations = {
            el.text for el in document.findall(".//{*}loc")
            if el.text is not None
        }
    except ET.ParseError as exc:
        return [f"sitemap XML cannot be parsed: {exc}"]
    return [
        f"sitemap is missing {ORIGIN + page}"
        for page in LANGUAGES.values()
        if ORIGIN + page not in locations
    ]


def main() -> int:
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--site", type=Path, default=Path("_site"))
    options = args.parse_args()
    errors = check_source()
    errors.extend(check_sitemap(options.site))
    for lang, path in LANGUAGES.items():
        errors.extend(check_page(options.site, lang, path))
    if errors:
        print("Portfolio quality checks failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("OK — EN/ID Jekyll pages, SEO, images, sections, CV and local links validated.")
    print("Note: external store URLs were preserved, not requested over the network.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
