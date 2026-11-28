# SEO Phase 4 Implementation Report

## A. Executive Summary

Phase 4 adds three monitoring layers: the existing generated-site checks are extended to prevent publishing monitoring artifacts; pinned Lighthouse CI configurations audit a representative route sample on mobile and desktop in GitHub Actions; and a standard-library production checker validates deployed routes, metadata, schema, sitemap, robots, local resources, and outbound links. Owner instructions are in `SEO_MONITORING_GUIDE.md`.

**Readiness:** local site validation passes. The live production check completed with 22/22 expected HTML pages and 23 sitemap URLs passing, with one warning because LinkedIn returned HTTP 999 (bot protection). Lighthouse configurations and thresholds are ready, but this machine has no Chrome installation, so no Lighthouse score or measured Lighthouse baseline is claimed. The first CI Lighthouse run must establish the actual runner baseline.

No public website code, analytics, or tracking was added. All six existing bilingual articles remain drafts; the local generated site still has 22 canonical HTML pages, no article/listing routes, and 23 sitemap entries including the existing CV PDF.

## B. Initial Repository Findings

- Starting commit: `76406e18bd29ab1d0a745e8ded909ff0a473dfb6` (`feat(seo): add bilingual engineering insights architecture`, 2026-11-27). The worktree was clean before changes.
- Existing implementation used Jekyll 3.10 and GitHub Pages. Shared metadata/schema are rendered by `_includes/seo.html`; home/project routes use explicit static pages and the shared project catalog.
- The existing `scripts/check_portfolio.py` already validates localized metadata, canonical/hreflang declarations, schema relationships, generated route inventory, sitemap contents/alternates, robots, draft isolation, local links, assets, and publication-aware navigation. `scripts/test_portfolio_validator.py` already had eight mutation tests. These utilities were retained and reused.
- `portfolio-quality.yml` already ran production-mode Jekyll, the generated-site validator, its mutation tests, and JavaScript syntax validation on PRs and `main` pushes.
- Gaps were deployed-site verification, Lighthouse coverage, measured current Lighthouse baseline, and owner instructions for Search Console and field Core Web Vitals.
- `_data/insights.json` has three bilingual article pairs, all with `status: draft`; `editorial/drafts/` is excluded by Jekyll. The Phase 3 validator ensures no article routes or empty Insights listing pages are generated. Draft exclusion does not make committed content private in this public repository.
- Production crawl policy already allows public pages and declares the production sitemap. The Search Console verification metadata is preserved. No existing external URLs were changed.
- No existing Lighthouse/npm development dependency or production monitor was present. Ruby uses the committed Gemfile lock; npm now uses an exact LHCI version and committed lockfile.

The repository-required code-review-graph service was unavailable in this session. Source and existing validator coverage were inspected directly instead.

## C. Monitoring Architecture

1. **Local/static validation:** Jekyll production build and the existing offline validator remain the source-of-truth for generated public inventory and site behavior. The validator now also rejects leaked monitoring configuration, packages, reports, and generated reports.
2. **Lighthouse CI:** official `@lhci/cli` 0.15.1 with locked Lighthouse 12.6.1, running against locally generated `_site` through a temporary Python HTTP server. Both desktop and mobile use the same `lighthouse-pages.json` inventory, separate presets, and three runs per page.
3. **Production SEO:** `scripts/check_production_seo.py` imports the existing checker’s project route inventory, validates 22 expected HTTPS HTML routes independently of the deployed sitemap, then checks the sitemap against those routes plus the CV PDF. Requests use 12-second timeouts, two bounded exponential-backoff retries for 429/5xx/network timeout, a 4 MB body limit, and a cap of 250 unique internal destinations and 30 deduplicated external URLs.
4. **Reporting:** Lighthouse JSON/HTML diagnostics and production JSON/Markdown reports are uploaded as 14-day Actions artifacts. Production and Lighthouse workflows append concise summaries to the Actions job summary. Reports are not committed.

No persistent LHCI server, database, paid tool, third-party dashboard, production script, or additional public network request was introduced.

## D. Lighthouse Configuration

