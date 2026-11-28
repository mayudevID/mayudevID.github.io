#!/usr/bin/env python3
"""Bounded production SEO check; local generated-site validation remains separate."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

from check_portfolio import CV_URL, LANGUAGES, ORIGIN, PROJECTS, Document, meta_values, legacy_redirects, check_redirect_document

TIMEOUT = 12
RETRIES = 2
USER_AGENT = "MayudevID-SEO-Monitor/1.0 (+https://mydv.my.id/)"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9", "xhtml": "http://www.w3.org/1999/xhtml"}


def classify_http(status: int) -> str:
    if status == 429:
        return "RATE_LIMITED"
    if status in {500, 502, 503, 504}:
        return "SERVER_ERROR"
    if status in {401, 403}:
        return "AUTH_OR_BOT_PROTECTION"
    if status == 999:
        return "BOT_PROTECTION"
    if status >= 400:
        return "PERMANENT_HTTP_FAILURE"
    return "AVAILABLE"


def expected_routes() -> set[str]:
    """Routes derive from the validator's canonical project catalog."""
    routes = {"/en/", "/id/"}
    for slug, _ in PROJECTS:
        routes.update({f"/en/projects/{slug}/", f"/id/projects/{slug}/"})
    return routes


class RedirectTracker(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        super().__init__()
        self.chain: list[str] = []

    def redirect_request(self, request, fp, code, message, headers, new_url):
        self.chain.append(new_url)
        return super().redirect_request(request, fp, code, message, headers, new_url)


_CACHE: dict[tuple[str, bool], tuple[int, str, str, str, str, int]] = {}


def fetch(url: str, *, include_body: bool = True) -> tuple[int, str, str, str, str, int]:
    cache_key = (url, include_body)
    if cache_key in _CACHE:
        return _CACHE[cache_key]
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xml,text/plain,*/*"})
    last = ""
    for attempt in range(RETRIES + 1):
        try:
            tracker = RedirectTracker()
            opener = urllib.request.build_opener(tracker)
            with opener.open(request, timeout=TIMEOUT) as response:
                body = response.read(4_000_001) if include_body else b""
                if len(body) > 4_000_000:
                    raise ValueError("response exceeded 4 MB safety limit")
                result = (response.status, response.geturl(), response.headers.get("Content-Type", ""), response.headers.get("X-Robots-Tag", ""), body.decode("utf-8", errors="replace"), len(tracker.chain))
                _CACHE[cache_key] = result
                return result
        except urllib.error.HTTPError as exc:
            status = exc.code
            if status in {429, 500, 502, 503, 504} and attempt < RETRIES:
                time.sleep(0.5 * (2 ** attempt))
                continue
            result = (status, url, exc.headers.get("Content-Type", ""), exc.headers.get("X-Robots-Tag", ""), "", 0)
            _CACHE[cache_key] = result
            return result
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            last = str(exc)
            if attempt < RETRIES:
                time.sleep(0.5 * (2 ** attempt))
                continue
    raise TimeoutError(last or "request failed after bounded retries")


def check_production() -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    pages: dict[str, dict] = {}
    parsed_pages: dict[str, Document] = {}
    internal_targets: set[str] = set()
    internal_fragments: list[tuple[str, str, str]] = []
    expected = expected_routes()
    for route in sorted(expected):
        url = ORIGIN + route
        try:
            status, final, content_type, x_robots, body, redirects = fetch(url)
        except TimeoutError as exc:
            errors.append(f"TEMPORARY/NETWORK: {url}: {exc}")
            pages[route] = {"status": "BLOCKED", "availability": "NETWORK_TIMEOUT", "reason": str(exc)}
            continue
        page_errors = []
        if status != 200:
            page_errors.append(f"HTTP {status}")
        if redirects > 3:
            page_errors.append(f"excessive redirect chain ({redirects})")
        if urlparse(final).scheme != "https" or urlparse(final).netloc != urlparse(ORIGIN).netloc or final.rstrip("/") != url.rstrip("/"):
            page_errors.append(f"unexpected final destination {final}")
        if "text/html" not in content_type.lower():
            page_errors.append(f"unexpected content type {content_type}")
        page = Document()
        page.feed(body)
        parsed_pages[route] = page
        canonical = url
        if len(page.titles) != 1 or not page.titles[0].strip():
            page_errors.append("missing or duplicate document title")
        if page.html_lang != ("id" if route.startswith("/id/") else "en"):
            page_errors.append("incorrect document language")
        if len(meta_values(page, name="description")) != 1 or not meta_values(page, name="description")[0].strip():
            page_errors.append("missing or duplicate meta description")
        if page.canonicals != [canonical]:
            page_errors.append(f"canonical mismatch: {page.canonicals}")
        lang = "id" if route.startswith("/id/") else "en"
        base = route.replace("/id/", "/en/", 1) if lang == "id" else route
        id_route = base.replace("/en/", "/id/", 1) if lang == "en" else route
        expected_alternates = {"en": ORIGIN + base, "id": ORIGIN + id_route, "x-default": ORIGIN + base}
        if len(page.alternate_declarations) != 3 or dict(page.alternate_declarations) != expected_alternates:
            page_errors.append("hreflang/x-default declarations do not match route pair")
        if meta_values(page, property="og:url") != [canonical]:
            page_errors.append("Open Graph URL mismatch")
        if len(meta_values(page, property="og:image")) != 1:
            page_errors.append("missing Open Graph social image")
        else:
            social_image = urljoin(url, meta_values(page, property="og:image")[0])
            try:
                image_status, image_final, image_type, _, _, image_redirects = fetch(social_image, include_body=False)
                if image_status != 200 or not image_type.lower().startswith("image/") or urlparse(image_final).scheme != "https" or image_redirects > 3:
                    page_errors.append(f"social image unavailable or invalid: {social_image} (HTTP {image_status}, {image_type})")
            except TimeoutError as exc:
                page_errors.append(f"social image unavailable: {exc}")
        if page.h1_count != 1 or not page.h1_text or not page.h1_text[0].strip():
            page_errors.append("expected exactly one meaningful H1")
        directives = ",".join(meta_values(page, name="robots") + [x_robots]).lower()
        robots_tokens = {token.strip() for token in directives.split(",")}
        if "noindex" in robots_tokens or "none" in robots_tokens:
            page_errors.append("unintended noindex directive")
        if any("TechArticle" in raw or "Article" in raw for raw in page.json_ld):
            page_errors.append("article structured data found while publication is frozen")
        try:
            if len(page.json_ld) != 1:
                raise ValueError("expected one JSON-LD script")
            graph = json.loads(page.json_ld[0]).get("@graph", [])
            types = [entity.get("@type") for entity in graph]
            if len(types) != len(set(types)):
                page_errors.append("duplicate primary structured data types")
            expected_types = {"Person", "WebSite", "ProfilePage"} if route in {"/en/", "/id/"} else {"Person", "WebSite", "WebPage", "CreativeWork", "BreadcrumbList"}
            if set(types) != expected_types:
                page_errors.append(f"structured data types mismatch: {types}")
            if not any(entity.get("@id") == ORIGIN + "/#person" for entity in graph):
                page_errors.append("shared Person entity identifier missing")
            entities = {entity.get("@type"): entity for entity in graph}
            if route in {"/en/", "/id/"}:
                profile = entities.get("ProfilePage", {})
                if profile.get("url") != canonical or profile.get("mainEntity", {}).get("@id") != ORIGIN + "/#person":
                    page_errors.append("ProfilePage canonical or Person relationship mismatch")
            else:
                webpage = entities.get("WebPage", {})
                work = entities.get("CreativeWork", {})
                crumbs = entities.get("BreadcrumbList", {}).get("itemListElement", [])
                if webpage.get("url") != canonical or webpage.get("mainEntity", {}).get("@id") != canonical + "#case-study":
                    page_errors.append("project WebPage canonical or primary entity relationship mismatch")
                if work.get("url") != canonical or work.get("mainEntityOfPage", {}).get("@id") != canonical + "#webpage":
                    page_errors.append("CreativeWork canonical or page relationship mismatch")
                if [node.get("position") for node in crumbs] != [1, 2] or not crumbs or crumbs[-1].get("item") != canonical:
                    page_errors.append("project BreadcrumbList does not end at canonical route")
        except (json.JSONDecodeError, ValueError, AttributeError, TypeError) as exc:
            page_errors.append(f"invalid JSON-LD: {exc}")
        for kind, href in page.links:
            target = urljoin(url, href)
            parsed = urlparse(target)
            if parsed.scheme == "https" and parsed.netloc == urlparse(ORIGIN).netloc:
                if kind == "link":
                    if "/insights/" in parsed.path:
                        page_errors.append(f"public link targets unpublished article route: {href}")
                    if parsed.fragment:
                        internal_fragments.append((route, parsed.path or "/", unquote(parsed.fragment)))
                    internal_targets.add(target.split("#", 1)[0])
                target_route = parsed.path or "/"
                if target_route.endswith((".png", ".jpg", ".jpeg", ".webp", ".svg", ".css", ".js", ".pdf")) or kind != "link":
                    try:
                        asset_status, asset_final, _, _, _, asset_redirects = fetch(target, include_body=False)
                        if asset_status != 200 or urlparse(asset_final).netloc != urlparse(ORIGIN).netloc:
                            page_errors.append(f"broken local {kind}: {href} (HTTP {asset_status})")
                        if asset_redirects > 3:
                            page_errors.append(f"excessive redirect chain for local resource: {href}")
                    except TimeoutError as exc:
                        page_errors.append(f"local resource unavailable: {href}: {exc}")
        pages[route] = {"status": "FAIL" if page_errors else "PASS", "http": status, "availability": classify_http(status), "canonical": "FAIL" if any("canonical" in e for e in page_errors) else "PASS", "hreflang": "FAIL" if any("hreflang" in e for e in page_errors) else "PASS", "indexability": "FAIL" if any("noindex" in e for e in page_errors) else "PASS", "structured_data": "FAIL" if any("structured data" in e or "JSON-LD" in e or "json-ld" in e for e in page_errors) else "PASS", "errors": page_errors}
        errors.extend(f"{url}: {error}" for error in page_errors)

    for source_route, target_route, fragment in internal_fragments:
        target_parser = parsed_pages.get(target_route)
        if target_parser and fragment not in target_parser.ids:
            errors.append(f"{ORIGIN + source_route}: broken internal fragment to {target_route}#{fragment}")

    if len(internal_targets) > 250:
        errors.append(f"internal URL request limit exceeded: {len(internal_targets)} unique targets (maximum 250)")
    for target in sorted(internal_targets)[:250]:
        try:
            link_status, link_final, link_type, _, _, link_redirects = fetch(target, include_body=False)
            target_path = urlparse(target).path or "/"
            is_pdf = target_path.lower().endswith(".pdf")
            if link_status != 200 or (not is_pdf and "text/html" not in link_type.lower()) or (is_pdf and "pdf" not in link_type.lower()):
                errors.append(f"broken internal link {target} (HTTP {link_status}, {link_type})")
            if link_redirects > 3 or urlparse(link_final).netloc != urlparse(ORIGIN).netloc:
                errors.append(f"unexpected internal link redirect for {target}: {link_final}")
            if "text/html" in link_type.lower() and target_path not in expected:
                errors.append(f"unexpected internal HTML route or soft-404 target: {target}")
        except TimeoutError as exc:
            errors.append(f"internal link unavailable {target}: {exc}")

    # GitHub Pages serves legacy URLs as static immediate HTML redirects.
    for source, destination in legacy_redirects().items():
        try:
            status, final, content_type, _, body, redirects = fetch(ORIGIN + source)
            if status != 200 or "text/html" not in content_type.lower():
                errors.append(f"{source}: legacy redirect unavailable (HTTP {status})")
                continue
            if final == ORIGIN + destination and redirects:
                continue
            if final != ORIGIN + source:
                errors.append(f"{source}: unexpected legacy redirect destination {final}")
                continue
            parser = Document()
            parser.feed(body)
            errors.extend(check_redirect_document(parser, source, destination))
        except TimeoutError as exc:
            errors.append(f"{source}: legacy redirect unavailable: {exc}")

    # Sitemap is an independent source under test; expected routes come from repository inventory.
    try:
        status, final, content_type, _, xml, redirects = fetch(ORIGIN + "/sitemap.xml")
        if status != 200 or "xml" not in content_type.lower() or final != ORIGIN + "/sitemap.xml":
            errors.append("sitemap: HTTP, content type, or final URL is incorrect")
        root = ET.fromstring(xml)
        locations = [node.text or "" for node in root.findall("sm:url/sm:loc", NS)]
        duplicates = [url for url, count in Counter(locations).items() if count > 1]
        if duplicates:
            errors.append(f"sitemap duplicate URLs: {duplicates}")
        expected_urls = {ORIGIN + route for route in expected} | {CV_URL}
        if set(locations) != expected_urls:
            errors.append(f"sitemap inventory mismatch: missing={sorted(expected_urls-set(locations))}, extra={sorted(set(locations)-expected_urls)}")
        if any("/insights/" in item for item in locations):
            errors.append("sitemap contains unpublished article route")
        for entry in root.findall("sm:url", NS):
            loc = entry.findtext("sm:loc", default="", namespaces=NS)
            route = urlparse(loc).path
            if route not in expected:
                continue
            lang = "id" if route.startswith("/id/") else "en"
            base = route.replace("/id/", "/en/", 1) if lang == "id" else route
            id_route = base.replace("/en/", "/id/", 1) if lang == "en" else route
            alternates = {(node.attrib.get("hreflang"), node.attrib.get("href")) for node in entry.findall("xhtml:link", NS)}
            wanted = {("en", ORIGIN + base), ("id", ORIGIN + id_route), ("x-default", ORIGIN + base)}
            if alternates != wanted:
                errors.append(f"sitemap hreflang mismatch for {loc}")
            lastmod = entry.findtext("sm:lastmod", default="", namespaces=NS)
            if lastmod:
                try:
                    datetime.fromisoformat(lastmod.replace("Z", "+00:00"))
                except ValueError:
                    errors.append(f"invalid sitemap lastmod value for {loc}: {lastmod}")
        cv_status, cv_final, cv_type, _, _, cv_redirects = fetch(CV_URL, include_body=False)
        if cv_status != 200 or "pdf" not in cv_type.lower() or cv_redirects > 3 or urlparse(cv_final).netloc != urlparse(ORIGIN).netloc:
            errors.append(f"CV sitemap resource unavailable or incorrect (HTTP {cv_status}, {cv_type})")
    except (TimeoutError, ET.ParseError, ValueError) as exc:
        errors.append(f"sitemap unavailable or invalid: {exc}")

    try:
        status, final, _, _, robots, _ = fetch(ORIGIN + "/robots.txt")
        if status != 200 or final != ORIGIN + "/robots.txt":
            errors.append("robots.txt unavailable or redirected unexpectedly")
        groups: list[tuple[list[str], list[tuple[str, str]]]] = []
        agents: list[str] = []
        rules: list[tuple[str, str]] = []
        sitemaps = []
        for raw in robots.splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            key, value = (part.strip() for part in line.split(":", 1))
            if key.lower() == "user-agent":
                if rules:
                    groups.append((agents, rules))
                    agents, rules = [], []
                agents.append(value.lower())
            elif key.lower() in {"allow", "disallow"}:
                if value:
                    rules.append((key.lower(), value))
            elif key.lower() == "sitemap":
                sitemaps.append(value)
        if agents:
            groups.append((agents, rules))
        if ORIGIN + "/sitemap.xml" not in sitemaps:
            errors.append("robots.txt does not declare production sitemap")
        wildcard = [group_rules for group_agents, group_rules in groups if "*" in group_agents]
        if wildcard:
            import re
            for route in sorted(expected | {"/assets/site.css", "/assets/js/site.js"}):
                matches = []
                for directive, rule in wildcard[-1]:
                    expression = "^" + re.escape(rule).replace(r"\*", ".*")
                    if rule.endswith("$"):
                        expression = expression[:-2] + "$"
                    if re.match(expression, route):
                        matches.append((len(rule.replace("*", "").rstrip("$")), directive == "allow", rule))
                if matches:
                    longest = max(item[0] for item in matches)
                    if not any(length == longest and allow for length, allow, _ in matches):
                        errors.append(f"robots.txt blocks intended public route/resource {route}")
    except TimeoutError as exc:
        errors.append(f"robots.txt unavailable: {exc}")

    # Keep external probing conservative; uncertain status is informational only.
    external = set()
    for route, item in pages.items():
        if item.get("status") != "PASS":
            continue
        try:
            parser = parsed_pages.get(route)
            if parser is None:
                continue
            for kind, href in parser.links:
                parsed = urlparse(urljoin(ORIGIN + route, href))
                if kind == "link" and parsed.scheme in {"http", "https"} and parsed.netloc and parsed.netloc != urlparse(ORIGIN).netloc:
                    external.add(parsed._replace(fragment="").geturl())
        except TimeoutError:
            pass
    for url in sorted(external)[:30]:
        try:
            status, final, _, _, _, _ = fetch(url, include_body=False)
            if status == 429:
                warnings.append(f"external link rate-limited (HTTP {status}): {url}")
            elif status in {401, 403}:
                warnings.append(f"external link may require authentication or bot access (HTTP {status}): {url}")
            elif status == 999:
                warnings.append(f"external link appears bot-protected (HTTP {status}): {url}")
            elif status >= 500:
                warnings.append(f"external link server error, retry later (HTTP {status}): {url}")
            elif status >= 400:
                warnings.append(f"external link confirmed unavailable (HTTP {status}): {url}")
            elif final != url:
                warnings.append(f"external link redirected to {final}: {url}")
        except TimeoutError as exc:
            warnings.append(f"external link unverified: {url} ({exc})")

    result = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "commit_sha": os.environ.get("GITHUB_SHA", "NOT AVAILABLE"), "workflow_context": os.environ.get("GITHUB_EVENT_NAME", "local execution"), "audited_environment": "production", "origin": ORIGIN, "expected_page_count": len(expected), "sitemap_url_count": len(locations) if "locations" in locals() else None, "pages": pages, "errors": errors, "warnings": warnings, "status": "FAIL" if errors else ("WARNING" if warnings else "PASS")}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=Path("production-seo-report.json"))
    parser.add_argument("--markdown", type=Path, default=Path("production-seo-report.md"))
    args = parser.parse_args()
    result = check_production()
    args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary = [f"# Production SEO Monitor: {result['status']}", "", f"- Timestamp: {result['timestamp_utc']}", f"- Commit: {result['commit_sha']}", f"- Workflow context: {result['workflow_context']}", f"- Audited environment: {result['audited_environment']} ({ORIGIN})", f"- Pages expected: {result['expected_page_count']}", f"- Sitemap URLs: {result['sitemap_url_count']}", f"- Pages passing: {sum(p['status'] == 'PASS' for p in result['pages'].values())}", f"- Pages failing/blocked: {sum(p['status'] != 'PASS' for p in result['pages'].values())}", f"- Warnings: {len(result['warnings'])}", ""]
    summary += ["## Errors", *(f"- {item}" for item in result["errors"])] or ["- None"]
    summary += ["", "## Warnings", *(f"- {item}" for item in result["warnings"])] or ["- None"]
    args.markdown.write_text("\n".join(summary) + "\n", encoding="utf-8")
    if "GITHUB_STEP_SUMMARY" in __import__("os").environ:
        with open(__import__("os").environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
            stream.write("\n".join(summary) + "\n")
    print("\n".join(summary))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
