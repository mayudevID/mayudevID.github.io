# MayudevID portfolio editing guide

This website is built with **Jekyll, HTML, CSS, and vanilla JavaScript**. No Node/npm build step is needed.

## Local development

```bash
bundle install
bundle exec jekyll serve --port 4001
```

Open http://127.0.0.1:4001/ and check both **EN** and **ID**. GitHub Pages builds the site from `main`.

## Where to edit

- `index.html` — page shell, navigation, metadata, and language includes.
- `_includes/portfolio-page.html` — page sections and localized hero/project preview text.
- `portfolio/portfolio-en.md` — English experience, skills, education, project details, and contact information.
- `portfolio/portfolio.md` — Indonesian content.
- `assets/css/site.css` — layout, colors, responsive breakpoints, reduced-motion styles.
- `assets/js/site.js` — persistent EN/ID switch, mobile menu, and case-study expansion.
- `assets/favicon.svg` — vector site icon.

### Important: Markdown section markers

The two Markdown files contain `<!-- PORTFOLIO:SECTION -->` comments. These **must remain in both files**, in the same order, because the Jekyll include splits each file into 13 segments and renders them in a custom order. The markers do not affect GitHub Markdown preview.

Section order in each Markdown source:
0. Original intro/contact references (kept as source)
1. About
2. Experience
3. Education
4. Skills
5. Certifications
6. Holy Smart (with the original Featured Projects heading)
7. Holy World
8. Ar-Rauda
9. Bloom
10. Cling!
11. KBBI Daring
12. Contact

The homepage intentionally places featured projects before experience. Project text, screenshots, and store links in the case-study sections are rendered **directly from the Markdown**, rather than duplicated in a second data file.

## Before publishing a content update

1. Keep English and Indonesian content consistent.
2. Do not change existing store URLs, company names, employment dates, or app identifiers without verifying them.
3. Check all six project sections and verify that case studies open from their overview cards.
4. Check desktop, mobile, keyboard tab focus, language switching, all external links, and PDF download.
5. Confirm GitHub Pages build status after deployment.

The design uses responsive CSS and respects `prefers-reduced-motion`. Screenshots use `loading="lazy"`, but large PNG assets should still be compressed separately.