- Tool: `@lhci/cli` **0.15.1**, exact version in `package.json` and `package-lock.json`; resolved Lighthouse **12.6.1**. Local Node was **26.13.1**, npm **11.20.0**. CI is configured to use Node **22** and `ubuntu-latest` Chrome; CI browser version is logged at runtime.
- Audit pages: `/`, `/id/`, `/projects/holy-smart/`, `/id/projects/ar-rauda/`, `/projects/emcare/`, `/id/projects/ktadbrnr/`, `/projects/cling/`.
- Mobile and desktop are separate LHCI configurations with actual `mobile` and `desktop` presets; each route/profile is run three times. Every assertion explicitly uses LHCI's supported `median` aggregation. LHCI is configured for filesystem artifacts and no temporary public upload service.
- Blocking category minimums: Performance 90, Accessibility 95, Best Practices 95, SEO 100. Preferred category target remains 100.
- Blocking audits include text contrast, document title/language, image alternative text, meta description, canonical, crawlable anchors, and page crawlability.
- Initial lab budgets: LCP ≤ 2,500 ms, CLS ≤ 0.10, TBT ≤ 300 ms, FCP ≤ 1,800 ms, Speed Index ≤ 3,400 ms. LCP/CLS use the referenced web.dev good thresholds. TBT/FCP/Speed Index budgets are conservative initial lab limits for this lightweight static site; they must be reviewed against first reproducible CI measurements, without silently lowering them to conceal a regression.
- **Measured baseline: NOT ESTABLISHED.** The historical 100/100/100/100 is not treated as current measurement. Both local LHCI commands loaded their configurations but stopped at the health check because Chrome is not installed. No GitHub Actions run was available in this implementation session.
- Lighthouse’s repeated-run aggregation is used to reduce variability. Exact CI baseline, actual scores, browser version, and category/metric result table remain to be filled from the first completed CI workflow run; the workflow summary and artifact preserve those results.

## E. Production Monitoring

- Expected inventory is two localized homepages plus English/Indonesian routes for each project in the existing validator project catalog. It is not inferred from production sitemap entries. The sitemap must exactly match this inventory plus `https://mydv.my.id/portfolio/cv_maulana_yusuf.pdf`.
- Every expected page is checked for status, HTTPS, final destination/redirect count, HTML content type, exactly one title and canonical, description, language, reciprocal hreflang/x-default, Open Graph URL/image, one meaningful H1, robots meta and `X-Robots-Tag`, expected JSON-LD entity types/relationships, and accidental article markup.
- Sitemap checks cover status/content type, valid XML, duplicate and unexpected/missing URLs, HTTPS inventory, localized alternate mappings, unpublished article leakage, and parseable `lastmod` values. The CV sitemap resource and PDF content type are checked.
- Robots checks parse user-agent groups, sitemap declaration, allow/disallow paths, wildcard patterns, and applicable longest-match rules for public routes and core assets. The production robots policy itself was not modified.
- Local links and required assets are deduplicated, checked for availability and redirect behavior, and same-site HTML links are checked against expected routes to catch fallback/soft-404 destinations. Known page fragments are checked against target IDs.
- External URLs are deduplicated, query strings retained, and probing is limited to 30 destinations. 401/403/999, rate limit, transient server failure, and timeouts are warning classifications; confirmed 4xx destinations are also reported as warnings and never automatically removed.
- Retry behavior was exercised with mocks. Permanent 404 does not retry; rate limits retry; timeout retries are bounded. Permanent expected-route failures fail the workflow; temporary network failures remain visible as blocked/network failures.

## F. Search Console Strategy

`SEO_MONITORING_GUIDE.md` documents manual Search Console checks for Search Performance (clicks, impressions, CTR, position, queries, landing pages, country, device), Page Indexing/canonical classifications, sitemap processing, Core Web Vitals, and representative URL Inspection. It distinguishes live URL testing from Google's indexed copy.

No Search Console API integration was implemented because authenticated credentials and authorization were not provided. No search results are scraped, and no clicks, impressions, rankings, indexed-page counts, or organic traffic are fabricated. No Indexing API or Analytics was added.

## G. CI/CD Configuration

- Existing **Portfolio Quality** workflow is preserved and remains triggered by PRs, `main` pushes, and manual dispatch.
- New **Lighthouse Quality** workflow runs for PRs, `main` pushes, and manual dispatch. It rebuilds/validates local output, records tool/browser versions, runs mobile and desktop sample audits, summarizes results, and retains diagnostics for 14 days.
- New **Production SEO Monitor** workflow runs Saturday 20:00 UTC (about Sunday 03:00 WIB) and supports manual dispatch. GitHub scheduled runs are best-effort and may be delayed. It builds and validates the expected route inventory before contacting production.
- All workflows use `contents: read`; no secret, production write permission, deployment, issue creation, or repository mutation is configured. Lighthouse and production workflows have concurrency groups, cancel obsolete runs, and set 40- and 15-minute job timeouts respectively.
- Workflow YAML parsed successfully with Ruby Psych. No GitHub Actions hosted execution occurred, so runtime workflow behavior remains to be confirmed by GitHub.

## H. Testing Results

