# MayudevID — portfolio maintenance guide

A lightweight **Jekyll + HTML + CSS + JavaScript** site with independently indexable English and Indonesian pages.

## Local setup

```bash
bundle install
bundle exec jekyll serve --port 4001
```

Open:
- English (canonical): http://localhost:4001/
- Indonesian: http://localhost:4001/id/

This project uses only Jekyll 3.10 and the dependencies in `Gemfile.lock`. No React or npm build is required.

## Source files

| File | Responsibility |
| --- | --- |
| `index.html` | English page: `/` |
| `id.html` | Indonesian page: `/id/` |
| `_layouts/default.html` | Shared metadata, header, footer, SEO, layout |
| `_includes/portfolio-page.html` | Shared page structure and localized featured previews |
| `portfolio/portfolio-en.md` | English content and project details |
| `portfolio/portfolio.md` | Indonesian content and project details |
| `assets/css/site.css` | Layout, colors, responsive breakpoints and reduced-motion styles |
| `assets/js/site.js` | Mobile navigation and accessible case-study expansion |
| `scripts/check_portfolio.py` | Offline HTML/content/link checker |
| `.github/workflows/portfolio-quality.yml` | Automated build and source checks |

The Markdown sources are still canonical. The `<!-- PORTFOLIO:SECTION -->` markers MUST remain at their existing positions and count (**12 markers per language**); the Jekyll include uses them to find the original content. Section order:

0. Original intro/contact summary (not shown on the redesigned home page)
1. About
2. Experience
3. Education
4. Skills
5. Certifications
6. Holy Smart
7. Holy World
8. Ar-Rauda
9. Bloom
10. Cling!
11. KBBI Daring
12. Contact

The displayed project descriptions, image galleries and store links come from these Markdown sources. **Do not change existing company names, employment dates, app identifiers, or store links without explicit verification.**

Local asset references must be **root-relative**, such as `/assets/holy_smart/1.png`, so they work on both `/` and `/id/`.

## Automated quality checks

```bash
bundle exec jekyll build --trace
python3 scripts/check_portfolio.py --site _site
node --check assets/js/site.js
```

GitHub Actions runs these on pushes to `main` and on pull requests. It checks both localized HTML files, canonical and hreflang URLs, heading count, app-store URL preservation, internal links, gallery images, language navigation, and sitemap coverage. External websites are not requested by the automated checker, avoiding false alerts due to bot restrictions.

## Visual and Lighthouse checks

Use Chrome DevTools Lighthouse against both `/` and `/id/` (mobile & desktop), and test the following viewports: **320px, 375px, 768px, 1024px, and 1440px**. Verify no horizontal overflow; the EN/ID links, keyboard focus, mobile menu, screenshot gallery, case-study accordions, Download CV, and Google Play/App Store links.

Suggested manual Lighthouse targets: **Accessibility ≥ 95**, **Best Practices ≥ 95**, **SEO ≥ 95** and **Performance ≥ 85** on mobile. These are targets, not measured results. Compressing large PNG screenshots and doing real-browser testing are useful follow-up tasks.
