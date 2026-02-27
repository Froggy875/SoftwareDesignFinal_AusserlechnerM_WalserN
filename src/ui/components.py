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
from image_io.image_importer import ImageImporter


def streamlit_ui():
    '''Erzeugt das User-Interface und steuert den Ablauf'''
    st.title("Structure Designer")

    if st.session_state.app_step == "main_page":
        st.header("Hauptmenü")
        previous_calculation_results()
        new_project_ui()
        
    # 2. Kraftpunkte, Festlager und Loslager auswählen
    elif st.session_state.app_step == "boundary_conditions":
        boundary_conditions_ui()

    # 4. Falls in Schritt 3 gewünscht, dann Optimierer auswählen
    elif st.session_state.app_step == "select_optimizer":
        select_optimizer()

    #5. Ergebnisseite anzeigen
    elif st.session_state.app_step == "results":
        show_result_page()

def previous_calculation_results():
    '''Zeigt eine Dropdown-Liste mit vorherigen Berechnungen an und ermöglicht das Laden eines Eintrags. 
    current_calc_id wird zu calc_id der ausgewählten Berechnung im Speicher'''
    
    st.divider()
    st.header("Bestehendes Projekt laden")
    
    #Datenbank laden
    db = db_connector.DatabaseConnector()
    table = db.get_table("inputdata")
    all_entries = table.all() 
    #Info, falls es noch keinen Eintrag gibt
    if not all_entries:
        st.info("Noch keine Berechnungen vorhanden.")
        return

    #hier noch anzeige ändern
    # Dictionary bauen: Label -> Datensatz 
    options = {}
    for entry in all_entries:
        label = f"Projekt{entry.doc_id} | {entry.get('project_type')} | Erstellt am {entry.get('created_date')} um {entry.get('created_time')}"
        options[label] = entry
    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    with col1:
        selected_label = st.selectbox("Projekt auswählen", 
            options=list(options.keys())
        )
        # Den passenden Datensatz heraussuchen
        selected_data = options[selected_label]

    #Auswahl laden
    with col2:
        if st.button("Projekt laden"):
            st.session_state.current_calc_id = selected_data.doc_id
            # --Alte Bild Maske aus dem Puffer löschen-- 
            st.session_state.pop('structure_mask', None)
            st.session_state.app_step = "results"
            st.rerun()

def new_project_ui():
    st.divider()
    st.header("Neues Projekt")
    tabs = st.radio("", ["Rechteckige Struktur", "Struktur zeichnen", "Struktur aus Bild generieren"], horizontal=True) #radio, damit canvas funktioniert

    if tabs == "Rechteckige Struktur":
        input_rectangle()
    
    if tabs == "Struktur zeichnen":
        draw_structure()
    
    if tabs == "Struktur aus Bild generieren":
        upload_image()

def input_rectangle():
    '''Eingabefelder für Länge und Breite des Balkens'''
    st.subheader("Form definieren")
    _, col2, _ = st.columns([1,2,1])
    
    with col2:
        length = st.slider("Länge", min_value=1, max_value=120, value=20, step=1)
        width = st.slider("Breite", min_value=1, max_value=120, value=10, step=1)
 
        fig = go.Figure()

        fig.add_shape(
            type="rect",
            x0=0, y0=0,
            x1=length, y1=width,
            line=dict(color="RoyalBlue", width=3),
            fillcolor="LightSkyBlue",
            opacity=0.5
        )
        # X-Achse bleibt normal (wächst nach rechts)
        fig.update_xaxes(range=[0, length], title_text="Länge")

        # Y-Achse umdrehen: Wir starten beim höchsten Wert (z.B. 80) und gehen bis -10
        fig.update_yaxes(
            range=[width, 0], # HIER: Der größere Wert steht links!
            title_text="Breite",
            scaleanchor="x",
            scaleratio=1
        ) 

        st.plotly_chart(fig, use_container_width=True)

    _, _, button_right = st.columns([1, 1, 1])
    with button_right:
        if st.button("Weiter zu Randbedingungen"):
            # Länge und Breite werden direkt gespeichert, der Berechnungsdurchlauf wird 
            # durch die Datenbank-calc-id eindeutig identifizierbar
            calc_id = db_repository.save_input_to_table(project_type="Rechteck", length=length, width=width)
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
            st.session_state.app_step = "boundary_conditions"
            st.rerun()

