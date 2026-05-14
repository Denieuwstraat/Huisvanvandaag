# 📦 Affiliate producten toevoegen – Huisvanvandaag

Deze handleiding beschrijft hoe je nieuwe affiliate producten toevoegt en hoe je ze automatisch in artikelen laat verschijnen.

---

## 📁 1. Waar voeg je producten toe?

Alle producten staan in:

```
affiliate-products.json
```

Dit is de centrale productdatabase die gebruikt wordt door de website en scripts.

---

## 🧩 2. Structuur van een product

Elk product heeft dezelfde opbouw:

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

### Stap 1 — Open JSON bestand

```bash
code affiliate-products.json
```

### Stap 2 — Voeg product toe

⚠️ Let op: altijd een komma vóór een nieuw product (behalve de eerste)

```json
,
"pir_sensor": {
  "name": "HC-SR501 PIR bewegingssensor",
  "description": "Populaire bewegingssensor voor DIY automatiseringen en slimme verlichting.",
  "images": [
    "assets/pir-sensor-1.jpg",
    "assets/pir-sensor-2.jpg"
  ],
  "aliases": [
    "pir sensor",
    "bewegingssensor",
    "hc-sr501",
    "motion sensor"
  ],
  "shops": [
    {
      "name": "AliExpress",
      "url": "JOUW_LINK",
      "label": "Budgetoptie",
      "badge": "€"
    }
  ]
}
```

---

## ⚠️ 4. Veelgemaakte fouten

* ❌ Komma vergeten tussen velden
* ❌ Komma vergeten tussen producten
* ❌ Extra komma na laatste item
* ❌ Afbeelding bestaat niet
* ❌ Alias ontbreekt
* ❌ Verkeerde JSON structuur

👉 Check altijd:

```powershell
python -m json.tool .\affiliate-products.json
```

---

## 🧠 5. Hoe werkt matching?

Het systeem:

1. Leest de **Benodigdheden-lijst** in artikelen
2. Normaliseert tekst
3. Matcht op aliases
4. Koppelt product_key
5. Injector voegt affiliate blok toe

👉 **Aliases zijn hier cruciaal**

Hoe beter je aliases → hoe beter je matches.

---

## 🖼️ 6. Afbeeldingen toevoegen

Plaats afbeeldingen in:

```
/assets/
```

Gebruik consistente namen:

```
product-1.jpg
product-2.jpg
```

---

## 🤖 7. Scripts gebruiken

### Stap 1 — Scan artikelen

```powershell
python .\tools\affiliate_inventory_scanner.py
```

Output:

```
Affiliate inventory scan voltooid.
Gescande HTML-bestanden: X
Artikelen met matches: X
Totaal gevonden productmatches: X
```

---

### Stap 2 — Controleer JSON

```powershell
python -m json.tool .\affiliate_report.json > $null
```

---

### Stap 3 — Inject affiliate blokken

```powershell
python .\tools\affiliate_injector.py --report .\affiliate_report.json --write
```

---

## 🔁 8. Workflow

1. Product toevoegen
2. JSON valideren
3. Scanner draaien
4. Injector draaien
5. Artikel controleren

---

## 🧪 9. Testen

Controleer per artikel:

* verschijnt product?
* juiste afbeelding?
* juiste link?
* juiste volgorde?

---

## 🚀 10. Aanbevolen producten

* pir_sensor
* relay_module
* dht11_sensor
* ldr_sensor
* reed_contact_sensor
* sound_sensor

---

## 📌 Tip

Hoe beter je productdatabase → hoe beter je automatisering → hoe meer conversie.
