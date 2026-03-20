// Centrale productlijst voor affiliate links en assets
//
// Gebruik:
// 1. Voeg dit bestand toe in je HTML:
//    <script src="affiliate-products.js"></script>
//
// 2. Maak ergens in je HTML een placeholder:
//    <div id="product-wemos"></div>
//
// 3. Render een product met:
//    renderAffiliateProduct("product-wemos", "wemos_d1_mini");
//
// 4. Alleen een link nodig?
//    AFFILIATE_PRODUCTS.wemos_d1_mini.url
//
// 5. Nieuw product toevoegen?
//    Kopieer een blok in AFFILIATE_PRODUCTS en pas naam, url en images aan.

window.AFFILIATE_PRODUCTS = {
  wemos_d1_mini: {
    name: "WeMos D1 Mini",
    description: "Compact ESP8266 ontwikkelbord voor Homeyduino, sensoren en DIY smart home projecten.",
    buttonText: "Bekijk op AliExpress",
    url: "https://s.click.aliexpress.com/e/_c3O1etpl",
    images: [
      "assets/wemos-d1-mini-1.jpg",
      "assets/wemos-d1-mini-2.jpg",
      "assets/wemos-d1-mini-3.jpg",
      "assets/wemos-d1-mini-4.jpg",
      "assets/wemos-d1-mini-5.jpg",
      "assets/wemos-d1-mini-6.jpg"
    ]
  }
};

window.getAffiliateProduct = function (key) {
  return window.AFFILIATE_PRODUCTS[key] || null;
};

window.renderAffiliateProduct = function (targetId, productKey) {
  const target = document.getElementById(targetId);
  const product = window.AFFILIATE_PRODUCTS[productKey];

  if (!target || !product) return;

  const imagesHtml = (product.images || [])
    .map(
      (img, index) => `
        <img
          src="${img}"
          alt="${product.name} afbeelding ${index + 1}"
          loading="lazy"
          style="width:100%;height:auto;border-radius:12px;display:block;"
        >`
    )
    .join("");

  target.innerHTML = `
    <section class="affiliate-product-card" style="border:1px solid rgba(255,255,255,.12);border-radius:18px;padding:20px;margin:24px 0;background:rgba(255,255,255,.03);">
      <h3 style="margin-top:0;">${product.name}</h3>
      ${product.description ? `<p>${product.description}</p>` : ""}
      ${product.images && product.images.length ? `
        <div class="affiliate-product-gallery" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin:16px 0;">
          ${imagesHtml}
        </div>
      ` : ""}
      <p>
        <a
          href="${product.url}"
          target="_blank"
          rel="nofollow sponsored noopener"
          style="display:inline-block;padding:12px 18px;border-radius:999px;text-decoration:none;font-weight:700;border:1px solid currentColor;"
        >${product.buttonText || "Bekijk product"}</a>
      </p>
      <p style="font-size:.9rem;opacity:.8;margin-bottom:0;">
        Dit blok bevat affiliate links. Bij aankoop ontvangen wij mogelijk een kleine commissie zonder extra kosten voor jou.
      </p>
    </section>`;
};
