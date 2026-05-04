# 📦 Affiliate producten toevoegen – Huis van Vandaag (v2)

Deze handleiding is bijgewerkt zodat hij volledig aansluit op de **nieuwe scanner + injector** (met review support).

---

## 📁 1. Waar voeg je producten toe?

Alle producten staan in:

```
affiliate-products.json
```

Dit is de centrale productdatabase voor:

- website (frontend rendering)
- scanner (matching)
- injector (plaatsing in artikelen)

---

## 🧩 2. Structuur van een product

```json
"product_key": {
  "name": "Naam van product",
  "description": "Korte functionele beschrijving.",
  "images": [
    "assets/product-1.jpg"
  ],
  "aliases": [
    "zoekterm 1",
    "zoekterm 2"
  ],
  "shops": [
    {
      "name": "AliExpress",
      "url": "",
      "label": "Budgetoptie",
      "badge": "€"
    }
  ]
}
```

---

## ➕ 3. Nieuw product toevoegen

### Stap 1 — Open JSON

```bash
code affiliate-products.json
```

### Stap 2 — Voeg product toe

```json
,
"nest_wifi_pro": {
  "name": "Nest Wifi Pro",
  "description": "Snelle en stabiele mesh wifi oplossing.",
  "images": [
    "assets/affiliate/nest-wifi-1.jpg"
  ],
  "aliases": [
    "nest wifi pro",
    "nest wifi",
    "google nest wifi",
    "mesh wifi"
  ],
  "shops": [
    {
      "name": "Bol.com",
      "url": "JOUW_LINK",
      "label": "Snelle levering NL",
      "badge": "NL"
    }
  ]
}
```

---

## ⚠️ 4. Veelgemaakte fouten

- ❌ Komma vergeten
- ❌ Alias ontbreekt
- ❌ Productnaam komt niet terug in artikel
- ❌ Verkeerd pad naar afbeelding
- ❌ Geen matchbare tekst in artikel

Controle:

```powershell
python -m json.tool .\affiliate-products.json
```

---

## 🧠 5. Hoe werkt matching (BELANGRIJK)

### Oude situatie
→ alleen "Benodigdheden"

### Nieuwe situatie (v2)

Scanner kijkt nu naar:

- titel (`<title>`)
- `<h1>`
- meta description
- artikeltekst
- benodigdheden (indien aanwezig)

👉 Hierdoor werken nu ook:
- reviews
- informatieve artikelen

---

## 🧪 6. Wanneer werkt matching NIET?

Geen match als:

- productnaam nergens letterlijk voorkomt
- alias niet goed gekozen is
- artikel te vaag is ("dit systeem", "de router")

👉 Oplossing:
Voeg expliciet toe in tekst:

```
De Nest Wifi Pro ...
```

---

## 🤖 7. Scripts gebruiken (NIEUW)

### Stap 1 — Scan

```powershell
python .\tools\affiliate_inventory_scanner_review_ready.py .
```

### Stap 2 — Check report

```powershell
python -m json.tool .\affiliate_report.json > $null
```

of lees:

```
affiliate_report.md
```

Je wilt zien:

```
- Herkende productkeys:
  - nest_wifi_pro
```

---

### Stap 3 — Inject

```powershell
python .\tools\affiliate_injector_review_ready.py . --report .\affiliate_report.json --write
```

---

## 📍 8. Waar worden affiliate blokken geplaatst?

### DIY / Tutorial
→ onder **Benodigdheden**

### Review
→ onder **Eindoordeel (review-score-panel)**

### Geen match?
→ geen blok

---

## ⚠️ 9. Belangrijke front-end check

Zorg dat ELK artikel dit bevat in `<head>`:

```html
<script src="affiliate-products.js"></script>
```

❗ Niet onderaan zetten → anders werkt render niet

---

## 🔁 10. Workflow

1. Product toevoegen
2. JSON checken
3. Scanner draaien
4. Report checken
5. Injector draaien
6. Artikel visueel controleren

---

## 🧪 11. Debug checklist

Werkt iets niet?

Check:

- staat product in report?
- klopt product_key?
- zit script in `<head>`?
- juiste pad naar affiliate-products.js?
- staat artikel niet in submap?
- gebruik je nieuwe scripts?

---

## 🚀 12. Pro tip

Beste resultaat krijg je als je:

- productnaam letterlijk noemt
- meerdere aliases gebruikt
- consistente termen gebruikt in artikelen

👉 Dit verhoogt:
- match rate
- automatisering
- conversie

---

Klaar 👍
