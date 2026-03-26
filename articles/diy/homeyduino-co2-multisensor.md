# CO₂ multi‑sensor met Homeyduino: bouw je eigen binnenklimaatmeter

Een gezond binnenklimaat gaat verder dan de temperatuur alleen.  Door CO₂, luchtvochtigheid, temperatuur en licht in één project te combineren, krijg je een compleet beeld van je leefomgeving.  Met een MH‑Z19B, een DHT11, een LDR en een Wemos D1 Mini bouw je een betaalbare multi‑sensor die al deze waarden tegelijk meet en naar Homey stuurt【29234308587589†L193-L200】.

## Wat ga je bouwen

Je realiseert een multi‑sensor die vier metingen uitvoert: CO₂‑concentratie, temperatuur, luchtvochtigheid en lichtsterkte.  De MH‑Z19B meet CO₂ via PWM; de DHT11 meet temperatuur en luchtvochtigheid; de LDR geeft de lichtintensiteit weer.  Via Homeyduino stuur je deze waarden naar Homey, waardoor je ze kunt volgen in Homey Insights en gebruiken als triggers of voorwaarden in flows【29234308587589†L201-L207】.  De sensor is geschikt voor integraties zoals automatische ventilatie, comfortflows of daglichtafhankelijke verlichting【29234308587589†L396-L400】.

## Waarom zelf bouwen?

Losse CO₂‑meters kosten vaak tussen €100 en €399, terwijl uitgebreide luchtkwaliteitsmeters nog duurder zijn【29234308587589†L246-L249】.  Door de sensoren zelf te combineren betaal je rond de €30 voor een complete multi‑sensor【29234308587589†L248-L249】.  Bovendien kun je de waarden integreren met je smart‑home flows; iets wat bij kant‑en‑klare meters meestal niet mogelijk is.

## Benodigdheden

* Wemos D1 Mini of NodeMCU (ESP8266)
* MH‑Z19B CO₂‑sensor
* DHT11‑sensor (of DHT22 voor nauwkeuriger metingen)
* LDR met bijpassende weerstand (ca. 10 kΩ)
* USB‑C‑voeding
* Homey met de Homeyduino‑app
* Arduino IDE, NodeMCU Flasher en Homeyduino

<div id="affiliate-benodigdheden-co2-multisensor"></div>

<script>
renderAffiliateRequirementsListV2("affiliate-benodigdheden-co2-multisensor", {
  title: "Benodigdheden",
  intro: "Deze sensoren vormen samen een volledige binnenklimaatmeter. Let op: de CO₂‑sensor is het duurste onderdeel.",
  products: ["mh_z19b", "wemos_d1_mini"]
});
</script>

## Stap‑voor‑stap uitleg

### 1. Sluit de sensoren aan

Verbind de sensoren als volgt【29234308587589†L253-L259】:

* **DHT11** → **D4** (GPIO 2)
* **LDR** → **A0** (analog)
* **MH‑Z19B (PWM)** → **D2** (GPIO 4)

Sluit de voeding van de MH‑Z19B aan op 5 V en GND (de sensor heeft een opwarmtijd van enkele minuten).  Plaats de DHT11 en LDR op een plek met voldoende luchtcirculatie en daglicht.  Gebruik een schema om alle verbindingen overzichtelijk te houden en check de polariteit van de sensoren.

### 2. Bereid de software voor

Installeer de Arduino IDE en voeg de **ESP8266‑boards**, de **Homeyduino‑bibliotheek** en de bibliotheken **SimpleDHT** en **MHZ** toe via het Bibliotheekbeheer.  Zorg er ook voor dat NodeMCU Flasher beschikbaar is als je de firmware van de Wemos wilt flashen.  Kies in *Hulpmiddelen → Board* voor de Wemos D1 Mini.

### 3. Upload de code

De onderstaande sketch leest de sensoren uit en stuurt de waarden naar Homey.  Vul `<SSID>` en `<PASSWORD>` in met je wifi‑gegevens en upload de code op 9600 baud.

