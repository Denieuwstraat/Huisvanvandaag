# Huis van Vandaag — GEO / SEO Schema Architectuur

## Doel van deze aanpak

Deze werkwijze zorgt ervoor dat:

- zoekmachines beter begrijpen waar pagina’s over gaan;
- AI-systemen zoals ChatGPT, Gemini en Perplexity je content beter kunnen interpreteren;
- artikelen semantisch consistent blijven;
- Huis van Vandaag als niche-authority rondom Homey, Homeyduino en DIY smart home wordt opgebouwd;
- structured data centraal onderhoudbaar blijft.

---

# Architectuur

De setup bestaat uit twee lagen:

| Bestand | Functie |
|---|---|
| `global-schema.js` | Site-identiteit (Organization, Website, Person) |
| `article-schema.js` | Paginaspecifieke schema’s (HowTo, TechArticle, Review) |

---

# Bestandsstructuur

```plaintext
/js/global-schema.js
/js/article-schema.js
```

---

# 1. Global schema implementeren

## Bestand aanmaken

Maak aan:

```plaintext
/js/global-schema.js
```

## Inhoud

Plaats hierin het centrale schema voor:

- Organization
- WebSite
- Person

Dit schema bevat onder andere:

- naam van de site
- auteur
- expertisegebieden
- nichefocus
- taal
- logo
- URL’s

---

# 2. Article schema implementeren

## Bestand aanmaken

Maak aan:

```plaintext
/js/article-schema.js
```

Dit script:

- leest automatisch gegevens uit de pagina;
- maakt het juiste schema aan;
- injecteert JSON-LD in de `<head>`.

Onder andere:

- titel
- meta description
- breadcrumbs
- hero afbeelding
- HowTo-stappen
- reviewinformatie

worden automatisch opgehaald.

---

# 3. Scripts toevoegen aan templates

Voeg in alle artikeltemplates vlak vóór `</head>` toe:

```html
<script src="/js/global-schema.js"></script>
<script src="/js/article-schema.js"></script>
</head>
```

Gebruik altijd:

```plaintext
/js/...
```

en niet:

```plaintext
js/...
```

Dit voorkomt problemen met submappen.

---

# 4. Schema-type per template instellen

Elke template krijgt een eigen schema-type via een meta-tag.

Deze plaats je in de `<head>`.

---

# DIY-template

```html
<meta name="hv-schema-type" content="howto">
```

---

# Tutorial-template

```html
<meta name="hv-schema-type" content="howto">
```

---

# Informatief-template

```html
<meta name="hv-schema-type" content="techarticle">
```

---

# Review-template

```html
<meta name="hv-schema-type" content="review">
```

Extra voor reviews:

```html
<meta name="hv-product-name" content="Homey Pro">
```

---

# 5. Volledige voorbeeldimplementatie

```html
<link rel="stylesheet" href="styles.css">

<meta name="hv-schema-type" content="howto">

<script src="affiliate-products.js"></script>

<script src="/js/global-schema.js"></script>
<script src="/js/article-schema.js"></script>
</head>
```

---

# 6. Hoe de schema-router werkt

`article-schema.js` kijkt automatisch naar:

```html
<meta name="hv-schema-type" content="...">
```

Daarna kiest het script automatisch:

| Schema type | Structured data |
|---|---|
| `howto` | `HowTo` |
| `techarticle` | `TechArticle` |
| `review` | `Review` + `Product` |

---

# 7. Waarom deze aanpak sterk is voor GEO / AI-zichtbaarheid

Deze structuur helpt AI-systemen begrijpen:

- wie de auteur is;
- waar de site over gaat;
- welke niche centraal staat;
- hoe pagina’s samenhangen;
- welk type content een pagina bevat.

Dit vergroot de kans op:

- correcte AI-citaties;
- betere entiteitsherkenning;
- hogere topical authority;
- betere semantische consistentie.

---

# 8. Aanbevolen nichefocus

Voor Huis van Vandaag is deze focus logisch:

```javascript
"knowsAbout": [
  "Homey",
  "Homeyduino",
  "ESP8266",
  "ESP32",
  "Wemos D1 Mini",
  "DIY smart home",
  "Smart home automatisering",
  "Slimme sensoren",
  "IoT automatisering",
  "Homey flows"
]
```

Deze combinatie is:

- nichegericht;
- technisch geloofwaardig;
- internationaal relevant;
- schaalbaar richting toekomstige Homey/LG groei.

---

# 9. Belangrijke richtlijnen

## Doe wel

- gebruik consistente terminologie;
- gebruik absolute URL’s;
- houd schema synchroon met zichtbare content;
- houd de niche scherp;
- gebruik echte expertisegebieden.

## Doe niet

- schema spammen;
- irrelevante expertise claimen;
- ratings verzinnen;
- verborgen content markeren;
- generieke SEO-termen toevoegen.

---

# 10. Volgende uitbreidingen

Later kunnen extra schema’s worden toegevoegd:

| Type | Mogelijke uitbreiding |
|---|---|
| DIY | `supply`, `tool`, `estimatedCost` |
| Reviews | ratings, offers, pros/cons |
| Producten | affiliate/product schema |
| Scripts/tools | `SoftwareSourceCode` |
| Artikelen | FAQPage |
| Site | SearchAction |

---

# 11. Validatie

Controleer live pagina’s via:

## Schema Validator

https://validator.schema.org/

## Google Rich Results Test

https://search.google.com/test/rich-results

---

# 12. Aanbevolen workflow

## Stap 1

Global schema implementeren.

## Stap 2

Article schema implementeren.

## Stap 3

Templates voorzien van schema-type.

## Stap 4

Valideren.

## Stap 5

Later uitbreiden met:
- Product schema;
- Review uitbreidingen;
- FAQ schema;
- Software schema.

---

# Eindresultaat

Met deze architectuur krijgt huisvanvandaag.nl:

- een consistente semantische structuur;
- betere AI-herkenning;
- schaalbare GEO-optimalisatie;
- onderhoudbare structured data;
- sterkere niche-authority rondom Homey en DIY smart home.
