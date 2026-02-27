## Kurzüberblick zu Implemtieren features

### Minimalanforderungen
* Eine Python-Anwendung mit Web-UI (streamlit) soll entwickelt ☑️
werden
* Darin kann die Topologieoptimierung beliebiger 2D-Strukturen mit ☑️
unseren Einschränkungen durchgeführt werden
* Die Ausgangsstruktur soll definiert werden können: 
- Ursprünglicher Bauraum als Rechteck mit Breite & Höhe ☑️
- Randbedingungen (Loslager, Festlager) an Massepunkten ☑️
- Externe Kräfte an Massepunkten ☑️
* Visualisierung der Struktur vor, während & nach der Optimierung
inkl. der Verformung ☑️
* Die Struktur inkl. Randbedingungen, etc. kann zu jedem Zeitpunkt
gespeichert und wieder geladen werden → Fortsetzung der
Optimierung möglich ☑️
* Lösung des Problems erfolgt in gedanklicher Anlehnung an die
Finite Elemente Methode (FEM) → so wie oben vereinfacht
beschrieben ☑️
* Es muss verifiziert werden, die Struktur nicht "auseinander fällt"
durch die Optimierung ☑️
* Testen der Implementierung am Beispiel des Messerschmitt
Bölkow–Blohm (MBB) Balken → in Dokumentation zeigen ☑️
* Die optimierte Geometrie kann als Bild heruntergeladen werden ☑️
* Die Anwendung soll mit streamlit deployed werden ☑️

### Erweiterungen
* 2 zusätzliche Optimierungs-Algorithmen ⭐
* Optimierer-Einstellungen können vom User konfiguriert werden ⭐
* Bilder können hochgeladen und in Strukturen konvertiert werden ⭐
* Strukturen können direkt in der UI gezeichnet werden ⭐
* Der Optimierungsverlauf kann als GIF heruntergeladen werden ⭐
* Die UI wurde aufwendig gestaltet ⭐
  - Auswahl von Randbedingungen mit Werkzeugpipette ⭐
  - Live-View für Balkendimensionen ⭐
  - Möglichkeit nur die Verformung zu berechnen ⭐
  - Logischer und übersichtlicher Aufbau ⭐
  - Unterstützung für Winkel von Kräften und vertikale Loslager ⭐
* Speicherung von Projekten über `.npz` Dateien ⭐
* Sorgfältige Programmstrukturierung ⭐
  - Ineinandergreifender Klassenaufbau: `Elements` ← `Structure` ← `StructureBuilder` ⭐
  - Getrennte Ordner und Dateien als Pakete (siehe UML) ⭐
  - Vererbungshierarchie bei den Optimierern ⭐
  - Wenig redundanter Code, insbesondere in `\core` ⭐
* Sehr ausführliche Dokumentation durch README.md ⭐
  - UML Diagramme, Ausfühliche Erklärungen (UI, Algorithmen, ...) ⭐
    

