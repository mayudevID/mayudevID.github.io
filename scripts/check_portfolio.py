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
import json
import re
import struct
from collections import Counter
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
import sys
import xml.etree.ElementTree as ET

ORIGIN = "https://mydv.my.id"
LANGUAGES = {"en": "/en/", "id": "/id/"}
SEARCH_CONSOLE_TOKEN = "vvVXmwxXpFyMHO-Yhf4qhy7qRgbTwD_pnTpD8XuyDLY"
PERSON_ID = ORIGIN + "/#person"
WEBSITE_ID = ORIGIN + "/#website"
SOCIAL_IMAGE = "/assets/seo/og-cover.png"
SOCIAL_IMAGE_ALT = {
    "en": "MayudevID portfolio for Maulana Yusuf, Flutter and mobile developer",
    "id": "Portofolio MayudevID oleh Maulana Yusuf, Flutter dan mobile developer",
}
CV_URL = ORIGIN + "/portfolio/cv_maulana_yusuf.pdf"
EXPECTED_STORE_URL = "https://apps.apple.com/us/app/holy-smart/id6789028854"
GOT_STORE_URLS = (
    "https://apps.apple.com/us/app/got-agency/id6805425415",
    "https://play.google.com/store/apps/details?id=com.hwgroup.got",
)
DTG_STORE_URLS = (
    "https://apps.apple.com/id/app/dtg-soms/id6832190198",
    "https://play.google.com/store/apps/details?id=com.dtg.travelpath&hl=id",
)
EXPECTED_SECTIONS = ("projects", "experience", "skills", "contact")
EXPECTED_PROJECTS = ("Holy Smart", "Holy World", "DTG SOMS", "Ar-Rauda", "GOT Agency", "KTADBRNR", "EMCare", "Bloom", "Cling!", "KBBI Daring")
EXPECTED_FEATURED_ORDER = (
    "#case-study-holy-smart-",
    "#case-study-holy-world-",
    "#case-study-dtg-soms-",
    "#case-study-ar-rauda-",
    "#case-study-got-agency-",
    "#case-study-ktadbrnr-",
    "#case-study-emcare-",
)
EXPECTED_FEATURED_IMAGES = (
    [f"/assets/projects/holy_smart/{index}.png" for index in (1, 2, 3)],
    [f"/assets/projects/holy_world/{index}.webp" for index in (2, 3, 4)],
    [f"/assets/projects/dtg_soms/ios_{index}.jpg" for index in (1, 2, 3)],
    [f"/assets/projects/ar_rauda/{index}.png" for index in (1, 2, 3)],
)
PROJECTS = (
    ("holy-smart", "Holy Smart"), ("holy-world", "Holy World"),
    ("dtg-soms", "DTG SOMS"), ("ar-rauda", "Ar-Rauda"),
    ("got-agency", "GOT Agency"), ("ktadbrnr", "KTADBRNR"),
    ("emcare", "EMCare"), ("bloom", "Bloom"), ("cling", "Cling!"),
    ("kbbi-daring", "KBBI Daring"),
)
PROJECT_SOCIAL_IMAGES = {
    "holy-smart": "/assets/projects/holy_smart/1.png",
    "holy-world": "/assets/projects/holy_world/2.webp",
    "dtg-soms": "/assets/projects/dtg_soms/ios_1.jpg",
    "ar-rauda": "/assets/projects/ar_rauda/1.png",
    "got-agency": "/assets/projects/got_agency/1.png",
    "ktadbrnr": "/assets/projects/ktadbrnr/1.jpg",
    "emcare": "/assets/projects/emcare/1.png",
    "bloom": "/assets/projects/bloom/cover.png",
    "cling": "/assets/projects/cling/cover.jpg",
    "kbbi-daring": "/assets/projects/kbbi_daring/cover.png",
}
PROJECT_LINKS = {
    "holy-smart": ("https://play.google.com/store/apps/details?id=com.hwgroup.holysmart", "https://apps.apple.com/us/app/holy-smart/id6789028854"),
    "holy-world": ("https://play.google.com/store/apps/details?id=com.holywingsindonesia.holywingsattendance", "https://apps.apple.com/id/app/holyworld-mobile/id1553614359"),
    "dtg-soms": DTG_STORE_URLS,
    "ar-rauda": ("https://play.google.com/store/apps/details?id=com.work.arraudhah&hl=en", "https://apps.apple.com/id/app/ar-rauda/id6762336087"),
    "got-agency": GOT_STORE_URLS,
    "ktadbrnr": ("https://play.google.com/store/apps/details?id=com.brnr.app&hl=id",),
    "emcare": ("https://play.google.com/store/apps/details?id=id.emc", "https://apps.apple.com/id/app/emcare-by-emc-healthcare/id1660724645", "https://suitmedia.com/work/emc-mobile"),
    "bloom": ("https://github.com/mayudevID/bloom",),
    "cling": ("https://github.com/mayudevID/cling",),
    "kbbi-daring": ("https://github.com/mayudevID/kbbi_daring_app",),
}


def check_store_badges(parser, urls, prefix):
    expected = {}
    for url in urls:
        if url.startswith("https://play.google.com/store/apps/details"):
            expected[url] = "/assets/platform/play_store/google_play_badge.png"
        elif url.startswith("https://apps.apple.com/"):
            expected[url] = "/assets/platform/app_store/app_store.svg"
    actual = [(url, src) for url, src, alt in parser.store_badges]
    errors = []
    if Counter(actual) != Counter(expected.items()) or any(not alt for url, src, alt in parser.store_badges):
        errors.append(f"{prefix}: incorrect, missing or inaccessible store badges")
    return errors


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.images = []
        self.metadata = []
        self.titles = []
        self.json_ld = []
        self._title_parts = []
        self._json_ld_parts = []
        self._in_title = False
        self._in_json_ld = False
        self.alternates = {}
        self.alternate_declarations = []
        self.canonicals = []
        self.html_lang = None
        self.h1_count = 0
        self.h1_text = []
        self._in_h1 = False
        self._h1_parts = []
        self.heading_levels = []
        self.landmarks = Counter()
        self.lang_switches = []
        self.featured_projects = []
        self.featured_images = []
        self.in_featured_media = False
        self.store_badges = []
        self.active_store_badge = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "html":
            self.html_lang = attrs.get("lang")
        if tag == "h1":
            self.h1_count += 1
            self._in_h1 = True
            self._h1_parts = []
        if tag in {"header", "main", "footer", "nav"}:
            self.landmarks[tag] += 1
        if len(tag) == 2 and tag[0] == "h" and tag[1].isdigit():
            self.heading_levels.append(int(tag[1]))
        if tag == "title":
            self._in_title = True
            self._title_parts = []
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._json_ld_parts = []
        if tag == "img":
            self.images.append(attrs)
            self.links.append(("image", attrs.get("src", "")))
            if self.in_featured_media:
                self.featured_images[-1].append(attrs.get("src", ""))
            if self.active_store_badge:
                self.store_badges.append((self.active_store_badge, attrs.get("src"), attrs.get("alt")))
        if tag == "script" and attrs.get("src"):
            self.links.append(("script", attrs["src"]))
        if tag == "a" and attrs.get("href"):
            self.links.append(("link", attrs["href"]))
            if "store-badge" in (attrs.get("class") or "").split():
                self.active_store_badge = attrs["href"]
            if "featured-card-media" in (attrs.get("class") or "").split():
                self.featured_projects.append(attrs["href"])
                self.featured_images.append([])
                self.in_featured_media = True
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
                self.alternate_declarations.append((attrs["hreflang"], attrs.get("href")))
        if tag == "meta":
            self.metadata.append(attrs)

    def handle_endtag(self, tag):
        if tag == "a":
            self.in_featured_media = False
            self.active_store_badge = None
        if tag == "title" and self._in_title:
            self.titles.append("".join(self._title_parts).strip())
            self._in_title = False
        if tag == "h1" and self._in_h1:
            self.h1_text.append("".join(self._h1_parts).strip())
            self._in_h1 = False
        if tag == "script" and self._in_json_ld:
            self.json_ld.append("".join(self._json_ld_parts).strip())
            self._in_json_ld = False

    def handle_data(self, data):
        if self._in_title:
            self._title_parts.append(data)
        if self._in_h1:
            self._h1_parts.append(data)
        if self._in_json_ld:
            self._json_ld_parts.append(data)


