const inventory = require('./lighthouse-pages.json');

module.exports = (preset, outputDir) => {
  const assertions = {
    'categories:performance': ['error', {minScore: 0.90}],
    'categories:accessibility': ['error', {minScore: 0.95}],
    'categories:best-practices': ['error', {minScore: 0.95}],
    'categories:seo': ['error', {minScore: 1}],
    'color-contrast': ['error', {minScore: 1}],
    'document-title': ['error', {minScore: 1}],
    'html-has-lang': ['error', {minScore: 1}],
    'image-alt': ['error', {minScore: 1}],
    'meta-description': ['error', {minScore: 1}],
    'canonical': ['error', {minScore: 1}],
    'crawlable-anchors': ['error', {minScore: 1}],
    'is-crawlable': ['error', {minScore: 1}],
    'largest-contentful-paint': ['error', {maxNumericValue: 2500}],
    'cumulative-layout-shift': ['error', {maxNumericValue: 0.1}],
    'total-blocking-time': ['error', {maxNumericValue: 300}],
    'first-contentful-paint': ['error', {maxNumericValue: 1800}],
    'speed-index': ['error', {maxNumericValue: 3400}],
  };
  for (const assertion of Object.values(assertions)) {
    assertion[1].aggregationMethod = 'median';
  }

  return {
    ci: {
      collect: {
        url: inventory.pages.map((page) => `http://127.0.0.1:4173${page.url}`),
        numberOfRuns: 3,
        settings: {
          ...(preset === 'desktop' ? { preset: 'desktop' } : {}),
          chromeFlags: '--no-sandbox --headless=new',
        },
        startServerCommand: 'python3 -u -m http.server 4173 --bind 127.0.0.1 --directory _site',
        startServerReadyPattern: 'Serving HTTP',
        startServerReadyTimeout: 30000,
      },
      assert: {preset: 'lighthouse:recommended', assertions},
      upload: {target: 'filesystem', outputDir},
    },
  };
};
