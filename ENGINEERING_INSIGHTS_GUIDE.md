# Engineering Insights Editorial Guide

This is the authoring and review workflow for bilingual technical articles on MayudevID. It is excluded from the generated Jekyll site. Drafts currently live under `editorial/drafts/` and are excluded as well.

## Current publishing state

`_data/insights.json` is the shared catalog. Each record uses a stable `article_id` and `slug`, localized title, description, summary and category, English and Indonesian route, source references, related project IDs, related article IDs, and review state. The three current article pairs are `draft`; none is rendered or indexable on the portfolio website; drafts in a public GitHub repository are still publicly readable. Keep draft metadata free of invented publication dates.

## Create an article and translation

1. Add one catalog record to `_data/insights.json` with a unique stable ID and lowercase hyphenated slug.
2. Draft both language versions at `editorial/drafts/{slug}/en.md` and `id.md`. Write natural prose for each audience; do not translate technical caveats away.
3. Link authoritative primary documentation and check every platform/version-sensitive statement on the review date. Keep source citations close to the statements they support.
4. Use project IDs from `_data/projects.yml` only where a documented project capability is a useful topic connection. A relationship does not assert that the author personally implemented that capability.
5. Keep `status` as `draft` until source, technical, translation, attribution, and owner reviews are complete.

## Publication freeze

The portfolio owner has chosen not to publish AI-generated articles. The existing draft infrastructure remains inactive; do not publish or index any draft without an explicit change in that policy.

## Publish only after review

To publish a reviewed article, create two static pages at `pages/en/insights/{slug}.md` and `pages/id/insights/{slug}.md`, using the `insight` layout and explicit permalinks `/en/insights/{slug}/` and `/id/insights/{slug}/`. Copy the reviewed article body out of the excluded editorial directory. Set `article_page: true`, `article_id`, `lang`, localized `title`, `description`, `summary`, `category`, `topics`, `insights_path`, `translation_url`, explicit reciprocal `hreflang` entries (`en`, `id`, `x-default`), `seo_indexable: true`, and `date_published` to the real publication date. Add `date_modified` only when substantive content changes. Use the shared fallback social image or a checked local 1200×630 image and write its accurate `social_image_alt`.

Once both pages exist, set `translation_review`, `editorial_review`, and `publication_review` to `approved`, then change the record's status to `published`. Then create `pages/en/insights/index.html` and `pages/id/insights/index.html` using `insights-index` layout and explicit permalinks `/en/insights/` and `/id/insights/`, with localized title, description, introduction, canonical paths, reciprocal alternates, `translation_url`, and `seo_indexable: true`. Do not create either listing page while there are no published articles. Set sitemap `last_modified_at` only to a truthful content change date, never the build date. Build and validate before committing; the sitemap discovers indexable static pages through `site.pages`.

The `insight` layout emits the article body, localized breadcrumbs, related project links, and published related articles. Shared SEO uses the page's canonical, language alternates, localized metadata, author `https://mydv.my.id/#person`, local social image, `TechArticle`, and `BreadcrumbList`. Listing pages emit `CollectionPage`, `ItemList`, and matching visible breadcrumbs. Keep all publication metadata in front matter and the catalog in sync; do not mark drafts indexable.

## Review checklist

- Technical claims match current authoritative documentation; identify recommendations as recommendations and examples as illustrative unless executed.
- Both language versions have equivalent caveats, intent, and links, with natural terminology.
- No fabricated incidents, measurements, project responsibilities, credentials, publication dates, or outcomes.
- Project links resolve to catalog IDs and are contextually useful. Related article IDs point only to published articles.
- Exactly one meaningful H1, logical headings, semantic article/main landmarks, descriptive link text, visible focus, readable line length, and responsive code blocks.
- Canonical URL, language, reciprocal `hreflang`, x-default, language switch, Open Graph image and alt, indexability, JSON-LD, and sitemap entry match the visible page.
- Publication and modification dates reflect actual editorial events, not build time.
- No private or confidential project details or private repository links.
- Run the build, generated-site validator, mutation tests, JavaScript syntax check, and `git diff --check`. Automated success does not equal editorial approval or production/browser verification.

## Social image and references

Use `/assets/seo/og-cover.png` until a lightweight, locally hosted article image is justified. If adding one, use `assets/seo/insights/{slug}.png`, 1200×630, MayudevID branding, a readable accurate title, and no fabricated interface or portrait. Do not add visible-page requests for decorative images.

Keep sources in each catalog record as `{ "label": "...", "url": "https://..." }`. Prefer official Flutter, Dart, Firebase, Android, and Apple documentation. Recheck changing platform behavior immediately before publication.

## Backlog (not published)

| Topic | Audience | Related projects | Evidence to collect | Suggested sources | Owner input |
|---|---|---|---|---|---|
| Flutter release flavors and configuration boundaries | Flutter developers preparing separate staging and production builds | Holy Smart, Cling! | Public-safe build workflow, environment separation, release checks | Flutter flavors docs; Android build variants; Apple build configurations | Yes, confirm which practices were personally used and can be described |
| Designing API error states in mobile clients | Developers integrating REST APIs | Ar-Rauda, Holy Smart | A sanitized request/response example and the app's user-visible recovery policy | Flutter architecture error handling; Dart exceptions; HTTP semantics | Yes, supply an approved non-confidential example |
| CI checks for Flutter mobile releases | Developers maintaining Android and iOS delivery | Cling!, Bloom | Public workflow evidence, platform signing boundaries, checks actually run | GitHub Actions docs; Flutter deployment docs; Android/iOS release docs | Yes, confirm actual workflow and what may be shared |

Do not automatically publish backlog topics. Add a topic only when there is useful evidence and a distinct audience need.
