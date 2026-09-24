# Handleiding: bestaande HuisvanVandaag-artikelen migreren

Deze handleiding hoort bij:

`migrate_existing_articles.py`

Het script scant bestaande HTML-artikelen van HuisvanVandaag en helpt ze geschikt te maken voor de nieuwe SEO-, AI- en structured-data-opzet.

Het uitgangspunt is bewust veilig:

- eerst analyseren;
- daarna pas technische wijzigingen toepassen;
- inhoudelijke tekst nooit automatisch verzinnen.

---

## 1. Waarvoor dient het script?

Het script controleert bestaande HTML-artikelen op onder andere:

- ontbrekende canonical URL;
- ontbrekende `hv-schema-type`;
- ontbrekende publicatie- of wijzigingsdatum;
- ontbrekende auteur-meta;
- ontbrekende robots-meta;
- dubbele `<body>`-tags;
- dubbele `script.js`-includes;
- ontbrekende `hv-product-name` bij reviews;
- niet-uitgestelde `affiliate-products.js`;
- ontbrekende lazy loading bij contentafbeeldingen;
- ontbrekende redactionele onderdelen zoals:
  - Kort antwoord;
  - Kort oordeel;
  - testcontext;
  - bronnenblok;
  - interne links.

Het script maakt onderscheid tussen:

### Technische problemen

Deze kunnen vaak veilig automatisch worden aangepast.

### Redactionele aandachtspunten

Deze worden alleen gerapporteerd en **niet automatisch ingevuld**.

Dat voorkomt dat het script inhoud gaat verzinnen.

---

## 2. Waar plaats je het script?

Plaats het script bijvoorbeeld in:

```text
Huisvanvandaag/
│
├── index.html
├── reviews.html
├── diy.html
├── tutorials.html
├── ...
│
└── tools/
    └── migrate_existing_articles.py
```

Open daarna PowerShell of een terminal in de hoofdmap van de website.

Bijvoorbeeld:

```powershell
cd C:\Users\mikey\Huisvanvandaag
```

---

## 3. Eerste run: alleen analyseren

Start altijd eerst zonder wijzigingen toe te passen:

```powershell
python tools/migrate_existing_articles.py .
```

Het script scant de bestaande artikelen en geeft een rapport.

Voorbeeld:

```text
[AANDACHT] homey-pro-2026.html
  Type : review
  Titel: Homey Pro 2026 review
  ! canonical ontbreekt
  ! modified_date ontbreekt
  ! author-meta ontbreekt
  ! hv-product-name ontbreekt
  ~ Kort oordeel ontbreekt
  ~ testcontext ontbreekt
```

### Betekenis van de symbolen

```text
! = technisch aandachtspunt
~ = redactioneel aandachtspunt
✓ = automatisch toegepaste fix
```

---

## 4. Een CSV-rapport maken

Voor een handig totaaloverzicht kun je een CSV-bestand laten maken:

```powershell
python tools/migrate_existing_articles.py . --csv migratie-rapport.csv
```

Daarin staan onder andere:

- bestandsnaam;
- status;
- artikeltype;
- titel;
- technische problemen;
- redactionele aandachtspunten;
- toegepaste fixes.

Dit is handig om artikel voor artikel af te werken.

---

## 5. Veilige technische fixes toepassen

Als het eerste rapport er logisch uitziet, kun je de veilige automatische fixes laten uitvoeren:

```powershell
python tools/migrate_existing_articles.py . --apply
```

Mijn voorkeur is om daarbij meteen backups te laten maken:

```powershell
python tools/migrate_existing_articles.py . --apply --backup
```

Voor een bestand als:

```text
homey-pro-2026.html
```

kan dan bijvoorbeeld een backup ontstaan als:

```text
homey-pro-2026.html.bak
```

---

## 6. Aanbevolen commando

Voor de eerste echte migratieronde:

```powershell
python tools/migrate_existing_articles.py . --apply --backup --csv migratie-rapport.csv
```

