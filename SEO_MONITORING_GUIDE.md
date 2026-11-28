# SEO Monitoring Guide

This guide describes the local and production checks for the static MayudevID portfolio. Monitoring is CI-only; the public pages do not load analytics, monitoring JavaScript, or third-party runtime services.

## Architecture and workflows

- **Portfolio Quality** (`.github/workflows/portfolio-quality.yml`) builds the production Jekyll site on pull requests, `main` pushes, and manual runs. It checks generated metadata, page inventory, schema, local links/assets, sitemap/robots, article draft isolation, validator mutations, and JavaScript syntax.
- **Lighthouse Quality** (`.github/workflows/lighthouse-quality.yml`) runs after the same triggers against local `_site` output, never against production deployment. Mobile and desktop use separate Lighthouse CI configurations and three measurements per representative page. Lighthouse reports are available as a GitHub Actions artifact for 14 days.
- **Production SEO Monitor** (`.github/workflows/seo-production-monitor.yml`) checks `https://mydv.my.id/` weekly on Saturday at 20:00 UTC (Sunday about 03:00 WIB), and supports `workflow_dispatch`. GitHub may delay or skip scheduled runs. Reports are artifacts retained for 14 days and are also written to the job summary.

All workflows use `contents: read`, have bounded job timeouts, and do not deploy, write repository content, create issues, or use secrets. The production monitor makes bounded GET requests with a 12-second timeout, two retries for transient failures, exponential backoff, a 4 MB response limit, and at most 30 deduplicated external link probes. External failures are warnings because bot controls and temporary errors are not reliable evidence of a dead destination.

## Local checks

Install Ruby dependencies using the committed `Gemfile.lock`, then run:

```sh
JEKYLL_ENV=production bundle exec jekyll build --trace
python3 scripts/check_portfolio.py --site _site
python3 scripts/test_portfolio_validator.py --site _site
python3 scripts/test_production_seo.py
node --check assets/js/site.js
```

Lighthouse CI is pinned in `package-lock.json` and is development-only:

```sh
npm ci
npm run lighthouse:mobile
npm run lighthouse:desktop
```

The local Lighthouse commands require a compatible Chrome/Chromium executable. CI runs on `ubuntu-latest`, records Node, npm, LHCI, and Chrome versions, starts a temporary HTTP server for `_site`, and LHCI stops it after each run. Reports go to ignored `.lighthouseci/`. A failed audit still uploads available diagnostics.

`lighthouse-pages.json` is the single representative audit inventory. It includes `/en/`, `/id/`, and English/Indonesian samples across enterprise, feature-rich mobile, internship, archived, and personal project categories. Update it when a representative route is removed or a better sample is needed. Full public route coverage belongs to the generated-site and production inventory checks.

## Quality policy

Lighthouse thresholds are provisional until a reproducible Linux CI baseline is available. Each route/device is measured three times; Lighthouse CI aggregates repeated runs using its supported median behavior. Current blocking aggregate minimums are Performance 90, Accessibility 95, Best Practices 95, and SEO 100. The preferred category target remains 100. Performance is allowed measurement variance; it does not silently relax SEO or accessibility assertions.

Critical audit assertions require a passing score for text contrast, document title/language, image alternatives, meta description, canonical, crawlable anchors, and crawlability. Initial lab budgets are LCP ≤ 2.5 s, CLS ≤ 0.10, TBT ≤ 300 ms, FCP ≤ 1.8 s, and Speed Index ≤ 3.4 s. These provisional lab budgets use common good-performance targets and conservative web.dev guidance; adjust only after comparing repeated measurements on the same CI runner class and reviewing the specific failing audits. TBT is a lab metric and is not INP.

Do not automatically replace the baseline or lower a threshold after a failure. Save the artifact, compare equivalent routes and device configuration, determine whether the change is a real regression or runner noise, and record the evidence and reason in a reviewed change. Historical Lighthouse 100 scores are context only; this repository has not yet established a current CI baseline.

## Reading reports and outcomes

GitHub Actions job summaries show the run context and concise measurements. Download the run's artifact for Lighthouse JSON/HTML diagnostics or the production monitor's Markdown and JSON. The production report distinguishes page checks, sitemap/robots checks, and external warnings. A report failure can come from availability, metadata, indexability, schema, routes, or internal links. `429`, `5xx`, and timeout conditions are retried and remain visible; an unresolved expected page is a failure. External destination failures are warnings and are not automatically removed or rewritten.

