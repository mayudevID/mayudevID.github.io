# Phase 1 Technical SEO Implementation Report

**Repository:** `mayudevID.github.io`  
**Production origin:** `https://mydv.my.id`  
**Implementation date:** 2026-11-27  
**Starting commit:** `02a9a8facf42`  
**Scope:** Technical SEO for the existing English and Indonesian homepages. No dedicated project routes or Phase 2 schemas were added.

## A. Executive Summary

Centralized page metadata in Jekyll data and a reusable SEO include, then localized the English and Indonesian titles, descriptions, social metadata, and profile-page descriptions. Canonicals now derive from each page URL by default and can be overridden per page. The two homepages share one Schema.org `Person` and `WebSite`, and each has a language-specific `ProfilePage`.

Replaced the Bloom-hosted social card with a locally hosted 1200 × 630 PNG using existing portfolio screenshots. Reworked sitemap generation to include the two canonical homepages and preserve the existing CV PDF entry, removed stale ranking hints, and made homepage modification dates explicit. Excluded raw portfolio Markdown and development instructions from generated output while keeping Jekyll’s `include_relative` rendering and CV links intact.

Expanded the existing generated-site checker and kept it in the current GitHub Actions job. The Jekyll build, portfolio SEO/content checks, JavaScript syntax check, and whitespace check pass. Lighthouse, external structured-data validation, Search Console data, and production behavior were not tested.

## B. Initial Findings

- The worktree was clean on `main` at `02a9a8facf42` before changes.
- `_layouts/default.html` owned all title, description, canonical, hreflang, Open Graph, Twitter, and JSON-LD markup. Both languages used the same English title and description.
- Canonical and hreflang behavior already matched the required homepage URLs. The language switch already linked to `/` and `/id/` with language attributes.
- Existing JSON-LD described a single `Person`, but used a fixed English job title and included public email, telephone, and location details. It had no page or website entities.
- Social cards referenced `bloom/main/assets/images/cover.png` from GitHub Raw. The metadata did not declare image dimensions or type, and the title and description were not localized.
- `sitemap.xml` used static November 13, 2026 dates and included `changefreq` and `priority`. It already listed `/`, `/id/`, and `/portfolio/cv_maulana_yusuf.pdf`.
- `robots.txt` allowed all crawlers and pointed to the production sitemap. The Search Console verification tag was present.
- Jekyll copied raw portfolio Markdown and several root instruction/configuration files to `_site`. The portfolio Markdown is also read by `include_relative` to generate the visible pages.
- Existing output had one H1 per page, server-generated project case studies, descriptive project sections, a language switch, and lazy-loaded screenshots. The initial build and existing portfolio validator passed.
- Existing project cover images for Bloom, Cling!, and KBBI Daring still use external GitHub Raw URLs. They were identified as candidates for local hosting; copying them was not needed for this metadata-focused change.

## C. Implementation Details