| Check | Result | Evidence / limitation |
|---|---|---|
| Production Jekyll build | PASS | `JEKYLL_ENV=production bundle exec jekyll build --trace` completed |
| Existing generated-site validator | PASS | `python3 scripts/check_portfolio.py --site _site` |
| Existing mutation tests | PASS | 8 tests passed |
| Production monitor deterministic tests | PASS | 7 tests cover route inventory, 404, 429 retry/recovery, 500 retry, bounded timeout retries, bot-protection classification, and long redirect-chain counting |
| JavaScript syntax | PASS | `node --check assets/js/site.js` |
| LHCI dependency install | PASS | `npm ci --ignore-scripts --offline` from committed lock; npm reported 0 vulnerabilities |
| Mobile LHCI | NOT TESTED | Configuration and output directory validated; health check stopped because Chrome is unavailable locally |
| Desktop LHCI | NOT TESTED | Same local Chrome limitation; no scores claimed |
| Production monitor | WARNING | Actual deployed run at 2026-11-27 11:28 UTC: 22/22 expected pages passed; sitemap contained 23 expected URLs; robots, localized metadata, schema, routes, resources, and internal links passed. LinkedIn returned HTTP 999 and was classified as bot-protected warning. No other external warning occurred. |
| Workflow syntax | PASS | All three workflow YAML files parsed |
| Hosted Actions workflow execution | NOT TESTED | No workflow was dispatched from this environment |
| Google Search Console/field data | NOT TESTED | No authenticated Search Console data was accessed; field Core Web Vitals not measured |
| Whitespace | PASS | `git diff --check` |

## I. Regression Assessment

- **Performance/accessibility/best practices/SEO:** no scores measured locally; thresholds and critical assertions are configured for CI. The site itself was not changed to accommodate monitoring.
- **Public payload:** monitoring dependencies, reports, guide, and implementation report are excluded by Jekyll; the generated-site validator passed. No runtime script or tracking request was introduced.
- **Navigation and project pages:** existing static project routes and visible behavior are unchanged; the existing route/link/schema validation passed.
- **Draft isolation:** all entries remain draft; the local validator passed and confirms no article route or listing page is generated. Draft files remain publicly readable in the Git repository.
- **Sitemap:** local validation passed the existing inventory; production run independently returned 23 expected URLs including the CV entry.
- **GitHub Pages compatibility:** the monitoring stack is outside Jekyll runtime. The website remains static Jekyll 3.10 output.
- **Monitoring reliability:** request and failure handling is bounded and deterministic failure classes are unit-tested. Production run completed without page/sitemap/robots/internal-link failures; LinkedIn automation is blocked.

## J. Cost and Maintenance Assessment

Production monitoring runs weekly and issues bounded requests across 22 expected pages, their deduplicated same-origin resources/links, and up to 30 outbound URLs. Lighthouse audits seven routes, two device configurations, and three runs per route/profile on PRs and `main` pushes. This is a finite local-build workload without a paid service or persistent server; actual GitHub Actions minutes depend on runner duration and were not measured here.

The only new tool dependency is pinned Lighthouse CI and its committed npm lockfile. Review the lockfile during routine dependency updates. Review production warnings weekly, Search Console monthly, and the first completed CI Lighthouse baseline before revising provisional metric budgets.

## K. Changed Files

**Created:**

- `.github/workflows/lighthouse-quality.yml`
- `.github/workflows/seo-production-monitor.yml`
- `SEO_MONITORING_GUIDE.md`
- `SEO_PHASE4_IMPLEMENTATION_REPORT.md`
- `lighthouse-pages.json`
- `lighthouserc.mobile.cjs`
- `lighthouserc.desktop.cjs`
- `lighthouserc.shared.cjs`
- `package.json`
- `package-lock.json`
- `scripts/check_production_seo.py`
- `scripts/test_production_seo.py`

**Modified:**

- `.gitignore`
- `_config.yml`
- `scripts/check_portfolio.py`

**Removed:** none.

Generated `_site`, Lighthouse output, local report files, and caches are not committed.

## L. Remaining Limitations

- Current Lighthouse scores and a measured baseline require the first successful GitHub Linux run with Chrome; local audit commands could not launch because no Chrome executable is installed.
- GitHub Actions configuration was syntax-checked but not executed in hosted Actions.
- The production checker observed current external behavior only once. LinkedIn's HTTP 999 is bot protection, not proof of a broken profile. External services can change after this check.
- No Search Console account, actual indexing evidence, CrUX field data, or real-user INP was available. Report field metrics as **INSUFFICIENT FIELD DATA** unless an authorized source provides them.
- Passing technical checks means pages are technically eligible to be crawled/indexed; it does not confirm Google indexed them or guarantee ranking or rich-result eligibility.

## M. Final SEO Roadmap Status

- **Phase 1 — Technical SEO:** retained; current generated-site validation passes.
- **Phase 2 — Project-Level SEO:** retained; 20 localized project routes and current production checks pass.
- **Phase 3 — Content infrastructure:** retained; all article publication remains intentionally skipped and frozen in draft state.
- **Phase 4 — Monitoring and Regression Prevention:** implemented. Static checks and actual production monitoring pass with one bot-protection warning. Lighthouse CI is configured; measured scores and baseline await hosted Chrome execution.

Technical SEO improvements do not guarantee higher rankings.