Hiermee:

1. worden artikelen gescand;
2. worden veilige technische fixes toegepast;
3. worden backups gemaakt;
4. wordt een CSV-rapport geschreven;
5. worden resterende redactionele punten getoond.

---

# 7. Wat wordt automatisch aangepast?

Het script mag alleen wijzigingen uitvoeren die relatief veilig technisch te bepalen zijn.

## Dubbele body-tags

Bijvoorbeeld:

```html
<body>
<body>
```

wordt teruggebracht naar één correcte `<body>`.

Ook meerdere:

```html
</body>
</body>
```

worden opgeschoond.

---

## Dubbele script.js-includes

Bijvoorbeeld:

```html
<script src="script.js"></script>
<script src="script.js"></script>
```

wordt één include.

---

## Canonical URL

Als deze ontbreekt:

```html
<link rel="canonical" href="...">
```

wordt hij toegevoegd op basis van het pad van het HTML-bestand.

Bijvoorbeeld:

```text
reviews/homey-pro-2026.html
```

wordt:

```text
https://www.huisvanvandaag.nl/reviews/homey-pro-2026.html
```

---

## Normalisatie naar www

Een bestaande canonical zoals:

```text
https://huisvanvandaag.nl/...
```

kan worden aangepast naar:

```text
https://www.huisvanvandaag.nl/...
```

zodat deze overeenkomt met de nieuwe structured-data-opzet.

---

## Artikeltype

Als `hv-schema-type` ontbreekt probeert het script het artikeltype te herkennen.

Mogelijke waarden:

```html
<meta name="hv-schema-type" content="howto">
```

```html
<meta name="hv-schema-type" content="techarticle">
```

```html
<meta name="hv-schema-type" content="review">
```

### Globale interpretatie

```text
DIY       → howto
Tutorial  → howto
Informatief → techarticle
Review    → review
```

---

## Auteur

Als de auteur-meta ontbreekt:

```html
<meta name="author" content="Mike Mulders">
```

wordt deze toegevoegd.

---

## Modified date

Als een pagina wel:

```html
<meta name="publish_date" content="2026-09-24">
```

heeft maar geen wijzigingsdatum, wordt voorlopig dezelfde datum gebruikt:

```html
<meta name="modified_date" content="2026-09-24">
```

Pas deze later alleen aan als het artikel daadwerkelijk inhoudelijk wordt bijgewerkt.

---

## Robots-meta

Als deze ontbreekt kan het script toevoegen:

```html
<meta
  name="robots"
  content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
```

---

## Review-productnaam

Bij een review probeert het script een ontbrekende:

```html
<meta name="hv-product-name" content="...">
```

af te leiden uit de titel.

Controleer deze waarde na migratie altijd even handmatig.

Bijvoorbeeld:

```text
Homey Pro 2026 review
```

zou moeten leiden tot:

```html
<meta name="hv-product-name" content="Homey Pro 2026">
```

---

## Affiliate JavaScript

Als:

```html
<script src="affiliate-products.js"></script>
```

geen `defer` of `async` bevat, kan dit worden aangepast naar:

```html
<script src="affiliate-products.js" defer></script>
```

---

## Afbeeldingen

Voor de hero-afbeelding kan worden toegevoegd:

```html
fetchpriority="high"
decoding="async"
```

Voor normale contentafbeeldingen:

```html
loading="lazy"
decoding="async"
```

---

# 8. Wat past het script bewust NIET automatisch aan?

Dit is belangrijk.

Het script genereert **geen inhoud**.

Het schrijft dus niet automatisch:

- Kort antwoord;
- Kort oordeel;
- FAQ;
- testervaring;
- testduur;
- testomgeving;
- bronnen;
- affiliate-producten;
- interne links;
- conclusies;
- plus- of minpunten.

Deze onderdelen verschijnen alleen als redactioneel aandachtspunt.

---

# 9. Waarom geen automatische AI-teksten?

