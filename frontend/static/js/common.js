/**
 * common.js — shared utilities for PerthPins.
 *
 * Security fix: sanitize the page parameter before using it in querySelector
 * to prevent CSS-injection via a crafted URL (closes #45).
 */
function loadComponent(id, file) {
  fetch(file)
    .then(function (res) { return res.text(); })
    .then(function (html) {
      const container = document.getElementById(id);
      if (!container) return;

      // Use DOMParser so the fetched HTML is parsed in an inert context
      // instead of being set directly via innerHTML.
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      container.replaceChildren(...Array.from(doc.body.childNodes).map(function (n) {
        return document.importNode(n, true);
      }));

      // Sanitize the page token: allow only alphanumeric, dash, underscore, dot
      const rawPage = window.location.pathname.split('/').pop() || 'index.html';
      const page = rawPage.replace(/[^a-zA-Z0-9._-]/g, '');
      const link = document.querySelector('#' + id + ' .nav-link[href="' + page + '"]');
      if (link) link.classList.add('active');
    })
    .catch(function (err) {
      console.warn('loadComponent failed for', file, err);
    });
}
