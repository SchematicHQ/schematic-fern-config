/*
 * Injects a "Cookie Settings" link into the Fern docs footer and wires it to
 * Osano's preferences drawer. Fern has no config for a custom footer action,
 * so this is the "fern way": a script registered under `js:` in docs.yml that
 * adds the entry point in the DOM. It pairs with the `.osano-cm-widget` hide
 * rule in styles.css — once Osano's floating widget is hidden, this link is the
 * required way for visitors to re-open and change their consent.
 *
 * Defensive notes:
 *  - Fern is a client-side SPA, so the footer can be re-rendered on navigation.
 *    A MutationObserver re-injects the link whenever a footer appears, and an id
 *    guard keeps it from being added twice.
 *  - Click handling is DELEGATED to the document rather than bound to the button
 *    node. When React reconciles/re-renders the footer it can swap out our
 *    injected button, which would drop a directly-attached listener (the button
 *    would render but clicking it does nothing). A single delegated listener
 *    survives every re-render.
 *  - The link reuses the same Tailwind classes as the footer's social links so
 *    it inherits their theme-reactive (light/dark) colors. It no-ops gracefully
 *    if Osano hasn't loaded (e.g. preview builds with no consent script).
 */
(function () {
  var LINK_ID = 'osano-cookie-settings-link';

  // Delegated click handler — bound once, never lost to a footer re-render.
  document.addEventListener('click', function (event) {
    var trigger = event.target.closest && event.target.closest('#' + LINK_ID);
    if (!trigger) return;
    event.preventDefault();
    if (window.Osano && window.Osano.cm && window.Osano.cm.showDrawer) {
      window.Osano.cm.showDrawer('osano-cm-dom-info-dialog-open');
    }
  });

  function inject() {
    var footer = document.querySelector('footer.fern-layout-footer') || document.querySelector('footer');
    if (!footer || footer.querySelector('#' + LINK_ID)) return;

    // Anchor next to the existing social links so placement + styling match.
    var social = footer.querySelector('a[href*="github"], a[href*="linkedin"]');

    var link = document.createElement('button');
    link.id = LINK_ID;
    link.type = 'button';
    link.textContent = 'Cookie Settings';
    link.className = 'text-(color:--grayscale-a9) hover:text-(color:--grayscale-a11) transition-colors';
    link.style.cssText = 'background:none;border:none;padding:0;cursor:pointer;font:inherit;';

    if (social && social.parentElement) {
      social.parentElement.appendChild(link);
    } else {
      footer.appendChild(link);
    }
  }

  function start() {
    inject();
    // Re-inject if the footer is re-rendered on client-side navigation.
    new MutationObserver(inject).observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
