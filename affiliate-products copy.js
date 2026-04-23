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

  const imageCount = Array.isArray(product.images) ? product.images.length : 0;
  const sliderId = `slider-${targetId}`;

  const slidesHtml = (product.images || [])
    .map(
      (img, index) => `
        <div
          class="affiliate-slide"
          data-slide-index="${index}"
          style="
            display:${index === 0 ? "block" : "none"};
            text-align:center;
          "
        >
          <img
            src="${img}"
            alt="${product.name} afbeelding ${index + 1}"
            loading="lazy"
            style="
              width:75%;
              max-width:520px;
              height:auto;
              border-radius:12px;
              display:block;
              margin:0 auto;
            "
          >
        </div>
      `
    )
    .join("");

  const dotsHtml =
    imageCount > 1
      ? `
        <div
          class="affiliate-slider-dots"
          style="
            display:flex;
            justify-content:center;
            gap:8px;
            margin-top:12px;
            flex-wrap:wrap;
          "
        >
          ${(product.images || [])
            .map(
              (_, index) => `
                <button
                  type="button"
                  class="affiliate-slider-dot"
                  data-dot-index="${index}"
                  aria-label="Ga naar afbeelding ${index + 1}"
                  style="
                    width:10px;
                    height:10px;
                    border-radius:999px;
                    border:none;
                    cursor:pointer;
                    padding:0;
                    opacity:${index === 0 ? "1" : ".4"};
                    background:currentColor;
                  "
                ></button>
              `
            )
            .join("")}
        </div>
      `
      : "";

  const sliderHtml = imageCount
    ? `
      <div class="affiliate-slider" id="${sliderId}" data-current-index="0" style="margin:16px 0;">
        <div
          class="affiliate-slider-viewport"
          style="
            position:relative;
            touch-action:pan-y;
            user-select:none;
          "
        >
          ${slidesHtml}
          ${
            imageCount > 1
              ? `
                <button
                  type="button"
                  class="affiliate-slider-prev"
                  aria-label="Vorige afbeelding"
                  style="
                    position:absolute;
                    top:50%;
                    left:10px;
                    transform:translateY(-50%);
                    border:none;
                    border-radius:999px;
                    padding:10px 12px;
                    cursor:pointer;
                    background:rgba(0,0,0,.6);
                    color:#fff;
                    font-size:18px;
                    line-height:1;
                  "
                >‹</button>
                <button
                  type="button"
                  class="affiliate-slider-next"
                  aria-label="Volgende afbeelding"
                  style="
                    position:absolute;
                    top:50%;
                    right:10px;
                    transform:translateY(-50%);
                    border:none;
                    border-radius:999px;
                    padding:10px 12px;
                    cursor:pointer;
                    background:rgba(0,0,0,.6);
                    color:#fff;
                    font-size:18px;
                    line-height:1;
                  "
                >›</button>
              `
              : ""
          }
        </div>

        ${
          imageCount > 1
            ? `
              <div
                class="affiliate-slider-counter"
                style="
                  margin-top:10px;
                  text-align:center;
                  font-size:.9rem;
                  opacity:.8;
                "
              >1 / ${imageCount}</div>
            `
            : ""
        }

        ${dotsHtml}
      </div>
    `
    : "";

  const shopsHtml = (product.shops || [])
    .filter(shop => shop.url)
    .map(
      shop => `
        <a
          href="${shop.url}"
          target="_blank"
          rel="nofollow sponsored noopener"
          style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            padding:12px;
            border-radius:12px;
            border:1px solid currentColor;
            margin-bottom:8px;
            text-decoration:none;
            font-weight:600;
          "
        >
          <span>Bekijk op ${shop.name}</span>
          <span style="font-size:.85rem;opacity:.8;">
            ${shop.label || ""} ${shop.badge ? `(${shop.badge})` : ""}
          </span>
        </a>
      `
    )
    .join("");

  target.innerHTML = `
    <section
      class="affiliate-product-card"
      style="
        border:1px solid rgba(255,255,255,.12);
        border-radius:18px;
        padding:20px;
        margin:24px 0;
        background:rgba(255,255,255,.03);
      "
    >
      <h3 style="margin-top:0;">${product.name}</h3>
      ${product.description ? `<p>${product.description}</p>` : ""}
      ${sliderHtml}
      ${shopsHtml ? `<div style="margin-top:16px;">${shopsHtml}</div>` : ""}
      <p style="font-size:.9rem;opacity:.8;margin-top:16px;margin-bottom:0;">
        Dit blok bevat affiliate links. Bij aankoop ontvangen wij mogelijk een kleine commissie zonder extra kosten voor jou.
      </p>
    </section>
  `;

  if (imageCount <= 1) return;

  const slider = target.querySelector(`#${CSS.escape(sliderId)}`);
  if (!slider) return;

  const slides = Array.from(slider.querySelectorAll(".affiliate-slide"));
  const dots = Array.from(slider.querySelectorAll(".affiliate-slider-dot"));
  const counter = slider.querySelector(".affiliate-slider-counter");
  const prevButton = slider.querySelector(".affiliate-slider-prev");
  const nextButton = slider.querySelector(".affiliate-slider-next");
  const viewport = slider.querySelector(".affiliate-slider-viewport");

  let touchStartX = 0;
  let touchEndX = 0;

  const updateSlider = (newIndex) => {
    const normalizedIndex = (newIndex + slides.length) % slides.length;
    slider.dataset.currentIndex = String(normalizedIndex);

    slides.forEach((slide, index) => {
      slide.style.display = index === normalizedIndex ? "block" : "none";
    });

    dots.forEach((dot, index) => {
      dot.style.opacity = index === normalizedIndex ? "1" : ".4";
    });

    if (counter) {
      counter.textContent = `${normalizedIndex + 1} / ${slides.length}`;
    }
  };

  prevButton?.addEventListener("click", () => {
    const currentIndex = Number(slider.dataset.currentIndex || 0);
    updateSlider(currentIndex - 1);
  });

  nextButton?.addEventListener("click", () => {
    const currentIndex = Number(slider.dataset.currentIndex || 0);
    updateSlider(currentIndex + 1);
  });

  dots.forEach((dot) => {
    dot.addEventListener("click", () => {
      const index = Number(dot.dataset.dotIndex || 0);
      updateSlider(index);
    });
  });

  viewport?.addEventListener("touchstart", (event) => {
    touchStartX = event.changedTouches[0].clientX;
  }, { passive: true });

  viewport?.addEventListener("touchend", (event) => {
    touchEndX = event.changedTouches[0].clientX;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) < 40) return;

    const currentIndex = Number(slider.dataset.currentIndex || 0);

    if (diff > 0) {
      updateSlider(currentIndex + 1);
    } else {
      updateSlider(currentIndex - 1);
    }
  }, { passive: true });
};