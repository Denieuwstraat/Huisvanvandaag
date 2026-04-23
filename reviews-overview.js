(function () {
  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function slugify(value) {
    return String(value || "")
      .toLowerCase()
      .trim()
      .replace(/\s+/g, "-")
      .replace(/[^\w-]/g, "");
  }

  function getReviews() {
    if (!Array.isArray(window.HVV_REVIEWS)) return [];
    return window.HVV_REVIEWS.slice();
  }

  function createFilterButtons(reviews) {
    const categories = [...new Set(reviews.map((r) => r.category).filter(Boolean))].sort();

    const filters = [
      { key: "all", label: "Alles" },
      ...categories.map((category) => ({
        key: slugify(category),
        label: category
      }))
    ];

    return filters.map((filter) => {
      const activeClass = filter.key === "all" ? " active" : "";
      return `
        <button class="review-filter-chip${activeClass}" type="button" data-filter="${escapeHtml(filter.key)}">
          ${escapeHtml(filter.label)}
        </button>
      `;
    }).join("");
  }

  function createReviewCard(review) {
    return `
      <article class="panel review-card" data-category="${escapeHtml(slugify(review.category))}">
        <a class="review-card-image-link" href="${escapeHtml(review.slug)}" aria-label="${escapeHtml(review.title)}">
          <img
            class="review-card-image"
            src="${escapeHtml(review.image)}"
            alt="${escapeHtml(review.imageAlt || review.title)}"
            loading="lazy"
          >
        </a>

        <div class="review-card-body">
          <div class="review-card-meta">
            <span class="meta-pill">Categorie: ${escapeHtml(review.category)}</span>
            <span class="meta-pill">Platform: ${escapeHtml(review.platform)}</span>
            <span class="meta-pill">Type: ${escapeHtml(review.productType)}</span>
          </div>

          <h3 class="review-card-title">
            <a href="${escapeHtml(review.slug)}">${escapeHtml(review.title)}</a>
          </h3>

          <p class="muted review-card-text">${escapeHtml(review.excerpt)}</p>

          <div class="review-card-footer">
            <span class="review-score-badge">${escapeHtml(review.score)}</span>
            <a class="button button-primary" href="${escapeHtml(review.slug)}">Lees review</a>
          </div>
        </div>
      </article>
    `;
  }

  function renderFeaturedReviews(reviews) {
    const featured = reviews.filter((review) => review.featured);
    if (!featured.length) return "";

    return `
      <section class="section-tight">
        <div class="container">
          <div class="section-heading">
            <h2>Uitgelichte reviews</h2>
            <p class="muted">Een snelle selectie van reviews die op dit moment extra interessant zijn.</p>
          </div>
          <div class="review-grid">
            ${featured.map(createReviewCard).join("")}
          </div>
        </div>
      </section>
    `;
  }

  function renderAllReviews(reviews) {
    return `
      <section class="section-tight">
        <div class="container">
          <div class="section-heading">
            <h2>Alle reviews</h2>
            <p class="muted">Eerlijke praktijkreviews van producten en systemen die relevant zijn voor een slimmer huis.</p>
          </div>

          <div class="review-filters" id="reviewFilters">
            ${createFilterButtons(reviews)}
          </div>

          <div class="review-grid" id="reviewGrid">
            ${reviews.map(createReviewCard).join("")}
          </div>
        </div>
      </section>
    `;
  }

  function initFilters() {
    const filters = document.getElementById("reviewFilters");
    const grid = document.getElementById("reviewGrid");
    if (!filters || !grid) return;

    const chips = filters.querySelectorAll("[data-filter]");
    const cards = grid.querySelectorAll(".review-card");

    chips.forEach((chip) => {
      chip.addEventListener("click", () => {
        const selected = chip.dataset.filter;

        chips.forEach((button) => button.classList.remove("active"));
        chip.classList.add("active");

        cards.forEach((card) => {
          const cardCategory = card.dataset.category;
          const shouldShow = selected === "all" || cardCategory === selected;
          card.style.display = shouldShow ? "" : "none";
        });
      });
    });
  }

  function renderReviewsOverview() {
    const mount = document.getElementById("reviews-overview");
    if (!mount) return;

    const reviews = getReviews();

    if (!reviews.length) {
      mount.innerHTML = `
        <section class="section-tight">
          <div class="container">
            <div class="panel">
              <h2>Nog geen reviews toegevoegd</h2>
              <p class="muted">Zodra de eerste reviews live staan, verschijnen ze hier automatisch.</p>
            </div>
          </div>
        </section>
      `;
      return;
    }

    mount.innerHTML = `
      ${renderFeaturedReviews(reviews)}
      ${renderAllReviews(reviews)}
    `;

    initFilters();
  }

  document.addEventListener("DOMContentLoaded", renderReviewsOverview);
})();