# Deur‑ en raamsensor met Homeyduino: betrouwbare contactdetectie

Slimme automatisering begint vaak bij simpele signalen.  Een deur die open‑ of dichtgaat is zo’n signaal met grote praktische waarde.  Met een MC‑38 contact‑sensor en een Wemos D1 Mini bouw je in korte tijd een deur‑ of raamsensor die Homey gebruikt voor meldingen, verlichting en beveiliging【198064767084510†L59-L63】.

## Wat ga je bouwen

Je maakt een contact‑sensor die detecteert of twee magneethelften bij elkaar komen.  De Wemos leest de status (open of gesloten) en stuurt die via Homeyduino naar Homey.  In Homey verschijnt de sensor als een apparaat met de capability `alarm_contact`: **waar** betekent dat het contact open is (deur of raam open), **onwaar** betekent gesloten.  Dat maakt deze sensor ideaal voor meldingen, verlichtingstriggers en eenvoudige beveiliging【198064767084510†L83-L88】.

## Benodigdheden

* Wemos D1 Mini of NodeMCU (ESP8266)
* MC‑38 deur‑ of raamcontact (magneetschakelaar)
* USB‑C‑voeding of batterijvoeding (met 5 V‑regulatie)
* Homey met de Homeyduino‑app
* Arduino IDE

<div id="affiliate-benodigdheden-deur-raam"></div>

<script>
renderAffiliateRequirementsListV2("affiliate-benodigdheden-deur-raam", {
  title: "Benodigdheden",
  intro: "Deze onderdelen zijn voldoende voor een simpele maar betrouwbare deur‑/raamsensor.",
  products: ["wemos_d1_mini"]
});
</script>

## Stap‑voor‑stap uitleg

### 1. Sluit het contact aan

De MC‑38 bestaat uit twee helften: een reed‑switch en een magneet.  Bevestig de reed‑switch aan het deur‑ of raamkozijn en de magneet aan het bewegende deel.  Verbind één draad van de reed‑switch met **GND** op de Wemos en de andere met bijvoorbeeld **D2** (GPIO 4).  Trek de kabel strak langs het kozijn en gebruik krimpkous of een kleine behuizing om alles netjes weg te werken.  Werkt de sensor op batterijen?  Overweeg dan een sleep‑modus (buiten het bestek van dit artikel) om stroom te besparen.

### 2. Installeer de software

Installeer de Arduino IDE en de **ESP8266‑boards**.  Voeg de **Homeyduino‑bibliotheek** toe via Bibliotheekbeheer.  Kies in het boardmenu de Wemos D1 Mini.

### 3. Upload de code

Onderstaande sketch registreert de deur‑/raamsensor als een `alarm_contact`‑capability.  Iedere keer dat de status verandert, stuurt de Wemos een update naar Homey.  Vul je wifi‑gegevens in en upload de code naar de Wemos.

```cpp
#include <ESP8266WiFi.h>
#include <Homey.h>

const int CONTACT_PIN = D2; // reed‑switch
bool lastState = false;

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
  Homey.begin("Door sensor");
  Homey.setClass("sensor");
  Homey.addCapability("alarm_contact");
  pinMode(CONTACT_PIN, INPUT_PULLUP);
  lastState = digitalRead(CONTACT_PIN);
  Homey.setCapabilityValue("alarm_contact", !lastState); // open = true
}

void loop() {
  wifi();
  Homey.loop();
  bool state = digitalRead(CONTACT_PIN);
  // Het contact is gesloten wanneer de pin HIGH leest (afhankelijk van je sensor)
  bool alarm = !state;
  if (alarm != lastState) {
    lastState = alarm;
    Homey.setCapabilityValue("alarm_contact", alarm);
  }
  delay(50);
}
```

### 4. Voeg het apparaat toe aan Homey

Open de Homey‑app, ga naar **Apparaten**, kies **Homeyduino** en voeg het apparaat “Door sensor” toe.  In Homey zie je een schuif die aangeeft of het contact open is (`waar`) of gesloten (`onwaar`).

### 5. Maak slimme toepassingen

Deze sensor lijkt simpel, maar maakt je smart home een stuk nuttiger:

* **Halverlichting:** Schakel de halverlichting aan wanneer een buitendeur opent en het donker is【198064767084510†L83-L85】.
* **Meldingen:** Laat Homey een melding sturen wanneer een raam open blijft terwijl er regen wordt verwacht【198064767084510†L83-L87】.
* **Beveiliging:** Start een alarmflow wanneer een deur opent terwijl niemand thuis is【198064767084510†L83-L87】.
* **Energie:** Zet de verwarming terug als een raam langere tijd open staat【198064767084510†L83-L88】.

## Praktisch gebruik

In de woonkamer wordt de sensor gebruikt om de sfeerverlichting aan te schakelen zodra de tuindeur opengaat bij schemering.  In een tweede flow stuurt Homey een pushmelding wanneer een slaapkamerraam ’s avonds nog open staat en de weersverwachting regen aangeeft.  Dankzij de lage latency van Homeyduino reageert de sensor vrijwel direct, waardoor automatiseringen natuurlijk aanvoelen.

## Aandachtspunten

* **Betrouwbare montage:** Plaats de reed‑switch en magneet zo dat ze nauwkeurig tegenover elkaar staan; een te grote afstand kan leiden tot een onbetrouwbaar signaal.
* **Batterij vs. netvoeding:** Werken op batterijen is mogelijk maar vraagt om slaaproutines en een lagere report‑frequentie.  Een permanente 5 V‑voeding via USB is eenvoudiger.
* **Systeemvertraging:** Bij wifi‑problemen kan de melding vertraagd zijn.  Zorg voor een stabiele verbinding of gebruik eventueel een bedrade variant.

## Conclusie

Een deur‑ of raamsensor lijkt eenvoudig, maar vormt de basis voor talloze automatiseringen.  Met een MC‑38‑contact en een Wemos D1 Mini bouw je voor een paar euro een betrouwbare detector die Homey direct inzet in flows voor verlichting, beveiliging en energiebesparing.  Dit project is perfect voor beginners en laat zien hoeveel waarde er schuilt in kleine, betrouwbare signalen.

## Verder lezen

- [Wat kan je met Homey?](/articles/seo/wat-kan-je-met-homey.md) – leer hoe Homey omgaat met contact‑sensoren.
- [Beste Homey‑flows](/articles/seo/beste-homey-flows.md) – maak snelle flows met deze sensor.
- [Clapper‑switch](/articles/diy/homeyduino-clapper-switch.md) – een andere leuke trigger met grote impact.