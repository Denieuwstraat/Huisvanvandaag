(function () {
  const SITE_URL = "https://huisvanvandaag.nl";
  const ORGANIZATION_ID = `${SITE_URL}/#organization`;
  const AUTHOR_ID = `${SITE_URL}/#mike-mulders`;

  function getMeta(name) {
    const el = document.querySelector(`meta[name="${name}"]`);
    return el ? el.getAttribute("content")?.trim() : "";
  }

  function getCanonicalUrl() {
    const canonical = document.querySelector('link[rel="canonical"]');
    return canonical?.href || window.location.href.split("#")[0];
  }

  function getPageTitle() {
    const h1 = document.querySelector("h1");
    return h1?.textContent.trim() || document.title.replace(" | huisvanvandaag.nl", "").trim();
  }

  function getDescription() {
    return getMeta("description");
  }

  function getHeroImage() {
    const heroImg = document.querySelector(".project-hero-media img, .article-hero img");
    if (!heroImg) return null;

    return new URL(heroImg.getAttribute("src"), SITE_URL).href;
  }

  function getBreadcrumbs() {
    const items = [];
    const crumbs = document.querySelectorAll(".breadcrumbs a, .breadcrumbs span");

    crumbs.forEach((crumb) => {
      const text = crumb.textContent.trim();

      if (!text || text === "•") return;

      const link = crumb.tagName.toLowerCase() === "a"
        ? new URL(crumb.getAttribute("href"), SITE_URL).href
        : getCanonicalUrl();

      items.push({
        "@type": "ListItem",
        "position": items.length + 1,
        "name": text,
        "item": link
      });
    });

    if (items.length < 2) return null;

    return {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "@id": `${getCanonicalUrl()}#breadcrumb`,
      "itemListElement": items
    };
  }

  function getArticleType() {
    return getMeta("hv-schema-type").toLowerCase();
  }

  function getArticleBase(type) {
    const url = getCanonicalUrl();
    const image = getHeroImage();

    const schema = {
      "@context": "https://schema.org",
      "@type": type,
      "@id": `${url}#article`,
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": url
      },
      "headline": getPageTitle(),
      "description": getDescription(),
      "url": url,
      "inLanguage": "nl-NL",
      "author": {
        "@id": AUTHOR_ID
      },
      "publisher": {
        "@id": ORGANIZATION_ID
      }
    };

    if (image) {
      schema.image = [image];
    }

    return schema;
  }

  function getHowToSteps() {
    const steps = [];
    const stepHeadings = document.querySelectorAll("article h3");

    stepHeadings.forEach((heading) => {
      const title = heading.textContent.trim();
      if (!title) return;

      let textParts = [];
      let current = heading.nextElementSibling;

      while (current && !["H2", "H3"].includes(current.tagName)) {
        if (current.tagName === "P" || current.tagName === "UL" || current.tagName === "OL") {
          textParts.push(current.textContent.trim());
        }
        current = current.nextElementSibling;
      }

      const text = textParts.join(" ").replace(/\s+/g, " ").trim();

      if (text) {
        steps.push({
          "@type": "HowToStep",
          "name": title,
          "text": text
        });
      }
    });

    return steps;
  }

  function createHowToSchema() {
    const schema = getArticleBase("HowTo");
    const steps = getHowToSteps();

    if (steps.length > 0) {
      schema.step = steps;
    }

    return schema;
  }

  function createTechArticleSchema() {
    return getArticleBase("TechArticle");
  }

  function createReviewSchema() {
    const url = getCanonicalUrl();

    return {
      "@context": "https://schema.org",
      "@type": "Review",
      "@id": `${url}#review`,
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": url
      },
      "name": getPageTitle(),
      "headline": getPageTitle(),
      "description": getDescription(),
      "url": url,
      "inLanguage": "nl-NL",
      "author": {
        "@id": AUTHOR_ID
      },
      "publisher": {
        "@id": ORGANIZATION_ID
      },
      "itemReviewed": {
        "@type": "Product",
        "name": getMeta("hv-product-name") || getPageTitle()
      }
    };
  }

  function injectSchemas(schemas) {
    const cleanSchemas = schemas.filter(Boolean);

    if (cleanSchemas.length === 0) return;

    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.text = JSON.stringify(cleanSchemas, null, 2);
    document.head.appendChild(script);
  }

  const schemaType = getArticleType();
  const schemas = [];

  const breadcrumbSchema = getBreadcrumbs();
  if (breadcrumbSchema) schemas.push(breadcrumbSchema);

  if (schemaType === "howto") {
    schemas.push(createHowToSchema());
  }

  if (schemaType === "techarticle") {
    schemas.push(createTechArticleSchema());
  }

  if (schemaType === "review") {
    schemas.push(createReviewSchema());
  }

  injectSchemas(schemas);
})();