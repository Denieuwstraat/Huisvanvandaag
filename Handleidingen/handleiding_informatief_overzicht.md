# Handleiding: Automatisch Informatieve Artikelen Overzicht

## Doel
Met dit script genereer je automatisch het overzicht van informatieve artikelen op je `informatief.html` pagina.

Deze pagina is bedoeld als kennisbank: eerst begrijpen, daarna pas kiezen (tutorial, review of DIY).

---

## Stap 1: Voorbereiding informatief.html

Zorg dat je deze markers in je pagina hebt staan:

```html
<!-- AUTO-GENERATED-INFORMATIEF-CARDS:START -->
<!-- AUTO-GENERATED-INFORMATIEF-CARDS:END -->
```

Alles tussen deze markers wordt automatisch vervangen.

---

## Stap 2: Script plaatsen

Sla het script op als:

```
tools/generate_informatief_index.py
```

---

## Stap 3: Script uitvoeren

Open PowerShell in je projectmap:

```powershell
python tools/generate_informatief_index.py . --write
```

---

## Stap 4: Wat doet het script?

Het script:

- Scant alle HTML-bestanden in je project
- Herkent informatieve artikelen op basis van:
  - titels zoals "Wat is...", "Hoe werkt..."
  - inhoud (uitleg, context, achtergrond)
  - structuur en tekstsignalen
- Sluit automatisch uit:
  - DIY-artikelen
  - tutorials
  - reviews
  - header/footer en sjablonen
- Vult automatisch je overzichtspagina

---

## Stap 5: Controle

Na uitvoeren zie je:

```
[INFO] Gevonden artikelen: X
```

Controleer:

- Kloppen de artikelen?
- Staat alles netjes op je pagina?
- Worden er geen verkeerde pagina’s meegenomen?

---

## Veelgemaakte fouten

### ❌ Script niet gevonden
→ Controleer of het bestand in de juiste map staat: `tools/`

### ❌ Markers niet gevonden
→ Voeg deze toe in informatief.html

### ❌ Verkeerde artikelen worden meegenomen
→ Detectie kan aangescherpt worden (bijv. via titel of structuur)

---

## Tips voor betere herkenning

Gebruik consistente structuren in je artikelen:

- duidelijke H1
- meta description
- lead paragraaf
- woorden zoals:
  - "Wat is..."
  - "Hoe werkt..."
  - "Wanneer gebruik je..."

---

## Slim gebruik (belangrijk!)

Deze pagina is je **SEO-ingang**.

Gebruik informatieve artikelen om bezoekers:

➡ te laten begrijpen  
➡ door te sturen naar tutorials  
➡ door te sturen naar DIY  
➡ of naar reviews / affiliate  

---

## Mogelijke uitbreidingen

- automatische interne links (funnel)
- featured artikel bovenaan
- sorteren op populariteit of datum
- koppeling met affiliate producten

---

## Samenvatting

- Informatief = begrijpen
- Tutorials = doen
- DIY = bouwen

Samen vormen ze je volledige funnel.