def meta_values(parser: Document, *, name=None, property=None) -> list[str]:
    key, value = ("name", name) if name is not None else ("property", property)
    return [meta.get("content", "") for meta in parser.metadata if meta.get(key) == value]


def check_seo_metadata(parser: Document, site: Path, lang: str, page_path: str, prefix: str) -> list[str]:
    errors = []
    canonical = ORIGIN + page_path
    expected_alternates = {lang: ORIGIN + route for lang, route in LANGUAGES.items()} | {"x-default": ORIGIN + LANGUAGES["en"]}
    if len(parser.titles) != 1 or not parser.titles[0]:
        errors.append(f"{prefix}: expected exactly one non-empty title")
    elif not parser.titles[0].startswith("Maulana Yusuf | ") or "Flutter" not in parser.titles[0] or "Developer" not in parser.titles[0]:
        errors.append(f"{prefix}: title must identify Maulana Yusuf and the Flutter developer focus")
    elif lang == "id" and "Indonesia" not in parser.titles[0]:
        errors.append(f"{prefix}: Indonesian title must identify the Indonesia audience")
    if parser.html_lang != lang:
        errors.append(f"{prefix}: HTML language expected {lang!r}, got {parser.html_lang!r}")
    descriptions = meta_values(parser, name="description")
    if len(descriptions) != 1 or not descriptions[0].strip():
        errors.append(f"{prefix}: expected exactly one non-empty meta description")
    elif lang == "en" and "Flutter" not in descriptions[0]:
        errors.append(f"{prefix}: English description omits the portfolio focus")
    elif lang == "id" and "Flutter" not in descriptions[0]:
        errors.append(f"{prefix}: Indonesian description omits the portfolio focus")
    if len(parser.canonicals) != 1 or parser.canonicals[0] != canonical:
        errors.append(f"{prefix}: expected exactly one canonical URL {canonical}, got {parser.canonicals}")

    # Keep all declarations so duplicate hreflang values cannot silently pass.
    alternate_pairs = parser.alternate_declarations
    if len(alternate_pairs) != 3 or dict(alternate_pairs) != expected_alternates:
        errors.append(f"{prefix}: hreflang declarations are missing, duplicated, or incorrect: {alternate_pairs}")
    for alt_lang, href in expected_alternates.items():
        if alt_lang in LANGUAGES and (alt_lang, LANGUAGES[alt_lang]) not in parser.lang_switches:
            errors.append(f"{prefix}: language switch missing {href}")

    for key, expected in (("og:url", canonical), ("og:title", parser.titles[0] if parser.titles else ""),
                          ("og:description", descriptions[0] if descriptions else "")):
        values = meta_values(parser, property=key)
        if len(values) != 1 or values[0] != expected:
            errors.append(f"{prefix}: {key} is missing, duplicated, or inconsistent")
    for key, expected in (("twitter:title", parser.titles[0] if parser.titles else ""),
                          ("twitter:description", descriptions[0] if descriptions else "")):
        values = meta_values(parser, name=key)
        if len(values) != 1 or values[0] != expected:
            errors.append(f"{prefix}: {key} is missing, duplicated, or inconsistent")
    if meta_values(parser, property="og:locale") != [{"en": "en_US", "id": "id_ID"}[lang]]:
        errors.append(f"{prefix}: incorrect Open Graph locale")
    if meta_values(parser, property="og:locale:alternate") != [{"en": "id_ID", "id": "en_US"}[lang]]:
        errors.append(f"{prefix}: incorrect alternate Open Graph locale")
    if meta_values(parser, property="og:site_name") != ["MayudevID"]:
        errors.append(f"{prefix}: incorrect Open Graph site name")
    if meta_values(parser, name="twitter:card") != ["summary_large_image"]:
        errors.append(f"{prefix}: incorrect Twitter card type")
    for key in ("og:image", "twitter:image"):
        values = meta_values(parser, property=key) if key.startswith("og:") else meta_values(parser, name=key)
        if values != [ORIGIN + SOCIAL_IMAGE]:
            errors.append(f"{prefix}: {key} must reference the local portfolio social image")
    for key in ("og:image:alt",):
        if meta_values(parser, property=key) != [SOCIAL_IMAGE_ALT[lang]]:
            errors.append(f"{prefix}: incorrect localized {key}")
    if meta_values(parser, name="twitter:image:alt") != [SOCIAL_IMAGE_ALT[lang]]:
        errors.append(f"{prefix}: incorrect localized Twitter image alt")
    if meta_values(parser, property="og:image:width") != ["1200"] or meta_values(parser, property="og:image:height") != ["630"]:
        errors.append(f"{prefix}: social image dimensions are missing or incorrect")
    if meta_values(parser, property="og:image:type") != ["image/png"]:
        errors.append(f"{prefix}: social image MIME type is missing or incorrect")
    if meta_values(parser, name="robots") != ["index, follow"]:
        errors.append(f"{prefix}: robots directive is missing, duplicated, or non-indexable")
    if any("noindex" in value.lower() for meta in parser.metadata for value in [meta.get("content", "")]
           if meta.get("name", "").lower() in {"robots", "googlebot", "bingbot"}):
        errors.append(f"{prefix}: unintended noindex directive found")
    if meta_values(parser, name="author") != ["Maulana Yusuf"]:
        errors.append(f"{prefix}: author metadata is missing or incorrect")
    if meta_values(parser, name="google-site-verification") != [SEARCH_CONSOLE_TOKEN]:
        errors.append(f"{prefix}: Google Search Console verification metadata changed")
    if meta_values(parser, name="keywords"):
        errors.append(f"{prefix}: obsolete meta keywords are present")

    image = site / SOCIAL_IMAGE.lstrip("/")
    if not image.is_file():
        errors.append(f"{prefix}: social image file not found: {image}")
    else:
        with image.open("rb") as stream:
            header = stream.read(24)
        if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
            errors.append(f"{prefix}: social image is not a valid PNG")
        else:
            width, height = struct.unpack(">II", header[16:24])
            if (width, height) != (1200, 630):
                errors.append(f"{prefix}: social image dimensions are {width}x{height}, expected 1200x630")

    if len(parser.json_ld) != 1:
        errors.append(f"{prefix}: expected exactly one JSON-LD script")
    else:
        try:
            document = json.loads(parser.json_ld[0])
            graph = document.get("@graph", [])
            types = [entity.get("@type") for entity in graph]
            if document.get("@context") != "https://schema.org" or sorted(types) != ["Person", "ProfilePage", "WebSite"]:
                errors.append(f"{prefix}: JSON-LD context or entity types are incorrect: {types}")
            entities = {entity.get("@type"): entity for entity in graph}
            person = entities.get("Person", {})
            website = entities.get("WebSite", {})
            profile = entities.get("ProfilePage", {})
            expected_profile = canonical + "#profilepage"
            if person.get("@id") != PERSON_ID or person.get("name") != "Maulana Yusuf" or person.get("alternateName") != "MayudevID":
                errors.append(f"{prefix}: Person identity is incorrect")
            if person.get("jobTitle") != "Flutter & Mobile Developer" or not person.get("knowsAbout"):
                errors.append(f"{prefix}: Person expertise metadata is missing or inconsistent")
            if person.get("alumniOf", {}).get("name") != "Universitas Pembangunan Nasional Veteran Jakarta":
                errors.append(f"{prefix}: Person education is missing or inconsistent with portfolio content")
            if website.get("@id") != WEBSITE_ID or website.get("url") != ORIGIN + "/" or website.get("publisher", {}).get("@id") != PERSON_ID:
                errors.append(f"{prefix}: WebSite identity or Person relationship is incorrect")
            if profile.get("@id") != expected_profile or profile.get("url") != canonical:
                errors.append(f"{prefix}: ProfilePage identifier or URL is incorrect")
            if profile.get("mainEntity", {}).get("@id") != PERSON_ID or profile.get("isPartOf", {}).get("@id") != WEBSITE_ID:
                errors.append(f"{prefix}: ProfilePage relationships are incorrect")
            if profile.get("inLanguage") != lang or profile.get("description") != (descriptions[0] if descriptions else None):
                errors.append(f"{prefix}: ProfilePage language or localized description is incorrect")
        except (json.JSONDecodeError, AttributeError, TypeError) as exc:
            errors.append(f"{prefix}: JSON-LD is invalid: {exc}")
    return errors


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
    errors.extend(check_seo_metadata(parser, site, lang, page_path, prefix))
    if parser.h1_count != 1:
        errors.append(f"{prefix}: expected exactly one H1, got {parser.h1_count}")
    for landmark in ("header", "main", "footer"):
        if parser.landmarks[landmark] != 1:
            errors.append(f"{prefix}: expected one semantic {landmark} landmark, got {parser.landmarks[landmark]}")
    if parser.landmarks["nav"] < 2:
        errors.append(f"{prefix}: expected primary and language navigation landmarks")
    if parser.heading_levels and parser.heading_levels[0] != 1:
        errors.append(f"{prefix}: the first heading must be the page H1")
    if any(current > previous + 1 for previous, current in zip(parser.heading_levels, parser.heading_levels[1:])):
        errors.append(f"{prefix}: heading hierarchy skips a level")
    repeated = [value for value, count in Counter(parser.ids).items() if count > 1]
    if repeated:
        errors.append(f"{prefix}: duplicate IDs: {repeated}")
    for section in EXPECTED_SECTIONS:
        if f"{section}-{lang}" not in parser.ids:
            errors.append(f"{prefix}: section anchor missing: {section}-{lang}")
    if html.count(EXPECTED_STORE_URL) != 1:
        errors.append(f"{prefix}: Holy Smart App Store URL was modified or duplicated")
    for name in EXPECTED_PROJECTS:
        if name not in html:
            errors.append(f"{prefix}: project missing: {name}")
    expected_order = [anchor + lang for anchor in EXPECTED_FEATURED_ORDER]
    if parser.featured_projects != expected_order:
        errors.append(f"{prefix}: featured projects are out of order: {parser.featured_projects}")
    shots = json.loads(Path("_data/ktadbrnr_screenshots.json").read_text(encoding="utf-8"))
    screenshot_sources = [shot["local_path"] for shot in shots]
    got_shots = json.loads(Path("_data/got_agency_screenshots.json").read_text(encoding="utf-8"))
    got_sources = [shot["local_path"] for shot in got_shots]
    if len(got_sources) != 7 or len(set(got_sources)) != 7:
        errors.append(f"{prefix}: expected seven unique GOT Agency screenshots")
    for index, src in enumerate(got_sources):
        if not (site / src.lstrip("/")).is_file():
            errors.append(f"{prefix}: GOT Agency local screenshot missing: {src}")
        matches = [img for img in parser.images if img.get("src") == src]
        if len(matches) != (2 if index < 3 else 0):
            errors.append(f"{prefix}: GOT Agency screenshot missing or duplicated: {src}")
    emcare_shots = json.loads(Path("_data/emcare_screenshots.json").read_text(encoding="utf-8"))
    emcare_sources = [shot["local_path"] for shot in emcare_shots]
    if len(emcare_sources) != 5 or len(set(emcare_sources)) != 5:
        errors.append(f"{prefix}: expected five unique EMCare screenshots")
    for index, (shot, src) in enumerate(zip(emcare_shots, emcare_sources)):
        if not shot["url"].startswith("https://play-lh.googleusercontent.com/") or not shot["url"].endswith("=s0"):
            errors.append(f"{prefix}: EMCare screenshot must reference the original-size Google Play image")
        if not (site / src.lstrip("/")).is_file():
            errors.append(f"{prefix}: EMCare local screenshot missing: {src}")
        matches = [img for img in parser.images if img.get("src") == src]
        if len(matches) != (2 if index < 3 else 0) or any(img.get("loading") != "lazy" for img in matches):
            errors.append(f"{prefix}: EMCare screenshot missing, duplicated, or not lazy-loaded: {src}")
    for url in (
        "https://play.google.com/store/apps/details?id=id.emc",
        "https://apps.apple.com/id/app/emcare-by-emc-healthcare/id1660724645",
        "https://suitmedia.com/work/emc-mobile",
    ):
        if sum(kind == "link" and link == url for kind, link in parser.links) != 1:
            errors.append(f"{prefix}: EMCare reference missing or duplicated: {url}")
    if f"case-study-emcare-{lang}" not in parser.ids:
        errors.append(f"{prefix}: EMCare case study anchor missing")
    expected_featured_images = [*EXPECTED_FEATURED_IMAGES, got_sources[:3], screenshot_sources[:3], emcare_sources[:3]]
    if parser.featured_images != expected_featured_images or any(len(group) != 3 or len(set(group)) != 3 for group in parser.featured_images):
        errors.append(f"{prefix}: each featured project must have three unique mobile screenshots in order: {parser.featured_images}")
    if len(screenshot_sources) != 8 or len(set(screenshot_sources)) != 8:
        errors.append(f"{prefix}: expected eight unique KTADBRNR screenshots")
    for index, src in enumerate(screenshot_sources):
        if not (site / src.lstrip("/")).is_file():
            errors.append(f"{prefix}: KTADBRNR local screenshot missing: {src}")
        expected_count = 2 if index < 3 else 0
        if sum(img.get("src") == src for img in parser.images) != expected_count:
            errors.append(f"{prefix}: KTADBRNR screenshot missing or duplicated: {src}")
    if sum(link == "https://play.google.com/store/apps/details?id=com.brnr.app&hl=id"
           for kind, link in parser.links if kind == "link") != 1:
        errors.append(f"{prefix}: KTADBRNR historical source link missing or duplicated")
    for asset in ("assets/projects/dtg_soms/web_screenshot.png", "assets/projects/holy_smart/web_screenshot.png"):
        if "/" + asset in html or (site / asset).exists():
            errors.append(f"{prefix}: unreviewed admin screenshot must not be published: {asset}")
    if html.count('class="project-preview"') != 7 or 'class="project-detail-content"' in html or 'class="project-section case-study-context"' in html:
        errors.append(f"{prefix}: homepage must contain seven compact project previews, not full case studies")
    errors.extend(check_store_badges(parser, [url for slug, urls in PROJECT_LINKS.items() if slug != "ktadbrnr" for url in urls], prefix))
    for url in DTG_STORE_URLS:
        if sum(link == url for _kind, link in parser.links) != 1:
            errors.append(f"{prefix}: DTG SOMS store link missing or duplicated: {url}")
    for url in GOT_STORE_URLS:
        if sum(kind == "link" and link == url for kind, link in parser.links) != 1:
            errors.append(f"{prefix}: GOT Agency store link missing or duplicated: {url}")
    if f"case-study-got-agency-{lang}" not in parser.ids:
        errors.append(f"{prefix}: GOT Agency case study anchor missing")
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
        if kind == "link" and target in legacy_redirects():
            errors.append(f"{prefix}: internal link still targets legacy route: {link}")
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
    for relative in ("pages/en/portfolio.md", "pages/id/portfolio.md"):
        source = Path(relative)
        if not source.is_file():
            errors.append(f"missing source: {source}")
            continue
        content = source.read_text(encoding="utf-8")
        if content.count("<!-- PORTFOLIO:SECTION -->") != 16:
            errors.append(f"{relative}: expected 16 Jekyll section markers")
        if 'src="./assets/' in content:
            errors.append(f"{relative}: relative assets break on /id/; use /assets/")
    return errors


