// Aanvullende producten voor het PRO affiliate systeem
// Laad dit bestand NA affiliate-products-v2.js
//
// <script src="affiliate-products-v2.js"></script>
// <script src="affiliate-products-v2-addons.js"></script>
// <script src="affiliate-components-v3.js"></script>
//
// Let op:
// Voor de MH-Z19B-afbeeldingen is hieronder uitgegaan van een schone naamgeving:
// assets/mh-z19b-1.jpg t/m assets/mh-z19b-5.jpg
// Als jouw bestandsnamen anders zijn, pas ze hieronder aan of hernoem de bestanden in /assets.

window.AFFILIATE_PRODUCTS_V2 = window.AFFILIATE_PRODUCTS_V2 || {};

window.AFFILIATE_PRODUCTS_V2.mh_z19b = {
  name: "MH-Z19B / MH-Z19C CO₂ sensor",
  description: "Infrarood CO₂ sensor voor luchtkwaliteitsmetingen, ventilatieprojecten en Homey/Home Assistant DIY builds.",
  images: [
    "assets/mh-z19b-1.jpg",
    "assets/mh-z19b-2.jpg",
    "assets/mh-z19b-3.jpg",
    "assets/mh-z19b-4.jpg",
    "assets/mh-z19b-5.jpg"
  ],
  shops: [
    {
      name: "AliExpress",
      url: "https://s.click.aliexpress.com/e/_c3bDOH19",
      label: "Vaak de slimste keuze als prijs belangrijker is dan snelheid",
      badge: "€",
      recommended: true
    },
    {
      name: "Bol.com",
      url: "",
      label: "Fijn als je liever bij een bekende NL-shop bestelt",
      badge: "NL"
    },
    {
      name: "Amazon",
      url: "",
      label: "Handig als je snelheid of internationale beschikbaarheid zoekt",
      badge: "Prime"
    }
  ]
};
