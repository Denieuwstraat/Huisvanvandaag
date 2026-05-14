# Internal Linker v2 – Handleiding (Huisvanvandaag)

## 🎯 Doel

De **internal_linker_v2.py** vult automatisch de *Gerelateerd*-sectie in de rechterkolom van je artikelen.

👉 Geen rommel meer in je content  
👉 Consistente UX  
👉 Betere interne linking (SEO)

---

## 📁 Installatie

Plaats het script in:

```
tools/internal_linker_v2.py
```

Ga daarna in je terminal naar de root van je project.

---

## 🚀 Gebruik

### 1. Preview (aanrader eerst)

```
python tools/internal_linker_v2.py .
```

👉 Laat zien wat er zou gebeuren  
👉 Wijzigt niets

---

### 2. Echt uitvoeren

```
python tools/internal_linker_v2.py . --write
```

👉 Past je HTML-bestanden aan  
👉 Vult de *Gerelateerd*-sectie automatisch

---

### 3. Met rapport

```
python tools/internal_linker_v2.py . --write \
  --json-out internal_links.json \
  --md-out internal_links_report.md
```

Je krijgt:

- `internal_links.json` → technisch overzicht  
- `internal_links_report.md` → leesbaar overzicht  

---

## ⚙️ Opties

### Aantal links per artikel aanpassen
```
--limit 2
```

### Strengere matching (minder maar relevanter)
```
--min-score 10
```

### Drafts meenemen
```
--include-drafts
```

---

## 🧠 Hoe werkt het?

Per artikel:

1. Titel + headings + tekst worden geanalyseerd  
2. Keywords worden bepaald  
3. Andere artikelen worden gescoord  
4. Beste matches worden gekozen  
5. Sidebar wordt gevuld:

```
Gerelateerd
→ artikel 1
→ artikel 2
→ artikel 3
```

---

## 🧩 Wat wordt aangepast?

Alleen dit deel:

```
.sidebar-card
  .footer-links
```

👉 Content blijft volledig onaangetast  
👉 Affiliate blokken blijven intact  

---

## 🔍 Slimme features

- Herkent artikeltypes (DIY / tutorial / review / informatief)
- Voorkomt dubbele links
- Slaat index/contact pagina’s over
- Maakt automatisch een *Gerelateerd*-blok als deze ontbreekt

---

## 🚨 Veelgemaakte fouten

### ❌ Script doet niets
→ waarschijnlijk geen matches → verlaag `--min-score`

### ❌ Sidebar niet gevonden
→ controleer of je HTML deze structuur heeft:

```
<aside class="side-stack">
  <div class="sidebar-card">
    <h3>Gerelateerd</h3>
    <div class="footer-links"></div>
  </div>
</aside>
```

---

## 🔥 Aanbevolen workflow (HVV)

```
python tools/internal_linker_v2.py . --write --json-out internal_links.json
python tools/affiliate_injector.py . --report affiliate_report.json --write
```

👉 Eerst interne links  
👉 Daarna affiliate injectie  

---

## 🚀 Volgende stap

Mogelijke upgrades:

- Sidebar + in-content links combineren  
- AI keyword matching  
- Content dashboard (alles in 1 overzicht)  

---

**Resultaat:**  
Een site die automatisch slimmer wordt na elke run.
