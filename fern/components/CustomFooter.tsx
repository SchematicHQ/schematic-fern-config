// Adds a "Cookie Settings" link to the docs footer that opens Osano's consent
// drawer. Wired in via `footer:` in docs.yml. Fern renders this in addition to
// its default footer, so we only add the one link here (the default footer
// already provides the social icons, "Built with Fern", and page nav). Because
// it's a real Fern-compiled component (not an injected <script>), it renders in
// `fern docs dev` and on the deployed site, and React owns it so it can't vanish.

function openCookieSettings() {
  (window as any).Osano?.cm?.showDrawer?.("osano-cm-dom-info-dialog-open");
}

export default function CustomFooter() {
  return (
    <div className="not-prose flex justify-center pb-8">
      <button
        type="button"
        onClick={openCookieSettings}
        className="text-(color:--grayscale-a9) hover:text-(color:--grayscale-a11) transition-colors text-sm"
      >
        Cookie Settings
      </button>
    </div>
  );
}
