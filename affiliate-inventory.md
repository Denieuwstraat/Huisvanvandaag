# Affiliate inventory

Dit bestand is de start van een centrale index van artikelen en benoemde benodigdheden,
zodat affiliate links later gericht en consistent kunnen worden toegevoegd.

## Scanstatus

- Status: eerste inventarisatie
- Bron: artikelen en templates die via GitHub-tooling direct uitleesbaar waren
- Opmerking: de code search in de gekoppelde GitHub-omgeving gaf geen volledige file-resultaten terug,
  dus deze index is nu gebaseerd op concreet leesbare bestanden en commitsporen.

## Gevonden artikelen

### 1. homeyduino-co2-sensor.html
- Type: artikel
- Onderwerp: slimme CO₂ sensor met Homeyduino
- Affiliate relevantie: hoog
- Benodigdheden gedetecteerd:
  - Wemos D1 Mini of NodeMCU met wifi en 5V
  - Micro USB-oplader
  - MH-Z19B CO₂ sensor
  - Homey met de Homeyduino-app geïnstalleerd
  - Een computer of laptop met Arduino IDE, NodeMCU Flasher en Homeyduino
- Herkende affiliate-producten:
  - wemos_d1_mini
  - mh_z19b
- Aanbevolen actie:
  - affiliate-blok invoegen onder de sectie 'Benodigdheden'
  - losse productverwijzingen in tekst later semantisch verrijken

### 2. homeyduino-co2-sensor-affiliate.html
- Type: affiliate-variant van bestaand artikel
- Onderwerp: slimme CO₂ sensor met Homeyduino
- Affiliate relevantie: al verwerkt
- Benodigdheden gedetecteerd:
  - Wemos D1 Mini of NodeMCU met wifi en 5V
  - Micro USB-oplader
  - MH-Z19B CO₂ sensor
  - Homey met de Homeyduino-app geïnstalleerd
  - Een computer of laptop met Arduino IDE, NodeMCU Flasher en Homeyduino
- Herkende affiliate-producten:
  - wemos_d1_mini
  - mh_z19b
- Status:
  - affiliate component toegevoegd

## Gevonden templates

### sjabloon-homeyduino-projecten.html
- Type: template
- Affiliate relevantie: zeer hoog
- Benodigdheden-sectie aanwezig: ja
- Aanbevolen actie:
  - affiliate placeholder standaard opnemen in template
  - per artikel alleen nog productkeys invullen

## Productindex

### wemos_d1_mini
- Status: aanwezig in affiliate catalogus
- Bronnen:
  - affiliate-products.js
  - affiliate-products-v2.js

### mh_z19b
- Status: aanwezig in affiliate catalogus
- Bronnen:
  - affiliate-products-v2-addons.js

## Volgende stap

1. Meer HTML-artikelen expliciet uitlezen zodra de bestandslijst vollediger beschikbaar is.
2. Per artikel de sectie 'Benodigdheden' registreren.
3. Per genoemd onderdeel koppelen aan een productkey.
4. Daarna pas automatisch affiliate blokken invoegen.
