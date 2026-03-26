# Homeyduino relay switch: maak je oude apparaten slim

Veel slimme stekkers zijn relatief duur en beperken je tot kant‑en‑klare oplossingen.  Toch wil je misschien juist bestaande apparaten – de tuinverlichting, een koffiezetapparaat of een buiten‑televisie – op afstand kunnen inschakelen en zelfs met je stem bedienen.  Met een eenvoudige relay op een Wemos D1 Mini bouw je in een middag een slimme schakelaar die je direct in Homey en Google Assistant kunt gebruiken.  Het project laat zien hoe snel je met zelfbouw tastbaar resultaat krijgt【430889073424816†L45-L48】.

## Wat ga je bouwen

Je maakt een compacte Homeyduino‑opstelling waarmee je één kanaal aan of uit kunt schakelen.  De Wemos D1 Mini stuurt een één‑kanaals relay aan; Homey ziet het project als een schakelaar en Google Assistant kan dezelfde schakelaar via Homey activeren.  Met flows koppel je deze schakelaar aan andere gebeurtenissen, bijvoorbeeld zodat de televisie in de tuin alleen aangaat als de buitendeuren open staan.  Belangrijk om te weten: omdat je rechtstreeks met netspanning werkt, draait dit project vooral om goede bedrading en een veilige behuizing【430889073424816†L49-L50】.

## Benodigdheden

* Wemos D1 Mini of NodeMCU (ESP8266‑bord) – het ‘brein’ van de schakelaar
* Eén‑kanaals relaymodule (5 V) – om het apparaat daadwerkelijk te schakelen
* USB‑C‑voeding (5 V) voor de Wemos
* Homey met de Homeyduino‑app geïnstalleerd
* Arduino IDE voor het uploaden van de sketch

<div id="affiliate-benodigdheden-relay"></div>

<script>
renderAffiliateRequirementsListV2("affiliate-benodigdheden-relay", {
  title: "Benodigdheden",
  intro: "Met deze onderdelen bouw je snel een veilige en betrouwbare schakelaar.",
  products: ["wemos_d1_mini"]
});
</script>

## Stap‑voor‑stap uitleg

### 1. Sluit de relay aan

Verbind de relaymodule met de Wemos D1 Mini.  Gebruik bij voorkeur een kant‑en‑klaar relay‑shield dat op de Wemos past; dat maakt de bedrading overzichtelijk.  Werk **nooit** onder spanning en zorg voor een goede trekontlasting en degelijke behuizing【430889073424816†L49-L50】.  In het eenvoudigste geval verbind je:

* IN van de relay → D1 (GPIO 5) op de Wemos
* VCC van de relay → 5 V op de Wemos
* GND van de relay → GND op de Wemos

De schakeldraden van het apparaat dat je wilt bedienen sluit je aan op de `COM`– en `NO`–klemmen van de relay (sluit het apparaat aan op de `NO` voor een normaal open schakeling).

### 2. Installeer de software

Installeer de Arduino IDE en voeg de **ESP8266‑boards** en de **Homeyduino‑bibliotheek** toe via het menu *Hulpmiddelen → Boardbeheer*.  Kies daarna het juiste board (`LOLIN (Wemos) D1 R2 & Mini`).

### 3. Upload de code

Gebruik onderstaande sketch als basis.  Vervang `<SSID>` en `<PASSWORD>` door je eigen wifi‑gegevens.  De code definieert een schakelaar met de capability `onoff` en reageert op wijzigingen van die capability door het relay‑relais te schakelen.  De `LOW`/`HIGH` logica kan per relay verschillen; test wat in jouw geval de juiste logica is.

