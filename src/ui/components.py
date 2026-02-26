import math
import streamlit as st
from database import db_connector
from database import db_repository
import numpy as np
import plotly.graph_objects as go
from image_io.image_exporter import ImageExporter
from streamlit_drawable_canvas import st_canvas
from pipeline.calculation_pipeline import get_prepared_structure
from ui import visualizer
import matplotlib.pyplot as plt
from pipeline.optimize_structure import run_optimization_loop
# --ZUM BILDER HOCHLADEN-- 
from image_io.image_importer import ImageImporter


def streamlit_ui():
    '''Zeigt Startseite und steuert den gesamten Wizard-Ablauf.'''

    st.title("Startseite")
    st.write("Mit dieser Applikation können Sie einen Balken optimieren und die Verformung berechnen.")

    # 1. Startpage
    if st.session_state.app_step == "input_form":
        input_length_and_width()
        upload_image()
        draw_structure()
        previous_calculation_results()

    # 2. Kraftpunkte, Festlager und Loslager auswählen
    elif st.session_state.app_step == "select_nodes":
        show_beam_structure(st.session_state.beam_length, st.session_state.beam_width)

    # 3. Kraftbetrag und Angriffswinkel eingeben
    elif st.session_state.app_step == "input_forces":
        input_force_data()

    # 4. Falls in Schritt 3 gewünscht, dann Optimierer auswählen
    elif st.session_state.app_step == "select_optimizer":
        select_optimizer()
    #5. Ergebnisseite anzeigen
    elif st.session_state.app_step == "results":
        show_result_page()
       
def input_length_and_width():
    '''Eingabefelder für Länge und Breite des Balkens'''

    col1, col2 = st.columns(2)
    with col1:
        st.header("Balkenlänge")
        length = st.number_input("Länge des Balkens (cm)", min_value=1, step=1, key="length")
        
    with col2:
        st.header("Balkenbreite")
        width = st.number_input("Breite des Balkens (cm)", min_value=1, step=1, key="width")
    
    if st.button("Balken generieren"):
        # Länge und Breite werden direkt gespeichert, der Berechnungsdurchlauf wird 
        # durch die Datenbank-calc-id eindeutig identifizierbar
        calc_id = db_repository.save_input_to_table(length=length, width=width)
        st.session_state.current_calc_id = calc_id
        # Zwischenspeicher length and width im session_state 
        st.session_state.beam_length = length
        st.session_state.beam_width = width
        # Alte Bild Maske aus dem Puffer löschen --
        st.session_state.pop('structure_mask', None)
        #Zwischenspeicher für Kraftpunkte und Lager zurücksetzen 
        # (für den Fall, dass der User vorher schon mal Daten eingegeben und dann zurück zum Start geklickt hat)
        st.session_state.force_points = []
        st.session_state.fixed_points = []
        st.session_state.roller_points = [] 
        # Navigation zum nächsten Schritt
        st.session_state.app_step = "select_nodes"
        st.rerun()

def upload_image():
    st.divider()
    st.subheader("Oder: Eigene Struktur als Bild hochladen")
    
    uploaded_file = st.file_uploader("Bild auswählen", type=['png', 'jpg', 'jpeg'])

    if uploaded_file is not None:
        # Bild direkt über das uploaded_file Objekt verarbeiten
        mask = ImageImporter.create_mask(uploaded_file, dark_is_material=True)        
        if mask is not None:
            img_length = mask.shape[1]
            img_width = mask.shape[0]
            
            if st.button("Balken aus Bild generieren"):
                # Maske in die DB speichern
                calc_id = db_repository.save_input_to_table(length=img_length, width=img_width, mask=mask)                
                
                # Werte für die UI-Navigation im State speichern
                st.session_state.current_calc_id = calc_id
                st.session_state.beam_length = img_length
                st.session_state.beam_width = img_width
                
                # Arrays leeren und weiter
                st.session_state.force_points = []
                st.session_state.fixed_points = []
                st.session_state.roller_points = [] 
                st.session_state.app_step = "select_nodes"
                st.rerun()
    # --PROVISORIUM ENDE--