| Area | Previous implementation and issue | Implemented solution and expected benefit | Affected files |
|---|---|---|---|
| Metadata ownership | SEO tags and one fixed JSON-LD object lived directly in the shared layout. New pages would inherit homepage canonical assumptions. | Added `_data/seo.yml` for shared identity and localized defaults and `_includes/seo.html` for rendering. Page front matter can override title, description, canonical URL/path, language, robots, author, and social image. Canonical defaults from `site.url + page.url`. This keeps defaults centralized while supporting future pages. | `_data/seo.yml`, `_includes/seo.html`, `_layouts/default.html` |
| Localized search and social text | The English and Indonesian homepages shared English copy. | Added independent localized titles, descriptions, Open Graph locale, alternate locale, and social-image alt text. Open Graph and Twitter title/description match the page title and description. | `_data/seo.yml`, `_includes/seo.html`, `index.html`, `id.html` |
| Canonical and language annotations | Homepage behavior was correct but hard-coded into the global layout. | Preserved exact absolute HTTPS canonicals, reciprocal `en`/`id` alternates, `x-default`, and language switching. Values are data-driven and page URL-based, with a per-page override for future routes. | `_data/seo.yml`, `_includes/seo.html`, `index.html`, `id.html` |
| Structured data | A single `Person` included email, phone, and address; there was no shared website/profile graph. | Emit one JSON-LD `@graph` with `Person`, `WebSite`, and `ProfilePage`. Both language pages use `https://mydv.my.id/#person` and `https://mydv.my.id/#website`; each profile ID follows its canonical URL. All dynamic JSON values use Liquid `jsonify`. Added visible expertise, portfolio-linked GitHub and LinkedIn profiles, and the university stated in the portfolio. Removed contact details from JSON-LD while leaving visible contact sections unchanged. | `_data/seo.yml`, `_includes/seo.html`, `_layouts/default.html` |
| Social preview | Open Graph and Twitter images used an external Bloom image and lacked explicit dimensions/type. | Added `assets/seo/og-cover.png` (1200 × 630). The composition uses MayudevID colors and wordmark treatment, Maulana Yusuf’s name, Flutter/mobile positioning, and existing Holy Smart, Holy World, and Ar-Rauda screenshots. The file is referenced only from metadata, so it adds no visible-page image request. | `assets/seo/og-cover.png`, `_data/seo.yml`, `_includes/seo.html` |
| Sitemap | Static dates had become stale; `changefreq` and `priority` added no useful accuracy. | Replaced static XML with a Jekyll template. Only pages marked `seo_indexable: true` are emitted; the homepages have explicit `last_modified_at: 2026-11-27`. Hreflang links are generated from the same mapping as HTML. Removed change frequency and priority. Preserved the existing CV URL without a lastmod value because no reliable source date is configured. | `sitemap.xml`, `index.html`, `id.html` |
| Crawlability and generated files | Crawlers were allowed, but raw Markdown and internal project instructions/configuration were copied into the published site. | Kept public crawling open. Excluded the implementation report, source Markdown, internal instruction/configuration files, and scripts while preserving CV PDFs and generated page content. A build confirmed Jekyll can still include the excluded Markdown sources through `include_relative`. | `_config.yml` |
| Image alternatives | Three personal-project cover images used terse English-only alternatives on both localized pages. | Clarified the English alternatives and localized the Indonesian alternatives as project cover images. Existing project screenshot alternatives, image sizing, and lazy loading were preserved. | `portfolio/portfolio-en.md`, `portfolio/portfolio.md` |
| Automated checks | The existing script checked basic page structure, links, screenshots, and homepage presence in XML. | Extended generated-site validation to cover titles, language, descriptions, metadata uniqueness/consistency, canonicals, hreflang reciprocity, social card references/dimensions, parsed JSON-LD entity relationships, H1 count, sitemap XML/duplicates/URLs/hreflang/lastmod, robots, verification token, generated exclusions, and existing local links/assets. The existing CI job runs this same command; its step name now states its SEO coverage. | `scripts/check_portfolio.py`, `.github/workflows/portfolio-quality.yml` |

The existing visual page layout, CSS colors, mobile navigation, language switch interaction, visible contact content, project copy, CV URLs, and screenshot loading behavior were not changed.

## D. Metadata Comparison

| Page | Previous title | Updated title | Previous description | Updated description |
|---|---|---|---|---|
| English `/` | `Maulana Yusuf \| Flutter & Mobile Developer \| MayudevID` | `Maulana Yusuf \| Flutter & Mobile App Developer` | `Explore Maulana Yusuf's Flutter and mobile development portfolio, featuring Android and iOS apps, native integrations, and production releases.` | `Flutter developer specializing in Android and iOS applications, native integrations, and production-ready mobile solutions. Explore my projects and experience.` |
| Indonesian `/id/` | Shared English title: `Maulana Yusuf \| Flutter & Mobile Developer \| MayudevID` | `Maulana Yusuf \| Flutter & Mobile Developer Indonesia` | Same shared English description as above. | `Portofolio Flutter Developer Indonesia dengan pengalaman membangun aplikasi Android dan iOS, integrasi native, serta pengembangan aplikasi produksi.` |

Meta description, Open Graph description, and Twitter description use the updated language-specific copy. Titles and descriptions are checked for non-empty, localized, distinct values and relevant subject terms rather than arbitrary length limits.

## E. Structured Data Architecture

The rendered `@graph` contains three entities:

