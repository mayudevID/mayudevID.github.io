# SEO Phase 2 Implementation Report

Date: 2026-11-27  
Starting commit: `3a6303f3fe9a20ed118d1cb303823b8cae1c61f2`

## A. Executive Summary

Phase 2 adds 20 static, independently addressable project pages: ten English routes under `/projects/` and ten Indonesian routes under `/id/projects/`. Both localized homepages remain intact. All 22 HTML content pages have self canonicals, localized metadata, reciprocal project-level hreflang, crawlable links, and page-appropriate JSON-LD. The existing CV PDF remains the 23rd sitemap entry.

Project facts, summaries, roles when supported, features, technologies, screenshots, links, localized SEO descriptions, and related-project relationships now live in `_data/projects.yml`. Reusable Liquid includes use that catalog for the homepage case study accordions, personal project cards, standalone case study pages, and project metadata. Existing accordion IDs and order remain compatible.

The local Jekyll build, expanded generated-site validator, JavaScript syntax check, and whitespace check pass. Browser/device, Lighthouse, external schema/social preview, and production deployment checks were not run. Their results are not inferred from the local checks.

## B. Initial Repository Findings

- Starting commit was `3a6303f3fe9a20ed118d1cb303823b8cae1c61f2`; the worktree was clean before implementation.
- Phase 1 uses `_data/seo.yml` for shared and localized homepage metadata, `_includes/seo.html` for metadata and JSON-LD, and page front matter for canonical and hreflang overrides.
- `_layouts/default.html` owns site navigation and the common document shell. It already served both localized homepages and retained the Search Console verification tag.
- `portfolio/portfolio-en.md` and `portfolio/portfolio.md` supplied localized homepage sections. The shared portfolio include split them at section comments and used positional segments for case studies and personal cards. New project pages do not use that positional parsing.
- Project screenshots were already stored locally for Holy Smart, Holy World, DTG SOMS, Ar-Rauda, GOT Agency, KTADBRNR, and EMCare. GOT Agency, KTADBRNR, and EMCare also had screenshot data files.
- Bloom, Cling!, and KBBI Daring originally referenced covers through GitHub Raw URLs. Identical source files were present in the corresponding checked-out project repositories and are now copied into this site.
- `sitemap.xml` already discovers pages marked `seo_indexable`, emits canonical URLs and page hreflang, and preserves the CV PDF URL. `robots.txt` already allows crawling and points to the production sitemap.
- The Phase 1 report records local SEO validation as passing, but Lighthouse, external structured-data validation, and production/Search Console results were not confirmed. Phase 2 does not claim those results.

## C. Architecture and Content Management

`_data/projects.yml` is the shared catalog. Each project record has one stable identifier and slug, factual project details, status and classification, optional contribution details, technology and platform lists, screenshot sources, outbound links, related project IDs, and independently written English and Indonesian title, description, and summary values.

Twenty small Jekyll pages provide explicit static route and language front matter. `_layouts/project.html` reuses the existing default layout. `_includes/project-content.html` renders the catalog entry both as a standalone case study and as the content of a homepage accordion. `_includes/project-card.html` renders personal project cards. No custom plugin, collection plugin, runtime route, or JavaScript routing was introduced.

To add a project, add one catalog record, two thin route files with reciprocal language paths, and its route/link expectations in `scripts/check_portfolio.py`. Add only verified content and available assets. This keeps the production build compatible with the repository's Jekyll 3.10 and GitHub Pages approach while keeping routes explicit for review.

The existing localized Markdown remains the source for About, Experience, Education, Skills, Certifications, and Contact. Its project-only sections were removed after those project facts moved into the catalog, eliminating a second maintained source for the rendered project content.

## D. Project Route Inventory

All listed pages are published, self-canonical, paired with a reciprocal translation, and included in the sitemap. Project pages do not declare `lastmod` because there is no reliable per-project modification date in the source data.

