# generate_reviews_index.py – handleiding

## 🎯 Doel

Dit script genereert automatisch:

👉 `reviews-index.js`

Op basis van je bestaande review HTML-pagina’s.

---

## ⚙️ Wat doet het script?

1. Scant alle `.html` bestanden
2. Detecteert welke pagina’s reviews zijn
3. Haalt metadata uit de HTML
4. Past eventuele overrides toe
5. Genereert `reviews-index.js`

---

## 🚀 Gebruik

### Dry run (alleen checken)

```
python tools/generate_reviews_index.py .
```

---

### Index genereren

```
python tools/generate_reviews_index.py . --write
```

---

### Met rapporten

```
python tools/generate_reviews_index.py . \
  --write \
  --json-out reviews-scan.json \
  --md-out reviews-scan.md
```

---

## 📂 Bestandsstructuur

```
project/
│
├── reviews.html
├── reviews-index.js   ← wordt gegenereerd
│
├── data/
│   └── reviews-overrides.json
│
└── tools/
    └── generate_reviews_index.py
```

---

## 🧠 Hoe detecteert het script reviews?

Het script gebruikt een puntsysteem:

| signaal                   | punten |
| ------------------------- | ------ |
| breadcrumb → reviews.html | +3     |
| "In deze review" sidebar  | +3     |
| "Eindoordeel"             | +2     |
| review-score              | +2     |
| Pluspunten / Minpunten    | +1     |

👉 Vanaf **6 punten = review**

---

## 📥 Welke data wordt opgehaald?

* titel (`<h1>` of `<title>`)
* excerpt (lead tekst)
* categorie
* platform
* producttype
* score
* afbeelding
* alt-tekst

---

## ✏️ Overrides (optioneel)

Bestand:

```
data/reviews-overrides.json
```

Voorbeeld:

```json
{
  "review-philips-hue.html": {
    "featured": true
  }
}
```

---

## ⚠️ Veelgemaakte fouten

### 1. HTML structuur inconsistent

👉 Dan werkt extractie niet goed

---

### 2. Ontbrekende meta-pills

Zorg dat je hebt:

```
Categorie:
Platform:
Type:
```

---

### 3. Geen review-score

Zorg dat deze bestaat:

```
.review-score-value
```

---

### 4. Verkeerde afbeelding

Idealiter:

```
.project-hero-media img
```

---

## 🔍 Debuggen

Gebruik:

```
--json-out
--md-out
```

Voor inzicht in:

* gevonden reviews
* ontbrekende velden
* detectiescore

---

## 🧪 Validatie

Wil je streng zijn:

```
--fail-on-missing
```

👉 script stopt als velden ontbreken

---

## 💡 Best practice

Gebruik:

* consistente templates
* duidelijke meta-pills
* korte excerpts

Dan werkt dit systeem vrijwel volledig automatisch.

---

## 📦 Samenvatting

* script scant je site
* detecteert reviews slim
* genereert overzicht automatisch
* uitbreidbaar en onderhoudbaar

---

Succes 🚀
