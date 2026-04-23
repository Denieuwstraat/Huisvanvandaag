# Reviews systeem – handleiding (huisvanvandaag.nl)

## 🎯 Doel

Dit systeem zorgt ervoor dat alle reviews automatisch worden weergegeven op `reviews.html`, zonder afhankelijk te zijn van slug-namen of handmatige HTML-aanpassingen.

Je beheert alles centraal via één bestand:
👉 `reviews-index.js`

---

## 🧩 Overzicht van het systeem

Het systeem bestaat uit 3 onderdelen:

1. **reviews.html**
   → De pagina waar alles wordt getoond

2. **reviews-index.js**
   → De centrale lijst met alle reviews (bron van waarheid)

3. **reviews-overview.js**
   → Script dat de reviews automatisch rendert

---

## 🪜 Stap 1 — Nieuwe review toevoegen

Open:

```
reviews-index.js
```

Voeg een nieuw object toe aan de array:

```javascript
{
  slug: "review-nieuw-product.html",
  title: "Nieuw product review",
  excerpt: "Korte eerlijke samenvatting van de review.",
  category: "Categorie",
  platform: "Homey / Google Home",
  productType: "Type product",
  score: "8,2/10",
  featured: false,
  image: "assets/reviews/nieuw-product.jpg",
  imageAlt: "Beschrijving van de afbeelding"
}
```

### 🔑 Velden uitgelegd

| veld        | uitleg                             |
| ----------- | ---------------------------------- |
| slug        | pad naar je reviewpagina           |
| title       | titel van de review                |
| excerpt     | korte samenvatting (max ±1 zin)    |
| category    | bv. Verlichting, Netwerk, Sensoren |
| platform    | Homey / Google Home / etc          |
| productType | type product                       |
| score       | eindoordeel                        |
| featured    | true = bovenaan tonen              |
| image       | afbeelding pad                     |
| imageAlt    | alt-tekst                          |

---

## 🧠 Best practices voor content

### ✅ Goed

* Kort, concreet en eerlijk
* Direct duidelijk voor wie het relevant is
* Focus op praktijk, niet specs

### ❌ Niet doen

* Marketingtaal ("beste ooit")
* Vage teksten ("goede kwaliteit")
* Te lange beschrijvingen

---

## 🧱 Stap 2 — Structuur van de pagina

De pagina bevat:

### 1. Intro (vast)

Blijft statisch in `reviews.html`

### 2. Uitgelichte reviews

Automatisch gegenereerd:

```javascript
featured: true
```

### 3. Alle reviews

Inclusief filters op categorie

---

## 🎛️ Filters (automatisch)

Filters worden automatisch opgebouwd op basis van:

```javascript
category
```

Dus:

* voeg je een nieuwe categorie toe → filter verschijnt automatisch

---

## 🎨 Styling aanpassen

Aanpassen via:

```
styles.css
```

Belangrijke classes:

```
.review-grid
.review-card
.review-card-image
.review-filter-chip
.review-score-badge
```

---

## ⚠️ Veelgemaakte fouten

### 1. Slug als logica gebruiken

❌ Fout:

```
"alles met 'review' in slug tonen"
```

👉 breekt zodra je naamgeving verandert

---

### 2. Geen centrale bron

❌ Reviews verspreid over HTML

👉 moeilijk te beheren

---

### 3. Geen samenvatting

❌ Alleen titel tonen

👉 lage klikratio

---

### 4. Verkeerde categorieën

❌ inconsistent gebruik

👉 filters werken slecht

---

### 5. Te veel featured reviews

❌ alles uitgelicht

👉 niets valt nog op

---

## 🚀 Aanbevolen workflow

1. Nieuwe review schrijven
2. HTML-pagina maken
3. Item toevoegen aan `reviews-index.js`
4. Klaar ✅

---

## 🔧 Toekomstige uitbreidingen (optioneel)

* Sorteren op score
* Sorteren op datum
* “Beste keuze voor Homey”
* Zoekfunctie
* Tags (ipv alleen categorie)

---

## 💡 Belangrijk inzicht

Dit systeem draait om:

👉 **controle + schaalbaarheid**

Je kunt:

* makkelijk uitbreiden
* consistent blijven
* SEO-technisch sterker worden

Zonder afhankelijk te zijn van:

* slug naming
* handmatig linken
* rommelige categoriepagina’s

---

## 📦 Samenvatting

* Gebruik **reviews-index.js als centrale bron**
* Laat alles automatisch renderen
* Werk met duidelijke categorieën
* Houd kaarten compact en eerlijk

---

Succes 🚀
