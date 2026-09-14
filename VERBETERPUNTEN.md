# Goedgekeurde Verbeterpunten (CoilMaster Pro)

Dit document bevat het overzicht van voorgestelde verbeterpunten met de status per punt op basis van overleg met de opdrachtgever.

---

## 1. Uiterlijk & Visuele Vormgeving (Looks)

### 1.1 Opstart Pop-ups
* **Status:** Afgewezen / Behouden zoals het is.
* **Toelichting:** Omdat de software zich in een bètafase bevindt, is het juist gewenst dat er pop-ups verschijnen als er icoontjes of assets ontbreken.

### 1.2 Contrast & Formaat in Formulieren
* **Status:** Goedgekeurd.
* **Actie:** Het contrast van de labels (`formLabel`) verhogen (bijv. naar `#c5c8ca`) en de lettergrootte aanpassen naar 12px-13px met verbeterde regelafstand voor betere leesbaarheid.

### 1.3 Visuele Statusindicatoren op Knoppen
* **Status:** Goedgekeurd.
* **Specificatie van Knoppen, Kleuren en Effecten:**
  1. **`btn_update` (Bereken knop op Prepare-tab):**
     * *Normale status:* Orca Blauw (`#007edc`).
     * *Gewijzigde status:* Verandert naar opvallend Oranje (`#d97706` / `#f59e0b`) zodra een invoerveld wordt aangepast, met de tekst `"⚠️ Berekenen vereist"`. Na klikken keert de knop terug naar blauw.
  2. **`btn_update_gcode` (G-Code Update knop op Preview-tab):**
     * *Normale status:* Standaard achtergrondkleur.
     * *Gewijzigde status:* Verandert naar Felle Groene rand/achtergrond (`#10b981`) zodra een offset, Z-force of feedrate is gewijzigd, om aan te geven dat de G-code opnieuw gegenereerd moet worden.

---

## 2. Gebruiksvriendelijkheid & UX (Usability)

### 2.1 Live Preview / Auto-Rebuild
* **Status:** Afgewezen.
* **Toelichting:** Omdat 3D rendering zwaar is, zou de UI anders enkele seconden vasthangen tijdens het typen. De handmatige update-knop blijft bewust gehandhaafd.

### 2.2 Invoervalidatie & Grenzen
* **Status:** Goedgekeurd.
* **Actie:** Direct visuele feedback tonen (bijv. een subtiele rode rand rond het invoerveld) bij ongeldige of onmogelijke invoer (zoals een gat-diameter die groter is dan de kern-diameter).

### 2.3 Presets voor Spoelen (Opslaan & Selecteren)
* **Status:** In afwachting van verduidelijking (Toelichting gegeven).
* **Toelichting:** Ja, dit houdt in dat de gebruiker eigen spoelafmetingen (kern, gat, flens, breedte) kan opslaan onder een eigen naam (bijv. *"Mijn Luidspreker Spoel A"*) en deze via een dropdown-menu snel kan herladen, aangevuld met een paar ingebouwde standaardmaten.

### 2.4 Tooltips & Begrippen
* **Status:** Afgewezen voor huidig stadium.
* **Toelichting:** Nog niet nodig in deze fase van de ontwikkeling.

---

## 3. Functionaliteit & Performance

### 3.1 Automatische G-Code Sync
* **Status:** Afgewezen.
* **Toelichting:** Niet gewenst omdat specifieke G-code instellingen (draadspanning, offsets, etc.) eerst handmatig ingesteld moeten worden door de gebruiker.

### 3.2 Performance bij hele lange wikkeldraden (Uitleg & Optie)
* **Status:** Ter verduidelijking uitgelegd.
* **Uitleg:** Bij spoelen met duizenden wikkelingen heeft het 3D-model meer dan 100.000 punten. Als de gebruiker aan de tijdlijnschuifbalk sleept op de Preview-tab, wordt bij elke millimeter beweging de 3D mesh opnieuw opgebouwd.
* **Voorgestelde Oplossing:** Tijdens het slepen van de tijdlijn een tijdelijk vereenvoudigd model tonen (Level of Detail) of de mesh pas bijwerken na een kleine pauze (throttling op max. 30 fps), zodat de schuifbalk 100% soepel blijft bewegen.

### 3.3 Pauze / Hervat knop op Device tab
* **Status:** Afgewezen.
* **Toelichting:** Niet van toepassing omdat de hardware/machine zelf daar momenteel nog niet ver genoeg voor is ontwikkeld.
