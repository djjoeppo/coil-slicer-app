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

### 2.3 Visuele Spoel Presets (Pop-up met Fotopreview)
* **Status:** Goedgekeurd.
* **Actie & Vormgeving:**
  * In plaats van een simpele dropdown komt er een **Pop-up Venster** (vergelijkbaar met de materialenmanager, maar dan visueel mooier ingericht met spoelkaarten/thumbnails).
  * Elke opgeslagen spoel krijgt een visuele kaart met:
    * Een thumbnail/foto of 3D-weergave van het type spoel.
    * Naam en afmetingen (Kern-Ø, Gat-Ø, Flens-Ø, Breedte).
    * Knoppen voor *"Opslaan als nieuwe preset"*, *"Selecteren"* en *"Verwijderen"*.

### 2.4 Tooltips & Begrippen
* **Status:** Afgewezen voor huidig stadium.
* **Toelichting:** Nog niet nodig in deze fase van de ontwikkeling.

---

## 3. Functionaliteit & Performance

### 3.1 Automatische G-Code Sync
* **Status:** Afgewezen.
* **Toelichting:** Niet gewenst omdat specifieke G-code instellingen (draadspanning, offsets, etc.) eerst handmatig ingesteld moeten worden door de gebruiker.

### 3.2 Caching, Bevriezen Voorkomen & G-Code Simulatie
* **Status:** Goedgekeurd.
* **Oplossingen voor de twee genoemde problemen:**
  1. **Voorkomen van bevriezen / herberekenen bij tab-switches (Caching):**
     * Het reeds berekende 3D-model uit de `Prepare`-tab moet 100% hergebruikt worden in de `Preview`-tab, zonder de zware wiskundige berekeningen of meshes opnieuw uit te voeren bij het openen van de tab.
  2. **Simulatie op basis van G-code (Ontleden / Parser):**
     * In plaats van puur de interne wiskundige punten te gebruiken, kan de applicatie de **gegenereerde G-code ontleden (parsen)** om de simulatie af te spelen. Hierdoor ziet de gebruiker in de simulatie exact wat de machine gaat uitvoeren (inclusief echte offsets, snelheden en A/X/Y bewegingen).

### 3.3 Pauze / Hervat knop op Device tab
* **Status:** Afgewezen.
* **Toelichting:** Niet van toepassing omdat de hardware/machine zelf daar momenteel nog niet ver genoeg voor is ontwikkeld.