Een bestaand artikel kan bijvoorbeeld gaan over:

```text
Homey Pro
```

Maar een script kan niet betrouwbaar bepalen:

- wat jij zelf getest hebt;
- wat jouw daadwerkelijke ervaring was;
- welke conclusie gerechtvaardigd is;
- welke bron je werkelijk hebt gebruikt;
- welke affiliate-link relevant is.

Daarom geldt:

```text
techniek → automatiseren

inhoud → controleren en redigeren
```

Dat voorkomt verzonnen informatie.

---

# 10. De drie mogelijke statussen

## GOED

Het artikel heeft geen technisch of redactioneel aandachtspunt dat door het script wordt herkend.

```text
[GOED]
```

---

## GOED + REDACTIONEEL

Technisch is de pagina goed, maar inhoudelijk kunnen nog verbeteringen worden toegevoegd.

Bijvoorbeeld:

```text
[GOED + REDACTIONEEL]

~ Kort antwoord ontbreekt
~ bronnenblok ontbreekt
```

Dit is geen fout.

De pagina kan technisch gewoon functioneren.

---

## AANDACHT

Er is minimaal één technisch probleem.

Bijvoorbeeld:

```text
[AANDACHT]

! canonical ontbreekt
! modified_date ontbreekt
```

Deze pagina verdient technische controle.

---

# 11. Welke pagina's worden standaard overgeslagen?

Het script probeert vooral echte artikelen te verwerken.

Onder andere deze algemene pagina's worden standaard overgeslagen:

```text
index.html
404.html
reviews.html
tutorials.html
diy.html
homey.html
privacy.html
contact.html
over.html
```

Ook mappen zoals bijvoorbeeld:

```text
.git
.github
node_modules
vendor
dist
build
backup
backups
```

worden niet meegenomen.

---

# 12. Alle HTML-bestanden scannen

Wil je ook pagina's meenemen die niet automatisch als artikel worden herkend:

```powershell
python tools/migrate_existing_articles.py . --all-html
```

Gebruik dit vooral voor controle.

Pas bij twijfel niet meteen `--apply` toe op alle HTML.

---

# 13. Aanbevolen migratiewerkwijze

Voor HuisvanVandaag adviseer ik deze volgorde.

## Fase 1 — inventariseren

```powershell
python tools/migrate_existing_articles.py . --csv migratie-rapport.csv
```

Bekijk daarna het rapport.

---

## Fase 2 — technische migratie

Als het rapport logisch is:

```powershell
python tools/migrate_existing_articles.py . --apply --backup --csv migratie-rapport.csv
```

Controleer daarna een aantal gewijzigde HTML-bestanden.

---

## Fase 3 — lokaal testen

Open of serveer de website lokaal.

Controleer onder andere:

- layout;
- afbeeldingen;
- navigatie;
- scripts;
- affiliateblokken;
- formulieren;
- inhoudsopgave.

---

## Fase 4 — redactionele migratie

Werk vervolgens de artikelen met de hoogste waarde als eerste bij.

Goede prioriteit:

1. artikelen die al organisch verkeer krijgen;
2. reviews met affiliate-potentie;
3. belangrijke Homey-pagina's;
4. Matter/Thread/Zigbee-artikelen;
5. ESP32- en DIY-artikelen;
6. oudere artikelen met redactionele hiaten.

---

# 14. Prioriteit geven aan bestaande artikelen

Niet ieder oud artikel hoeft direct volledig naar de nieuwe template.

Een praktische aanpak:

```text
NIVEAU 1
technisch compatibel maken

↓ 

NIVEAU 2
Kort antwoord / testcontext / bronnen toevoegen

↓

NIVEAU 3
interne links verbeteren

↓

NIVEAU 4
artikel inhoudelijk actualiseren
```

Hiermee kun je de site geleidelijk verbeteren.

---

# 15. Samenwerking met global-schema.js

Iedere pagina laadt:

```html
<script src="/js/global-schema.js" defer></script>
```

