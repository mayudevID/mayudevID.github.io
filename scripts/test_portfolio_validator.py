#!/usr/bin/env python3
"""Mutation checks proving the generated project-page validator catches regressions."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from check_portfolio import check_insights, check_project_pages, check_sitemap, check_legacy_redirects


class ProjectValidatorMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument("--site", type=Path, default=Path("_site"))
        cls.site = parser.parse_args().site.resolve()
        if not cls.site.is_dir():
            raise RuntimeError(f"generated site not found: {cls.site}")
        cls.temporary = tempfile.TemporaryDirectory(prefix="portfolio-validator-")
        cls.fixture = Path(cls.temporary.name) / "site"

        def ignore_assets(directory: str, names: list[str]) -> set[str]:
            return {"assets"} if Path(directory).resolve() == cls.site else set()

        shutil.copytree(cls.site, cls.fixture, ignore=ignore_assets)
        (cls.fixture / "assets").symlink_to(cls.site / "assets", target_is_directory=True)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def assert_mutation_detected(self, transform, expected_error: str):
        page = self.fixture / "en/projects/holy-smart/index.html"
        original = page.read_text(encoding="utf-8")
        changed = transform(original)
        self.assertNotEqual(original, changed, "fixture mutation did not change the page")
        try:
            page.write_text(changed, encoding="utf-8")
            errors = check_project_pages(self.fixture)
            self.assertTrue(any(expected_error in error for error in errors), "\n".join(errors))
        finally:
            page.write_text(original, encoding="utf-8")

    def test_legacy_redirect_wrong_target_is_detected(self):
        page = self.fixture / "projects/holy-smart/index.html"
        original = page.read_text(encoding="utf-8")
        changed = original.replace("0; url=/en/projects/holy-smart/", "0; url=/en/projects/cling/")
        self.assertNotEqual(original, changed)
        try:
            page.write_text(changed, encoding="utf-8")
            self.assertTrue(any("incorrect legacy meta refresh" in e for e in check_legacy_redirects(self.fixture)))
        finally:
            page.write_text(original, encoding="utf-8")

    def test_missing_header_screenshot_is_detected(self):
        self.assert_mutation_detected(
            lambda source: re.sub(r'<img src="/assets/projects/holy_smart/4\.png"[^>]*>', '', source, count=1),
            "header gallery must contain all approved screenshots in order",
        )

    def test_related_project_section_is_detected(self):
        self.assert_mutation_detected(
            lambda source: source.replace('</article>', '<section id="related-title-holy-smart"><h2>Related projects</h2></section></article>', 1),
            "removed screenshot or related-project section must not be rendered",
        )

    def test_wrong_canonical_is_detected(self):
        def mutate(source: str) -> str:
            return source.replace(
                '<link rel="canonical" href="https://mydv.my.id/en/projects/holy-smart/" />',
                '<link rel="canonical" href="https://mydv.my.id/" />',
                1,
            )

        self.assert_mutation_detected(mutate, "expected self-canonical")

    def test_broken_localized_switch_is_detected(self):
        def mutate(source: str) -> str:
            return source.replace(
                '<a href="/id/projects/holy-smart/" lang="id"',
                '<a href="/id/projects/missing/" lang="id"',
                1,
            )

        self.assert_mutation_detected(mutate, "language switch does not preserve project context")

    def test_incorrect_structured_data_type_is_detected(self):
        def mutate(source: str) -> str:
            return source.replace('"@type": "CreativeWork"', '"@type": "SoftwareApplication"', 1)

        self.assert_mutation_detected(mutate, "project JSON-LD entities are incorrect")

    def test_draft_output_leak_is_detected(self):
        leaked = self.fixture / "editorial/drafts/flutter-production-readiness/en.md"
        leaked.parent.mkdir(parents=True, exist_ok=True)
        leaked.write_text("# unpublished draft", encoding="utf-8")
        try:
            errors = check_insights(self.fixture)
            self.assertTrue(any("draft source leaked into generated output" in error for error in errors), "\n".join(errors))
        finally:
            leaked.unlink()

    def write_catalog(self, mutate):
        catalog = json.loads(Path("_data/insights.json").read_text(encoding="utf-8"))
        mutate(catalog)
        path = Path(self.temporary.name) / "insights.json"
        path.write_text(json.dumps(catalog), encoding="utf-8")
        return path

    def test_mismatched_article_translation_route_is_detected(self):
        path = self.write_catalog(lambda catalog: catalog[0].update(id_path="/id/insights/wrong-slug/"))
        errors = check_insights(self.fixture, path)
        self.assertTrue(any("language routes do not match the stable slug" in error for error in errors), "\n".join(errors))

    def test_unpublished_related_article_is_detected(self):
        def mutate(catalog):
            catalog[0]["status"] = "published"
            catalog[0]["related_insights"] = [catalog[1]["article_id"]]

        errors = check_insights(self.fixture, self.write_catalog(mutate))
        self.assertTrue(any("related article links target unpublished articles" in error for error in errors), "\n".join(errors))

    def test_draft_sitemap_entry_is_detected(self):
        sitemap = self.fixture / "sitemap.xml"
        original = sitemap.read_text(encoding="utf-8")
        sitemap.write_text(original.replace("</urlset>", "<url><loc>https://mydv.my.id/en/insights/draft-only/</loc></url></urlset>"), encoding="utf-8")
        try:
            errors = check_sitemap(self.fixture)
            self.assertTrue(any("sitemap does not match generated indexable pages" in error for error in errors), "\n".join(errors))
        finally:
            sitemap.write_text(original, encoding="utf-8")

    def test_wrong_published_article_canonical_and_schema_are_detected(self):
        def mutate(catalog):
            article = catalog[0]
            article["status"] = "published"
            article["translation_review"] = "approved"
            article["editorial_review"] = "approved"
            article["publication_review"] = "approved"

        item = json.loads(Path("_data/insights.json").read_text(encoding="utf-8"))[0]
        en_route = item["en_path"]
        id_route = item["id_path"]
        for route, language, title, canonical in ((en_route, "en", item["title_en"], "https://mydv.my.id/"), (id_route, "id", item["title_id"], "https://mydv.my.id" + id_route)):
            page = self.fixture / route.lstrip("/") / "index.html"
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(
                f'<html lang="{language}"><head><title>{title}</title><link rel="canonical" href="{canonical}" />'
                f'<link rel="alternate" hreflang="en" href="https://mydv.my.id{en_route}" />'
                f'<link rel="alternate" hreflang="id" href="https://mydv.my.id{id_route}" />'
                f'<link rel="alternate" hreflang="x-default" href="https://mydv.my.id{en_route}" />'
                f'<meta property="og:type" content="article" /><meta name="robots" content="index, follow" /></head>'
                f'<body><h1>{title}</h1><script type="application/ld+json">{{broken json</script></body></html>', encoding="utf-8")
        errors = check_insights(self.fixture, self.write_catalog(mutate))
        self.assertTrue(any("must use its own canonical URL" in error for error in errors), "\n".join(errors))
        self.assertTrue(any("article JSON-LD is invalid" in error for error in errors), "\n".join(errors))


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]])