```cpp
// Code for Homeyduino multi‑sensor project
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <Homey.h>
#include <SimpleDHT.h>
#include <MHZ.h>

// Pinnen toewijzen
#define PIN_DHT D4
SimpleDHT11 dht11;
#define CO2_PWM_PIN D2
#define CO2_RX_PIN D6
#define CO2_TX_PIN D5
MHZ co2(CO2_RX_PIN, CO2_TX_PIN, CO2_PWM_PIN, MHZ19B);
const int LDR_PIN = A0;

unsigned long previousMillis = 0;
const unsigned long dhtInterval = 10000; // 10 s

void wifi() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin("<SSID>", "<PASSWORD>");
    uint8_t timeout = 30;
    while (WiFi.status() != WL_CONNECTED && timeout--) {
      delay(500);
    }
  }
}

void setup() {
  Serial.begin(9600);
  Homey.begin("CO2 multi sensor");
  Homey.setClass("sensor");
  Homey.addCapability("measure_temperature");
  Homey.addCapability("measure_humidity");
  Homey.addCapability("measure_co2");
  Homey.addCapability("measure_luminance");
  pinMode(CO2_PWM_PIN, INPUT);
}

void dhtLoop() {
  static unsigned long lastDht = 0;
  if (millis() - lastDht > dhtInterval) {
    lastDht = millis();
    byte temperature = 0;
    byte humidity = 0;
    if (dht11.read(PIN_DHT, &temperature, &humidity, NULL) == SimpleDHTErrSuccess) {
      Homey.setCapabilityValue("measure_temperature", (int)temperature);
      Homey.setCapabilityValue("measure_humidity", (int)humidity);
    }
  }
}

void co2Loop() {
  int ppm_pwm = co2.readCO2PWM();
  Homey.setCapabilityValue("measure_co2", (int)ppm_pwm);
  delay(5000);
}

void ldrLoop() {
  int ldrValue = analogRead(LDR_PIN);
  Homey.setCapabilityValue("measure_luminance", ldrValue);
  delay(1000);
}

void loop() {
  wifi();
  Homey.loop();
  dhtLoop();
  co2Loop();
  ldrLoop();
}
```

### 4. Test de metingen

Open de seriële monitor (CTRL + SHIFT + M) in de Arduino IDE en wacht een paar minuten zodat de MH‑Z19B opwarmt.  Je zou regelmatige updates moeten zien voor CO₂, temperatuur, luchtvochtigheid en lichtsterkte.  Als de waarden onrealistisch lijken, controleer dan de aansluitingen en sensor‑kalibratie.

### 5. Koppel de sensor aan Homey

Gebruik de Homey‑app om het apparaat “CO2 multi sensor” toe te voegen via **Homeyduino**.  Homey toont vier meetinstrumenten.  In Homey Insights kun je trends volgen en alarmwaarden bepalen.  De waarden zijn beschikbaar als triggers of voorwaarden in flows, bijvoorbeeld om mechanische ventilatie automatisch in te schakelen bij een hoge CO₂‑waarde【29234308587589†L409-L415】.

## Praktisch gebruik

In de praktijk wordt deze multi‑sensor ingezet om het binnenklimaat te bewaken.  Wanneer de CO₂‑waarde boven 1000 ppm komt, start Homey automatisch de mechanische ventilatie van Itho Daalderop via een gekoppelde Spider‑gateway【29234308587589†L409-L415】.  Bij een hoge luchtvochtigheid wordt een meldingsflow geactiveerd zodat er tijdig geventileerd wordt.  De lichtmeting dient als extra voorwaarde om overdag bepaalde lampen uit te houden【29234308587589†L396-L400】.

## Aandachtspunten

* **Verwarming:** De MH‑Z19B heeft een opwarmtijd; meet pas na een paar minuten om betrouwbare waarden te krijgen.
* **Kalibratie:** Test de CO₂‑meter buiten; bij een buitenconcentratie van 400–500 ppm kun je controleren of de sensor correct meet【29234308587589†L214-L214】.
* **Capaciteiten:** In deze opstelling gebruik je PWM voor de CO₂‑meting, ook al staan UART‑pinnen in de sketch; dat is bewust gedaan voor eenvoud【29234308587589†L421-L423】.
* **Voeding:** Gebruik een stabiele 5 V‑voeding; fluctuaties beïnvloeden vooral de CO₂‑sensor.

## Conclusie

Met een Wemos D1 Mini, een MH‑Z19B, een DHT11 en een LDR bouw je voor een fractie van de prijs een uitgebreide binnenklimaatmeter.  Je meet meerdere waarden tegelijk, krijgt inzicht via Homey Insights en kunt de data direct gebruiken in automatiseringen.  Zo wordt ventileren niet alleen slim, maar ook proactief.  Dit project vormt een natuurlijke uitbreiding op de losse CO₂‑sensor en laat zien hoe krachtig zelfbouw kan zijn voor een gezond en comfortabel huis.

## Verder lezen

- [Wat kan je met Homey?](/articles/seo/wat-kan-je-met-homey.md) – leer hoe je sensoren koppelt aan Homey Insights.
- [Losse CO₂‑sensor](/articles/diy/homeyduino-co2-sensor.md) – een eenvoudiger project als je alleen CO₂ wilt meten.
- [Beste Homey‑flows](/articles/seo/beste-homey-flows.md) – maak flows die ventilatie starten op basis van CO₂.