```cpp
#include <ESP8266WiFi.h>
#include <Homey.h>

const int RELAY_PIN = D1;   // pin waarop de relay is aangesloten
bool state = false;         // huidige schakelstand

void wifi() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin("<SSID>", "<PASSWORD>");
    uint8_t timeout = 30;
    while (WiFi.status() != WL_CONNECTED && timeout > 0) {
      delay(500);
      timeout--;
    }
  }
}

void setup() {
  Serial.begin(9600);
  Homey.begin("Relay switch");
  Homey.setClass("socket");
  Homey.addCapability("onoff");
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // standaard uit (afhankelijk van je module)
}

void loop() {
  wifi();
  Homey.loop();
  bool newState = Homey.getCapabilityValue("onoff");
  if (newState != state) {
    state = newState;
    // Zet het relay op LOW om aan te schakelen en HIGH om uit te schakelen
    digitalWrite(RELAY_PIN, state ? LOW : HIGH);
  }
  delay(10);
}
```

Upload de code via *Hulpmiddelen → Board* en kies het juiste board.  Selecteer daarna *Uploaden* in de Arduino IDE.  Wanneer het uploaden voltooid is, sluit je de Wemos weer aan op de voeding.

### 4. Voeg de sensor toe aan Homey

Open de Homey‑app en gebruik de **Homeyduino**‑app om het nieuwe apparaat toe te voegen.  Kies het apparaat met de naam “Relay switch”.  Je ziet een eenvoudige aan/uit‑schakelaar verschijnen.  Je kunt deze schakelaar ook koppelen aan Google Assistant zodat je het apparaat met je stem kunt bedienen.

### 5. Maak flows en test

Test de schakelaar via de Homey‑app.  Schakel het apparaat een paar keer in en uit en controleer dat het relay klikt en het aangesloten apparaat reageert.  Maak vervolgens een flow waarin de schakelaar automatisch wordt ingeschakeld, bijvoorbeeld wanneer de zon ondergaat of wanneer een deur opengaat.  Zo haal je het meeste uit de zelfgebouwde schakelaar.

## Praktisch gebruik

In de tuin wordt deze relay ingezet om een televisie op het terras te schakelen.  Met een eenvoudige flow wordt de televisie automatisch ingeschakeld zodra het terras wordt gebruikt, en uitgeschakeld bij vertrek.  De koppeling met Google Assistant maakt het mogelijk om handsfree te roepen “Oké Google, zet de tuin‑tv aan”.  Dat laat zien hoe een ouderwets apparaat slim wordt zonder dure smart‑plugs【430889073424816†L71-L74】.

## Aandachtspunten

* **Werk veilig.**  Netspanning is gevaarlijk; trek altijd de stekker uit het stopcontact voordat je aan de bedrading werkt en gebruik een degelijke behuizing【430889073424816†L49-L50】.
* **Test zonder belasting.**  Schakel het relay eerst zonder aangesloten apparaat om de logica (hoog/laag) te controleren.
* **Gebruik een goede voeding.**  Een onstabiele of onderbemeten voeding kan ervoor zorgen dat het wifi‑signaal wegvalt en de schakelaar niet reageert.

## Conclusie

Met een eenvoudige Wemos D1 Mini en een relaymodule geef je bestaande apparaten een slim tweede leven.  Het project toont hoe Homeyduino projecten toegankelijk maakt: de hardwarekosten zijn laag, de code is overzichtelijk en het resultaat is direct bruikbaar.  Wie het zelf aandurft met netspanning en netjes werkt, krijgt een betrouwbare schakelaar die via Homey en Google Assistant bediend kan worden.  Wil je verder experimenteren?  Bekijk dan ook de CO₂‑sensor of de clapper‑switch voor meer inspiratie.

## Verder lezen

- [Wat kan je met Homey?](/articles/seo/wat-kan-je-met-homey.md) – begrijp hoe Homey werkt en welke apps je nodig hebt.
- [Beste Homey‑flows](/articles/seo/beste-homey-flows.md) – leer hoe je eenvoudige automatiseringen opbouwt.
- [Zelfbouw CO₂‑sensor](/articles/diy/homeyduino-co2-sensor.md) – combineer Homeyduino met een CO₂‑sensor voor inzicht in je binnenklimaat.