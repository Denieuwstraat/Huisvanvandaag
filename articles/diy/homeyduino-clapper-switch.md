# Clap‑switch met Homeyduino: bedien je flows met twee klappen

Wie het oorspronkelijke “Clapper”‑apparaat uit de jaren 80 kent, herinnert zich vooral het plezier: twee keer klappen en een lamp springt aan.  Met moderne hardware breng je dat idee tot leven in je smart home.  Een geluidssensor op een Wemos D1 Mini herkent twee klappen en stuurt via Homeyduino een trigger naar Homey.  Zo start je een scène of zet je verlichting uit zonder je smartphone aan te raken【467871344401027†L175-L180】.

## Wat ga je bouwen

Dit project maakt een eenvoudige **clap‑switch**.  Een geluidssensor herkent twee klappen binnen korte tijd en wisselt tussen twee staten: `clap_on` en `clap_off`.  Via Homeyduino maak je van deze sensor een apparaat in Homey, waardoor je de triggers kunt gebruiken in flows.  Met één dubbele klap start bijvoorbeeld je avondroutine; met de volgende dubbele klap schakel je alles weer uit.  Dankzij de lage kosten en overzichtelijke code is dit een ideaal instapproject【467871344401027†L125-L154】.

## Benodigdheden

* Wemos D1 Mini of NodeMCU (ESP8266)
* Geluidssensor voor Arduino/ESP8266 (bijvoorbeeld met digitale uitgang)
* USB‑C‑voeding
* Homey met de Homeyduino‑app
* Arduino IDE voor de code en bibliotheken

<div id="affiliate-benodigdheden-clapper"></div>

<script>
renderAffiliateRequirementsListV2("affiliate-benodigdheden-clapper", {
  title: "Benodigdheden",
  intro: "Deze onderdelen vormen de basis voor de modernste Clapper ooit.",
  products: ["wemos_d1_mini"]
});
</script>

## Stap‑voor‑stap uitleg

### 1. Sluit de geluidssensor aan

Verbind de digitale uitgang van de geluidssensor met **D2** (GPIO 4) op de Wemos D1 Mini.  Sluit **VCC** aan op 5 V en **GND** op GND【467871344401027†L211-L218】.  Plaats de sensor op een plek waar hij klappen kan horen maar waar achtergrondgeluid beperkt blijft.  Experimenteer later met de gevoeligheids‑potentiometer op de module om valse triggers te voorkomen.

### 2. Installeer de software

Installeer de Arduino IDE en voeg de **ESP8266‑boards** en de **Homeyduino‑bibliotheek** toe.  Kies in het boardbeheer het juiste board (`LOLIN (Wemos) D1 R2 & Mini`).

### 3. Upload de code

Deze sketch detecteert twee klappen binnen 400 milliseconden en wisselt vervolgens tussen `clap_on` en `clap_off`.  Vul je eigen wifi‑gegevens in en upload de code naar de Wemos.

```cpp
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <Homey.h>

int soundSensor = D2;
int claps = 0;
unsigned long detectionSpanInitial = 0;
unsigned long detectionSpan = 0;
bool clapState = false;

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
  Homey.begin("Clapper");
  Homey.setClass("sensor");
  pinMode(soundSensor, INPUT);
}

void loop() {
  wifi();
  Homey.loop();
  int sensorState = digitalRead(soundSensor);
  if (sensorState == LOW) {
    if (claps == 0) {
      detectionSpanInitial = detectionSpan = millis();
      claps++;
    } else if (millis() - detectionSpan >= 50) {
      detectionSpan = millis();
      claps++;
    }
  }
  if (millis() - detectionSpanInitial >= 400) {
    if (claps == 2) {
      clapState = !clapState;
      if (clapState) {
        Serial.println("Licht aan");
        Homey.trigger("clap_on", true);
      } else {
        Serial.println("Licht uit");
        Homey.trigger("clap_off", false);
      }
    }
    claps = 0;
  }
  delay(10);
}
```

### 4. Voeg de sensor toe aan Homey

Open de Homey‑app en voeg via de **Homeyduino**‑app het apparaat “Clapper” toe.  Er verschijnen geen knoppen; in plaats daarvan genereert het apparaat de triggers `clap_on` en `clap_off`.  Gebruik deze triggers in flows om lampen of scènes aan en uit te schakelen.【467871344401027†L314-L323】

### 5. Bouw slimme flows

Voorbeelden van flows:

* **Slaapkamerverlichting:** Twee klappen schakelen alle slaapkamerlampen uit.
* **Avondroutine:** De eerste dubbele klap start je avondroutine; de volgende dubbele klap zet alles weer uit en vergrendelt de voordeur【467871344401027†L329-L344】.
* **Meervoudige apparaten:** Gebruik de triggers om meerdere apparaten tegelijk te bedienen (bijvoorbeeld tv, receiver en lampen)【467871344401027†L316-L320】.

## Praktisch gebruik

De clapper‑sensor hangt naast het bed.  ’s Avonds hoef je niet meer naar een smartphone te grijpen om de lichten uit te doen; twee klappen volstaan.  In een andere flow start dezelfde dubbele klap een avondmodus waarin de woonkamerlampen dimmen en de televisie op pauze gaat.  Juist omdat Homey meerdere apparaten tegelijk kan schakelen, overstijgt dit project de gimmick van de originele Clapper【467871344401027†L329-L337】.

## Aandachtspunten

* **Unieke naamgeving:** Geef elke clapper‑sensor een herkenbare naam wanneer je er meerdere gebruikt, zodat je flows helder blijven【467871344401027†L339-L344】.
* **Gevoeligheid:** Stem de drempel van de geluidssensor af op de ruimte.  Te hoge gevoeligheid leidt tot valse triggers, te lage gevoeligheid herkent klappen niet.
* **Omgevingsgeluid:** Plaats de sensor op een rustige plek; harde muziek of ruis kan de detectie beïnvloeden.

## Conclusie

Deze moderne clapper‑switch geeft een nostalgisch idee nieuw leven in je smart home.  Met weinig onderdelen en overzichtelijke code maak je een leuke en praktische trigger die direct inzetbaar is in Homey‑flows.  Het project is budgetvriendelijk, levert snel resultaat en is daarom perfect voor beginners.  Wie verder wil experimenteren kan de sensor uitbreiden met extra capabilities of combineren met andere triggers voor complexere automatiseringen.

## Verder lezen

- [Wat kan je met Homey?](/articles/seo/wat-kan-je-met-homey.md) – de basis van apparaten en flows in Homey.
- [Beste Homey‑flows](/articles/seo/beste-homey-flows.md) – leer hoe je triggers zoals `clap_on` gebruikt.
- [Deur‑ en raamsensor](/articles/diy/homeyduino-deur-raamsensor.md) – ontdek een andere goedkope sensor met grote praktische waarde.