def expected_case_study_screenshots(slug: str) -> list[str]:
    numbered = {
        "holy-smart": ("holy_smart", "", ".png", 4),
        "holy-world": ("holy_world", "", ".webp", 5),
        "dtg-soms": ("dtg_soms", "ios_", ".jpg", 4),
        "ar-rauda": ("ar_rauda", "", ".png", 5),
    }
    if slug in numbered:
        directory, prefix, extension, count = numbered[slug]
        return [f"/assets/projects/{directory}/{prefix}{i}{extension}" for i in range(1, count + 1)]
    if slug in {"got-agency", "ktadbrnr", "emcare"}:
        catalog = Path("_data") / f"{slug.replace('-', '_')}_screenshots.json"
        return [shot["local_path"] for shot in json.loads(catalog.read_text(encoding="utf-8"))]
    return [PROJECT_SOCIAL_IMAGES[slug]]


def check_project_pages(site: Path) -> list[str]:
    errors = []
    project_descriptions = []
    home_parsers = {}
    for lang, home_path in LANGUAGES.items():
        home_file = site / home_path.lstrip("/") / "index.html"
        if home_file.is_file():
            home = Document()
            home.feed(home_file.read_text(encoding="utf-8"))
            home_parsers[lang] = home

    for slug, name in PROJECTS:
        localized_routes = {
            "en": f"/en/projects/{slug}/",
            "id": f"/id/projects/{slug}/",
        }
        for lang, page_path in localized_routes.items():
            page_file = site / page_path.lstrip("/") / "index.html"
            prefix = f"project {name} ({lang}, {page_path})"
            if not page_file.is_file():
                errors.append(f"{prefix}: generated page is missing")
                continue
            source = page_file.read_text(encoding="utf-8")
            parser = Document()
            parser.feed(source)
            canonical = ORIGIN + page_path
            expected_alternates = {
                "en": ORIGIN + localized_routes["en"],
                "id": ORIGIN + localized_routes["id"],
                "x-default": ORIGIN + localized_routes["en"],
            }

            if len(parser.titles) != 1 or not parser.titles[0] or name not in parser.titles[0]:
                errors.append(f"{prefix}: expected one localized project title containing its name")
            if parser.html_lang != lang:
                errors.append(f"{prefix}: HTML language expected {lang!r}, got {parser.html_lang!r}")
            descriptions = meta_values(parser, name="description")
            if len(descriptions) != 1 or not descriptions[0].strip():
                errors.append(f"{prefix}: expected one non-empty project description")
            elif descriptions[0] in project_descriptions:
                errors.append(f"{prefix}: project meta description is duplicated")
            else:
                project_descriptions.append(descriptions[0])
            if len(parser.canonicals) != 1 or parser.canonicals[0] != canonical:
                errors.append(f"{prefix}: expected self-canonical {canonical}")
            if len(parser.alternate_declarations) != 3 or dict(parser.alternate_declarations) != expected_alternates:
                errors.append(f"{prefix}: project hreflang declarations are missing, duplicated, or incorrect")
            if parser.lang_switches.count(("en", localized_routes["en"])) != 1 or parser.lang_switches.count(("id", localized_routes["id"])) != 1:
                errors.append(f"{prefix}: language switch does not preserve project context")
            for key, expected in (("og:url", canonical), ("og:title", parser.titles[0] if parser.titles else ""),
                                  ("og:description", descriptions[0] if descriptions else "")):
                values = meta_values(parser, property=key)
                if values != [expected]:
                    errors.append(f"{prefix}: {key} is missing, duplicated, or inconsistent")
            for key, expected in (("twitter:title", parser.titles[0] if parser.titles else ""),
                                  ("twitter:description", descriptions[0] if descriptions else "")):
                if meta_values(parser, name=key) != [expected]:
                    errors.append(f"{prefix}: {key} is missing, duplicated, or inconsistent")
            expected_image = ORIGIN + PROJECT_SOCIAL_IMAGES.get(slug, SOCIAL_IMAGE)
            images = meta_values(parser, property="og:image")
            if images != [expected_image] or meta_values(parser, name="twitter:image") != images:
                errors.append(f"{prefix}: social image is missing or incorrect")
            image_file = site / PROJECT_SOCIAL_IMAGES.get(slug, SOCIAL_IMAGE).lstrip("/")
            if not image_file.is_file():
                errors.append(f"{prefix}: social image asset is missing: {image_file}")
            extension = image_file.suffix.lower()
            expected_type = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(extension)
            if expected_type and meta_values(parser, property="og:image:type") != [expected_type]:
                errors.append(f"{prefix}: social image MIME type is incorrect")
            if slug in PROJECT_SOCIAL_IMAGES and (meta_values(parser, property="og:image:width") or meta_values(parser, property="og:image:height")):
                errors.append(f"{prefix}: dimensions must be omitted for unverified project image dimensions")
            image_alt = meta_values(parser, property="og:image:alt")
            if len(image_alt) != 1 or name.lower() not in image_alt[0].lower():
                errors.append(f"{prefix}: social image alt must identify the project")
            if meta_values(parser, name="robots") != ["index, follow"]:
                errors.append(f"{prefix}: project page must remain indexable")
            if parser.h1_count != 1 or parser.h1_text != [name]:
                errors.append(f"{prefix}: expected one meaningful H1 matching {name!r}")
            if 'class="breadcrumbs"' not in source or 'aria-current="page"' not in source:
                errors.append(f"{prefix}: visible breadcrumb or current-page marker is missing")
            breadcrumb = re.search(r'<nav class="breadcrumbs".*?</nav>', source, flags=re.DOTALL)
            if not breadcrumb or name not in re.sub(r"<[^>]+>", " ", breadcrumb.group(0)):
                errors.append(f"{prefix}: visible breadcrumb does not name the current project")
            expected_shots = expected_case_study_screenshots(slug)
            hero = re.search(r'<header class="project-hero">.*?</header>', source, flags=re.DOTALL)
            gallery = re.search(r'<div class="project-gallery project-header-gallery"[^>]*>.*?</div>', hero.group(0), flags=re.DOTALL) if hero else None
            if not gallery:
                errors.append(f"{prefix}: missing case study header screenshot gallery")
            else:
                gallery_parser = Document()
                gallery_parser.feed(gallery.group(0))
                if [img.get("src") for img in gallery_parser.images] != expected_shots:
                    errors.append(f"{prefix}: header gallery must contain all approved screenshots in order")
                if 'role="region"' not in gallery.group(0) or 'aria-label=' not in gallery.group(0) or (len(expected_shots) > 1 and 'tabindex="0"' not in gallery.group(0)):
                    errors.append(f"{prefix}: screenshot gallery must be labeled and keyboard-scrollable when needed")
            if any(sum(img.get("src") == shot for img in parser.images) != 1 for shot in expected_shots):
                errors.append(f"{prefix}: each case study screenshot must appear exactly once")
            if f"project-screenshots-{slug}" in parser.ids or f"related-title-{slug}" in parser.ids:
                errors.append(f"{prefix}: removed screenshot or related-project section must not be rendered")
            if "Google-site-verification" in source:
                errors.append(f"{prefix}: verification meta tag casing changed unexpectedly")
            if meta_values(parser, name="google-site-verification") != [SEARCH_CONSOLE_TOKEN]:
                errors.append(f"{prefix}: Google Search Console verification metadata is missing")
            if "{%" in source or "{{" in source:
                errors.append(f"{prefix}: unrendered Liquid tokens found")

            if len(parser.json_ld) != 1:
                errors.append(f"{prefix}: expected exactly one JSON-LD block")
                graph = []
            else:
                try:
                    json_document = json.loads(parser.json_ld[0])
                    graph = json_document.get("@graph", [])
                except (json.JSONDecodeError, AttributeError, TypeError) as exc:
                    errors.append(f"{prefix}: JSON-LD is invalid: {exc}")
                    graph = []
            types = sorted(entity.get("@type") for entity in graph)
            expected_types = sorted(("Person", "WebSite", "WebPage", "CreativeWork", "BreadcrumbList"))
            if types != expected_types:
                errors.append(f"{prefix}: project JSON-LD entities are incorrect: {types}")
            entities = {entity.get("@type"): entity for entity in graph}
            person = entities.get("Person", {})
            website = entities.get("WebSite", {})
            webpage = entities.get("WebPage", {})
            work = entities.get("CreativeWork", {})
            breadcrumb = entities.get("BreadcrumbList", {})
            if person.get("@id") != PERSON_ID or website.get("@id") != WEBSITE_ID:
                errors.append(f"{prefix}: shared Person or WebSite identifier changed")
            if website.get("publisher", {}).get("@id") != PERSON_ID:
                errors.append(f"{prefix}: WebSite publisher relationship is incorrect")
            if webpage.get("url") != canonical or webpage.get("inLanguage") != lang:
                errors.append(f"{prefix}: WebPage URL or language is incorrect")
            if webpage.get("mainEntity", {}).get("@id") != canonical + "#case-study":
                errors.append(f"{prefix}: WebPage main entity does not identify its case study")
            if work.get("name") != name or work.get("url") != canonical or work.get("inLanguage") != lang:
                errors.append(f"{prefix}: CreativeWork does not match visible project content")
            if work.get("author", {}).get("@id") != PERSON_ID or work.get("mainEntityOfPage", {}).get("@id") != canonical + "#webpage":
                errors.append(f"{prefix}: CreativeWork author or page relationship is incorrect")
            breadcrumb_items = breadcrumb.get("itemListElement", [])
            home_url = ORIGIN + LANGUAGES[lang]
            if [item.get("position") for item in breadcrumb_items] != [1, 2] or [item.get("item") for item in breadcrumb_items] != [home_url, canonical]:
                errors.append(f"{prefix}: breadcrumb schema does not match visible Home > project navigation")
            if any(entity.get("@type") == "ProfilePage" for entity in graph):
                errors.append(f"{prefix}: project must not be classified as ProfilePage")

            for attrs in parser.images:
                if not attrs.get("alt"):
                    errors.append(f"{prefix}: project image has no alt text: {attrs.get('src')}")
                src = attrs.get("src", "")
                if src.startswith("/assets/") and not (site / src.lstrip("/")).is_file():
                    errors.append(f"{prefix}: local image is missing: {src}")
            errors.extend(check_store_badges(parser, PROJECT_LINKS[slug] if slug != "ktadbrnr" else (), prefix))
            if slug in {item[0] for item in PROJECTS[:7]} and ('class="project-section case-study-context"' not in source or 'class="project-preview"' in source):
                errors.append(f"{prefix}: professional case study must contain its expanded context")
            linked_urls = [link for kind, link in parser.links if kind == "link"]
            for expected_url in PROJECT_LINKS[slug]:
                if linked_urls.count(expected_url) != 1:
                    errors.append(f"{prefix}: expected preserved project link once: {expected_url}")
            local_ids = set(parser.ids)
            for kind, link in parser.links:
                parsed = urlparse(urljoin(ORIGIN + page_path, link))
                if parsed.scheme not in ("http", "https") or parsed.netloc != urlparse(ORIGIN).netloc:
                    continue
                target_path = unquote(parsed.path)
                if kind == "link" and target_path in legacy_redirects():
                    errors.append(f"{prefix}: internal link still targets legacy route: {link}")
                target_file = site / target_path.lstrip("/")
                if not target_path or target_path.endswith("/"):
                    target_file = target_file / "index.html"
                if not target_file.is_file():
                    errors.append(f"{prefix}: broken local {kind}: {link}")
                if parsed.fragment:
                    if target_path == page_path:
                        target_ids = local_ids
                    elif target_file.is_file() and target_file.suffix == ".html":
                        target_parser = Document()
                        target_parser.feed(target_file.read_text(encoding="utf-8"))
                        target_ids = set(target_parser.ids)
                    else:
                        target_ids = set()
                    if unquote(parsed.fragment) not in target_ids:
                        errors.append(f"{prefix}: broken local fragment link: {link}")

            home = home_parsers.get(lang)
            if home and not any(kind == "link" and link == page_path for kind, link in home.links):
                errors.append(f"{prefix}: localized homepage does not link to this project page")

    generated_routes = {
        "/" + str(path.relative_to(site)).replace("\\", "/").removesuffix("index.html")
        for path in site.glob("**/projects/**/index.html")
    }
    expected_routes = {
        route for slug, _name in PROJECTS
        for route in (f"/en/projects/{slug}/", f"/id/projects/{slug}/")
    }
    expected_routes |= set(legacy_redirects()) - {"/"}
    if generated_routes != expected_routes:
        errors.append(f"project page generation mismatch; missing={expected_routes - generated_routes}, extra={generated_routes - expected_routes}")
    for listing in (site / "projects" / "index.html", site / "en" / "projects" / "index.html", site / "id" / "projects" / "index.html"):
        if listing.exists():
            errors.append(f"unrequested project listing page was generated: {listing.relative_to(site)}")
    return errors