def draw_structure():
    # --PROVISORIUM ZUM BILDER ZEICHEN--Nils
    st.divider()
    st.subheader("Oder: Struktur selbst zeichnen (Schwarz/Weiß)")
    
    # Canvas = Zeichenfeld 
    # width und height definieren die Auflösung -> damit die maximal mögliche Knotenzahl
    canvas_result = st_canvas(
        fill_color="black",
        stroke_width=5,        # Pinselbreite
        stroke_color="black",  # Pinselfarbe
        background_color="white", # Hintergrundfarbe
        width=120,             # Canvas Breite
        height=120,             # Canvas Höhe
        drawing_mode="freedraw",
        key="canvas",
    )

    if st.button("Balken aus Zeichnung generieren"):
        # canvas_result.image_data bekommt die Pixel, sobald gezeichnet wurde
        if canvas_result.image_data is not None:
            mask = ImageImporter.create_mask(
                canvas_result.image_data, 
                dark_is_material=True
            )       
            
            if mask is not None:
                img_length = mask.shape[1]
                img_width = mask.shape[0]
                
                # In die DB speichern
                calc_id = db_repository.save_input_to_table(length=img_length, width=img_width, mask=mask)                
                
                # States aktualisieren
                st.session_state.current_calc_id = calc_id
                st.session_state.beam_length = img_length
                st.session_state.beam_width = img_width
                
                # Arrays leeren und weiter zu Node Selection
                st.session_state.force_points = []
                st.session_state.fixed_points = []
                st.session_state.roller_points = [] 
                st.session_state.app_step = "select_nodes"
                st.rerun()
    #--PROVISORIUM ENDE--


def previous_calculation_results():
    '''Zeigt eine Dropdown-Liste mit vorherigen Berechnungen an und ermöglicht das Laden eines Eintrags. 
    current_calc_id wird zu calc_id der ausgewählten Berechnung im Speicher'''
    st.divider()
    st.header("Vorherige Berechnungen")
    
    db = db_connector.DatabaseConnector()
    table = db.get_table("inputdata")
    all_entries = table.all() 
    
    if not all_entries:
        st.info("Noch keine Berechnungen vorhanden.")
        return

    # Dictionary bauen: Label -> Datensatz
    options = {}
    for entry in all_entries:
        label = f"ID {entry.doc_id}: L={entry.get('length')}cm, B={entry.get('width')}cm"
        options[label] = entry

    selected_label = st.selectbox(
        "Wähle eine vorherige Berechnung aus:", 
        options=list(options.keys())
    )

    # Den passenden Datensatz heraussuchen
    selected_data = options[selected_label]

    if st.button("Diese Daten laden"):
        st.session_state.current_calc_id = selected_data.doc_id
        
        # --Alte Bild Maske aus dem Puffer löschen-- 
        st.session_state.pop('structure_mask', None)
        
        st.session_state.app_step = "results"
        st.rerun()

