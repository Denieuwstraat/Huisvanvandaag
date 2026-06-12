# Handleiding RSS-feed voor Huis van Vandaag

## Doel

Met `generate_rss.py` genereer je automatisch een RSS-feed op basis van alle gepubliceerde artikelen op huisvanvandaag.nl.

De feed kan later gebruikt worden voor:

- MailerLite RSS-campagnes
- RSS-readers
- Externe aggregators
- Automatische contentdistributie

---

## Stap 1 – Voeg een publicatiedatum toe aan alle sjablonen

Plaats direct onder:

```html
<meta name="hv-schema-type" content="howto">
```

de regel:

```html
<meta name="publish_date" content="[[PUBLISH_DATE]]">
```

Doe dit voor:

- DIY-sjabloon
- Tutorial-sjabloon
- Review-sjabloon
- Informatief-sjabloon

---

## Stap 2 – Laat de LLM de datum invullen

Voeg aan je prompt toe:

```text
Vervang [[PUBLISH_DATE]] altijd door de actuele datum van vandaag.
Formaat: YYYY-MM-DD.
Laat [[PUBLISH_DATE]] nooit als placeholder staan.
```

Voorbeeld:

```html
<meta name="publish_date" content="2026-06-12">
```

---

## Stap 3 – RSS genereren

Plaats `generate_rss.py` in dezelfde map als:

- generate_diy_index.py
- generate_tutorial_index.py
- generate_reviews_index.py
- generate_informatief_index.py
- generate_sitemap.py

Genereer daarna de RSS-feed:

```bash
cd tools python generate_rss.py .. --write
```

of

```bash
python generate_rss.py . --write
```

---

## Resultaat

Het script maakt:

```text
rss.xml
```

aan in de root van de website.

De feed bevat:

- titel
- url
- beschrijving
- publicatiedatum

en wordt automatisch gesorteerd van nieuw naar oud.

---

## MailerLite koppelen

Ga naar:

1. Campaigns
2. Create campaign
3. RSS campaign
4. Feed URL

Gebruik:

```text
https://www.huisvanvandaag.nl/rss.xml
```

Nieuwe artikelen kunnen daarna automatisch in nieuwsbrieven worden opgenomen.

---

## Aanbevolen vervolg

Later kunnen extra feeds worden toegevoegd:

```text
rss-homey.xml
rss-diy.xml
rss-reviews.xml
rss-informatief.xml
```

Maar begin met één centrale feed:

```text
rss.xml
```

Dat is het eenvoudigst te beheren en sluit het beste aan op de huidige structuur van Huis van Vandaag.
