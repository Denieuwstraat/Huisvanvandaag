# Handleiding: DIY-overzicht automatisch genereren voor huisvanvandaag.nl

Deze handleiding legt stap voor stap uit hoe je jouw DIY-overzichtspagina automatisch laat vullen op basis van je bestaande DIY-artikelen.

## Doel

Met deze aanpak:

- blijft je bestaande `diy.html` grotendeels intact
- wordt alleen het kaartenblok automatisch vernieuwd
- voorkom je handmatig bijwerken van je DIY-overzicht
- kun je nieuwe DIY-artikelen na publicatie automatisch laten verschijnen op de overzichtspagina

---

## Benodigdheden

Zorg dat je het volgende hebt:

- een werkende lokale kopie van je site
- Python geïnstalleerd
- `beautifulsoup4` geïnstalleerd
- het script `tools/generate_diy_index.py`
- een bestaande `diy.html`

Installeer BeautifulSoup indien nodig met:

```powershell
pip install beautifulsoup4
```

---

## Werking in het kort

Het script doet het volgende:

1. het scant alle `.html`-bestanden in je project
2. het probeert echte DIY-artikelen te herkennen
3. het leest titel, intro, platform, hardware en afbeelding uit
4. het vervangt alleen het kaartenblok in `diy.html`
5. de rest van jouw pagina blijft behouden

---

## Stap 1 — Pas `diy.html` eenmalig aan

Open `diy.html` en zorg dat het overzichtsblok deze markers bevat:

```html
<div class="article-grid">
  <!-- AUTO-GENERATED-DIY-CARDS:START -->
  <!-- AUTO-GENERATED-DIY-CARDS:END -->
</div>
```

Deze markers zijn verplicht. Het script zoekt exact naar deze twee regels.

### Belangrijk

Alles tussen deze markers wordt door het script overschreven.

Alles buiten deze markers blijft behouden.

---

## Stap 2 — Sla het script op

Plaats het script op deze locatie:

```text
tools/generate_diy_index.py
```

Let erop dat het script `diy.html` niet als bronartikel meeneemt. Dat voorkomt dat het script zijn eigen output opnieuw gaat verwerken.

---

## Stap 3 — Voer het script uit

Gebruik in PowerShell:

```powershell
python tools/generate_diy_index.py . --write
```

Hiermee gebeurt het volgende:

- de website-root wordt gescand vanaf de huidige map
- `diy.html` wordt gelezen
- het kaartenblok wordt opnieuw opgebouwd
- de aangepaste pagina wordt direct teruggeschreven

---

## Stap 4 — Controleer de terminal-output

Een geslaagde run geeft bijvoorbeeld iets als:

```text
[OK] DIY-overzicht bijgewerkt: C:\Users\mikey\Huisvanvandaag\diy.html
[INFO] Gevonden DIY-artikelen: 10
 - homeyduino-co2-sensor.html -> Bouw je eigen slimme CO₂ sensor met Homeyduino (UART)
 - homeyduino-clapper-switch.html -> Bouw je eigen ‘Clapper’ switch met Homeyduino
```

Controleer vooral:

- of alleen echte DIY-artikelen in de lijst staan
- of er geen reviews of informatieve pagina’s tussendoor glippen
- of er geen oude doublures in staan

---

## Stap 5 — Controleer de pagina lokaal

Open daarna `diy.html` in je lokale preview of browser en controleer:

- of de kaarten correct worden weergegeven
- of links naar de juiste pagina’s wijzen
- of afbeeldingen goed laden
- of de volgorde logisch is
- of er geen dubbele artikelen in staan

---

## Hoe DIY-artikelen worden herkend

Het script kijkt onder meer naar signalen zoals:

- breadcrumb met `DIY`
- een DIY-eyebrow
- categorie `DIY`
- titels zoals `Bouw je eigen` of `Maak je eigen`
- typische DIY-structuur zoals `Wat ga je bouwen?`
- onderdelen als `Benodigdheden` en `Stap-voor-stap uitleg`

Daarnaast worden bepaalde bestanden juist uitgesloten, zoals:

- `diy.html`
- `index.html`
- `header.html`
- `footer.html`
- reviewpagina’s
- sjabloonbestanden
- algemene pagina’s zoals `waarom-dit-blog-bestaat.html`

---

## Veelvoorkomende problemen

### 1. Markers niet gevonden

Foutmelding:

```text
ValueError: Markers niet gevonden in diy.html
```

Oorzaak:
De markers staan nog niet in `diy.html`.

Oplossing:
Voeg deze toe:

```html
<!-- AUTO-GENERATED-DIY-CARDS:START -->
<!-- AUTO-GENERATED-DIY-CARDS:END -->
```

---

### 2. Er worden verkeerde pagina’s gevonden

Voorbeelden:

- reviews
- informatieve artikelen
- header/footer
- oude sjablonen

Oorzaak:
De detectie is nog te ruim of sommige pagina’s bevatten per ongeluk DIY-signalen.

Oplossing:
Verfijn de herkenning in `generate_diy_index.py` door:

- extra bestanden toe te voegen aan `SKIP_FILES`
- extra bestandsnaampatronen toe te voegen aan `SKIP_NAME_PATTERNS`
- de scorelogica strenger te maken

---

### 3. Dubbele artikelen in het overzicht

Oorzaak:
Er staan meerdere versies van hetzelfde artikel in je project.

Oplossing:
Controleer of je bijvoorbeeld een oude en nieuwe slug naast elkaar hebt staan. Verwijder of archiveer ongebruikte varianten.

---

### 4. Afbeelding ontbreekt

Oorzaak:
Het script kan niet altijd een hero-afbeelding vinden.

Oplossing:
Controleer of je artikel een duidelijke hero-afbeelding bevat, bijvoorbeeld in:

- `.project-hero-media img`
- `.article-hero img`

---

## Aanbevolen workflow

Een praktische workflow is:

1. nieuw DIY-artikel schrijven en opslaan
2. controleren of breadcrumb, categorie en structuur kloppen
3. script draaien:

```powershell
python tools/generate_diy_index.py . --write
```

4. `diy.html` controleren
5. committen en pushen naar GitHub

---

## Slimme vervolgstappen

Je kunt dit later nog uitbreiden met:

- automatische sortering op datum
- filtering op categorie, zoals sensoren of schakelen
- automatisch tellen van het aantal projecten in het info-blok
- featured projecten bovenaan
- een vergelijkbaar script voor tutorials
- een vergelijkbaar script voor informatieve artikelen

---

## Samenvatting

De kern is simpel:

- `diy.html` blijft jouw vaste overzichtspagina
- alleen het kaartenblok wordt automatisch vervangen
- het script leest je DIY-artikelen uit de site zelf
- dat bespaart handwerk en houdt je overzicht consistenter

---

## Handige commando’s

### Script uitvoeren

```powershell
python tools/generate_diy_index.py . --write
```

### BeautifulSoup installeren

```powershell
pip install beautifulsoup4
```

---

## Aanrader

Test na elke wijziging altijd even:

- de terminal-output
- de gegenereerde kaarten
- de uiteindelijke weergave in de browser

Zo merk je snel of er per ongeluk een pagina wordt meegenomen die geen echt DIY-artikel is.