@st.fragment
def show_beam_structure(length, width):

    # 1. Initialisierung der benötigten States
    if 'force_points' not in st.session_state: st.session_state.force_points = []
    if 'fixed_points' not in st.session_state: st.session_state.fixed_points = []
    if 'roller_points' not in st.session_state: st.session_state.roller_points = []
    if 'selection_step' not in st.session_state: st.session_state.selection_step = 1

    # 2. WIZARD-LOGIK: Welcher Schritt ist aktiv?
    step = st.session_state.selection_step
    
    if step == 1:
        st.subheader("Schritt 1: Kraftangriffspunkte wählen")
        st.info("Klicke auf Punkte, an denen Kräfte angreifen sollen (Rot).")
        active_list = st.session_state.force_points
    elif step == 2:
        st.subheader("Schritt 2: Festlager wählen")
        st.info("Klicke auf Punkte, die als Festlager dienen sollen (Blau).")
        active_list = st.session_state.fixed_points
    else:
        st.subheader("Schritt 3: Loslager wählen")
        st.info("Klicke auf Punkte, die als Loslager dienen sollen (Grün).")
        active_list = st.session_state.roller_points

    # Raster aufbauen
    x_range = np.arange(0, length)
    y_range = np.arange(0, width)
    X, Y = np.meshgrid(x_range, y_range)
    x_flat_all = X.flatten()
    y_flat_all = Y.flatten()

    # --ANPASSUNG FÜR BILDMASKEN-- 
    x_flat, y_flat = [], []

    # Maske aus der Datenbank holen
    calc_data = db_repository.get_calculation_data(st.session_state.current_calc_id)
    mask = calc_data.get('mask', None)

    # Nur Knoten übernehmen, die laut Maske auch Material sind
    for x, y in zip(x_flat_all, y_flat_all):
        if mask is not None:
            # mask-Array [y, x] (Zeilen, Spalten)
            if mask[int(y), int(x)] > 0:
                x_flat.append(x)
                y_flat.append(y)
        else:
            x_flat.append(x)
            y_flat.append(y)
    # --ANPASSUNG ENDE--

    # 3. Farben bestimmen 
    point_colors = []
    for x, y in zip(x_flat, y_flat):
        coords = (x, y)
        if coords in st.session_state.fixed_points:
            point_colors.append('blue')
        elif coords in st.session_state.roller_points:
            point_colors.append('green')
        elif coords in st.session_state.force_points:
            point_colors.append('red')
        else:
            point_colors.append('white')

    fig = go.Figure()

    fig.add_trace(go.Scattergl(
        x=x_flat,
        y=y_flat,
        mode='markers',
        marker=dict(size=10, color=point_colors, line=dict(width=1, color='black')),
        hoverinfo='text',
        text=[f"X: {xi:.0f}, Y: {yi:.0f}" for xi, yi in zip(x_flat, y_flat)]
    ))

    buf_x = max(1, length * 0.05)
    buf_y = max(1, width * 0.05)
    fig.update_layout(
        width=None,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(
            title="Länge in cm", 
            range=[-buf_x, length + buf_x], 
            showgrid=False, 
            constrain="domain"
        ),
        yaxis=dict(
            title="Breite in cm", 
            range=[buf_y + width, -buf_y], 
            showgrid=False,
            scaleanchor="x",
            scaleratio=1,       
            constrain="domain"
        ),
    )

    event_data = st.plotly_chart(fig, on_select="rerun", selection_mode="points", key="beam_plot")

    needs_rerun = False

    # 4. Klick-Logik
    if event_data and "selection" in event_data and "points" in event_data["selection"]:
        selected_points = event_data["selection"]["points"]
        
        if selected_points:
            for pt in selected_points:
                coords = (pt['x'], pt['y'])
                
                # Wenn der Punkt schon in der Liste ist -> entfernen
                if coords in active_list:
                    active_list.remove(coords)
                    needs_rerun = True
                else:
                    # Wenn er neu ist: Zuerst aus allen anderen Listen löschen, damit es keine Konflikte gibt
                    if coords in st.session_state.force_points: st.session_state.force_points.remove(coords)
                    if coords in st.session_state.fixed_points: st.session_state.fixed_points.remove(coords)
                    if coords in st.session_state.roller_points: st.session_state.roller_points.remove(coords)
                    
                    # Dann zur aktiven Liste hinzufügen
                    active_list.append(coords)
                    needs_rerun = True

    if needs_rerun:
        st.rerun(scope="fragment")

    # 5. Navigation (Buttons für Weiter / Zurück / Speichern)
    st.divider() 
    col1, col2 = st.columns(2)
    
    with col1:
        if step > 1:
            if st.button("Zurück"):
                st.session_state.selection_step -= 1
                st.rerun() # Hier komplettes Rerun, weil sich das UI stark ändert

    with col2:
        if step == 1:
            if st.button("Weiter zu Festlagern"):
                st.session_state.selection_step = 2
                st.rerun()
        elif step == 2:
            if st.button("Weiter zu Loslagern"):
                st.session_state.selection_step = 3
                st.rerun()
        elif step == 3:
            if st.button("Auswahl abschließen"):
                st.session_state.app_step = "input_forces"
                st.session_state.selection_step = 1 # selection_step wieder auf 1 zurücksetzen
                st.rerun(scope="app")

