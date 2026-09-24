(function () {
  const schema = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "@id": "https://www.huisvanvandaag.nl/#organization",
        "name": "HuisvanVandaag",
        "alternateName": "huisvanvandaag.nl",
        "url": "https://www.huisvanvandaag.nl/",
        "logo": {
          "@type": "ImageObject",
          "@id": "https://www.huisvanvandaag.nl/#logo",
          "url": "https://www.huisvanvandaag.nl/assets/logo-white.png",
          "contentUrl": "https://www.huisvanvandaag.nl/assets/logo-white.png"
        },
        "description": "Praktisch kennisplatform over smart home, Homey, Homeyduino, ESP8266, ESP32 en DIY smart home-projecten.",
        "founder": {
          "@id": "https://www.huisvanvandaag.nl/#mike-mulders"
        },
        "knowsAbout": [
          "Homey",
          "Homeyduino",
          "Matter",
          "Thread",
          "Zigbee",
          "ESP8266",
          "ESP32",
          "DIY smart home",
          "Slimme sensoren",
          "Smart home-automatisering"
        ]
      },
      {
        "@type": "WebSite",
        "@id": "https://www.huisvanvandaag.nl/#website",
        "url": "https://www.huisvanvandaag.nl/",
        "name": "HuisvanVandaag",
        "alternateName": "huisvanvandaag.nl",
        "description": "Praktische uitleg, DIY-projecten, tutorials en reviews over smart home, Homey, Homeyduino en zelfbouwsensoren.",
        "publisher": {
          "@id": "https://www.huisvanvandaag.nl/#organization"
        },
        "author": {
          "@id": "https://www.huisvanvandaag.nl/#mike-mulders"
        },
        "inLanguage": "nl-NL"
      },
      {
        "@type": "Person",
        "@id": "https://www.huisvanvandaag.nl/#mike-mulders",
        "name": "Mike Mulders",
        "url": "https://www.huisvanvandaag.nl/over.html",
        "mainEntityOfPage": {
          "@id": "https://www.huisvanvandaag.nl/over.html"
        },
        "affiliation": {
          "@id": "https://www.huisvanvandaag.nl/#organization"
        },
        "knowsAbout": [
          "Homey",
          "Homeyduino",
          "Matter",
          "Thread",
          "Zigbee",
          "ESP8266",
          "ESP32",
          "Wemos D1 Mini",
          "DIY smart home",
          "Smart home-automatisering",
          "Slimme sensoren",
          "IoT-automatisering",
          "Homey Flows"
        ]
      }
    ]
  };

  const script = document.createElement("script");
  script.type = "application/ld+json";
  script.textContent = JSON.stringify(schema);
  document.head.appendChild(script);
})();