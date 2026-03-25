// PRO affiliate componenten voor multi-shop productkaarten en benodigdhedenlijsten
// Vereist: <script src="affiliate-products-v2.js"></script>
// Daarna:   <script src="affiliate-components-v3.js"></script>
//
// Voorbeeld losse kaart:
// <div id="product-wemos"></div>
// <script>
//   renderAffiliateProductCardV2("product-wemos", "wemos_d1_mini");
// </script>
//
// Voorbeeld benodigdhedenlijst:
// <div id="benodigdheden"></div>
// <script>
//   renderAffiliateRequirementsListV3("benodigdheden", {
//     title: "Benodigdheden",
//     intro: "Dit zijn de onderdelen die ik zelf voor dit project zou kiezen.",
//     products: ["wemos_d1_mini"]
//   });
// </script>

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
    return typeof entry === "string" ? { key: entry } : (entry || null);
  }

  function getProductsStore() {
    return window.AFFILIATE_PRODUCTS_V2 || {};
  }

  function getProduct(key) {
    return getProductsStore()[key] || null;
  }

  function getAvailableShops(product) {
    if (!product || !Array.isArray(product.shops)) return [];
    return product.shops.filter(function (shop) {
      return shop && typeof shop.url === "string" && shop.url.trim() !== "";
    });
  }

  function scoreShop(shop) {
    const text = `${shop.name || ""} ${shop.label || ""}`.toLowerCase();
    let score = 0;
    if (shop.recommended) score += 100;
    if (text.includes("goedkoop") || text.includes("budget")) score += 40;
    if (text.includes("snel")) score += 30;
    if (text.includes("nl") || text.includes("nederland")) score += 20;
    if ((shop.name || "").toLowerCase().includes("bol")) score += 10;
    if ((shop.name || "").toLowerCase().includes("amazon")) score += 8;
    if ((shop.name || "").toLowerCase().includes("aliexpress")) score += 6;
    return score;
  }

  function getPrimaryBadge(shop, index) {
    const text = `${shop.name || ""} ${shop.label || ""}`.toLowerCase();
    if (shop.recommended || index === 0) return "Aanrader";
    if (text.includes("goedkoop") || text.includes("budget")) return "Beste prijsgevoel";
    if (text.includes("snel")) return "Minste wachttijd";
    if (text.includes("nl") || text.includes("nederland") || (shop.name || "").toLowerCase().includes("bol")) return "Vertrouwde keuze";
    return "Keuzeoptie";
  }

  function getSecondaryLine(shop) {
    if (shop.label) return shop.label;
    if ((shop.name || "").toLowerCase().includes("aliexpress")) return "Vaak interessant als prijs belangrijker is dan snelheid.";
    if ((shop.name || "").toLowerCase().includes("bol")) return "Fijn als je liever bij een bekende NL-shop bestelt.";
    if ((shop.name || "").toLowerCase().includes("amazon")) return "Handig als je snelheid of internationale beschikbaarheid zoekt.";
    return "Affiliate link";
  }

  function buildShopButtons(product) {
    const shops = getAvailableShops(product)
      .slice()
      .sort(function (a, b) {
        return scoreShop(b) - scoreShop(a);
      });

    if (!shops.length) {
      return '<p style="margin:12px 0 0 0;opacity:.8;">Nog geen shoplinks ingevuld.</p>';
    }

    return shops
      .map(function (shop, index) {
        const primaryBadge = getPrimaryBadge(shop, index);
        const secondaryLine = getSecondaryLine(shop);
        const microBadge = shop.badge ? `<span style="font-size:.72rem;padding:4px 8px;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);white-space:nowrap;">${escapeHtml(shop.badge)}</span>` : "";
        const emphasis = index === 0
          ? 'border:1px solid rgba(255,255,255,.24);background:rgba(255,255,255,.06);box-shadow:0 6px 24px rgba(0,0,0,.12);'
          : 'border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.03);';

        return `
          <a
            href="${escapeHtml(shop.url)}"
            target="_blank"
            rel="nofollow sponsored noopener"
            style="display:block;text-decoration:none;color:inherit;border-radius:16px;padding:14px 16px;${emphasis}"
          >
            <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;">
              <div>
                <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
                  <strong style="font-size:1rem;">${escapeHtml(shop.name)}</strong>
                  <span style="font-size:.72rem;padding:4px 8px;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);white-space:nowrap;">${escapeHtml(primaryBadge)}</span>
                  ${microBadge}
                </div>
                <div style="font-size:.92rem;opacity:.82;margin-top:7px;">${escapeHtml(secondaryLine)}</div>
              </div>
              <div style="font-weight:700;white-space:nowrap;opacity:.95;">Bekijk →</div>
            </div>
          </a>`;
      })
      .join('');
  }

  function buildGallery(product) {
    if (!product.images || !product.images.length) return '';

    return `
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:10px;margin:16px 0 18px 0;">
        ${product.images.map(function (img, index) {
          return `<img src="${escapeHtml(img)}" alt="${escapeHtml(product.name)} afbeelding ${index + 1}" loading="lazy" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:12px;display:block;">`;
        }).join('')}
      </div>`;
  }

  window.renderAffiliateProductCardV2 = function (targetId, key) {
    const target = document.getElementById(targetId);
    const product = getProduct(key);
    if (!target || !product) return;

    target.innerHTML = `
      <section style="border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:20px;margin:24px 0;background:rgba(255,255,255,.03);">
        <div style="display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap;">
          <div>
            <h3 style="margin:0 0 8px 0;">${escapeHtml(product.name)}</h3>
            ${product.description ? `<p style="margin:0;opacity:.9;max-width:62ch;">${escapeHtml(product.description)}</p>` : ''}
          </div>
          <span style="font-size:.78rem;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);">Slim kiezen = minder twijfel</span>
        </div>
        ${buildGallery(product)}
        <div style="display:grid;gap:10px;">
          ${buildShopButtons(product)}
        </div>
        <p style="font-size:.9rem;opacity:.78;margin:14px 0 0 0;">Deze kaart bevat affiliate links. Als je via deze links iets koopt, ontvangen wij mogelijk een kleine commissie zonder extra kosten voor jou.</p>
      </section>`;
  };

  function buildRequirementItem(entry) {
    const normalized = normalizeProductEntry(entry);
    if (!normalized) return '';

    const product = getProduct(normalized.key);
    if (!product) return '';

    const image = normalized.image || (product.images && product.images[0]) || '';
    const note = normalized.note || product.description || '';

    return `
      <li style="list-style:none;margin:0;padding:0;">
        <article style="display:grid;grid-template-columns:minmax(96px,120px) 1fr;gap:16px;align-items:start;border:1px solid rgba(255,255,255,.12);border-radius:18px;padding:16px;background:rgba(255,255,255,.03);">
          <div>
            ${image ? `<img src="${escapeHtml(image)}" alt="${escapeHtml(product.name)}" loading="lazy" style="width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:12px;display:block;">` : ''}
          </div>
          <div>
            <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;flex-wrap:wrap;">
              <h3 style="margin:0 0 8px 0;font-size:1.05rem;">${escapeHtml(product.name)}</h3>
              <span style="font-size:.72rem;padding:4px 8px;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);">Makkelijk vergelijken</span>
            </div>
            ${note ? `<p style="margin:0 0 12px 0;opacity:.9;">${escapeHtml(note)}</p>` : ''}
            <div style="display:grid;gap:8px;">
              ${buildShopButtons(product)}
            </div>
          </div>
        </article>
      </li>`;
  }

  window.renderAffiliateRequirementsListV3 = function (targetId, config) {
    const target = document.getElementById(targetId);
    if (!target || !config || !Array.isArray(config.products)) return;

    const title = config.title || 'Benodigdheden';
    const intro = config.intro || 'Dit zijn de onderdelen die ik hier zelf voor zou kiezen.';
    const itemsHtml = config.products.map(buildRequirementItem).join('');

    target.innerHTML = `
      <section style="margin:32px 0;">
        <div style="display:flex;align-items:end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:14px;">
          <div>
            <h2 style="margin:0 0 6px 0;">${escapeHtml(title)}</h2>
            <p style="margin:0;opacity:.85;max-width:68ch;">${escapeHtml(intro)}</p>
          </div>
          <span style="font-size:.78rem;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);">Keuzehulp zonder keuzestress</span>
        </div>
        <ul style="display:grid;gap:14px;padding:0;margin:0;">
          ${itemsHtml}
        </ul>
        <p style="font-size:.9rem;opacity:.78;margin-top:14px;">Dit overzicht bevat affiliate links. Als je via deze links iets koopt, ontvangen wij mogelijk een kleine commissie zonder extra kosten voor jou.</p>
      </section>`;
  };
})();