Deze bevat onder andere:

- Organization;
- WebSite;
- Person;
- auteurrelaties.

De artikelen verwijzen vervolgens naar dezelfde vaste schema-ID's.

---

# 16. Samenwerking met article-schema.js

Daarnaast laadt een artikel:

```html
<script src="/js/article-schema.js" defer></script>
```

Dit script leest informatie uit de HTML, zoals:

```text
hv-schema-type
publish_date
modified_date
hv-product-name
canonical
H1
meta description
hero-afbeelding
breadcrumbs
pluspunten
minpunten
reviewscore
```

Daaruit wordt automatisch structured data opgebouwd.

Voorbeelden:

```text
Informatief
→ Article + TechArticle
```

```text
DIY / Tutorial
→ Article + HowTo
```

```text
Review
→ Product
   └── Review
```

---

# 17. Controle na migratie

Controleer na wijzigingen altijd een aantal pagina's handmatig.

Let vooral op:

- precies één `<body>`;
- precies één `script.js`;
- juiste canonical;
- correcte productnaam;
- juiste datum;
- juiste hero-afbeelding;
- geen kapotte layout;
- geen ontbrekende scripts.

---

# 18. Structured data controleren

Na publicatie kun je belangrijke pagina's controleren met Google's Rich Results Test.

Voor reviews is vooral interessant of Google de Product/Review-structuur herkent.

Controleer daarnaast in de browser eventueel de gegenereerde JSON-LD.

Open Developer Tools en zoek bijvoorbeeld in de DOM naar:

```html
<script type="application/ld+json">
```

Je zou zowel globale structured data als artikeldata moeten zien.

---

# 19. Git gebruiken als extra vangnet

Als de site in Git staat, is dat naast `.bak`-bestanden een extra veiligheidslaag.

Voor de migratie:

```powershell
git status
```

Maak eventueel eerst een commit:

```powershell
git add .
git commit -m "Backup voor SEO migratie bestaande artikelen"
```

Voer daarna het migratiescript uit.

Daarna kun je precies zien wat gewijzigd is:

```powershell
git diff
```

Dit is sterk aanbevolen.

---

# 20. Terugdraaien

Gebruik je:

```powershell
--backup
```

dan kun je een individueel bestand herstellen vanuit de `.bak`-versie.

Bij Git kun je wijzigingen ook terugzien en gecontroleerd herstellen.

Verwijder backups pas wanneer je zeker weet dat de nieuwe pagina's correct werken.

---

# 21. Belangrijkste commando's

## Alleen scannen

```powershell
python tools/migrate_existing_articles.py .
```

## Scannen + CSV

```powershell
python tools/migrate_existing_articles.py . --csv migratie-rapport.csv
```

## Veilige fixes uitvoeren

```powershell
python tools/migrate_existing_articles.py . --apply
```

## Veilige fixes + backup

```powershell
python tools/migrate_existing_articles.py . --apply --backup
```

## Aanbevolen volledige migratierun

```powershell
python tools/migrate_existing_articles.py . --apply --backup --csv migratie-rapport.csv
```

## Alle HTML controleren

```powershell
python tools/migrate_existing_articles.py . --all-html
```

---

# 22. Aanbevolen werkwijze in één overzicht

```text
Git commit maken
       ↓
scanner draaien
       ↓
rapport controleren
       ↓
--apply --backup
       ↓
HTML lokaal testen
       ↓
CSV redactioneel afwerken
       ↓
structured data controleren
       ↓
publiceren
       ↓
Search Console / Bing volgen
```

---

# 23. Belangrijk uitgangspunt

Het migratiescript is geen automatische contentschrijver.

Het is vooral een:

```text
technische scanner
+
veilige migrator
+
redactionele checklist
```

Daarmee kun je bestaande HuisvanVandaag-artikelen stapsgewijs geschikt maken voor de nieuwe SEO-, AI- en structured-data-opzet zonder de inhoud onnodig automatisch te herschrijven.