def legacy_redirects() -> dict[str, str]:
    return {"/": LANGUAGES["en"]} | {f"/projects/{slug}/": f"/en/projects/{slug}/" for slug, _ in PROJECTS}


def check_redirect_document(parser: Document, source: str, destination: str) -> list[str]:
    errors = []
    if parser.canonicals != [ORIGIN + destination]:
        errors.append(f"{source}: legacy canonical must point to {destination}")
    refresh = [meta.get("content") for meta in parser.metadata if (meta.get("http-equiv") or "").lower() == "refresh"]
    if refresh != [f"0; url={destination}"]:
        errors.append(f"{source}: incorrect legacy meta refresh destination")
    if "noindex" not in ",".join(meta_values(parser, name="robots")).lower():
        errors.append(f"{source}: legacy redirect must be non-indexable")
    if ("link", destination) not in parser.links:
        errors.append(f"{source}: missing accessible legacy redirect fallback link")
    if source == "/" and meta_values(parser, name="google-site-verification") != [SEARCH_CONSOLE_TOKEN]:
        errors.append("root redirect lost Search Console verification")
    return errors


def check_legacy_redirects(site: Path) -> list[str]:
    errors = []
    for source, destination in legacy_redirects().items():
        file = site / source.lstrip("/") / "index.html"
        target = site / destination.lstrip("/") / "index.html"
        if not file.is_file() or not target.is_file():
            errors.append(f"{source}: missing legacy redirect or canonical destination")
            continue
        parser = Document()
        parser.feed(file.read_text(encoding="utf-8"))
        errors.extend(check_redirect_document(parser, source, destination))
    if (site / "pages").exists():
        errors.append("source pages directory leaked into generated output")
    return errors


