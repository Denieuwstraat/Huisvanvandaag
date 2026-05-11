(function () {
  const schemas = [
    {
      "@context": "https://schema.org",
      "@type": "Organization",
      "@id": "https://huisvanvandaag.nl/#organization",
      "name": "Huis van Vandaag",
      "url": "https://huisvanvandaag.nl",
      "logo": {
        "@type": "ImageObject",
        "url": "https://www.huisvanvandaag.nl/assets/logo-white.png"
      },
      "description": "Persoonlijk kennisplatform over smart home, Homey, Homeyduino, ESP8266, ESP32 en DIY smart home projecten.",
      "founder": {
        "@id": "https://huisvanvandaag.nl/#mike-mulders"
      },
      "knowsAbout": [
        "Homey",
        "Homeyduino",
        "ESP8266",
        "ESP32",
        "DIY sensoren",
        "Smart home automatisering",
        "DIY smart home projecten",
        "Slimme woningautomatisering",
        "Praktische Homey automatisering"
      ]
    },

    {
      "@context": "https://schema.org",
      "@type": "WebSite",
      "@id": "https://huisvanvandaag.nl/#website",
      "url": "https://huisvanvandaag.nl",
      "name": "Huis van Vandaag",
      "description": "Praktische uitleg, DIY-projecten en tutorials over smart home, Homey, Homeyduino en zelfbouwsensoren.",
      "publisher": {
        "@id": "https://huisvanvandaag.nl/#organization"
      },
      "author": {
        "@id": "https://huisvanvandaag.nl/#mike-mulders"
      },
      "inLanguage": "nl-NL"
    },

    {
      "@context": "https://schema.org",
      "@type": "Person",
      "@id": "https://huisvanvandaag.nl/#mike-mulders",
      "name": "Mike Mulders",
      "url": "https://huisvanvandaag.nl",
      "worksFor": {
        "@id": "https://huisvanvandaag.nl/#organization"
      },
      "affiliation": {
        "@id": "https://huisvanvandaag.nl/#organization"
      },
      "knowsAbout": [
        "Homey",
        "Homeyduino",
        "ESP8266",
        "ESP32",
        "Wemos D1 Mini",
        "DIY smart home",
        "Smart home automatisering",
        "Slimme sensoren",
        "IoT automatisering",
        "Homey flows"
      ]
    }
  ];

  const script = document.createElement("script");
  script.type = "application/ld+json";
  script.text = JSON.stringify(schemas);
  document.head.appendChild(script);
})();