| Project | English URL | Indonesian URL | Status/classification | Canonical | Hreflang | Sitemap | Publication |
|---|---|---|---|---|---|---|---|
| Holy Smart | `/projects/holy-smart/` | `/id/projects/holy-smart/` | Professional | PASS | PASS | PASS | Published |
| Holy World | `/projects/holy-world/` | `/id/projects/holy-world/` | Professional | PASS | PASS | PASS | Published |
| DTG SOMS | `/projects/dtg-soms/` | `/id/projects/dtg-soms/` | Professional | PASS | PASS | PASS | Published |
| Ar-Rauda | `/projects/ar-rauda/` | `/id/projects/ar-rauda/` | Professional | PASS | PASS | PASS | Published |
| GOT Agency | `/projects/got-agency/` | `/id/projects/got-agency/` | Professional | PASS | PASS | PASS | Published |
| KTADBRNR | `/projects/ktadbrnr/` | `/id/projects/ktadbrnr/` | Archived; operations discontinued February 2026 | PASS | PASS | PASS | Published as historical documentation |
| EMCare | `/projects/emcare/` | `/id/projects/emcare/` | Suitmedia internship contribution, February–June 2023 | PASS | PASS | PASS | Published |
| Bloom | `/projects/bloom/` | `/id/projects/bloom/` | Personal project | PASS | PASS | PASS | Published |
| Cling! | `/projects/cling/` | `/id/projects/cling/` | Personal project | PASS | PASS | PASS | Published |
| KBBI Daring | `/projects/kbbi-daring/` | `/id/projects/kbbi-daring/` | Personal project | PASS | PASS | PASS | Published |

No project was excluded for insufficient source content. No `/projects/` or `/id/projects/` directory listing page was added.

## E. Homepage Compatibility

- Featured Projects, Project Case Studies, Personal Projects, Professional Experience, Technical Skills, Education and Certifications, and Contact remain present.
- The seven professional accordion IDs remain `case-study-{slug}-{lang}` for Holy Smart, Holy World, DTG SOMS, Ar-Rauda, GOT Agency, KTADBRNR, and EMCare. Native `<details>` behavior and the existing progressive-enhancement JavaScript remain in place.
- The featured project order and its existing card links remain unchanged. Personal project cards retain their project order and now use the shared catalog.
- Every project has a standard HTML link from its matching homepage. Professional project links are within their existing accordion content; personal project links are on their cards.
- The homepage section links still target local fragments. From project pages, the brand and Projects, Experience, Skills, and Contact navigation links point to the correct localized homepage section.
- English/Indonesian links on project pages switch to the paired project route. Homepage switching remains `/` and `/id/`.
- Breadcrumb navigation visibly links to the real localized homepage and marks the current project. No nonexistent projects index is linked.
- The source contains no added click-only navigation dependency. Browser interaction itself remains untested.

## F. Project Metadata

Project title and description overrides are stored under each project's `en` and `id` keys in `_data/projects.yml`. The shared SEO include selects those values based on the page language. Canonicals use the explicit page route; project alternates use the paired project routes, with the English route as `x-default`.

Examples:

- EN Holy Smart title: `Holy Smart — Employee Learning Platform | MayudevID`
- ID Holy Smart title: `Holy Smart — Platform Pembelajaran Karyawan | MayudevID`
- EN EMCare description: `Internship case study of a Flutter contribution to EMCare, EMC Healthcare's patient app, completed with Suitmedia's development team.`
- ID EMCare description: `Studi kontribusi magang pada aplikasi pasien EMCare berbasis Flutter, dikerjakan bersama tim pengembangan Suitmedia.`

Every project has a locally hosted social image with localized descriptive alternative text and a matching MIME type. Seven project images reuse existing local screenshots. Bloom, Cling!, and KBBI Daring use local copies of their original project covers. Project-image dimensions are omitted from Open Graph metadata because those source images have not all been measured as intended share-card dimensions. The existing Phase 1 1200 × 630 PNG and its declared dimensions remain in use for the localized homepages.

Asset provenance for the copied covers:

| Local asset | Identical source file |
|---|---|
| `assets/projects/bloom/cover.png` | `/Users/maul089/Work/personal_project/bloom/assets/images/cover.png` |
| `assets/projects/cling/cover.jpg` | `/Users/maul089/Work/personal_project/cling/assets/cover.jpg` |
| `assets/projects/kbbi_daring/cover.png` | `/Users/maul089/Work/personal_project/kbbi_daring_app/cover.png` |

The files were visually checked and byte-compared to their source files. They were not recompressed. Their sizes are approximately 436 KB, 632 KB, and 872 KB respectively.

## G. Structured Data Architecture

The common `Person` and `WebSite` IDs remain `https://mydv.my.id/#person` and `https://mydv.my.id/#website`. Homepage pages continue to use `ProfilePage`. A project page emits `WebPage`, `CreativeWork`, and `BreadcrumbList` instead, with IDs based on its canonical URL. `CreativeWork.author` points to the portfolio owner as author of the case study; it does not assert ownership of the underlying employer or client application.

