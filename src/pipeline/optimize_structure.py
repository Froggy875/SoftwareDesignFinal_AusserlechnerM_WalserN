import streamlit as st
import matplotlib.pyplot as plt
import time
from ui.visualizer import plot_optimization_step
from core.optimizer import ESO_HardKill_Optimizer, ESO_SoftKill_Optimizer, SIMP_Optimizer
from database.db_repository import get_calculation_data 


def run_optimization_loop(structure, optimizer_type, plot_placeholder, calc_id):
    """Führt die Schleife aus und schreibt in den übergebenen Placeholder."""
    
    # Optimizer-Initialisierung
    if 'opt_generator' not in st.session_state:
        
        # 1. Prüfen, ob in der DB schon eine gespeicherte Optimierung vorhanden ist
        calc_data = get_calculation_data(calc_id)
        saved_state = calc_data.get('saved_opt_state', None)

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
        
        st.session_state.opt_generator = gen
        st.session_state.current_opt = opt
        st.session_state.current_opt_type = opt_type

    # Schleife konsumiert den Generator
    for step_data in st.session_state.opt_generator:
        st.session_state.json_ready_state = step_data
        current_iter = step_data["iteration"]        
        
        fig = plot_optimization_step(st.session_state.current_opt.structure, st.session_state.current_opt, st.session_state.current_opt_type, current_iter)
        
        plot_placeholder.pyplot(fig, use_container_width=True)
        plt.close(fig)
        
        # Kleines Delay, damit Streamlit UI-Updates zulässt
        time.sleep(0.01)

    st.session_state.opt_state = "finished"
    st.rerun()
