# SEO Phase 3 Implementation Report

## A. Executive Summary

Phase 3 adds a bilingual Engineering Insights authoring architecture, reusable article and listing layouts, page-type-aware SEO/schema branches, publication-aware navigation and project cross-links, and draft-exclusion validation. Three substantive article pairs (six Markdown drafts) are prepared for review. They remain unpublished because translations and final owner/editor review are outstanding. No listing pages were created because the public article count is zero; this avoids empty indexable routes.

Technical implementation is complete for the draft workflow. Editorial publication readiness is **not complete**. The public generated inventory remains unchanged at 22 canonical HTML pages and 23 sitemap URLs including the CV PDF.

## B. Initial Repository Findings

- Starting commit: `33f6cf76d353` (`feat(seo): add bilingual project case studies and project-level SEO`). The worktree was clean before changes.
- Jekyll 3.10/GitHub Pages uses localized explicit homepage pages and explicit project pages. Shared SEO lives in `_includes/seo.html`; layouts use `_layouts/default.html`; projects are driven by `_data/projects.yml`.
- The sitemap enumerates `site.pages` filtered by `seo_indexable: true`, so explicit static pages are compatible without a plugin or collection. The original validator expected exactly 23 sitemap entries.
- Shared SEO classified every non-project page as `ProfilePage`; the default layout's navigation and language switch assumed home or project context. These shared assumptions needed page-type branches before adding articles.
- Portfolio source describes Flutter/Dart development, UI and API work, state management, native integrations, Firebase/FCM, app deployment, and project capabilities. Project features alone do not establish an individual contribution.
- Holy Smart, Holy World, DTG SOMS, and Ar-Rauda lack a specific personal role or responsibility statement in their project records. Their technology/features were not used to infer ownership.
- Existing `--faint: #617187` was preserved. The existing professional identity, sameAs links, Search Console verification, robots policy, home sections, project accordions, and project routes were preserved.

## C. Content Architecture

`_data/insights.json` is the shared catalog keyed by stable `article_id` and `slug`. It holds localized titles, descriptions, summaries, categories, paths, source references, status, related project IDs, and related article IDs. `_layouts/insight.html` and `_layouts/insights-index.html` share the existing default layout and SEO include. Reusable card and related-content includes consume only `status: published` entries.

Six Markdown drafts live under excluded `editorial/drafts/{slug}/{en,id}.md`. Jekyll does not generate these files. Publication instructions in `ENGINEERING_INSIGHTS_GUIDE.md` explain how reviewed content becomes explicit bilingual static pages and how the two listing pages are created only once content is ready. This avoids plugins, JavaScript discovery, a second SEO system, and empty public pages.

The shared SEO include retains Person and WebSite entities and adds page-aware TechArticle, CollectionPage/ItemList, and breadcrumbs. The sitemap continues to discover explicitly indexable static pages and now the validator derives the expected URL set from generated canonical/indexable pages.

Rollback is straightforward: remove the new draft/catalog/template/nav-related changes as one commit revert; there are no data migrations or external writes. No existing content was removed or rewritten.

## D. Article Inventory

All entries below are **draft**, have no publication/modification dates, are absent from generated output and sitemap, and require owner review. The listed URLs are reserved target routes, not live generated routes.

| Article | English target | Indonesian target | Category | Related projects | Sources | Technical review | Translation/editorial | Publication | Sitemap |
|---|---|---|---|---|---|---|---|---|---|
| Flutter Production Readiness: A Practical Engineering Checklist | `/insights/flutter-production-readiness/` | `/id/insights/flutter-production-readiness/` | Flutter application engineering | Holy Smart, Ar-Rauda, Cling! | Flutter architecture, error, testing, performance docs | Primary Flutter docs checked 2026-11-27; no project-specific claim; no executable code | Draft translation and editorial review needed | Draft | Excluded |
| Designing Reliable Push Notifications in Flutter with Firebase Cloud Messaging | `/insights/flutter-firebase-push-notifications/` | `/id/insights/flutter-firebase-push-notifications/` | Native mobile integration | KTADBRNR, Cling! | Firebase receive, setup, and message type docs | Firebase primary docs checked 2026-11-27; delivery limitations and lifecycle differences included | Draft translation and editorial review needed | Draft | Excluded |
| Managing Offline Data and Application State in Flutter | `/insights/flutter-offline-state-management/` | `/id/insights/flutter-offline-state-management/` | Offline-first mobile applications | Bloom, Cling! | Flutter offline-first, data layer, SQL persistence docs | Primary Flutter docs checked 2026-11-27; no project-specific implementation claim | Draft translation and editorial review needed | Draft | Excluded |

## E. Professional Authority Improvements

The existing “Maulana Yusuf — Flutter & Mobile Developer” identity and verified `sameAs` profiles remain centralized and unchanged. The site now has an article structure to connect general engineering guidance to relevant documented project capabilities when an article is published. No title, seniority, employment, or experience claim was added.

No project contribution details were added for Holy Smart, Holy World, DTG SOMS, or Ar-Rauda because available public source content does not identify personal responsibilities. Owner input needed per project: role and collaboration context; personally implemented features or integrations; one approved engineering challenge and approach; measurable outcomes only if documented; and any confidentiality limits.

## F. Internal Linking

- Future homepage article previews and navigation render only when a published catalog entry exists. Since all entries are drafts, these links do not appear on current public pages.
- Published article templates link to configured related project IDs and only published related article IDs.
- Project detail templates link back to published articles whose `related_projects` contains that project's stable ID.
- Draft records define contextual relationships: production readiness ↔ Holy Smart/Ar-Rauda/Cling!, FCM ↔ KTADBRNR/Cling!, offline state ↔ Bloom/Cling! These relationships are not public links yet.
- Existing project-to-project links and homepage project links remain intact.