def input_force_data():
    st.header("Kräfte definieren")
    st.info("Konvention: 0° = nach unten | -90° = nach links | 90° = nach rechts")

    # Dictionary für die Werte vorbereiten
    if 'forces_data' not in st.session_state:
        st.session_state.forces_data = {}

    # Warnung, falls im Wizard gar keine roten Punkte gewählt wurden
    if len(st.session_state.force_points) == 0:
        st.warning("Du hast keine Kraftangriffspunkte (Rot) ausgewählt.")
        st.session_state.app_step = "select_nodes"
        st.rerun()

    # Eingabefelder für jeden Punkt generieren
    for i, pt in enumerate(st.session_state.force_points):
        x, y = pt
        
        st.markdown(f"**Punkt {i+1} (X: {x:.0f}, Y: {y:.0f})**")
        col1, col2 = st.columns(2)
        
        with col1:
            mag = st.number_input(
                "Kraft (N)", 
                min_value=0.0, 
                value=1.0, 
                step=0.1, 
                key=f"mag_{x}_{y}"
            )
        with col2:
            angle = st.number_input(
                "Winkel (°)", 
                value=0, 
                step=1, 
                key=f"angle_{x}_{y}"
            )
        
        #Key für jede Kraftkomponente
        pt_key_str = f"{x}_{y}"

        angle_rad = math.radians(angle)

        force_x = round(mag * math.sin(angle_rad), 4)  # X-Komponente
        force_y = round(mag * math.cos(angle_rad), 4)  # Y-Komponente
        # Werte direkt in den State schreiben
        st.session_state.forces_data[pt_key_str] = [force_x, force_y]
        
    st.divider()
    
    # Der nächste Übergang
    if st.button("Verbiegung berechnen"):
        st.session_state.mode = 'bending_only'
        st.session_state.app_step = "results"
        
        db_repository.update_calculation_data(
            calc_id=st.session_state.current_calc_id,
            fixed_points=st.session_state.fixed_points,
            roller_points=st.session_state.roller_points,
            force_points=st.session_state.force_points,
            forces_data=st.session_state.forces_data,
            mode=st.session_state.mode
        )
        st.rerun()

    if st.button("Optimierer hinzufügen"):
        st.session_state.app_step = "select_optimizer"
        st.rerun()

def select_optimizer():
    st.header("Wähle den Optimierungsalgorithmus")

    st.selectbox(
        "Algorithmus:",
        options=["SIMP Optimizer", "ESO HardKill Optimizer", "ESO SoftKill Optimizer"],
        key="optimizer_choice"
    )

    # Für GIF Export --
    wants_gif = st.checkbox("Verlauf für GIF-Export aufzeichnen (kann die Berechnung leicht verlangsamen)")
    
    if st.button("Verformung berechnen"):
        st.session_state.mode = 'optimization_and_bending'

        # Checkbox State speichern --
        st.session_state.record_gif = wants_gif

        db_repository.update_calculation_data(
            calc_id=st.session_state.current_calc_id,
            fixed_points=st.session_state.fixed_points,
            roller_points=st.session_state.roller_points,
            force_points=st.session_state.force_points,
            forces_data=st.session_state.forces_data,
            mode=st.session_state.mode,
            optimizer=st.session_state.optimizer_choice
        )

        st.session_state.app_step = "results"
        st.rerun()

def show_result_page():

    st.title("Ergebnisse")
        
    st.write(f"Ergebnis für ID {st.session_state.current_calc_id}:")
    render_results_page(st.session_state.current_calc_id)

    # --ZUM GIFS downloaden-- -> noch in funktion auslagern
    if st.session_state.get("opt_state") == "finished":
        st.divider()
        st.subheader("Export")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'final_png_bytes' in st.session_state:
                st.download_button(
                    label="Finales Bild speichern (PNG)",
                    data=st.session_state.final_png_bytes,
                    file_name=f"topologie_final_{st.session_state.current_calc_id}.png",
                    mime="image/png"
                )
        
        with col2:
            # GIF nur anbieten, wenn Checkbox aktiv war und Frames da sind
            if 'opt_frames' in st.session_state and len(st.session_state.opt_frames) > 0:
                gif_bytes = ImageExporter.get_gif_bytes(st.session_state.opt_frames, duration=150)
                if gif_bytes:
                    st.download_button(
                        label="Verlauf speichern (GIF)",
                        data=gif_bytes,
                        file_name=f"topologie_verlauf_{st.session_state.current_calc_id}.gif",
                        mime="image/gif"
                    )
    # --ÄNDERUNG ENDE--
    if st.button("Zurück zur Eingabe"):
        st.session_state.app_step = "input_form"
        st.session_state.opt_state = "pending" 

        #--Bilder Cache leeren-- 
        st.session_state.pop('opt_frames', None)
        st.session_state.pop('final_png_bytes', None)
        #--ÄNDERUNG ENDE--

        st.rerun()


