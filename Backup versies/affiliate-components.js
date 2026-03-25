// Herbruikbare componenten voor affiliate producten
// Vereist: <script src="affiliate-products.js"></script>
// Daarna:   <script src="affiliate-components.js"></script>
//
// Voorbeeldgebruik:
// <div id="benodigdheden-clapper"></div>
// <script>
//   renderAffiliateRequirementsList("benodigdheden-clapper", {
//     title: "Benodigdheden",
//     intro: "Dit heb ik gebruikt voor dit project.",
//     products: ["wemos_d1_mini"]
//   });
// </script>
//
// Of met custom tekst per product:
// renderAffiliateRequirementsList("benodigdheden", {
//   title: "Benodigdheden",
//   products: [
//     { key: "wemos_d1_mini", note: "Het compacte bordje dat ik hier zelf voor zou kiezen." }
//   ]
// });

(function () {
  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function normalizeProductEntry(entry) {
    if (typeof entry === "string") {
      return { key: entry };
    }
    return entry || null;
  }

  function buildProductItem(entry) {
    const normalized = normalizeProductEntry(entry);
    if (!normalized || !window.AFFILIATE_PRODUCTS) return "";

    const product = window.AFFILIATE_PRODUCTS[normalized.key];
    if (!product) return "";

    const image = normalized.image || (product.images && product.images[0]) || "";
    const note = normalized.note || product.description || "";
    const buttonText = normalized.buttonText || product.buttonText || "Bekijk product";

    return `
      <li class="affiliate-req-item" style="list-style:none;margin:0;padding:0;">
        <article style="display:grid;grid-template-columns:minmax(90px,120px) 1fr;gap:16px;align-items:start;border:1px solid rgba(255,255,255,.12);border-radius:18px;padding:16px;background:rgba(255,255,255,.03);">
          <div>
            ${image ? `<img src="${escapeHtml(image)}" alt="${escapeHtml(product.name)}" loading="lazy" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:12px;display:block;">` : ""}
          </div>
          <div>
            <h3 style="margin:0 0 8px 0;font-size:1.05rem;">${escapeHtml(product.name)}</h3>
            ${note ? `<p style="margin:0 0 12px 0;opacity:.9;">${escapeHtml(note)}</p>` : ""}
            <p style="margin:0;display:flex;flex-wrap:wrap;gap:10px;align-items:center;">
              <a href="${escapeHtml(product.url)}" target="_blank" rel="nofollow sponsored noopener" style="display:inline-block;padding:10px 16px;border-radius:999px;text-decoration:none;font-weight:700;border:1px solid currentColor;">${escapeHtml(buttonText)}</a>
              <span style="font-size:.92rem;opacity:.75;">Affiliate link</span>
            </p>
          </div>
        </article>
      </li>`;
  }

  window.renderAffiliateRequirementsList = function (targetId, config) {
    const target = document.getElementById(targetId);
    if (!target || !config || !Array.isArray(config.products)) return;

    const title = config.title || "Benodigdheden";
    const intro = config.intro || "Dit zijn de producten die je voor dit project nodig hebt.";
    const itemsHtml = config.products.map(buildProductItem).join("");

    target.innerHTML = `
      <section class="affiliate-requirements" style="margin:32px 0;">
        <div style="display:flex;align-items:end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:14px;">
          <div>
            <h2 style="margin:0 0 6px 0;">${escapeHtml(title)}</h2>
            ${intro ? `<p style="margin:0;opacity:.85;">${escapeHtml(intro)}</p>` : ""}
          </div>
        </div>
        <ul style="display:grid;gap:14px;padding:0;margin:0;">
          ${itemsHtml}
        </ul>
        <p style="font-size:.9rem;opacity:.78;margin-top:14px;">
          Dit overzicht bevat affiliate links. Als je via deze links iets koopt, ontvangen wij mogelijk een kleine commissie zonder extra kosten voor jou.
        </p>
      </section>`;
  };
})();
