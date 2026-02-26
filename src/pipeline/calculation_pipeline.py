from database.db_repository import get_calculation_data
from pipeline.build_and_solve_structure import build_and_solve_structure

def get_prepared_structure(calc_id: int):
    """
    Lädt die Daten aus der Datenbank und baut die fertige Basis-Struktur.
    """
    calc_data = get_calculation_data(calc_id)
    structure = build_and_solve_structure(calc_data)
    
    return structure, calc_data


'''def render_optimization_section(structure, optimizer_type, calc_id):
    """Baut das UI für die Optimierung auf und steuert die Buttons."""
    
    # 1. Datenbank-Stand prüfen
    calc_data = get_calculation_data(calc_id)
    saved_state = calc_data.get('saved_opt_state')
    has_saved_state = saved_state is not None

    if 'opt_state' not in st.session_state:
        st.session_state.opt_state = "pending"

    st.divider()
    st.subheader("2. Strukturoptimierung")

    col_l, col_main, col_r = st.columns([1, 4, 1])
    
    with col_main:
        plot_spot = st.empty() 
        
        # Plot-Vorschau: Entweder aus der laufenden Session oder aus dem DB-Stand
        if "json_ready_state" in st.session_state and "current_opt" in st.session_state:
            # Fall A: Optimierung läuft gerade oder wurde pausiert
            opt = st.session_state.current_opt
            iteration = st.session_state.json_ready_state["iteration"]
            fig = visualizer.plot_optimization_step(opt.structure, opt, st.session_state.current_opt_type, iteration)
            plot_spot.pyplot(fig, use_container_width=True)
            plt.close(fig)
            
        elif has_saved_state:
            # Fall B: Seite wurde frisch geladen, aber wir haben Daten in der DB
            st.info(f"Gespeicherter Spielstand gefunden: Iteration {saved_state['iteration']}")

        # Interaktions-Logik
        state = st.session_state.get("opt_state", "pending")

        if state == "pending":
            if has_saved_state:
                label = f"▶️ Optimierung fortsetzen (ab Iteration {saved_state['iteration']})"
            else:
                label = "🚀 Optimierung starten"
                
            if st.button(label, type="primary", use_container_width=True):
                st.session_state.opt_state = "running"
                st.rerun()

        elif state == "running":
            if st.button("⏸️ Pausieren", use_container_width=True):
                st.session_state.opt_state = "stopped"
                st.rerun()
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
                        #Optimierungswerte löschen
                        delete_optimization_state(calc_id) 
                        
                        st.session_state.opt_state = "pending"
                        st.session_state.pop("json_ready_state", None)
                        st.session_state.pop("opt_generator", None)
                        st.session_state.pop("current_opt", None) # Das am besten auch leeren!
                        st.rerun()
            
            with col2:
                if st.button("💾 In Datenbank speichern", use_container_width=True):
                    save_optimization_state(calc_id, st.session_state.json_ready_state, st.session_state.current_opt_type)
                    st.success("Zustand in TinyDB gesichert!")'''