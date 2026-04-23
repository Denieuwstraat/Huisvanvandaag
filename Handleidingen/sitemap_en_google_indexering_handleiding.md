# Handleiding: Sitemap genereren & Google indexering instellen

## Doel
Met deze handleiding zorg je ervoor dat Google jouw website:
- kan vinden
- begrijpt
- sneller indexeert

We behandelen:
1. Sitemap genereren (automatisch)
2. robots.txt instellen
3. Google Search Console koppelen

---

# 1. Sitemap genereren

## Script locatie
Plaats het script in:

```
tools/generate_sitemap.py
```

## Script uitvoeren

Open PowerShell in je projectmap:

```
python tools/generate_sitemap.py
```

## Resultaat

Er wordt automatisch een bestand aangemaakt:

```
/sitemap.xml
```

---

## Wat doet het script?

- Scant alle `.html` bestanden
- Sluit uit:
  - header.html
  - footer.html
  - sjablonen
- Zet alles om naar correcte URL’s
- Voegt datum toe (`lastmod`)

---

## Controle

Open in browser:

```
https://www.huisvanvandaag.nl/sitemap.xml
```

Je moet een lijst met URL’s zien.

---

# 2. robots.txt instellen

Maak bestand in root:

```
/robots.txt
```

Inhoud:

```
User-agent: *
Allow: /

Sitemap: https://www.huisvanvandaag.nl/sitemap.xml
```

---

# 3. Google Search Console

Ga naar:

https://search.google.com/search-console/

---

## Stap 1 — website toevoegen

Kies:

**Domein**

Voer in:

```
huisvanvandaag.nl
```

---

## Stap 2 — verificatie

Via host:

- voeg DNS TXT record toe
- wacht ±5 minuten
- klik “Verifiëren”

---

## Stap 3 — sitemap indienen

Ga naar:

```
Indexering → Sitemaps
```

Voer in:

```
sitemap.xml
```

Klik:

👉 Verzenden

---

## Stap 4 — pagina indexeren

Ga naar:

```
URL-inspectie
```

Plak een pagina, bijvoorbeeld:

```
https://www.huisvanvandaag.nl/homeyduino-co2-sensor.html
```

Klik:

👉 Indexering aanvragen

---

# Veelgemaakte fouten

## ❌ Sitemap niet bereikbaar
Controleer:
- staat hij in root?
- klopt URL?

## ❌ robots.txt ontbreekt
→ Google moet weten waar sitemap staat

## ❌ pagina heeft noindex
Controleer HTML:

```
<meta name="robots" content="noindex">
```

---

# Tips voor snellere indexering

- Publiceer regelmatig nieuwe content
- Gebruik interne links (heb je al goed 👍)
- Vraag indexering handmatig aan bij nieuwe artikelen

---

# Samenvatting

✔ Sitemap gegenereerd  
✔ robots.txt ingesteld  
✔ Google Search Console gekoppeld  

→ Je site is nu klaar om goed geïndexeerd te worden

---
