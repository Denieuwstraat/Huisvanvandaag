# Licht- en temperatuursensor met Homeyduino: meer context voor slimmere flows

Veel automatiseringen reageren alleen op aanwezigheid of tijdstippen.  Maar een lamp die midden op een zonnige dag aangaat voelt onlogisch, net als een verwarming die blijft draaien terwijl het eigenlijk te warm is.  Door lichtsterkte en temperatuur te meten krijgt Homey extra context – je smart home wordt flexibeler en voorkomt onnodig schakelen【185316766573532†L62-L66】.

## Wat ga je bouwen

Je combineert een eenvoudige lichtsensor (LDR) met een DHT11‑temperatuur‑/vochtigheidssensor op een Wemos D1 Mini.  Via Homeyduino stuur je drie meetwaarden door naar Homey: lichtsterkte, temperatuur en luchtvochtigheid.  Zo kun je verlichting automatisch inschakelen als het donker genoeg is, meldingen sturen bij hitte en comfortflows verfijnen.  Deze contextsensor vormt een brug tussen losse sensoren en uitgebreidere multisensor‑projecten【185316766573532†L86-L99】.

## Benodigdheden

* Wemos D1 Mini of NodeMCU (ESP8266)
* LDR of andere lichtsensor (plus bijpassende weerstand van ca. 10 kΩ)
* DHT11‑sensor (of DHT22 voor nauwkeuriger metingen)
* USB‑C‑voeding
* Homey met de Homeyduino‑app
* Arduino IDE met de libraries voor DHT‑sensoren en Homeyduino

<div id="affiliate-benodigdheden-licht-temperatuur"></div>

<script>
renderAffiliateRequirementsListV2("affiliate-benodigdheden-licht-temperatuur", {
  title: "Benodigdheden",
  intro: "Met deze basis kun je direct aan de slag. De LDR en DHT‑sensor zijn goedkoop en makkelijk verkrijgbaar.",
  products: ["wemos_d1_mini"]
});
</script>

## Stap‑voor‑stap uitleg

### 1. Sluit de sensoren aan

Gebruik de Wemos D1 Mini als centrale controller.  Sluit de LDR aan tussen 3.3 V en analoge pin **A0** met een serieweerstand van ongeveer 10 kΩ naar GND.  Plaats de DHT11 op pin **D4** (GPIO 2) en verbind VCC met 3.3 V en GND met GND.  Let op dat de DHT11 traag is; plaats eventueel een 4.7 kΩ‑pull‑up weerstand tussen data en VCC voor stabielere waarden.

### 2. Installeer de software

Installeer de Arduino IDE en voeg de **ESP8266‑boards** toe via het boardbeheer.  Installeer vervolgens de bibliotheken **Homeyduino** en **SimpleDHT** (of de officiële DHT‑bibliotheek).  Kies in het menu *Hulpmiddelen → Board* het juiste board voor de Wemos D1 Mini.

### 3. Upload de code

De volgende sketch leest de lichtwaarde via `analogRead()` en gebruikt de DHT11‑bibliotheek voor temperatuur en luchtvochtigheid.  Homey krijgt drie capabilities: `measure_luminance`, `measure_temperature` en `measure_humidity`.  Vul je eigen wifi‑gegevens in en upload de code op 9600 baud.

```cpp
#include <ESP8266WiFi.h>
#include <Homey.h>
#include <SimpleDHT.h>

const int LDR_PIN = A0;        // analoge lichtsensor
const int DHT_PIN = D4;        // DHT11
SimpleDHT11 dht11;

unsigned long previousMillis = 0;
const unsigned long interval = 10000; // 10 seconden tussen DHT‑metingen

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
  Homey.begin("LightTemp Sensor");
  Homey.setClass("sensor");
  Homey.addCapability("measure_luminance");
  Homey.addCapability("measure_temperature");
  Homey.addCapability("measure_humidity");
}

void loop() {
  wifi();
  Homey.loop();
  // meet lichtsterkte
  int ldrValue = analogRead(LDR_PIN);
  Homey.setCapabilityValue("measure_luminance", ldrValue);
  // meet temperatuur en vochtigheid iedere 10 s
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis > interval) {
    previousMillis = currentMillis;
    byte temperature = 0;
    byte humidity = 0;
    int err = dht11.read(DHT_PIN, &temperature, &humidity, NULL);
    if (err == SimpleDHTErrSuccess) {
      Homey.setCapabilityValue("measure_temperature", (int)temperature);
      Homey.setCapabilityValue("measure_humidity", (int)humidity);
    }
  }
  delay(1000);
}
```

### 4. Voeg het apparaat toe aan Homey

Open de Homey‑app, ga naar **Apparaten**, kies **Homeyduino** en voeg het nieuwe apparaat “LightTemp Sensor” toe.  Homey toont de drie waarden als afzonderlijke meetinstrumenten.  Controleer in Homey Insights of de grafieken waardes tonen.

### 5. Maak slimme flows

Combineer de meetgegevens met je bestaande automatiseringen.  Voorbeelden uit de praktijk:

* Laat de hal‑ of buitenverlichting alleen aangaan als het daadwerkelijk donker genoeg is【185316766573532†L92-L97】.
* Stuur een melding wanneer een zolderkamer te warm wordt【185316766573532†L92-L97】.
* Gebruik licht en temperatuur als extra voorwaarde in aanwezigheid‑flows om comfortscènes te verfijnen.

## Praktisch gebruik

De sensor wordt in de hal gemonteerd.  Wanneer de buitendeur open gaat en het lichtniveau onder een drempelwaarde komt, schakelt Homey automatisch de halverlichting in.  ’s Zomers helpt de temperatuursensor om tijdig ramen te openen of een ventilator aan te zetten in de slaapkamer.  Zo voorkomen we onnodig energieverbruik en verhogen we het wooncomfort.

## Aandachtspunten

* **Calibratie:** de absolute waardes van een LDR verschillen per exemplaar en per opstelling.  Gebruik drempelwaardes in je flows in plaats van absolute lux‑waarden.
* **Sensor‑nauwkeurigheid:** een DHT11 is goedkoop maar niet bijzonder nauwkeurig.  Voor nauwkeurigere metingen kun je een DHT22 gebruiken.
* **Voeding:** zorg voor een stabiele 5 V‑voeding; fluctuaties kunnen vooral de wifi‑verbinding beïnvloeden.

## Conclusie

Een kleine investering in een LDR en DHT11 geeft je smart home een schat aan context.  Door lichtsterkte en temperatuur te meten voorkom je onlogische automatiseringen en maak je flows slimmer.  Deze sensor past naadloos in het Homey‑ecosysteem en laat zien hoe eenvoudig het is om met Homeyduino meerdere waarden tegelijk te meten.  Wie de smaak te pakken heeft kan later uitbreiden naar een complete CO₂‑multisensor of andere contextbronnen.

## Verder lezen

- [Wat kan je met Homey?](/articles/seo/wat-kan-je-met-homey.md) – begrijp hoe Homey omgaat met sensoren en flows.
- [Beste Homey‑flows](/articles/seo/beste-homey-flows.md) – start met slimme automatiseringen.
- [CO₂ multi‑sensor](/articles/diy/homeyduino-co2-multisensor.md) – meet CO₂, temperatuur, luchtvochtigheid en licht in één project.