def check_sitemap(site: Path) -> list[str]:
    path = site / "sitemap.xml"
    if not path.is_file():
        return ["missing generated sitemap.xml"]
    try:
        document = ET.parse(path)
        root = document.getroot()
    except ET.ParseError as exc:
        return [f"sitemap XML cannot be parsed: {exc}"]
    errors = []
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    xhtml_namespace = "{http://www.w3.org/1999/xhtml}"
    entries = root.findall(f"{namespace}url")
    locations = [entry.findtext(f"{namespace}loc") for entry in entries]
    if len(locations) != len(set(locations)):
        errors.append("sitemap contains duplicate URLs")
    required_html_urls = {ORIGIN + page for page in LANGUAGES.values()}
    required_html_urls |= {
        ORIGIN + route for slug, _name in PROJECTS
        for route in (f"/en/projects/{slug}/", f"/id/projects/{slug}/")
    }
    indexable_routes = {}
    for html_path in site.rglob("*.html"):
        parser = Document()
        parser.feed(html_path.read_text(encoding="utf-8"))
        canonical = parser.canonicals[0] if len(parser.canonicals) == 1 else None
        robots = meta_values(parser, name="robots")
        if canonical and robots and "noindex" not in robots[0].lower():
            indexable_routes[canonical] = parser.alternate_declarations
    expected_urls = set(indexable_routes) | {CV_URL}
    if not required_html_urls.issubset(set(indexable_routes)):
        errors.append(f"required homepage or project pages are not generated as indexable canonical pages: {required_html_urls - set(indexable_routes)}")
    if set(locations) != expected_urls:
        errors.append(f"sitemap does not match generated indexable pages and CV; missing={expected_urls - set(locations)}, extra={set(locations) - expected_urls}")
    for location in locations:
        parsed = urlparse(location or "")
        if parsed.scheme != "https" or parsed.netloc != urlparse(ORIGIN).netloc:
            errors.append(f"sitemap URL is not an absolute production HTTPS URL: {location}")
        elif location != CV_URL and location not in indexable_routes:
            errors.append(f"sitemap URL is not a generated canonical indexable page: {location}")
    for entry, location in zip(entries, locations):
        if location != CV_URL:
            expected = set(indexable_routes.get(location, []))
            alternates = {
                (link.get("hreflang"), link.get("href"))
                for link in entry.findall(f"{xhtml_namespace}link")
            }
            if alternates != expected:
                errors.append(f"sitemap hreflang annotations are incorrect for {location}: {alternates}")
            lastmod = entry.findtext(f"{namespace}lastmod")
            if location in {ORIGIN + page for page in LANGUAGES.values()} and not lastmod:
                errors.append(f"sitemap page has no explicit content modification date: {location}")
            elif "/projects/" in urlparse(location).path and lastmod:
                errors.append(f"project sitemap page has an unverified lastmod date: {location}")
            elif lastmod:
                try:
                    datetime.fromisoformat(lastmod.replace("Z", "+00:00"))
                except ValueError:
                    errors.append(f"sitemap lastmod is not a valid ISO date: {location} ({lastmod})")
        else:
            if entry.find(f"{namespace}lastmod") is not None:
                errors.append("CV PDF sitemap entry has a lastmod value without reliable source metadata")
            if entry.findall(f"{xhtml_namespace}link"):
                errors.append("CV PDF sitemap entry must not have homepage hreflang annotations")
    if root.tag != f"{namespace}urlset":
        errors.append("sitemap root must be a urlset")
    if root.findall(f".//{namespace}changefreq") or root.findall(f".//{namespace}priority"):
        errors.append("sitemap contains obsolete changefreq or priority elements")
    return errors