The breadcrumb schema has two entries matching the visible `Home/Beranda > project` navigation. Dynamic JSON values continue to use Liquid `jsonify`. `SoftwareApplication` was omitted for all projects: public app links exist for several, but verified publisher, licensing/ownership, and application availability facts are not consistently established. The case-study `CreativeWork` is Schema.org descriptive markup; it is not a claim of Google rich-result eligibility. No ratings, prices, offers, or review data were created.

The generated-site checker parsed every JSON-LD block, checked page classification and shared identities, verified canonical/language relationships, and matched breadcrumb items to generated routes. This is local syntax/relationship validation, not an external Schema Markup Validator or Google Rich Results Test result.

## H. Sitemap and Indexability

- Generated canonical HTML pages: 22 (two homepages and 20 project pages).
- Sitemap entries: 23 (the 22 HTML pages and the existing Indonesian CV PDF URL).
- Project entries use the same three hreflang annotations as their HTML pages. The sitemap has no duplicate URLs and does not add a lastmod to project pages.
- Homepage `lastmod` behavior remains unchanged. The CV remains without `lastmod` because no reliable modification date is configured.
- The report, raw portfolio Markdown, scripts, and development files are excluded from the generated site. No new directory listing or utility page was published.
- `robots.txt` and Google Search Console verification metadata were preserved.

## I. Content Accuracy Assessment

Project summaries, descriptions, features, technologies, links, and screenshots were migrated from the existing bilingual portfolio and existing screenshot data. Existing classifications were retained. No unsupported numerical performance or business outcomes were added.

KTADBRNR is visibly labeled archived, states that operations ended in February 2026, describes its case study as historical, and retains the original Google Play listing only as a historical source reference. No current-download claim or replacement store link was added. Its sourced historical 100,000+ download figure retains the source's November 26, 2026 date.

EMCare is labeled as a Suitmedia internship contribution from February–June 2023. Its description says the work was part of Suitmedia's team; the page does not claim sole ownership. The public Suitmedia case study remains linked, and the screenshot note explains that current public listing images may differ from the 2023 version.

For Holy Smart, Holy World, DTG SOMS, and Ar-Rauda, the source portfolio did not state a precise personal role. The standalone content therefore describes the projects without adding a role claim. No additional owner input was needed to publish the verified scope. Further project dates or responsibilities can be added if the owner supplies verified details.

## J. Testing Results

| Test | Expected result | Actual result | Status | Notes |
|---|---|---|---|---|
| `bundle exec jekyll build --trace` | Jekyll generates static pages without Liquid or YAML errors | Build completed successfully | PASS | Jekyll 3.10 from the locked bundle |
| `python3 scripts/check_portfolio.py --site _site` | Validate both homepages, 20 project pages, SEO tags, JSON-LD, local links/assets, existing content, robots, and sitemap | All generated-site checks passed | PASS | Offline/deterministic; outbound URLs are preserved, not probed |
| `python3 scripts/test_portfolio_validator.py --site _site` | Prove detection of malformed canonical, broken language switch, and incorrect JSON-LD type | 3 mutation tests passed | PASS | Uses temporary generated HTML and a symlink to the built assets directory |
| Project route inventory | 10 EN + 10 ID routes, no listing routes | 20 project `index.html` pages; no project listing pages | PASS | Generated output checked by the validator |
| Sitemap inventory | 23 unique entries: 22 canonical HTML pages plus the CV | 23 entries | PASS | Sitemap XML parsed; project hreflang checked against HTML |
| `node --check assets/js/site.js` | Existing navigation/case-study enhancement remains syntactically valid | No syntax errors | PASS | This does not exercise browser interactions |
| `git diff --check` | No whitespace errors | No errors | PASS | Run after the final changes |
| Copied-cover provenance | Local covers match verified source project files | All three `cmp` checks passed; file signatures/dimensions identified | PASS | Visual content was inspected; byte equality confirmed |
| Browser, keyboard, and responsive interaction testing | Check accordions, language switch, links, mobile layout, and galleries | Not run | NOT TESTED | No browser automation interface was available in the session |
| Lighthouse mobile/desktop | Compare homepages and representative project pages against the supplied baseline | Not run | NOT TESTED | No Lighthouse run; no score is claimed |
| External structured-data/social preview validation | Validate representative production URLs externally | Not run | NOT TESTED | Local JSON-LD and metadata checks passed only |
| GitHub Pages production deployment/Search Console | Confirm deployed output and indexing signals | Not run | NOT TESTED | No deployment or private Search Console access was attempted |

## K. Regression Assessment

