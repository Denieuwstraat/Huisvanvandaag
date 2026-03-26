# Beginnergids: bouw je eerste slimme sensor met Homeyduino

## Introductie
Zelf een sensor bouwen klinkt misschien ingewikkeld, maar met de juiste stappen kan iedereen het. Op de DIY‑pagina wordt benadrukt dat projecten met betaalbare hardware, Homeyduino en een beetje creativiteit oplossingen bieden die je niet zomaar in de winkel vindt【614465383051354†L38-L46】. Deze gids leidt je door het proces van je eerste Homeyduino‑sensor, gebaseerd op de principes van goede tutorials: eerst het doel, dan de techniek en altijd een praktijkvoorbeeld【82555473540639†L26-L27】.

## Waarom zelf bouwen?
Een zelfgebouwde sensor is vaak goedkoper en flexibeler dan een kant‑en‑klare oplossing. Je kunt de sensor aanpassen aan jouw wensen en hem naadloos integreren met Homey. Eenvoudige projectvoorbeelden zijn een deur‑ en raamsensor om meldingen te ontvangen wanneer een deur opengaat【198064767084510†L59-L63】 of een CO₂‑sensor om de ventilatie aan te sturen【177584658689336†L167-L169】. Zelfbouw geeft je controle over de hardware en laat je snel schakelen tussen ideeën.

## Wat ga je bouwen?
In deze gids bouwen we een eenvoudige contact‑sensor met een magneetschakelaar en een Wemos D1 Mini (ESP8266). Deze sensor meldt via Homeyduino of een deur open of dicht is en kan flows starten zoals verlichting inschakelen of meldingen versturen. Je kunt dezelfde stappen gebruiken voor andere sensoren, zoals temperatuur, licht of luchtkwaliteit.

## Benodigdheden
- **Wemos D1 Mini of NodeMCU** – een ESP8266‑board dat via WiFi communiceert met Homey.
- **Magneetschakelaar (reed switch)** – detecteert of een deur of raam open of dicht is.
- **Een paar Dupont‑kabels en eventueel een breadboard**.
- **Homey met de Homeyduino‑app geïnstalleerd**.

<div id="affiliate-benodigdheden-beginner"></div>

<script>
renderAffiliateRequirementsListV2("affiliate-benodigdheden-beginner", {
  title: "Benodigdheden",
  intro: "Met deze onderdelen kun je de sensor uit deze gids direct nabouwen.",
  products: ["wemos_d1_mini"]
});
</script>

## Stap‑voor‑stap uitleg

1. **Reed‑switch aansluiten** – Verbind één kant van de reed‑switch met de grond (GND) en de andere kant met een digitale pin (bijvoorbeeld D2) op de Wemos D1 Mini. Sluit ook 3.3 V aan op de andere kant van de reed‑switch via een pull‑up‑weerstand indien nodig.
2. **Installeer software** – Installeer de Arduino IDE en de Homeyduino‑bibliotheek. Zorg ervoor dat je het juiste board (Wemos D1 Mini) hebt geselecteerd voordat je code uploadt.
3. **Schrijf de code** – Gebruik een eenvoudige sketch die de digitale pin uitleest en de status doorstuurt naar Homey. In de deur‑ en raamsensor‑gids staat een voorbeeld voor het versturen van een `alarm_contact`‑capability【198064767084510†L83-L88】.
4. **Upload de code** – Vul je wifi‑gegevens in en upload de sketch via USB naar het board. Zodra de sensor verbinding heeft, verschijnt hij in Homey onder de categorie ‘sensoren’.
5. **Maak flows in Homey** – Maak een nieuwe flow die een pushmelding stuurt wanneer de sensor een ‘open’ status doorgeeft【198064767084510†L83-L88】, of die de verlichting inschakelt wanneer je de deur opent. Bedenk een doel en laat je techniek daarop aansluiten【82555473540639†L26-L27】.

## Tips en aandachtspunten
- **Test op een breadboard** – Bouw eerst op een breadboard voordat je alles permanent monteert. Zo kun je eenvoudig aanpassen.
- **Gebruik kleine sensoren** – Sensoren zoals de DHT11 of MH‑Z19B zijn eenvoudig te integreren met de Wemos D1 Mini. Zie de andere projecten op deze site voor voorbeelden【177584658689336†L193-L201】.
- **Verplaatsbaar** – Houd de sensor compact zodat je hem kunt verplaatsen en testen op verschillende locaties.
- **Flows verbeteren** – Combineer meerdere sensoren voor context. Bijvoorbeeld: laat het licht alleen aangaan bij deur‑opening als het donker is (gebruik een LDR voor lichtmeting).

## Conclusie
Een slimme sensor bouwen met Homeyduino is eenvoudiger dan veel mensen denken. Door stap voor stap te werken creëer je binnen korte tijd een sensor die perfect aansluit bij jouw leefritme. Met de basisprincipes uit deze gids kun je ook andere sensoren bouwen, zoals een CO₂‑meter of een multi‑sensor die meerdere waarden meet【177584658689336†L193-L201】.

## Verder lezen
 - **[Deur‑ en raamsensor project](/articles/diy/homeyduino-deur-raamsensor.md)** – uitgebreid artikel over het bouwen van een reed‑switch‑sensor met flows【198064767084510†L59-L63】.
 - **[Licht‑ en temperatuursensor](/articles/diy/homeyduino-licht-temperatuur-sensor.md)** – combineer licht en temperatuur voor contextgevoelige flows【185316766573532†L62-L66】.
 - **[Goede CO₂‑waarde](/articles/seo/goede-co2-waarde.md)** – leer welke CO₂‑waarde gezond is en waarom ventileren belangrijk is【177584658689336†L214-L214】.