def upload_image():
    st.subheader("Eigene Struktur als Bild hochladen")
    uploaded_file = st.file_uploader("Bild auswählen", type=['png', 'jpg', 'jpeg'], width=300)

    if uploaded_file is not None:
        # Bild direkt über das uploaded_file Objekt verarbeiten
        mask = ImageImporter.create_mask(uploaded_file, dark_is_material=True)        
        if mask is not None:
            img_length = mask.shape[1]
            img_width = mask.shape[0]
            
            if st.button("Balken aus Bild generieren"):
                # Maske in die DB speichern
                calc_id = db_repository.save_input_to_table(project_type="Upload", length=img_length, width=img_width, mask=mask)                
                
                # Werte für die UI-Navigation im State speichern
                st.session_state.current_calc_id = calc_id
                st.session_state.beam_length = img_length
                st.session_state.beam_width = img_width
                
                # Arrays leeren und weiter
                st.session_state.force_points = []
                st.session_state.fixed_points = []
                st.session_state.roller_points = [] 
                st.session_state.app_step = "boundary_conditions"
                st.rerun()
    # --PROVISORIUM ENDE--

def draw_structure():
    # --PROVISORIUM ZUM BILDER ZEICHEN--Nils
    st.subheader("Struktur zeichnen")
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
                calc_id = db_repository.save_input_to_table(project_type="Zeichnung", length=img_length, width=img_width, mask=mask)                
                
                # States aktualisieren
                st.session_state.current_calc_id = calc_id
                st.session_state.beam_length = img_length
                st.session_state.beam_width = img_width
                
                # Arrays leeren und weiter zu Node Selection
                st.session_state.force_points = []
                st.session_state.fixed_points = []
                st.session_state.roller_points = [] 
                st.session_state.app_step = "boundary_conditions"
                st.rerun()
    #--PROVISORIUM ENDE--

