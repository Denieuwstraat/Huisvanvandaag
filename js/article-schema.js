(function () {
  const SITE_URL = "https://www.huisvanvandaag.nl";
  const ORGANIZATION_ID = `${SITE_URL}/#organization`;
  const WEBSITE_ID = `${SITE_URL}/#website`;
  const AUTHOR_ID = `${SITE_URL}/#mike-mulders`;

  function getMeta(name) {
    const el = document.querySelector(`meta[name="${name}"]`);
    return el ? (el.getAttribute("content") || "").trim() : "";
  }

  function getPropertyMeta(property) {
    const el = document.querySelector(`meta[property="${property}"]`);
    return el ? (el.getAttribute("content") || "").trim() : "";
  }

  function absoluteUrl(value) {
    if (!value) return "";

    try {
      return new URL(value, `${SITE_URL}/`).href;
    } catch {
      return "";
    }
  }

  function getCanonicalUrl() {
    const canonical = document.querySelector('link[rel="canonical"]');
    const href = canonical ? canonical.getAttribute("href") : "";

    return absoluteUrl(href) || window.location.href.split("#")[0];
  }

  function getPageTitle() {
    const h1 = document.querySelector("h1");

    if (h1 && h1.textContent.trim()) {
      return h1.textContent.trim();
    }

    return document.title
      .replace(/\s*\|\s*huisvanvandaag\.nl\s*$/i, "")
      .trim();
  }

  function getDescription() {
    return getMeta("description");
  }

  function getHeroImage() {
    const ogImage = absoluteUrl(getPropertyMeta("og:image"));
    if (ogImage) return ogImage;

    const heroImg = document.querySelector(
      ".project-hero-media img, .article-hero img"
    );

    if (!heroImg) return "";

    return absoluteUrl(heroImg.getAttribute("src"));
  }

  function getPublishDate() {
    return getMeta("publish_date");
  }

  function getModifiedDate() {
    return getMeta("modified_date") || getPublishDate();
  }

  function getVisibleText(selector) {
    const el = document.querySelector(selector);
    return el ? el.textContent.replace(/\s+/g, " ").trim() : "";
  }

  function getListItems(selector) {
    return Array.from(document.querySelectorAll(selector))
      .map((item) => item.textContent.replace(/\s+/g, " ").trim())
      .filter(Boolean);
  }

  function toItemList(items) {
    if (!items.length) return null;

    return {
      "@type": "ItemList",
      "itemListElement": items.map((name, index) => ({
        "@type": "ListItem",
        "position": index + 1,
        "name": name
      }))
    };
  }

  function getBreadcrumbs() {
    const items = [];
    const crumbs = document.querySelectorAll(
      ".breadcrumbs a, .breadcrumbs span"
    );

    crumbs.forEach((crumb) => {
      const text = crumb.textContent.trim();

      if (!text || text === "•") return;

      const item = {
        "@type": "ListItem",
        "position": items.length + 1,
        "name": text
      };

      if (crumb.tagName.toLowerCase() === "a") {
        const href = absoluteUrl(crumb.getAttribute("href"));
        if (href) item.item = href;
      } else {
        item.item = getCanonicalUrl();
      }

      items.push(item);
    });

    if (items.length < 2) return null;

    return {
      "@type": "BreadcrumbList",
      "@id": `${getCanonicalUrl()}#breadcrumb`,
      "itemListElement": items
    };
  }

  function getArticleType() {
    return getMeta("hv-schema-type").toLowerCase();
  }

  function getArticleBase(types) {
    const url = getCanonicalUrl();
    const image = getHeroImage();
    const publishDate = getPublishDate();
    const modifiedDate = getModifiedDate();

    const schema = {
      "@type": types,
      "@id": `${url}#article`,
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": url
      },
      "isPartOf": {
        "@id": WEBSITE_ID
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

    if (publishDate) {
      schema.datePublished = publishDate;
    }

    if (modifiedDate) {
      schema.dateModified = modifiedDate;
    }

    return schema;
  }

  function getHowToSteps() {
    const steps = [];

    const stepHeadings = Array.from(
      document.querySelectorAll(".project-article h3, article h3")
    ).filter((heading) =>
      /^\s*\d+\s*[.)-]\s*/.test(heading.textContent)
    );

    stepHeadings.forEach((heading, index) => {
      const rawTitle = heading.textContent.replace(/\s+/g, " ").trim();
      const title = rawTitle
        .replace(/^\s*\d+\s*[.)-]\s*/, "")
        .trim();

      const textParts = [];
      let current = heading.nextElementSibling;

      while (current && !["H2", "H3"].includes(current.tagName)) {
        if (
          ["P", "UL", "OL"].includes(current.tagName) ||
          current.classList.contains("tutorial-check")
        ) {
          const text = current.textContent
            .replace(/\s+/g, " ")
            .trim();

          if (text) {
            textParts.push(text);
          }
        }

        current = current.nextElementSibling;
      }

      const text = textParts.join(" ").trim();

      if (!title || !text) return;

      steps.push({
        "@type": "HowToStep",
        "position": index + 1,
        "name": title,
        "text": text
      });
    });

    return steps;
  }

  function createHowToArticleSchema() {
    const schema = getArticleBase(["Article", "HowTo"]);
    const steps = getHowToSteps();

    if (steps.length > 0) {
      schema.step = steps;
    }

    return schema;
  }

  function createTechArticleSchema() {
    return getArticleBase(["Article", "TechArticle"]);
  }

  function parseReviewRating() {
    const raw = getVisibleText(".review-score-value");
    if (!raw) return null;

    const fractionMatch = raw.match(
      /(\d+(?:[.,]\d+)?)\s*\/\s*(\d+(?:[.,]\d+)?)/
    );

    if (fractionMatch) {
      const ratingValue = Number(
        fractionMatch[1].replace(",", ".")
      );

      const bestRating = Number(
        fractionMatch[2].replace(",", ".")
      );

      if (
        Number.isFinite(ratingValue) &&
        Number.isFinite(bestRating) &&
        bestRating > 0 &&
        ratingValue >= 0 &&
        ratingValue <= bestRating
      ) {
        return {
          "@type": "Rating",
          "ratingValue": ratingValue,
          "bestRating": bestRating,
          "worstRating": 0
        };
      }
    }

    const percentageMatch = raw.match(
      /(\d+(?:[.,]\d+)?)\s*%/
    );

    if (percentageMatch) {
      const ratingValue = Number(
        percentageMatch[1].replace(",", ".")
      );

      if (
        Number.isFinite(ratingValue) &&
        ratingValue >= 0 &&
        ratingValue <= 100
      ) {
        return {
          "@type": "Rating",
          "ratingValue": ratingValue,
          "bestRating": 100,
          "worstRating": 0
        };
      }
    }

    return null;
  }

  function createReviewProductSchema() {
    const url = getCanonicalUrl();
    const image = getHeroImage();

    const productName =
      getMeta("hv-product-name") ||
      getPageTitle();

    const publishDate = getPublishDate();
    const modifiedDate = getModifiedDate();

    const positiveNotes = toItemList(
      getListItems("#pluspunten + ul li")
    );

    const negativeNotes = toItemList(
      getListItems("#minpunten + ul li")
    );

    const reviewBody =
      getVisibleText("#kort-oordeel + p") ||
      getVisibleText("#conclusie + p") ||
      getDescription();

    const review = {
      "@type": "Review",
      "@id": `${url}#review`,
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
      }
    };

    const rating = parseReviewRating();

    if (rating) {
      review.reviewRating = rating;
    }

    if (reviewBody) {
      review.reviewBody = reviewBody;
    }

    if (positiveNotes) {
      review.positiveNotes = positiveNotes;
    }

    if (negativeNotes) {
      review.negativeNotes = negativeNotes;
    }

    if (publishDate) {
      review.datePublished = publishDate;
    }

    if (modifiedDate) {
      review.dateModified = modifiedDate;
    }

    const product = {
      "@type": "Product",
      "@id": `${url}#product`,
      "name": productName,
      "description": getDescription(),
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": url
      },
      "isPartOf": {
        "@id": WEBSITE_ID
      },
      "review": review
    };

    if (image) {
      product.image = [image];
    }

    return product;
  }

  function injectSchemas(nodes) {
    const cleanNodes = nodes.filter(Boolean);

    if (cleanNodes.length === 0) return;

    const schema = {
      "@context": "https://schema.org",
      "@graph": cleanNodes
    };

    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.textContent = JSON.stringify(schema, null, 2);

    document.head.appendChild(script);
  }

  const schemaType = getArticleType();
  const schemas = [];

  const breadcrumbSchema = getBreadcrumbs();

  if (breadcrumbSchema) {
    schemas.push(breadcrumbSchema);
  }

  if (schemaType === "howto") {
    schemas.push(createHowToArticleSchema());
  } else if (schemaType === "techarticle") {
    schemas.push(createTechArticleSchema());
  } else if (schemaType === "review") {
    schemas.push(createReviewProductSchema());
  }

  injectSchemas(schemas);
})();