def check_insights(site: Path, catalog_path: Path = Path("_data/insights.json")) -> list[str]:
    path = catalog_path
    try:
        insights = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Engineering Insights metadata cannot be read: {exc}"]
    errors = []
    ids = [item.get("article_id") for item in insights]
    slugs = [item.get("slug") for item in insights]
    if None in ids or len(ids) != len(set(ids)):
        errors.append("Engineering Insights article identifiers must be present and unique")
    if None in slugs or len(slugs) != len(set(slugs)) or any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug or "") for slug in slugs):
        errors.append("Engineering Insights slugs must be unique lowercase URL slugs")
    by_id = {item.get("article_id"): item for item in insights if item.get("article_id")}
    known_project_ids = {slug for slug, _name in PROJECTS}
    for item in insights:
        article_id = item.get("article_id", "<missing>")
        if item.get("status") not in {"draft", "published"}:
            errors.append(f"{article_id}: publication state must be draft or published")
        for field in ("title_en", "title_id", "description_en", "description_id", "summary_en", "summary_id", "en_path", "id_path", "draft_en", "draft_id", "sources", "related_projects"):
            if not item.get(field):
                errors.append(f"{article_id}: required metadata missing: {field}")
        for language, title_key, draft_key, route_key in (("en", "title_en", "draft_en", "en_path"), ("id", "title_id", "draft_id", "id_path")):
            draft_path = Path(item.get(draft_key, ""))
            route = item.get(route_key, "")
            if not route.startswith(("/en/insights/", "/id/insights/")) or not route.endswith("/"):
                errors.append(f"{article_id}: invalid {language} article route: {route}")
            if item.get("status") == "draft":
                if not draft_path.is_file():
                    errors.append(f"{article_id}: {language} draft source is missing: {draft_path}")
                if (site / draft_path).exists():
                    errors.append(f"{article_id}: draft source leaked into generated output: {draft_path}")
                if (site / route.lstrip("/") / "index.html").exists():
                    errors.append(f"{article_id}: unpublished {language} route was generated: {route}")
            else:
                generated = site / route.lstrip("/") / "index.html"
                if not generated.is_file():
                    errors.append(f"{article_id}: published {language} route is missing: {route}")
                else:
                    parser = Document()
                    parser.feed(generated.read_text(encoding="utf-8"))
                    canonical = ORIGIN + route
                    expected_alternates = [("en", ORIGIN + item.get("en_path", "")), ("id", ORIGIN + item.get("id_path", "")), ("x-default", ORIGIN + item.get("en_path", ""))]
                    if parser.html_lang != language or parser.h1_text != [item.get(title_key)]:
                        errors.append(f"{article_id}: {language} article language or H1 does not match catalog")
                    if parser.canonicals != [canonical]:
                        errors.append(f"{article_id}: {language} article must use its own canonical URL")
                    if parser.alternate_declarations != expected_alternates:
                        errors.append(f"{article_id}: {language} article translation declarations are incorrect")
                    if meta_values(parser, property="og:type") != ["article"] or meta_values(parser, name="robots") != ["index, follow"]:
                        errors.append(f"{article_id}: {language} article Open Graph type or indexability is incorrect")
                    descriptions = meta_values(parser, name="description")
                    if len(descriptions) != 1 or descriptions[0] != item.get(f"description_{language}"):
                        errors.append(f"{article_id}: {language} article description does not match catalog")
                    published_dates = meta_values(parser, property="article:published_time")
                    if len(published_dates) != 1:
                        errors.append(f"{article_id}: {language} published article needs a real publication date")
                    else:
                        try:
                            datetime.fromisoformat(published_dates[0].replace("Z", "+00:00"))
                        except ValueError:
                            errors.append(f"{article_id}: {language} article publication date is invalid")
                    if len(parser.json_ld) != 1:
                        errors.append(f"{article_id}: {language} article must emit one JSON-LD graph")
                    else:
                        try:
                            graph = json.loads(parser.json_ld[0]).get("@graph", [])
                            article = next(entity for entity in graph if entity.get("@type") == "TechArticle")
                            if article.get("author", {}).get("@id") != PERSON_ID or article.get("url") != canonical or article.get("datePublished") != published_dates[0]:
                                errors.append(f"{article_id}: {language} article schema author or URL is incorrect")
                            if any(entity.get("@type") == "ProfilePage" for entity in graph):
                                errors.append(f"{article_id}: {language} article must not be classified as ProfilePage")
                        except (json.JSONDecodeError, AttributeError, TypeError, StopIteration):
                            errors.append(f"{article_id}: {language} article JSON-LD is invalid or lacks TechArticle")
        if item.get("en_path") != f"/en/insights/{item.get('slug', '')}/" or item.get("id_path") != f"/id/insights/{item.get('slug', '')}/":
            errors.append(f"{article_id}: language routes do not match the stable slug")
        unknown_projects = set(item.get("related_projects", [])) - known_project_ids
        if unknown_projects:
            errors.append(f"{article_id}: unknown related project identifiers: {sorted(unknown_projects)}")
        unknown_articles = set(item.get("related_insights", [])) - set(by_id)
        if unknown_articles:
            errors.append(f"{article_id}: unknown related article identifiers: {sorted(unknown_articles)}")
        elif item.get("status") == "published":
            unpublished_related = [related_id for related_id in item.get("related_insights", []) if by_id[related_id].get("status") != "published"]
            if unpublished_related:
                errors.append(f"{article_id}: related article links target unpublished articles: {unpublished_related}")
        if len(item.get("sources", [])) == 0:
            errors.append(f"{article_id}: at least one authoritative source is required")
        for source in item.get("sources", []):
            if not source.get("label") or urlparse(source.get("url", "")).scheme != "https":
                errors.append(f"{article_id}: each source needs a label and HTTPS URL")
        if item.get("status") == "published" and any(item.get(field) != "approved" for field in ("translation_review", "editorial_review", "publication_review")):
            errors.append(f"{article_id}: translation, editorial, and publication review must be approved before publishing")
    if any(item.get("status") == "published" for item in insights):
        for lang, route in (("en", "/en/insights/"), ("id", "/id/insights/")):
            listing = site / route.lstrip("/") / "index.html"
            if not listing.is_file():
                errors.append(f"published articles require a generated {lang} listing page: {route}")
            else:
                parser = Document()
                parser.feed(listing.read_text(encoding="utf-8"))
                expected_canonical = ORIGIN + route
                expected_alternates = [("en", ORIGIN + "/en/insights/"), ("id", ORIGIN + "/id/insights/"), ("x-default", ORIGIN + "/en/insights/")]
                if parser.canonicals != [expected_canonical] or parser.html_lang != lang:
                    errors.append(f"{lang} Insights listing canonical or HTML language is incorrect")
                if parser.alternate_declarations != expected_alternates:
                    errors.append(f"{lang} Insights listing translation declarations are incorrect")
                expected_routes = {item.get("en_path") if lang == "en" else item.get("id_path") for item in insights if item.get("status") == "published"}
                linked_routes = {urlparse(link).path for kind, link in parser.links if kind == "link"}
                if not expected_routes.issubset(linked_routes):
                    errors.append(f"{lang} Insights listing is missing published article links: {expected_routes - linked_routes}")
                if len(parser.json_ld) != 1:
                    errors.append(f"{lang} Insights listing must emit one JSON-LD graph")
                else:
                    try:
                        types = {entity.get("@type") for entity in json.loads(parser.json_ld[0]).get("@graph", [])}
                        if not {"CollectionPage", "ItemList"}.issubset(types) or "ProfilePage" in types:
                            errors.append(f"{lang} Insights listing schema types are incorrect: {sorted(types)}")
                    except (json.JSONDecodeError, AttributeError, TypeError):
                        errors.append(f"{lang} Insights listing JSON-LD is invalid")
    else:
        for route in ("/insights/", "/en/insights/", "/id/insights/"):
            if (site / route.lstrip("/") / "index.html").exists():
                errors.append(f"empty Insights listing must not be generated: {route}")
    return errors