@st.fragment
def boundary_conditions_ui():
    st.subheader("Randbedingungen & Belastung")
    # 1. Initialisierung der benötigten States
    if 'force_points' not in st.session_state: st.session_state.force_points = []
    if 'fixed_points' not in st.session_state: st.session_state.fixed_points = []
    if 'roller_points' not in st.session_state: st.session_state.roller_points = []

    length = st.session_state.beam_length
    width = st.session_state.beam_width

    # 2. Werkzeugauswahl
    st.subheader("Struktur definieren")

    mode = st.radio(
        "Was möchtest du auf dem Gitter platzieren?",
        options=["Kräfte (Rot)", "Festlager (Blau)", "Loslager (Grün)"],
        horizontal=True
    )
    
    if mode == "Kräfte (Rot)":
        active_list = st.session_state.force_points
        st.info("Klicke auf Punkte, an denen Kräfte angreifen sollen.")
    elif mode == "Festlager (Blau)":
        active_list = st.session_state.fixed_points
        st.info("Klicke auf Punkte, die als Festlager dienen sollen.")
    else:
        active_list = st.session_state.roller_points
        st.info("Klicke auf Punkte, die als Loslager dienen sollen.")

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
        marker=dict(size=get_dynamic_point_size(length), color=point_colors, line=dict(width=1, color='black')),
        hoverinfo='text',
        text=[f"X: {xi:.0f}, Z: {yi:.0f}" for xi, yi in zip(x_flat, y_flat)]
    ))

    buf_x = max(1, length * 0.02)
    buf_y = max(1, width * 0.02)
    fig.update_layout(
        height = get_dynamic_plot_height(length, width),
        width=None,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(
            title="Länge", 
            range=[-buf_x, length + buf_x], 
            showgrid=False, 
            constrain="domain"
        ),
        yaxis=dict(
            title="Breite", 
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

    #5. Krafteingabe
    st.divider()
    st.subheader("Kräfte definieren")
    
    if len(st.session_state.force_points) == 0:
        st.info("Wähle im Gitter Kraftpunkte (Rot) aus, um hier deren Werte zu definieren.")
    else:
        st.info("Konvention: 0° = nach unten | -90° = nach links | 90° = nach rechts")

        if 'forces_data' not in st.session_state:
            st.session_state.forces_data = {}

        # Eingabefelder für jeden Punkt generieren
        for i, pt in enumerate(st.session_state.force_points):
            x, y = pt
            st.markdown(f"**Punkt {i+1} (X: {x:.0f}, Y: {y:.0f})**")
            col1, col2 = st.columns(2)
            
            with col1:
                mag = st.number_input("Kraft (N)", min_value=0.0, value=1.0, step=0.1, key=f"mag_{x}_{y}")
            with col2:
                angle = st.number_input("Winkel (°)", value=0, step=1, key=f"angle_{x}_{y}")
            
            # Berechnungen
            pt_key_str = f"{x}_{y}"
            angle_rad = math.radians(angle)
            force_x = round(mag * math.sin(angle_rad), 4) 
            force_y = round(mag * math.cos(angle_rad), 4) 
            
            # Direkt im State speichern
            st.session_state.forces_data[pt_key_str] = [force_x, force_y]

    #6. Abschlussbutton und in DB speichern
    st.divider()
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        # Button ist nur aktiv, wenn es mindestens eine Kraft gibt
        if st.button("Verformung berechnen", disabled=len(st.session_state.force_points) == 0, use_container_width=True):
            st.session_state.mode = 'bending_only'
            
            valid_force_keys = [f"{x}_{y}" for x, y in st.session_state.force_points]
            st.session_state.forces_data = {
                k: v for k, v in st.session_state.forces_data.items() 
                if k in valid_force_keys
            }
            # DB Update
            db_repository.update_calculation_data(
                calc_id=st.session_state.current_calc_id,
                fixed_points=st.session_state.fixed_points,
                roller_points=st.session_state.roller_points,
                force_points=st.session_state.force_points,
                forces_data=st.session_state.forces_data,
                mode=st.session_state.mode
            )
            
            st.session_state.app_step = "results"
            st.rerun(scope="app") # alles laden

    with col_btn2:
        if st.button("Optimierer hinzufügen", disabled=len(st.session_state.force_points) == 0, use_container_width=True):
            valid_force_keys = [f"{x}_{y}" for x, y in st.session_state.force_points]
            st.session_state.forces_data = {
                k: v for k, v in st.session_state.forces_data.items() 
                if k in valid_force_keys
            }
            
            st.session_state.app_step = "select_optimizer"
            st.rerun(scope="app")

def get_dynamic_plot_height(length, width,min_height=300, max_height=1000):
        """
        Berechnet die optimale Pixel-Höhe für den Plotly-Graphen
        """
        
        if length == 0: # Sicherheitscheck
            return min_height
            
        # Verhältnis von Breite zu Länge bestimmt die Höhe.
        ratio = width / length
        
        # Annahme: 700px Grundbreite, 80px für Schrift
        calculated_height = int(700 * ratio) + 80
        
        # Begrenzen, damit der Plot nicht sehr klein oder sehr groß wird
        if calculated_height < min_height:
            return min_height
        elif calculated_height > max_height:
            return max_height
        else:
            return calculated_height

def get_dynamic_point_size(length, plot_width_px=650):
    """
    Berechnet die optimale Punktgröße in Plotly
    """
    if length <= 0:
        return 5

    num_points_x = length
    
    # Verfügbare Pixel durch Anzahl der Punkte teilen -> Annahme 650px
    ideal_size = plot_width_px / num_points_x
    
    calculated_size = ideal_size * 1.05
    
    # size ncht größer als 15 oder kleiner als 3
    return max(3, min(calculated_size, 15))

def select_optimizer():
    st.header("Wähle den Optimierungsalgorithmus")

    # Auswahl des Algorithmus
    selected_opt = st.selectbox(
        "Algorithmus:",
        options=["SIMP Optimizer", "ESO HardKill Optimizer", "ESO SoftKill Optimizer"],
        key="optimizer_choice"
    )

    st.subheader("Parameter-Einstellungen")
    
    # Dictionary zum Sammeln der Parameter
    opt_settings = {}
    
    col1, col2 = st.columns(2)
    
    # Dieser Parameter gilt für alle:
    with col1:
        opt_settings["target_mass_ratio"] = st.slider(
            "Ziel-Massenverhältnis", min_value=0.1, max_value=0.9, value=0.4, step=0.05
        )

    # Dynamische Felder je nach Algorithmus:
    if selected_opt == "SIMP Optimizer":
        with col2:
            opt_settings["max_iterations"] = st.number_input("Max Iterationen", min_value=10, max_value=200, value=40, step=10)
        
        col3, col4 = st.columns(2)
        with col3:
            opt_settings["max_penalty"] = st.slider("Max Penalty", min_value=1.0, max_value=5.0, value=3.0, step=0.1)
        with col4:
            opt_settings["r_min"] = st.slider("Filter-Radius (r_min)", min_value=1.0, max_value=5.0, value=1.5, step=0.1)

    elif selected_opt == "ESO HardKill Optimizer":
        with col2:
            opt_settings["max_iterations"] = st.number_input("Max Iterationen", min_value=10, max_value=500, value=100, step=10)

    elif selected_opt == "ESO SoftKill Optimizer":
        with col2:
            opt_settings["max_iterations"] = st.number_input("Max Iterationen", min_value=10, max_value=500, value=100, step=10)
        
        col3, _ = st.columns(2)
        with col3:
             opt_settings["r_min"] = st.slider("Filter-Radius (r_min)", min_value=1.0, max_value=5.0, value=1.5, step=0.1)

    st.divider()

    # Für GIF Export --
    wants_gif = st.checkbox("Verlauf für GIF-Export aufzeichnen (kann die Berechnung leicht verlangsamen)")
    
    if st.button("Optimierung starten"):
        st.session_state.mode = 'optimization_and_bending'
        st.session_state.record_gif = wants_gif

        # Parameter in die Datenbank schicken
        db_repository.update_calculation_data(
            calc_id=st.session_state.current_calc_id,
            fixed_points=st.session_state.fixed_points,
            roller_points=st.session_state.roller_points,
            force_points=st.session_state.force_points,
            forces_data=st.session_state.forces_data,
            mode=st.session_state.mode,
            optimizer=st.session_state.optimizer_choice,
            optimizer_settings=opt_settings  # NEU HINZUGEFÜGT
        )

        st.session_state.app_step = "results"
        st.rerun()

def show_result_page():

    current_calc_id = st.session_state.get("current_calc_id")
    last_id = st.session_state.get("last_viewed_calc_id")
    if current_calc_id != last_id:
        reset_optimization_state() 
        st.session_state.last_viewed_calc_id = current_calc_id

    if "saved_structure" not in st.session_state or st.session_state.get("struct_calc_id") != current_calc_id:
        structure, calc_data = get_prepared_structure(current_calc_id)
        

        st.session_state.saved_structure = structure
        st.session_state.saved_calc_data = calc_data
        st.session_state.struct_calc_id = current_calc_id
    else:
        structure = st.session_state.saved_structure
        calc_data = st.session_state.saved_calc_data

    mode = calc_data.get('mode', 'bending_only')
    optimizer_type = calc_data.get('optimizer', None)
    if mode == 'optimization_and_bending':
        
        st.header("Rechenvorgang")
        opt1, opt2 = st.columns([2,1], vertical_alignment="bottom")
        with opt1:
            with st.container(border=True):
                plot_spot = st.empty()
                with st.spinner("Berechnung lädt (kann bei großen Strukturen etwas Zeit in Anspruch nehmen)..."):
                    run_optimization_loop(structure, optimizer_type, plot_spot, current_calc_id)
        with opt2:
            if st.button("💾 In Datenbank speichern"):
                db_repository.save_optimization_state(current_calc_id, st.session_state.json_ready_state, st.session_state.current_opt_type)
                st.success("Zustand in TinyDB gesichert!")

            if 'final_png_bytes' in st.session_state:
                st.download_button(
                    label="Bild speichern (PNG)",
                    data=st.session_state.final_png_bytes,
                    file_name=f"topologie_final_{current_calc_id}.png",
                    mime="image/png"
                )
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
        vis1, vis2 = st.columns([2,1], vertical_alignment="bottom")
        with vis1:
            with st.container(border=True):
                deformation = visualizer.plot_deformation(structure,  opt=st.session_state.current_opt, opt_type_internal=st.session_state.current_opt_type)
                st.pyplot(deformation, use_container_width=True)
                plt.close(deformation)

        with vis2:
            img_bytes = ImageExporter.get_image_bytes(deformation)
            st.download_button(
                label="Bild speichern (PNG)",
                data=img_bytes,
                file_name=f"deformation_{current_calc_id}.png",
                mime="image/png"
            )
    
    st.divider()
    st.header("Verformung der ganzen Struktur")
    def1, def2 = st.columns([2,1], vertical_alignment="bottom")
    with def1:
        with st.container(border=True):
            initial_beam, _ = get_prepared_structure(current_calc_id)
            initial_deformation = visualizer.plot_deformation(initial_beam, scale_factor=1.0)
            st.pyplot(initial_deformation, use_container_width=True)
    
    with def2:
        img_bytes = ImageExporter.get_image_bytes(initial_deformation)
        st.download_button(
            label="Bild speichern (PNG)",
            key="ganzeVerformung",
            data=img_bytes,
            file_name=f"deformation_{current_calc_id}.png",
            mime="image/png"
        )

    if st.button("🏠 Zurück zur Startseite"):
        reset_optimization_state() # 1. Speicher aufräumen
        st.session_state.app_step = "main_page"
        st.session_state.current_calc_id = None
        st.rerun() 

def reset_optimization_state():
    """Löscht alle spezifischen Optimierungs-Variablen aus dem Speicher."""
    keys_to_clear = [
        'current_opt', 
        'current_opt_type', 
        'opt_generator', 
        'opt_state', 
        'last_iteration', 
        'opt_frames', 
        'json_ready_state', 
        'final_png_bytes',
        'saved_structure',
        'saved_calc_data',
        'deformation_plot'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]