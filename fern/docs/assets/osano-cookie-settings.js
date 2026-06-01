/*
 * Adds a "Cookie Settings" link to the docs footer that opens Osano's
 * preferences drawer. Fern has no config for a custom footer action, so this
 * script (registered under `js:` in docs.yml) injects it. It pairs with the
 * `.osano-cm-widget` hide rule in styles.css — once Osano's floating widget is
 * hidden, this link is how visitors re-open and change their consent.
 *
 * Fern's footer is React-rendered and gets reconciled often, which removes a
 * plain injected node. So we just keep re-asserting the link: a MutationObserver
 * re-adds it the instant it's removed, plus an interval backstop, plus delegated
 * click handling that never depends on the node staying put.
 */
(function () {
  var LINK_ID = 'osano-cookie-settings-link';

  // Delegated click — works no matter how many times the button is re-created.
  document.addEventListener('click', function (event) {
    if (!event.target.closest || !event.target.closest('#' + LINK_ID)) return;
    event.preventDefault();
    if (window.Osano && window.Osano.cm && window.Osano.cm.showDrawer) {
      window.Osano.cm.showDrawer('osano-cm-dom-info-dialog-open');
    }
  });

  function ensure() {
    if (document.getElementById(LINK_ID)) return;
    var footer = document.querySelector('footer.fern-layout-footer') || document.querySelector('footer');
    if (!footer) return;

    // Sit next to the existing social links so placement + styling match.
    var social = footer.querySelector('a[href*="github"], a[href*="linkedin"]');

    var link = document.createElement('button');
    link.id = LINK_ID;
    link.type = 'button';
    link.textContent = 'Cookie Settings';
    link.className = 'text-(color:--grayscale-a9) hover:text-(color:--grayscale-a11) transition-colors';
    link.style.cssText = 'background:none;border:none;padding:0;cursor:pointer;font:inherit;';

    (social && social.parentElement ? social.parentElement : footer).appendChild(link);
  }

  // Re-assert on every DOM change (catches React re-renders) and on a timer.
  new MutationObserver(ensure).observe(document.documentElement, { childList: true, subtree: true });
  setInterval(ensure, 1000);
  ensure();
})();