| Type | Stable identifier | Relationships and supported properties |
|---|---|---|
| `Person` | `https://mydv.my.id/#person` | Maulana Yusuf; alternate name MayudevID; Flutter & Mobile Developer; portfolio-grounded expertise; verified GitHub and LinkedIn profiles; `alumniOf` Universitas Pembangunan Nasional Veteran Jakarta. |
| `WebSite` | `https://mydv.my.id/#website` | Represents MayudevID at `https://mydv.my.id/`; languages `en` and `id`; publisher references the shared Person. |
| English `ProfilePage` | `https://mydv.my.id/#profilepage` | Canonical English page; localized title/description; English language; `mainEntity` points to the shared Person and `isPartOf` points to WebSite. |
| Indonesian `ProfilePage` | `https://mydv.my.id/id/#profilepage` | Canonical Indonesian page; localized title/description; Indonesian language; same Person and WebSite references. |

The automated check parses each generated JSON-LD script and validates the entity types, stable IDs, page URL, language, and relationships. `alumniOf` is supported by the visible Education section. Contact email, telephone, and address were removed from structured data because they were unnecessary for entity identity; visible contact information remains unchanged. No employment, rating, award, review, SearchAction, or project-level schema was added. External Schema.org validators were not run.

## F. Sitemap and Indexability

- Sitemap entries: `https://mydv.my.id/`, `https://mydv.my.id/id/`, and the existing `https://mydv.my.id/portfolio/cv_maulana_yusuf.pdf`.
- Homepage `lastmod` values use explicit Jekyll front matter and currently render as November 27, 2026. They are not derived from build time. The CV entry omits `lastmod` because no trustworthy modification date is configured.
- Both homepage entries contain `en`, `id`, and `x-default` XHTML annotations matching the page HTML. New pages can opt in with `seo_indexable: true` and override hreflang values when needed.
- `changefreq` and `priority` were removed. The checker validates XML, URL uniqueness, canonical/indexable generated routes, hreflang consistency, and date syntax.
- `robots.txt` remains `User-agent: *`, `Allow: /`, with the production sitemap URL. No `noindex` or blocking rule was added.
- The CV PDF remains at its existing download URL and in the sitemap. This is reasonable while the document is a deliberate public download linked from the portfolio. Search engines may index its contents; the owner should review the CV’s contact details and search visibility preference. The repository does not configure response headers to suppress PDF indexing.
- The English CV PDF also exists in the repository and was not changed. The current sitemap’s existing Indonesian CV URL was preserved; no new PDF entry was introduced.
- Raw `portfolio/portfolio-en.md` and `portfolio/portfolio.md` plus root development instructions/configuration are excluded from generated output. They still build the visible pages, and the CV files remain published.

## G. Social Preview

- **Location:** `assets/seo/og-cover.png`
- **Dimensions:** 1200 × 630 pixels
- **File size:** 168,180 bytes (about 164 KiB)
- **Format:** PNG; metadata declares `og:image:type`, width, height, alt text, and absolute HTTPS URL.
- **Design:** Original local composition using the portfolio’s navy/teal palette, MayudevID branding, Maulana Yusuf’s identity, Flutter & Mobile Developer positioning, and three existing project screenshots. No portrait or screenshot was fabricated.
- **Metadata:** Localized `og:title`, `og:description`, `og:locale`, `og:locale:alternate`, `og:url`, `og:image:alt`, and corresponding Twitter card metadata. `twitter:card` remains `summary_large_image`.
- **Account metadata:** The old `@mayudevID` Twitter site tag had no corroborating social profile link in the repository, so it was omitted rather than asserting an unverified account.
- The social image is not inserted into page content and is not fetched by the visible page. Existing external Bloom, Cling!, and KBBI Daring project-cover images remain unchanged and are candidates for future local hosting.

## H. Testing Results

