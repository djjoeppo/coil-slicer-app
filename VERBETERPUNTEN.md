# VERBETERPUNTEN EN ROUTEMAP - COILMASTER PRO

Dit document bevat de goedgekeurde verbeterpunten, feature-beslissingen en de optimale volgorde van aanpak voor verdere ontwikkeling van CoilMaster Pro.

---

## 📌 Goedgekeurde Punten & Beslissingen

### 1. **Visuele & Interface Verbeteringen**
- **1.1 G-Code Syntax Highlighting (Dropdown in Instellingen):**
  - Toevoegen van een dropdown-keuze in het instellingentabblad (*Viewer Settings*): **Standaard** (1 kleur) vs. **Verbeterd** (Kleurcodering voor `G0/G1`, `M`-codes, coördinaten $A, X, Y, Z$, en getallen).
- **1.2 Configuraties Opslaan (Instellingen Persistentie):**
  - Automatisch opslaan en herstellen van `user_config.json`:
    - Taalselectie (`NL` / `EN`)
    - Eenheden (`mm` / `inch`)
    - Thema (`Dark Mode` / `Light Mode`)
    - G-Code Highlighting Modus (`Standaard` / `Verbeterd`)
    - Laatst gebruikte Seriële Poort & Baudrate
  - *Expliciet uitgesloten:* Spoel-afmetingen worden **niet** automatisch persistent opgeslagen bij afsluiten (blijven per sessie).
- **1.3 Statusbalk (Bottom Bar):**
  - *Afgewezen/Niet nodig:* Geen onderbalk toevoegen; interface blijft strak.
- **1.4 Geanimeerde DRO (Digital Read Out) Uitleg & Werking:**
  - *Uitleg:* Het DRO-dashboard toont live posities van de $X, Y, Z, A$ assen en $Z$-kracht.
  - *Verbetering:* Een subtiel groen "LIVE" status-lampje / gloei-effect toevoegen wanneer er actieve positie-updates vanuit de ESP32 binnenkomen, zodat de gebruiker direct ziet dat de machine communicatie actief is.

---

### 2. **Functionele Verbeteringen**
- **2.1 Baudrate Selectie & Automatisch Herverbinden:**
  - Dropdown toevoegen voor Baudrate (`9600`, `57600`, `115200`, `250000`, standaard op `115200`).
  - Automatisch de laatst gebruikte COM-poort en baudrate onthouden en herselecteren bij opstarten.
- **2.2 Handmatige Besturing (Manual Jogging Controls):**
  - Een niet-bulky, logisch ingedeeld Jog-paneel toevoegen in de **Device** tab:
    - Knoppen voor `X+ / X-`, `A+ / A-`, `Y+ / Y-` met stapgrootte selectie (bijv. `0.1mm`, `1mm`, `10mm`, `15°`, `90°`, `360°`).
    - Nulstel-knop `G92 X0 A0 Y0` en Homing `G28`.
- **2.3 Spoel Informatie Pop-up & Wikkeltijdschatting:**
  - **Informatie-knop (Links Boven in Prepare Tab):** Een knop die een halfdoorzichtig, strak informatie-schema opent met berekende spoelgegevens:
    - Binnendiameter koper ($i$)
    - Buitendiameter koper ($i + 2 \times \text{lagen} \times w \times 0.866$)
    - Berekende weerstand in Ohm ($\Omega$)
    - Totale draadlengte (meters)
    - Totaal aantal omwentelingen / wikkels
    - Berekend kopergewicht (grammen op basis van koperdichtheid $8.96\,\text{g/cm}^3$)
    - *Opmerking:* Geen foutieve/onbekende waarden; onberekenbare velden tonen een vraagteken `?`.
  - **Geschatte Wikkeltijd:** Weergave van geschatte wikkeltijd in minuten/seconden (berekend op basis van omwentelingen, spoelbreedte en ingestelde feedrate $F$).
- **2.4 G-Code Inladen (Inladen van Opgeslagen Bestanden):**
  - Mogelijkheid om een eerder opgeslagen `.gcode` of `.txt` bestand in te laden in het **Preview** / **Device** tabblad om dit direct af te spelen of te controleren.
- **2.5 Profielen Import/Export:**
  - *Tijdelijk geparkeerd:* Nog niet van toepassing op dit moment.

---

## 🚀 Aanbevolen Volgorde van Aanpak (Roadmap)

Om de ontwikkeling overzichtelijk, stabiel en efficiënt te houden, is de volgende stapsgewijze volgorde het handigst:

### **Fase 1: Configuraties & Instellingen Persistentie (Snel & Stabiel)**
1. **Instellingen Opslaan in `user_config.json`:**
   - Onthouden van Taal, Thema, Eenheden, en G-code Highlighting modus.
2. **G-Code Syntax Highlighting & Dropdown:**
   - Implementeren van de `QSyntaxHighlighter` met aan/uit dropdown in Instellingen.

### **Fase 2: Hardware communicatie & Apparatenbesturing**
3. **Baudrate Selectie & Laatst Gebruikte Poort:**
   - Dropdown voor baudrates toevoegen in **Device** tab en automatisch herstellen van laatst gebruikte COM-poort/baudrate.
4. **Logische, Niet-Bulky Handmatige Jog Controls:**
   - Toevoegen van het Jog-paneel met `X`, `A`, `Y` knoppen, stapgroottes en `G92` nulstelling.
5. **DRO Live-Status Lampje:**
   - Toevoegen van de visuele "LIVE" indicator bij actieve positie-updates.

### **Fase 3: Berekende Informatie & Spoel Statistieken**
6. **Spoel Informatie Pop-up Knop (Prepare Tab):**
   - Knop linksboven in Prepare tab met halfdoorzichtig schema (binnendiameter, buitendiameter, Ohm, lengte, wikkels, kopergewicht in gram).
7. **Geschatte Wikkeltijd Weergave:**
   - Berekenen en tonen van de verwachte wikkeltijd in minutes/seconden.

### **Fase 4: Bestandsbeheer**
8. **Opgeslagen G-code Inladen:**
   - Knop en drag-and-drop om bestaande `.gcode` bestanden in de preview/terminal te laden.

---

*Gemaakt en bijgewerkt voor CoilMaster Pro.*
