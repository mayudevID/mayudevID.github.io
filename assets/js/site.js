/* MayudevID — progressive enhancement for navigation and case studies.
 * Language changes are standard links to independently indexable URLs.
 */
(() => {
  "use strict";
  const header = document.querySelector(".site-header");
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.getElementById("primary-navigation");
  const year = document.querySelector("[data-current-year]");

  if (year) year.textContent = String(new Date().getFullYear());

  function closeNavigation() {
    if (!header || !toggle) return;
    header.classList.remove("nav-open");
    toggle.setAttribute("aria-expanded", "false");
  }

  if (header && toggle && nav) {
    toggle.addEventListener("click", () => {
      const isOpen = header.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", String(isOpen));
    });
    nav.addEventListener("click", (event) => {
      if (event.target.closest("a")) closeNavigation();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        if (header.classList.contains("nav-open")) {
          closeNavigation();
          toggle.focus();
        }
      }
    });
    document.addEventListener("click", (event) => {
      if (!header.contains(event.target)) closeNavigation();
    });
  }

  function openCaseStudy(hash) {
    if (!hash || hash[0] !== "#") return;
    let target;
    try { target = document.getElementById(decodeURIComponent(hash.slice(1))); }
    catch { return; }
    if (target && target.tagName === "DETAILS") target.open = true;
  }
  document.querySelectorAll("[data-open-case-study]").forEach((link) => {
    link.addEventListener("click", () => openCaseStudy(link.hash));
  });
  openCaseStudy(window.location.hash);
  window.addEventListener("hashchange", () => openCaseStudy(window.location.hash));
})();