| Test | Expected result | Actual result | Status | Notes |
|---|---|---|---|---|
| `bundle exec jekyll build --trace` | Build both language pages and static assets. | Build completed successfully. | PASS | Run after the implementation changes. |
| `python3 scripts/check_portfolio.py --site _site` | Validate generated metadata, structure, headings/landmarks, JSON-LD, sitemap, robots, assets, and existing portfolio checks. | All checks passed. | PASS | Uses generated `_site` output; no network probes. |
| `node --check assets/js/site.js` | JavaScript syntax remains valid. | No syntax errors. | PASS | JavaScript file unchanged. |
| `git diff --check` | No whitespace errors. | No output; exit code 0. | PASS |  |
| Generated-page spot checks | English and Indonesian outputs, report exclusion, and social image exist as expected. | Both HTML pages exist; report HTML is absent; built image is 168,180 bytes. | PASS | Metadata and schema are also parsed by the portfolio checker. |
| Social image inspection | Readable, branded composition using existing project imagery. | 1200 × 630 composition visually inspected. | PASS | No browser/device screenshot validation. |
| Lighthouse mobile and desktop | Preserve 100 scores across all categories. | Not run. | NOT TESTED | Lighthouse/browser automation was unavailable in the local workflow. Baseline scores are user-provided and were not remeasured. |
| External structured-data validator | Confirm external validator acceptance. | Not run. | NOT TESTED | Local JSON parsing and relationship checks pass. |
| Production/GitHub Pages deployment and Search Console | Confirm deployed metadata, indexing, and search reports. | Not run. | NOT TESTED | No deployment or private Search Console access was attempted. |
| External store/project image URLs | Confirm remote endpoints respond. | Not probed. | NOT TESTED | Existing checker intentionally avoids network requests. |

## I. Regression Assessment

| Area | Assessment |
|---|---|
| Performance | No visible image, script, font, framework, or analytics dependency was added. The 164 KiB preview image is metadata-only. No Lighthouse measurement was run. |
| Accessibility | Visible page markup and controls were not changed. The localized social image alt text is metadata for share previews. Existing project image alternatives remain in place. No new accessibility audit was run. |
| Best Practices | Search Console verification token, local assets, and existing JavaScript behavior were preserved. Production deployment was not tested. |
| SEO | Generated metadata, canonical/hreflang declarations, schema graph, robots, and sitemap passed local automated checks. Indexing/ranking results remain unverified. |
| Responsive design | CSS and visible layout were not changed. No device/browser rendering test was run. |
| Existing project content | Project case studies remain in server-generated HTML and existing content/link assertions pass. Portfolio Markdown still feeds Jekyll through `include_relative`. |
| GitHub Pages compatibility | No plugin or dependency was added. Build passed with the repository’s locked Jekyll 3.10.0 dependencies. GitHub Actions itself was not run remotely. |
| Multilingual navigation | Existing `/` and `/id/` language switch is preserved and validated along with reciprocal hreflang. |

## J. Remaining Recommendations

- After deployment, inspect both canonical URLs and submit the sitemap through Search Console; review real indexing and performance evidence before drawing conclusions.
- Run mobile and desktop Lighthouse audits after deployment to confirm the stated baseline in a comparable environment.
- Consider hosting the Bloom, Cling!, and KBBI Daring cover images locally if endpoint reliability or external requests become a concern.
- In Phase 2, evaluate dedicated project pages and only then consider project-level `SoftwareApplication`, `CreativeWork`, and breadcrumb structured data.
- Review the public CV’s personal details and whether PDF search indexing remains desired. No restriction was made in Phase 1.

## K. Changed Files

| File | Change |
|---|---|
| `_config.yml` | Set the default author/language and exclude report, raw content sources, scripts, and internal development files from generated output. |
| `_data/seo.yml` | Central localized metadata, identity, social image, hreflang, and structured-data values. |
| `_includes/seo.html` | Reusable localized metadata and JSON-LD rendering with per-page override support. |
| `_layouts/default.html` | Use configured HTML language and centralized SEO include; preserve Search Console verification and the existing page shell. |
| `index.html` | Mark English homepage indexable and record its explicit content-modified date. |
| `id.html` | Mark Indonesian homepage indexable and record its explicit content-modified date. |
| `sitemap.xml` | Generate canonical pages, explicit lastmod values, multilingual annotations, and preserve the existing CV entry. |
| `assets/seo/og-cover.png` | New local 1200 × 630 portfolio social-sharing image. |
| `portfolio/portfolio-en.md`, `portfolio/portfolio.md` | Clarified English project-cover alternatives and localized the corresponding Indonesian alternatives; raw output remains excluded. |
| `scripts/check_portfolio.py` | Validate generated SEO metadata, structured data, image, sitemap, robots, and output exclusions alongside existing content checks. |
| `.github/workflows/portfolio-quality.yml` | Clarify that the existing generated-site validation step covers SEO. |
| `SEO_PHASE1_IMPLEMENTATION_REPORT.md` | This implementation and validation report; excluded from public output. |

No project-level pages or schemas, analytics, CSS/JavaScript changes, commits to production, or remote deployments were made as part of the implementation.