def check_robots(site: Path) -> list[str]:
    path = site / "robots.txt"
    if not path.is_file():
        return ["missing generated robots.txt"]
    content = path.read_text(encoding="utf-8")
    errors = []
    if "Sitemap: https://mydv.my.id/sitemap.xml" not in content:
        errors.append("robots.txt does not declare the production sitemap")
    if "Disallow: /" in content or "noindex" in content.lower():
        errors.append("robots.txt unexpectedly blocks the public website")
    if "User-agent: *" not in content or "Allow: /" not in content:
        errors.append("robots.txt must leave public pages and assets crawlable")
    return errors


def check_generated_exclusions(site: Path) -> list[str]:
    internal_paths = (
        "AGENTS.html", "CLAUDE.html", "CODEBUDDY.html", "GEMINI.html", "QODER.html",
        "opencode.jsonc", "skills-lock.json", "script.txt", "SEO_PHASE1_IMPLEMENTATION_REPORT.html",
        "SEO_PHASE2_IMPLEMENTATION_REPORT.html",
        "SEO_PHASE3_IMPLEMENTATION_REPORT.html", "ENGINEERING_INSIGHTS_GUIDE.html",
        "SEO_MONITORING_GUIDE.html", "SEO_PHASE4_IMPLEMENTATION_REPORT.html",
        "package.json", "package-lock.json", "lighthouse-pages.json",
        "production-seo-report.json", "production-seo-report.md",
        "pages/en/portfolio.md", "pages/id/portfolio.md",
    )
    errors = [f"development-only source was published: {path}" for path in internal_paths if (site / path).exists()]
    errors.extend(f"monitoring output was published: {path}" for path in ("node_modules", ".lighthouseci", "reports") if (site / path).exists())
    errors.extend(f"Lighthouse configuration was published: {path.name}" for path in site.glob("lighthouserc.*.cjs"))
    return errors


