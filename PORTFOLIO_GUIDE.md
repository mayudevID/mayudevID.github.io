# MayudevID — portfolio maintenance guide

A lightweight **Jekyll + HTML + CSS + JavaScript** site with independently indexable English and Indonesian pages.

## Local setup

```bash
bundle install
bundle exec jekyll serve --port 4001
```

Open:
- English (canonical): http://localhost:4001/en/
- Indonesian: http://localhost:4001/id/

This project uses only Jekyll 3.10 and the dependencies in `Gemfile.lock`. No React or npm build is required.

## Source files

| File | Responsibility |
| --- | --- |
| `index.html` | Legacy root redirect to `/en/` |
| `pages/en/index.html` | English page: `/en/` |
| `pages/id/index.html` | Indonesian page: `/id/` |
| `pages/{en,id}/projects/{slug}.html` | Canonical localized case studies; explicit permalinks |
| `pages/redirects/projects/` | Old English project URL compatibility redirects |
| `_layouts/default.html` | Shared metadata, header, footer, SEO, layout |
| `_includes/portfolio-page.html` | Shared page structure and localized featured previews |
| `pages/en/portfolio.md` | English content and project details |
| `pages/id/portfolio.md` | Indonesian content and project details |
| `assets/css/site.css` | Layout, colors, responsive breakpoints and reduced-motion styles |
| `assets/js/site.js` | Mobile navigation and accessible case-study expansion |
| `scripts/check_portfolio.py` | Offline HTML/content/link checker |
| `.github/workflows/portfolio-quality.yml` | Automated build and source checks |

The Markdown sources are still canonical. The `<!-- PORTFOLIO:SECTION -->` markers MUST remain at their existing positions and count (**16 markers per language**); the Jekyll include uses them to find the original content. Section order:

0. Original intro/contact summary (not shown on the redesigned home page)
1. About
2. Experience
3. Education
4. Skills
5. Certifications
6. Holy Smart
7. Holy World
8. DTG SOMS
9. Ar-Rauda
10. GOT Agency
11. KTADBRNR (archived)
12. EMCare
13. Bloom
14. Cling!
15. KBBI Daring
16. Contact

The homepage biography, experience and contact sections come from these Markdown sources. Project descriptions, image galleries and store links come from `_data/projects.yml`. **Do not change existing company names, employment dates, app identifiers, or store links without explicit verification.**

Local asset references must be **root-relative**, such as `/assets/projects/holy_smart/1.png`, so they work on both `/en/` and `/id/`.

Project screenshots live in `assets/projects/` (`ar_rauda`, `dtg_soms`, `got_agency`, `holy_smart`, `holy_world`, and `ktadbrnr`). Store badges live in `assets/platform/` (`app_store` and `play_store`). Shared site assets such as CSS, JavaScript, and the favicon stay directly under `assets/` or in their existing `css/` and `js/` folders.

## Project screenshot archives

The seven GOT Agency screenshots and eight KTADBRNR screenshots are listed in `_data/got_agency_screenshots.json` and `_data/ktadbrnr_screenshots.json`. Their `local_path` entries point to the downloaded assets in `assets/projects/got_agency/` and `assets/projects/ktadbrnr/`, preserving each source image format. Both the featured cards and case study galleries use these local files; the Google Play URLs remain as source references and for re-archiving.

EMCare uses five official Google Play screenshots listed in `_data/emcare_screenshots.json` and archived under `assets/projects/emcare/`. Both the featured cover and case study gallery use these local files. The Google Play URLs remain as source references for re-archiving.

To refresh missing local copies, run from the repository root while Google Play still serves the source images:

```bash
python3 scripts/archive_project_screenshots.py
```

The script uses only the Python standard library and writes files to the configured paths. Review and commit downloaded assets.

## Automated quality checks

```bash
bundle exec jekyll build --trace
python3 scripts/check_portfolio.py --site _site
node --check assets/js/site.js
```

GitHub Actions runs these on pushes to `main` and on pull requests. It checks both localized HTML files, canonical and hreflang URLs, heading count, app-store URL preservation, internal links, gallery images, language navigation, and sitemap coverage. External websites are not requested by the automated checker, avoiding false alerts due to bot restrictions.

## Visual and Lighthouse checks

Use Chrome DevTools Lighthouse against both `/en/` and `/id/` (mobile & desktop), and test the following viewports: **320px, 375px, 768px, 1024px, and 1440px**. Verify no horizontal overflow; the EN/ID links, keyboard focus, mobile menu, screenshot gallery, case-study accordions, Download CV, and Google Play/App Store links.

Suggested manual Lighthouse targets: **Accessibility ≥ 95**, **Best Practices ≥ 95**, **SEO ≥ 95** and **Performance ≥ 85** on mobile. These are targets, not measured results. Compressing large PNG screenshots and doing real-browser testing are useful follow-up tasks.

## Project previews, case studies and confidentiality

Professional homepage dropdowns use `_includes/project-preview.html` (three selected mobile screenshots and up to three features); standalone case studies use `_includes/project-content.html` and documented context/contributions in `_data/projects.yml`. Both use local store badges via `_includes/project-store-links.html`. Historical KTADBRNR retains a text reference. Do not add internal architectures, unpublished metrics, credentials, or unapproved operational screenshots. Two unreviewed admin screenshots are excluded from the site build; GitHub repository access and history remain separate from website publishing. Preserve the article publication freeze.

## Multilingual URLs

Canonical English routes use `/en/`, Indonesian routes use `/id/`. Source pages are under `pages/{en,id}/` and their explicit permalinks keep `/pages/` out of public URLs. `/` and each old `/projects/{slug}/` use immediate static HTML redirects with canonical destination, noindex, and a fallback link; GitHub Pages does not provide per-page HTTP 301 configuration. The redirect script preserves query strings and fragments. Keep legacy redirects and the root Search Console verification tag. The sitemap lists 22 canonical HTML pages and the existing CV PDF, never the redirects. Shared Person/WebSite IDs remain stable at the domain root. English x-default points to the canonical `/en/` route (or corresponding English project).

Case-study pages display the complete approved screenshot gallery inside the project header. The gallery scrolls horizontally when needed; no separate screenshots or related-projects section is rendered. The homepage previews remain unchanged. Keep unpublished admin images excluded.