The expected production page inventory is derived from the same `PROJECTS` catalog used by `scripts/check_portfolio.py`, plus the two homepages. The sitemap is checked against this independent source and the preserved CV PDF URL. Add/remove a project in the existing project catalog and update the validator's project inventory as required; do not update a fixed sitemap count. Sitemap URLs and localized alternate mappings are both validated. The monitor checks deployed page routes, metadata, indexability headers/directives, JSON-LD, sitemap, robots, local resources, and internal links. External checks are capped and conservative.

## Laboratory results and field data

Lighthouse runs measure a controlled lab simulation for regression detection. They do not represent visitors' Core Web Vitals. Production field results come from real Chrome user experiences through CrUX/Search Console when eligible page/group data exists. Use the 75th percentile and current good thresholds: LCP ≤ 2.5 s, INP ≤ 200 ms, and CLS ≤ 0.1. If Google has too little eligible traffic, record **INSUFFICIENT FIELD DATA**; never substitute Lighthouse TBT for INP or report lab results as real-user measurements.

## Google Search Console routine

The site retains its Search Console verification metadata. Use the owner-authorized Search Console property for actual search/indexing evidence; this project does not scrape Google results or call authenticated Search Console APIs.

1. **Search results > Performance:** review clicks, impressions, CTR, average position, query, landing page, country, and device. Compare equivalent date ranges and account for low volume; no values are copied into CI as fabricated traffic.
2. **Indexing > Pages:** inspect indexed, discovered-but-not-indexed, crawled-but-not-indexed, duplicate/canonical classifications, exclusions, and errors. Check whether Google's selected canonical matches each intended localized URL.
3. **Sitemaps:** submit `https://mydv.my.id/sitemap.xml` once, then review discovery, processing errors, and expected URL coverage. Compare reported routes with the 22 canonical HTML routes plus the CV PDF.
4. **Experience > Core Web Vitals:** review mobile and desktop LCP, INP, and CLS when sufficient field data exists. Search Console may report insufficient data for a small portfolio.
5. **URL Inspection:** inspect `/en/`, `/id/`, a professional project such as `/en/projects/holy-smart/`, and a personal project such as `/en/projects/cling/`. Live URL testing describes the current fetched page; the indexed version describes Google's last stored crawl. Technical eligibility does not prove indexing. Request indexing selectively when there is a material page change; do not request every URL after each deployment.

No Google Analytics, tracking script, Indexing API, or Search Console API credential was added. Ordinary portfolio pages are not eligible use cases for Google's Indexing API.

## Article publication freeze

All entries in `_data/insights.json` remain `draft`; no article content is generated, edited, or published in this phase. Draft source is excluded from Jekyll output, and CI asserts that there are no public article routes or empty Insights listing pages. Excluding draft files from generated output does **not** make committed drafts private: this is a public GitHub repository, so the draft source remains publicly readable in repository history. Preserve the editorial infrastructure without linking to drafts or changing their status.

## Maintenance cadence

- **Weekly:** review the production monitor, production availability, internal-link failures, and warnings that persist across runs.
- **Monthly:** review Search Console performance and Page Indexing, check Core Web Vitals data availability, and compare equivalent periods.
- **After significant portfolio changes:** let CI validate the build; inspect Lighthouse results, localized metadata, canonical/hreflang, sitemap updates, and production deployment after it completes.

For a confirmed internal failure, reproduce the exact production URL and check the relevant page/resource and recent deployment. For temporary external failures, check again later and classify bot protection/authorization explicitly. For production failures, rerun manually only after checking the scheduled report; avoid repeated crawling. To add a project, update `_data/projects.yml`, the existing project route validator inventory and page files, then allow the monitor to derive its route pair from that shared inventory. To change thresholds, compare three-run measurements for both device profiles and document measured rationale in the policy and implementation report.

## Official metric references

- [web.dev: Core Web Vitals thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds) — LCP, INP, and CLS good/poor thresholds and 75th percentile evaluation.
- [Chrome for Developers: Lighthouse Total Blocking Time](https://developer.chrome.com/docs/lighthouse/performance/lighthouse-total-blocking-time) — TBT is a Lighthouse lab metric.
- [Chrome for Developers: Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci) — official Lighthouse CI tooling and configuration.

Legacy `/` and `/projects/{slug}/` are separately monitored for their static HTML redirect target; they are intentionally excluded from the canonical inventory and sitemap.