def check_localized_metadata(site: Path) -> list[str]:
    summaries = {}
    for lang, page_path in LANGUAGES.items():
        page = site / page_path.lstrip("/") / "index.html"
        if not page.is_file():
            continue
        parser = Document()
        parser.feed(page.read_text(encoding="utf-8"))
        summaries[lang] = (parser.titles[0] if parser.titles else "", meta_values(parser, name="description"))
    if set(summaries) == set(LANGUAGES):
        if summaries["en"][0] == summaries["id"][0]:
            return ["English and Indonesian titles must be independently localized"]
        if len(summaries["en"][1]) == 1 and len(summaries["id"][1]) == 1 and summaries["en"][1][0] == summaries["id"][1][0]:
            return ["English and Indonesian descriptions must be independently localized"]
    return []


def main() -> int:
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--site", type=Path, default=Path("_site"))
    options = args.parse_args()
    errors = check_source()
    errors.extend(check_sitemap(options.site))
    errors.extend(check_legacy_redirects(options.site))
    errors.extend(check_insights(options.site))
    errors.extend(check_robots(options.site))
    errors.extend(check_generated_exclusions(options.site))
    errors.extend(check_localized_metadata(options.site))
    errors.extend(check_project_pages(options.site))
    for lang, path in LANGUAGES.items():
        errors.extend(check_page(options.site, lang, path))
    if errors:
        print("Portfolio quality checks failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("OK — EN/ID metadata, canonical/hreflang, Schema.org graph, social image, sitemap, robots, content, assets and local links validated.")
    print("Note: external store URLs were preserved, not requested over the network.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
