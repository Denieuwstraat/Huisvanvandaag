# De beste Homey‑flows voor beginners

## Introductie
Met Homey kun je zelf automatiseringen (‘flows’) bouwen die apparaten en sensoren slim laten samenwerken. Voor wie net begint kan het aanbod overweldigend zijn. Daarom verzamelen we hier een aantal eenvoudige maar krachtige flows die comfort, veiligheid en energiebesparing combineren. Deze voorbeelden sluiten aan op de principes van goede tutorials: eerst het doel, dan pas de techniek en altijd met een praktijkvoorbeeld【82555473540639†L26-L27】.

## Flow 1: Thuiskomst
Een klassieke en geliefde automatisering. Wanneer je thuiskomt schakelt Homey automatisch de verlichting in, zet de verwarming op comfortstand en speelt je favoriete muziek. Deze flow wordt op de tutorialpagina genoemd als nuttig startpunt【82555473540639†L26-L28】. Gebruik een aanwezigheidstrigger (bijvoorbeeld de app “Home/Away” of een bewegingssensor) om de flow te starten.

## Flow 2: Nachtmodus
‘s Nachts wil je niet dat lichten fel branden of het huis je wakker maakt met meldingen. Een eenvoudige nachtmodus dimt automatisch alle lampen, schakelt niet‑essentiële apparaten uit en zet meldingen in de “stille stand”. De nachtmodus kan ingaan bij een ingestelde tijd of wanneer je op “Ik ga slapen” drukt.

## Flow 3: Ventilatie en binnenklimaat
Een goede luchtkwaliteit is essentieel voor je gezondheid. In de multi‑sensor DIY‑gids wordt beschreven hoe je CO₂, temperatuur, luchtvochtigheid en licht meet【177584658689336†L193-L201】. Gebruik deze sensoren om je mechanische ventilatie automatisch te laten inschakelen wanneer de CO₂‑concentratie te hoog wordt【177584658689336†L167-L169】. Je kunt ook meldingen laten sturen wanneer de lucht te vochtig of te droog is【177584658689336†L210-L213】.

## Flow 4: Meldingen en veiligheid
Een eenvoudige deur‑ en raamsensor is ideaal voor meldingen: laat Homey een pushmelding sturen wanneer iemand de voordeur opent of wanneer een raam al te lang openstaat【198064767084510†L83-L88】. Combineer dat met het aansturen van verlichting of het starten van een alarm voor extra veiligheid. Vergeet ook niet een flow die alle ramen checkt voordat je gaat slapen.

## Flow 5: Energiebesparing
Energie besparen gaat niet alleen om lampen uitzetten. Combineer de hierboven beschreven sensoren met tijdsprofielen en energieprijzen. Laat Homey stroomslurpers uitzetten wanneer niemand thuis is of wanneer de energieprijs piekt【82555473540639†L26-L28】. Met een relaisproject kun je oudere apparaten slim schakelen zonder ze te vervangen【430889073424816†L45-L50】.

## Benodigdheden
Veel flows werken beter met sensoren en schakelaars. Een Wemos D1 Mini en MH‑Z19B CO₂‑sensor vormen de basis voor je eigen sensoren, terwijl een relaismodule je helpt om bestaande apparaten slim te schakelen. Gebruik de onderstaande affiliate‑sectie om de juiste hardware te vinden.

<div id="affiliate-benodigdheden-flows"></div>

<script>
renderAffiliateRequirementsListV2("affiliate-benodigdheden-flows", {
  title: "Hardware voor slimme flows",
  intro: "Deze onderdelen helpen je om de flows hierboven in de praktijk te brengen.",
  products: ["wemos_d1_mini", "mh_z19b"]
});
</script>

## Verder lezen
- **Wat kun je doen met Homey?** – een overzicht van Homey als centrale hub en inspirerende praktijkvoorbeelden.
- **DIY‑projecten voor Homey** – bouw je eigen CO₂‑sensor, relais, licht‑ en temperatuursensor of clapper switch.
- **Belang van ventileren** – leer waarom frisse lucht belangrijk is en hoe je weet wanneer je moet ventileren.