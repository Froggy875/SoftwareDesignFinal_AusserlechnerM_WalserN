import streamlit as st
import matplotlib.pyplot as plt
import time
from ui.visualizer import plot_optimization_step
from core.optimizer import ESO_HardKill_Optimizer, ESO_SoftKill_Optimizer, SIMP_Optimizer
from database.db_repository import get_calculation_data 
from image_io.image_exporter import ImageExporter

def run_optimization_loop(structure, optimizer_type, plot_placeholder, calc_id):
    """Führt die Schleife aus und schreibt in den übergebenen Placeholder."""
    
    calc_data = get_calculation_data(calc_id)
    saved_state = calc_data.get('saved_opt_state', None)
    # Optimizer-Initialisierung
    if 'current_opt' not in st.session_state:
        if optimizer_type == "SIMP Optimizer":
            opt = SIMP_Optimizer(structure, initial_state=saved_state)
            gen = opt.optimize(target_mass_ratio=0.4)
            opt_type = "SIMP"
            
        elif "HardKill" in optimizer_type:
            opt = ESO_HardKill_Optimizer(structure, initial_state=saved_state)
            gen = opt.optimize(target_mass_ratio=0.4)
            opt_type = "HARD_KILL"
            
        else:
            opt = ESO_SoftKill_Optimizer(structure, initial_state=saved_state)
            gen = opt.optimize(target_mass_ratio=0.4)
            opt_type = "SOFT_KILL"
        
        st.session_state.current_opt = opt
        st.session_state.current_opt_type = opt_type
        st.session_state.last_iteration = saved_state.get("iteration", 0) if saved_state else 0
        #Leere Liste für die GIF-Frames initialisieren --
        st.session_state.opt_frames = []

        if saved_state:
            st.session_state.opt_state = "waiting"
        else:
            st.session_state.opt_state = "running"
            st.session_state.opt_generator = opt.optimize(target_mass_ratio=0.4)

    state = st.session_state.get("opt_state", "waiting")

    if state in ["waiting", "stopped"]:
        # 1. Statisches Bild vom aktuellen Stand zeigen
        fig = plot_optimization_step(
            st.session_state.current_opt.structure, 
            st.session_state.current_opt, 
            st.session_state.current_opt_type, 
            st.session_state.last_iteration
        )
        plot_placeholder.pyplot(fig, use_container_width=True)
        plt.close(fig)

        if st.button("▶️ Optimierung fortsetzen"):
            st.session_state.opt_state = "running"
            # Falls noch kein Generator existiert
            if 'opt_generator' not in st.session_state:
                st.session_state.opt_generator = st.session_state.current_opt.optimize(target_mass_ratio=0.4)
            st.rerun()
            
        return
    
    if state =="running":
        if st.button("🛑 Stop"):
            st.session_state.opt_state = "stopped"
            st.rerun()

        # Schleife konsumiert den Generator
        for step_data in st.session_state.opt_generator:
            st.session_state.json_ready_state = step_data
            current_iter = step_data["iteration"]
            st.session_state.last_iteration = current_iter  
            
            fig = plot_optimization_step(st.session_state.current_opt.structure, st.session_state.current_opt, st.session_state.current_opt_type, current_iter)
            
            # Frame nur für GIF umwandeln, wenn User die Checkbox angeklickt hat --
            if st.session_state.get("record_gif", False):
                frame = ImageExporter.fig_to_pil(fig)
                st.session_state.opt_frames.append(frame)

            plot_placeholder.pyplot(fig, use_container_width=True)
            st.session_state.final_png_bytes = ImageExporter.get_image_bytes(fig)
            plt.close(fig)
            
            # Kleines Delay, damit Streamlit UI-Updates zulässt
            time.sleep(0.02)

        st.session_state.opt_state = "finished"
        if 'opt_generator' in st.session_state:
            del st.session_state.opt_generator
        st.rerun()

    if state == "finished":
        # Finales Bild dauerhaft anzeigen
        if "final_png_bytes" in st.session_state:
            plot_placeholder.image(st.session_state.final_png_bytes, use_container_width=True)
            st.success("✅ Optimierung abgeschlossen!")
