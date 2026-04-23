async function loadAffiliateProducts() {
  if (window.AFFILIATE_PRODUCTS) {
    return window.AFFILIATE_PRODUCTS;
  }

  const response = await fetch("affiliate-products.json", { cache: "no-cache" });
  if (!response.ok) {
    throw new Error(`Kon affiliate-products.json niet laden (${response.status})`);
  }

  const data = await response.json();
  window.AFFILIATE_PRODUCTS = data;
  return data;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function ensureAffiliateBlockDisclaimer(target) {
  if (!target) return;

  const block = target.closest(".affiliate-auto-block");
  if (!block) return;

  if (block.querySelector(".affiliate-disclaimer")) return;

  const note = document.createElement("p");
  note.className = "affiliate-disclaimer";
  note.textContent =
    "Dit blok bevat affiliate links. Bij aankoop ontvangen wij mogelijk een kleine commissie zonder extra kosten voor jou.";

  block.appendChild(note);
}

window.getAffiliateProduct = async function (key) {
  const products = await loadAffiliateProducts();
  return products[key] || null;
};

window.renderAffiliateProduct = async function (targetId, productKey) {
  const target = document.getElementById(targetId);
  if (!target) return;

  let product;
  try {
    product = await window.getAffiliateProduct(productKey);
  } catch (error) {
    console.error("Fout bij laden affiliate-producten:", error);
    return;
  }

  if (!product) {
    console.warn(`Affiliate-product niet gevonden: ${productKey}`);
    return;
  }

  const firstImage =
    Array.isArray(product.images) && product.images.length > 0
      ? product.images[0]
      : "";

  const shops = Array.isArray(product.shops)
    ? product.shops.filter((shop) => shop && shop.url)
    : [];

  const imageHtml = firstImage
    ? `
      <div class="affiliate-product-image">
        <img
          src="${escapeHtml(firstImage)}"
          alt="${escapeHtml(product.name)}"
          loading="lazy"
        >
      </div>
    `
    : "";

  const descriptionHtml = product.description
    ? `
      <div class="affiliate-product-description">
        <p>${escapeHtml(product.description)}</p>
      </div>
    `
    : "";

  const shopsHtml = shops.length
    ? `
      <div class="affiliate-shop-links">
        ${shops
          .map((shop) => {
            const badgeHtml = shop.badge
              ? `<span class="affiliate-shop-badge">${escapeHtml(shop.badge)}</span>`
              : "";

            const labelText = shop.label
              ? `<span class="affiliate-shop-label">${escapeHtml(shop.label)}</span>`
              : "";

            return `
              <a
                href="${escapeHtml(shop.url)}"
                target="_blank"
                rel="nofollow sponsored noopener"
                class="affiliate-shop-link"
                aria-label="Bekijk ${escapeHtml(product.name)} op ${escapeHtml(shop.name)}"
              >
                <span class="affiliate-shop-name">Bekijk op ${escapeHtml(shop.name)}</span>
                ${labelText}
                ${badgeHtml}
              </a>
            `;
          })
          .join("")}
      </div>
    `
    : "";

  target.innerHTML = `
    <section class="affiliate-product-card" aria-label="${escapeHtml(product.name)}">
      ${imageHtml}
      <div class="affiliate-product-content">
        <h4 class="affiliate-product-title">${escapeHtml(product.name)}</h4>
        ${descriptionHtml}
        ${shopsHtml}
      </div>
    </section>
  `;

  ensureAffiliateBlockDisclaimer(target);
};