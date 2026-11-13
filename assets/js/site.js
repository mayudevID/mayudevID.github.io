/* MayudevID — progressive navigation, language switching, and case-study interaction. */
(() => {
  "use strict";
  const supportedLanguages = ["en", "id"];
  const pages = document.querySelectorAll("[data-language-content]");
  const buttons = document.querySelectorAll("[data-language-button]");
  const translations = document.querySelectorAll("[data-i18n-en][data-i18n-id]");
  const header = document.querySelector(".site-header");
  const nav = document.getElementById("primary-navigation");
  const toggle = document.querySelector(".menu-toggle");
  const year = document.querySelector("[data-current-year]");
  if (year) year.textContent = String(new Date().getFullYear());

  function savedLanguage() {
    try {
      return window.localStorage.getItem("portfolioLanguage");
    } catch {
      return null;
    }
  }
  function rememberLanguage(language) {
    try {
      window.localStorage.setItem("portfolioLanguage", language);
    } catch {
      // Switching language still works if storage is unavailable.
    }
  }
  function closeNavigation() {
    if (!header || !toggle) return;
    header.classList.remove("nav-open");
    toggle.setAttribute("aria-expanded", "false");
  }
  function setLanguage(requested, remember = true) {
    const language = supportedLanguages.includes(requested) ? requested : "en";
    document.documentElement.lang = language;
    document.documentElement.dataset.language = language;
    pages.forEach((page) => { page.hidden = page.dataset.languageContent !== language; });
    buttons.forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.languageButton === language));
    });
    translations.forEach((element) => {
      element.textContent = element.dataset[language === "id" ? "i18nId" : "i18nEn"];
    });
    document.querySelectorAll("[data-nav-target]").forEach((link) => {
      link.setAttribute("href", "#" + link.dataset.navTarget + "-" + language);
    });
    if (remember) rememberLanguage(language);
    closeNavigation();

    // Point an existing section anchor at the newly visible localized section.
    const currentHash = decodeURIComponent(window.location.hash || "");
    const matchingAnchor = currentHash.match(/^(#.+)-(?:en|id)$/);
    if (matchingAnchor) {
      const nextHash = matchingAnchor[1] + "-" + language;
      if (document.getElementById(nextHash.slice(1)) && nextHash !== currentHash) {
        window.history.replaceState(null, "", nextHash);
      }
    }
  }

  buttons.forEach((button) => {
    button.addEventListener("click", () => setLanguage(button.dataset.languageButton));
  });
  if (toggle && nav && header) {
    toggle.addEventListener("click", () => {
      const isOpen = header.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", String(isOpen));
    });
    nav.addEventListener("click", (event) => {
      if (event.target.closest("a")) closeNavigation();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeNavigation();
    });
    document.addEventListener("click", (event) => {
      if (!header.contains(event.target)) closeNavigation();
    });
  }

  function expandLinkedCaseStudy(anchor) {
    const id = anchor.getAttribute("href")?.slice(1);
    if (!id) return;
    const target = document.getElementById(id);
    if (target?.tagName === "DETAILS") target.open = true;
  }
  document.querySelectorAll("[data-open-case-study]").forEach((link) => {
    link.addEventListener("click", () => expandLinkedCaseStudy(link));
  });
  function openHashTarget() {
    const id = decodeURIComponent(window.location.hash.slice(1));
    const target = id ? document.getElementById(id) : null;
    if (target?.tagName === "DETAILS") target.open = true;
  }

  setLanguage(savedLanguage() || "en", false);
  openHashTarget();
  window.addEventListener("hashchange", openHashTarget);
})();