def render_results_page(calc_id: int):
    """Haupt-UI für die Ergebnisseite."""
    
    # 1. Daten und fertige Struktur von der Pipeline anfordern
    structure, calc_data = get_prepared_structure(calc_id)

    # 2. Verbiegung Plotten
    st.subheader("1. Verformung des Balkens")
    fig_bending = visualizer.plot_deformation(structure, scale_factor=1.0)
    
    _, center_col, _ = st.columns([1, 3, 1]) # Zentrierung des Plots
    with center_col:
        st.pyplot(fig_bending, use_container_width=True)
        # schließen, damit RAM nicht voll wird
        plt.close(fig_bending) 

    # 3. Je nach Modus das Optimierer-UI laden
    mode = calc_data.get('mode', 'bending_only')
    if mode == 'optimization_and_bending':
        _render_optimization_ui(structure, calc_data, calc_id)


def _render_optimization_ui(structure, calc_data, calc_id):
    """Baut das UI für die Optimierung auf und steuert die Buttons."""
    st.divider()
    st.subheader("2. Strukturoptimierung")

    saved_state = calc_data.get('saved_opt_state')
    has_saved_state = saved_state is not None

    if 'opt_state' not in st.session_state:
        st.session_state.opt_state = "pending"

    col_l, col_main, col_r = st.columns([1, 4, 1])
    
    with col_main:
        # Fenster für Live-Plot
        plot_spot = st.empty() 
        
        # Plot-Vorschau: Aus aktueller Session oder aus DB
        if "json_ready_state" in st.session_state and "current_opt" in st.session_state:
            opt = st.session_state.current_opt
            iteration = st.session_state.json_ready_state["iteration"]
            fig = visualizer.plot_optimization_step(opt.structure, opt, st.session_state.current_opt_type, iteration)
            plot_spot.pyplot(fig, use_container_width=True)
            plt.close(fig)
            
        elif has_saved_state:
            st.info(f"Gespeicherter Spielstand gefunden: Iteration {saved_state['iteration']}")

        # Interaktions-Logik
        state = st.session_state.get("opt_state", "pending")

        if state == "pending":
            if has_saved_state:
                label = f"▶️ Optimierung fortsetzen (ab Iteration {saved_state['iteration']})"
            else:
                label = "🚀 Optimierung starten"
                
            if st.button(label, type="primary", use_container_width=True):
                # Alte Generatoren sicher löschen
                st.session_state.pop("opt_generator", None)
                st.session_state.pop("current_opt", None)
                
                st.session_state.opt_state = "running"
                st.rerun()

        elif state == "running":
            if st.button("⏸️ Pausieren", use_container_width=True):
                st.session_state.opt_state = "stopped"
                st.rerun()
                
            # live-plot starten
            optimizer_type = calc_data.get('optimizer')
            # hier evtl fragment und pause-button drinnen??
            run_optimization_loop(structure, optimizer_type, plot_spot, calc_id)

        elif state in ["stopped", "finished"]:
            if state == "finished":
                st.success("🎉 Optimierung abgeschlossen!")
            
            col1, col2 = st.columns(2)
            with col1:
                if state == "stopped":
                    if st.button("▶️ Weiterlaufen lassen", type="primary", use_container_width=True):
                        st.session_state.opt_state = "running"
                        st.rerun()
                elif state == "finished":
                    if st.button("🔄 Neustart (leert DB-Stand)", use_container_width=True):
                        db_repository.delete_optimization_state(calc_id) 
                        st.session_state.opt_state = "pending"
                        st.session_state.pop("json_ready_state", None)
                        st.session_state.pop("opt_generator", None)
                        st.session_state.pop("current_opt", None)
                        st.rerun()
            
            with col2:
                if st.button("💾 In Datenbank speichern", use_container_width=True):
                    db_repository.save_optimization_state(calc_id, st.session_state.json_ready_state, st.session_state.current_opt_type)
                    st.success("Zustand in TinyDB gesichert!")
