# Handleiding: Automatisch Tutorials Overzicht Genereren

## Doel
Met dit script genereer je automatisch de tutorialkaarten op je `tutorials.html` pagina, op basis van bestaande HTML-artikelen.

---

## Stap 1: Voorbereiding tutorials.html

Plaats deze markers op de plek waar de kaarten moeten komen:

```html
<!-- AUTO-GENERATED-TUTORIAL-CARDS:START -->
<!-- AUTO-GENERATED-TUTORIAL-CARDS:END -->
```

Alles tussen deze markers wordt automatisch vervangen.

---

## Stap 2: Script plaatsen

Sla het script op als:

```
tools/generate_tutorial_index.py
```

---

## Stap 3: Script uitvoeren

Open PowerShell in je projectmap en run:

```powershell
python tools/generate_tutorial_index.py . --write
```

---

## Stap 4: Wat doet het script?

- Scant alle HTML-bestanden
- Herkent tutorial-artikelen op basis van:
  - breadcrumbs
  - structuur (zoals "Wat leer je in deze tutorial?")
  - meta informatie
- Negeert:
  - reviews
  - DIY-artikelen
  - header/footer bestanden
- Vervangt alleen het kaartenblok in tutorials.html

---

## Stap 5: Controle

Na uitvoeren zie je:

```
[INFO] Gevonden tutorials: X
```

Controleer:
- Kloppen de gevonden pagina’s?
- Staan ze netjes op je pagina?

---

## Veelgemaakte fouten

### ❌ Script niet gevonden
→ Controleer pad: `tools/generate_tutorial_index.py`

### ❌ Markers niet gevonden
→ Voeg deze toe in tutorials.html

### ❌ Verkeerde artikelen worden meegenomen
→ Detectie kan aangescherpt worden 
---

## Tips

- Zorg dat je tutorials consistente structuur hebben
- Gebruik duidelijke kopjes zoals:
  - Wat leer je in deze tutorial?
  - Voor wie is deze tutorial?
- Voeg altijd een hero-afbeelding toe voor betere weergave

---

## Toekomstige uitbreidingen

- Automatisch aantal tutorials tonen
- Featured tutorial bovenaan
- Sorteren op datum of niveau
