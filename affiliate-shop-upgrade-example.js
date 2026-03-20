// Voorbeeldstructuur voor producten met meerdere shops.
// Dit bestand is alleen als referentie toegevoegd.
// De uiteindelijke upgrade van affiliate-products.js en affiliate-components.js
// kan daarna hierop worden gebaseerd.

window.AFFILIATE_MULTI_SHOP_EXAMPLE = {
  wemos_d1_mini: {
    name: "WeMos D1 Mini",
    description: "Compact ESP8266 ontwikkelbord voor Homeyduino, sensoren en DIY smart home projecten.",
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
        key: "aliexpress",
        name: "AliExpress",
        url: "https://s.click.aliexpress.com/e/_c3O1etpl",
        label: "Budgetkeuze"
      },
      {
        key: "bol",
        name: "Bol.com",
        url: "",
        label: "Sneller in huis"
      },
      {
        key: "amazon",
        name: "Amazon.com",
        url: "",
        label: "Internationale optie"
      }
    ]
  }
};
