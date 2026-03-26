// MULTI-SHOP AFFILIATE SYSTEM (PRO)
// Nieuwe versie naast bestaande file zodat niets breekt

window.AFFILIATE_PRODUCTS_V2 = {
  wemos_d1_mini: {
    name: "WeMos D1 Mini",
    description: "Compact ESP8266 ontwikkelbord voor Homeyduino en DIY projecten.",
    images: [
      "assets/wemos-d1-mini-1.jpg",
      "assets/wemos-d1-mini-2.jpg",
      "assets/wemos-d1-mini-3.jpg",
      "assets/wemos-d1-mini-4.jpg",
      "assets/wemos-d1-mini-5.jpg",
      "assets/wemos-d1-mini-6.jpg"
    ],
    shops: [
      {
        name: "AliExpress",
        url: "https://s.click.aliexpress.com/e/_c3O1etpl",
        label: "Goedkoopste optie",
        badge: "€"
      },
      {
        name: "Bol.com",
        url: "",
        label: "Snelle levering NL",
        badge: "NL"
      },
      {
        name: "Amazon",
        url: "",
        label: "Snelle internationale levering",
        badge: "Prime"
      }
    ]
  }
};

window.renderAffiliateProductV2 = function(targetId, key) {
  const product = AFFILIATE_PRODUCTS_V2[key];
  const el = document.getElementById(targetId);
  if (!product || !el) return;

  const shopsHtml = product.shops
    .filter(s => s.url)
    .map(s => `
      <a href="${s.url}" target="_blank" rel="nofollow sponsored noopener"
         style="display:flex;justify-content:space-between;align-items:center;padding:12px;border-radius:12px;border:1px solid currentColor;margin-bottom:8px;text-decoration:none;font-weight:600;">
        <span>Bekijk op ${s.name}</span>
        <span style="font-size:.85rem;opacity:.8;">${s.label || ""} ${s.badge ? `(${s.badge})` : ""}</span>
      </a>
    `).join("");

  el.innerHTML = `
    <div style="border:1px solid rgba(255,255,255,.1);padding:20px;border-radius:16px;">
      <h3>${product.name}</h3>
      <p>${product.description}</p>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
        ${product.images.map(img => `<img src="${img}" style="width:100%;border-radius:8px;">`).join("")}
      </div>
      <div style="margin-top:16px;">${shopsHtml}</div>
    </div>
  `;
};