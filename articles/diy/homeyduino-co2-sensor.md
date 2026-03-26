# Bouw een slimme CO₂‑sensor met Homeyduino

## Inleiding

Een gezond binnenklimaat is belangrijker dan veel mensen beseffen. In goed geïsoleerde woningen kan de lucht lang stil blijven staan, waardoor koolstofdioxide zich ophoopt en je je zonder het te merken vermoeid voelt. Met een paar betaalbare onderdelen – een **MH‑Z19B CO₂‑sensor**, een **Wemos D1 Mini** en de **Homeyduino**‑app – bouw je zelf een slimme sensor die continu de CO₂‑waarde meet en deze beschikbaar maakt in Homey. Zo zie je precies wanneer ventileren nodig is en kun je de sensormeting zelfs gebruiken als trigger voor flows die automatisch de mechanische ventilatie inschakelen【272765891191267†L195-L205】.

## Wat ga je bouwen?

In dit project realiseer je een compacte CO₂‑sensor die via Homey wordt uitgelezen. De sensor leest de CO₂‑concentratie uit via PWM en stuurt deze naar Homey, zodat je de waarden kunt bekijken in Insights en gebruiken in automatiseringen. Samengevat bestaat het eindresultaat uit:

- **CO₂‑meting** – de MH‑Z19B sensor meet de CO₂‑concentratie in ppm en geeft deze door aan de microcontroller【272765891191267†L204-L209】.
- **Integratie met Homey** – Homeyduino publiceert de meting als capability `measure_co2`, waardoor de waarde zichtbaar wordt in Homey en direct kan dienen als trigger voor flows【272765891191267†L325-L333】.

## Benodigdheden

* Wemos D1 Mini of NodeMCU met wifi en 5 V【272765891191267†L212-L219】
* USB‑C‑oplader【272765891191267†L212-L219】
* MH‑Z19B CO₂‑sensor【272765891191267†L212-L219】
* Homey met geïnstalleerde Homeyduino‑app【272765891191267†L212-L219】
* Een laptop of computer met Arduino IDE en Homeyduino【272765891191267†L212-L219】

<div id="affiliate-benodigdheden"></div>

<script>
  renderAffiliateRequirementsListV2("affiliate-benodigdheden", {
    title: "Benodigdheden",
    intro: "Dit zijn de onderdelen die echt het verschil maken in dit project.",
    products: [
      "wemos_d1_mini",
      "mh_z19b"
    ]
  });
</script>

## Stappenplan

1. **Sluit de sensor aan.** Verbind de MH‑Z19B volgens het aansluitschema: PWM naar **D2**, 5 V naar **5 V** en **GND** naar **G**【272765891191267†L237-L244】. Zorg voor een stabiele voeding en een degelijke behuizing.
2. **Installeer de software.** Installeer Arduino IDE, de NodeMCU‑flasher en Homeyduino. Selecteer het juiste bord (Wemos D1 Mini) in de IDE en installeer de benodigde bibliotheken voor de MH‑Z19B【272765891191267†L252-L257】.
3. **Upload de code.** Vul in de sketch je wifi‑gegevens in en upload de code op 9600 baud naar de Wemos. De sketch registreert de sensor als Homey‑device met de capability `measure_co2`【272765891191267†L256-L310】.
4. **Test de meting.** Open de seriële monitor (CTRL+SHIFT+M) om te controleren of de sensor waardevolle gegevens teruggeeft. De sensor moet enkele minuten opwarmen voordat er realistische waarden verschijnen【272765891191267†L312-L317】.
5. **Kalibreer je gevoel voor de waarden.** Meet ook even buiten om een referentiewaarde te hebben; buiten bedraagt de CO₂‑concentratie rond de 400–450 ppm. Als je binnen boven de 1000 ppm komt, is ventilatie nodig【272765891191267†L315-L318】.

## Code

De onderstaande sketch leest de PWM‑uitgang van de MH‑Z19B uit en publiceert de waarde via Homeyduino. Pas `<SSID>` en `<PASSWORD>` aan voor je wifi‑netwerk.

```cpp
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <SoftwareSerial.h>
#include <MHZ.h>
#include <Homey.h>

#define CO2_IN D2
#define MH_Z19_RX D6
#define MH_Z19_TX D5

MHZ co2(MH_Z19_RX, MH_Z19_TX, CO2_IN, MHZ19B);

void wifi() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin("<SSID>", "<PASSWORD>");
    uint8_t timeout = 30;
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      if (timeout < 1) break;
      timeout--;
    }
  }
}

void setup() {
  Serial.begin(9600);
  Homey.begin("Co2 sensor");
  Homey.setClass("sensor");
  Homey.addCapability("measure_co2");
  pinMode(CO2_IN, INPUT);
}

void loop() {
  wifi();
  Homey.loop();

  int ppm_pwm = co2.readCO2PWM();
  Serial.print("PPM: ");
  Serial.println(ppm_pwm);
  Homey.setCapabilityValue("measure_co2", ppm_pwm);

  delay(5000);
}
```

## Praktisch gebruik

Wanneer de sensor draait, verschijnt de CO₂‑waarde in Homey Insights. Je kunt er praktische automatiseringen mee maken, zoals het inschakelen van de mechanische ventilatie wanneer de waarde boven de 1000 ppm komt【272765891191267†L329-L333】. In het voorbeeld in de eigen woning is de sensor gekoppeld aan een Itho Daalderop Spider thermostaat; Homey zet de ventilatie in de booststand voor 30 minuten wanneer de CO₂‑waarde te hoog wordt【272765891191267†L342-L348】.

## Aandachtspunten

- De sensor moet bij de eerste start enkele minuten opwarmen voordat er betrouwbare waarden verschijnen【272765891191267†L352-L355】.
- Deze opstelling gebruikt de PWM‑uitgang; let erop dat de UART‑pinnen in de code aanwezig zijn, maar niet voor de meting worden gebruikt【272765891191267†L435-L437】.
- Controleer in Arduino IDE of het juiste board is geselecteerd en upload de code op 9600 baud【272765891191267†L435-L437】.

## Conclusie

Met een **MH‑Z19B**, een **Wemos D1 Mini** en **Homeyduino** bouw je voor relatief weinig geld een bruikbare CO₂‑sensor. Je krijgt inzicht in je binnenklimaat, kunt de waarden terugzien in Homey en activeert automatisch ventilatie wanneer dat nodig is. Het is een perfect project voor iedereen die zelf wil bijdragen aan een slim en gezond huis【272765891191267†L358-L359】.

### Verder lezen

**[Wat kan je met Homey?](/articles/seo/wat-kan-je-met-homey.md)** – leer wat Homey is en hoe je het als centrale hub gebruikt.
**[Beginnergids slimme sensoren](/articles/seo/beginnergids-slimme-sensoren.md)** – uitgebreide tutorial over het koppelen van zelfbouwsensoren in Homey.
**[Multi‑sensor met CO₂, licht en temperatuur](/articles/diy/homeyduino-co2-multisensor.md)** – combineer meerdere sensoren in één project voor nog meer inzichten.