- **Performance:** No framework, plugin, third-party script, font, analytics request, or JavaScript routing was added. Each project page references only its own screenshots; the top cover is eager and gallery images are lazy. Lighthouse was not run, so parity with the historical score is unknown.
- **Accessibility:** Shared focus indicators remain, including the required `--faint: #617187`. Project pages have one H1, ordered headings, landmarks, localized language attributes, visible breadcrumbs, descriptive image alts, and keyboard-focusable screenshot regions. Automated markup checks pass; contrast and interactions were not remeasured in a browser.
- **Best Practices:** Existing site shell and Search Console verification remain. No external scripts or unverified ratings/offers were added. Lighthouse was not run.
- **SEO:** All generated project metadata, canonical/hreflang pairs, page entities, route links, robots behavior, and sitemap entries passed local checks. Production indexing, search ranking, and rich-result eligibility are unverified.
- **Homepage/content:** Sections, featured order, accordion behavior hooks, project deep-link IDs, CV links, project store/repository links, and project screenshots remain represented. Generated output checks pass; accordion interaction was not browser-tested.
- **Responsive design:** New styles use existing tokens and responsive layouts. Mobile and desktop visual rendering was not inspected in a browser.
- **GitHub Pages:** Uses static pages, Liquid, YAML/JSON data, and Jekyll 3.10 only; no custom plugin was added. Local build passes; remote GitHub Pages deployment was not run.
- **Asset reliability:** Project images now resolve locally, including the three formerly external cover files. Store/repository URLs remain outbound and were not network-probed.
- **Multilingual navigation:** Both pages in every pair have reciprocal annotations and explicit language-switch targets; project-to-home section links are absolute and localized. Automated generated HTML checks pass; browser interaction was not run.

## L. Changed Files

Created:

- `_data/projects.yml` — bilingual project catalog and metadata.
- `_includes/project-card.html` — reusable personal project card.
- `_includes/project-content.html` — reusable project detail rendering for page and homepage contexts.
- `_layouts/project.html` — project page layout using the shared site shell.
- `projects/{holy-smart,holy-world,dtg-soms,ar-rauda,got-agency,ktadbrnr,emcare,bloom,cling,kbbi-daring}/index.html` — ten English routes.
- `id/projects/{holy-smart,holy-world,dtg-soms,ar-rauda,got-agency,ktadbrnr,emcare,bloom,cling,kbbi-daring}/index.html` — ten Indonesian routes.
- `assets/projects/bloom/cover.png`, `assets/projects/cling/cover.jpg`, and `assets/projects/kbbi_daring/cover.png` — verified local copies of existing project covers.
- `SEO_PHASE2_IMPLEMENTATION_REPORT.md` — this report; excluded from Jekyll output.

Modified:

- `_config.yml` — exclude the Phase 2 report from generated output.
- `_includes/portfolio-page.html` — render project summaries, accordion content, and personal cards from the shared catalog while retaining existing IDs and section order.
- `_includes/seo.html` — project metadata, social image selection, localized alternates, and page-specific JSON-LD.
- `_layouts/default.html` — nested-route-safe navigation and project-context language switching.
- `assets/css/site.css` — project page styles and keyboard gallery focus styling.
- `portfolio/portfolio-en.md` and `portfolio/portfolio.md` — remove project-only facts now owned by the shared catalog while preserving the existing section markers needed by the rest of the portfolio renderer.
- `scripts/check_portfolio.py` — validate the 20 project routes, metadata, structured data, links, assets, homepage reachability, and sitemap count alongside Phase 1 checks.
- `scripts/test_portfolio_validator.py` — exercise malformed canonical, localized link, and structured-data fixtures against the project-page validator.
- `.github/workflows/portfolio-quality.yml` — run the validator regression checks after the generated-site validation.

Unmodified by design: `sitemap.xml` and `robots.txt`. The existing sitemap template already includes `seo_indexable` pages, and the existing robots policy remains valid. CI already ran the generated-site checker and now also runs the three mutation checks after the Jekyll build.

No generated `_site` output, temporary files, dependencies, or unrelated files are included.

## M. Remaining Risks and Future Recommendations

- Run Lighthouse and browser checks after deployment for both homepages and representative project pages, including the accordion/deep-link behavior, mobile layout, keyboard navigation, and language switching.
- Validate deployed representative pages with an external Schema Markup Validator and social preview debuggers. Do not infer indexing or ranking improvements from this implementation.
- Submit the updated sitemap through Search Console after the normal production release and review actual crawl/index status.
- Check that the outbound application store and project repository URLs remain available; the local checker intentionally does not request those external services.
- Project-level professional responsibilities are intentionally omitted for the four entries where the source did not state a personal role. Add only owner-verified contributions and dates in a future content update.
- No Phase 3 features were added.