## G. Metadata and Structured Data

Existing homepage `ProfilePage` and project `WebPage`/`CreativeWork`/`BreadcrumbList` outputs remain in the shared SEO include. Article page front matter supplies localized title, description, canonical path, reciprocal `en`/`id`/`x-default`, translation URL, publication dates, social image, and article category; article schema references the shared Person ID. Listing pages emit `CollectionPage`, `ItemList`, and visible localized breadcrumbs. Article Open Graph type is `article`; other current pages retain `website`.

Article templates use the existing local social image fallback with contextual localized alt text. No image was added. No draft emits article metadata because draft Markdown is outside the generated site.

## H. Sitemap and Indexability

Actual local build: 22 HTML files, 22 canonical HTML content pages (2 homes + 20 projects), 0 article pages, 0 listing pages, 3 bilingual article pairs in draft state, and 23 sitemap entries (22 canonical pages + existing CV PDF). Draft files do not occur in `_site`; no Insights URLs occur in the sitemap. Existing homepage last-modified dates remain explicit; no build date was introduced for content. The sitemap validator now compares entries with generated canonical indexable pages plus the CV rather than fixing a total.

## I. Content Quality Assessment

All three article topics have actionable checklists and limitations, separate general advice from project evidence, avoid personal incident claims, and cite official Flutter or Firebase documentation. The FCM article does not promise delivery and distinguishes receipt, display, background handling, and tap navigation. No code snippets are included, so no example execution is claimed. The documentation pages were checked on 2026-11-27; platform details must be rechecked immediately before publication because they can change. Indonesian prose is a draft and still needs owner fluency review.

No keyword volume research was conducted. No search volume or ranking claim is made. No confidential information or private repository links were added.

## J. Testing Results

| Check | Result | Evidence |
|---|---|---|
| `bundle exec jekyll build --trace` | PASS | Build completed successfully |
| `python3 scripts/check_portfolio.py --site _site` | PASS | Existing homepage/project metadata, schema, links, assets, sitemap, robots, and draft exclusion checks passed |
| `python3 scripts/test_portfolio_validator.py --site _site` | PASS | Eight mutation tests passed across existing project cases plus draft leakage, article translation mapping, unpublished related articles, sitemap leakage, article canonical, and article schema |
| `node --check assets/js/site.js` | PASS | No JavaScript syntax errors |
| `git diff --check` | PASS | No whitespace errors |
| Generated inventory inspection | PASS | 22 HTML files, 23 sitemap entries, no article listings/routes or draft output |
| Published article template rendering | NOT TESTED | No articles are approved/published; no route was generated for inspection |
| Browser, mobile layout, keyboard interaction, Lighthouse | NOT TESTED | No browser/Lighthouse run was performed |
| Editorial/translation approval | NOT TESTED | Requires owner review |
| Production measurement/deployment | NOT TESTED | No production verification or push performed |

## K. Regression Assessment

- **Homepage/projects:** Existing sections, IDs, accordion behavior, project links, and project routes remain. Existing validators pass.
- **SEO/schema:** Current homepage and project graph checks pass. Article/listing branches are ready but cannot be confirmed by current generated pages until a reviewed article is published.
- **Accessibility/performance:** Article templates use semantic article/nav landmarks, one H1, text links, responsive reading width, and overflow-safe code blocks. Existing faint text token remains. No script, font, analytics, or visible image request was added. Device/browser behavior remains unverified.
- **Multilingual behavior:** Existing home language switches remain. Article pages require reciprocal translation URLs; listing and detail templates include localized destinations. Routes are not live until publication.
- **GitHub Pages:** Uses Jekyll-supported static pages, Liquid, JSON/YAML data, and built-in filters; no plugin or dependency was introduced.

## L. Future Content Backlog

See the editorial guide for proposed topics, audience, related projects, evidence, primary references, and owner-input needs. The backlog covers Flutter release configuration, API error states, and Flutter CI/release checks. None is in the publishing catalog or automatically published.

## M. Changed Files

- Added: `ENGINEERING_INSIGHTS_GUIDE.md`, `SEO_PHASE3_IMPLEMENTATION_REPORT.md`, `_data/insights.json`, `_layouts/insight.html`, `_layouts/insights-index.html`, `_includes/insight-card.html`, `_includes/related-insights.html`, `_includes/related-projects.html`, and six bilingual draft Markdown files under `editorial/drafts/`.
- Modified: `_config.yml`, `_includes/seo.html`, `_includes/project-content.html`, `_layouts/default.html`, `index.html`, `id.html`, `assets/css/site.css`, `scripts/check_portfolio.py`, `scripts/test_portfolio_validator.py`.
- Removed/relocated: none.
- Generated `_site` is ignored and was not staged.

## N. Remaining Risks

- Owner must approve factual claims, authorship, bilingual terminology, publication date, and release status before any draft is published.
- Article and listing templates have not yet been rendered from a published route or browser-checked.
- Specific personal responsibilities remain unknown for Holy Smart, Holy World, DTG SOMS, and Ar-Rauda; gather approved evidence before updating their case studies.
- No production Lighthouse or indexing measurement was performed. Those checks belong after publication and Phase 4 measurement planning.
- Recheck Firebase/Flutter documentation before publishing platform-specific advice.
- Optional distribution after approval: share a short article link from existing GitHub or LinkedIn profiles only if desired; no posts or external repository changes were made.
