import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

def plot_deformation(structure, scale_factor=1.0):
    """
    Erstellt einen Plot der unverformten und verformten Struktur.
    Gibt das Matplotlib Figure-Objekt zurück.
    """
    fig, ax = plt.subplots(figsize=(5, 3))

    # A) Unverformte Struktur (Grau) als Referenz
    for edge in structure.get_edges():
        spring = structure.get_graph().edges[edge]['data']
        pos_i = spring.node_i.pos
        pos_j = spring.node_j.pos
        ax.plot([pos_i[0], pos_j[0]], [pos_i[1], pos_j[1]], 'k--', linewidth=1, alpha=0.3)

    # B) Verformung berechnen (blau)
    for edge in structure.get_edges():
        spring = structure.get_graph().edges[edge]['data']
        
        # Position nach Verformung berechnen
        pos_i_def = spring.node_i.pos + spring.node_i.displacement * scale_factor
        pos_j_def = spring.node_j.pos + spring.node_j.displacement * scale_factor
        
        ax.plot([pos_i_def[0], pos_j_def[0]], [pos_i_def[1], pos_j_def[1]], 'b-', linewidth=2, alpha=0.8)

    # C) Zeichne Knoten an der NEUEN Position
    for node_id in structure.get_nodes():
        node = structure.get_node(node_id)
        # Und auch hier für die Knoten-Punkte:
        new_pos = node.pos + node.displacement * scale_factor
        
        # Farbe: Rot wenn fest, Gelb wenn Rolle, Grün wenn Kraft drauf, sonst Blau
        color = 'blue'
        if node.fixed[0] != node.fixed[1]: 
            color = 'yellow'  # Rollenlager
        elif any(node.fixed): 
            color = 'red'     # Festlager
        elif np.linalg.norm(node.force) > 0: 
            color = 'green'   # Kraft
            
        ax.plot(new_pos[0], new_pos[1], marker='o', color=color, markersize=5, zorder=5)

    # D) Plot-Einstellungen
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title(f'Verformung (Skalierung: {scale_factor}x)\nRot=Festlager, Gelb=Loslager, Grün=Kraft')
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    
    # Y-Achse invertieren (da positive y-Achse runter zeigt)
    ax.invert_yaxis() 
    
    plt.tight_layout()
    return fig


def plot_optimization_step(structure, opt, opt_type_internal, iteration):
    """
    Zeichnet den aktuellen Zustand der Optimierung (Dichten/Hardkill-Status).
    Gibt ein fertiges Matplotlib-Figure Objekt zurück.
    """
    fig, ax = plt.subplots(figsize=(5, 3))
    visible_elements = 0
    
    segments = []
    linewidths = []
    alphas = []
    
    # 1. Elemente und Dichten auswerten
    for u, v in list(structure.get_edges()):
        edge_key = tuple(sorted((u, v)))
        rho = 1.0 
        
        # Dichte je nach Optimierer abrufen
        if opt_type_internal == "SIMP":
            spring = opt.structure.get_spring(*edge_key) 
            rho = spring.density
        elif opt_type_internal in ["SOFT_KILL", "BESO"]:
            rho = min(opt.node_states.get(u, 1.0), opt.node_states.get(v, 1.0))

        # Unsichtbare Elemente überspringen
        if rho < 0.1:
            continue
            
        visible_elements += 1
        
        p1 = structure.get_node(u).pos
        p2 = structure.get_node(v).pos
        
        segments.append([p1, p2])
        linewidths.append(2.5 * rho)
        alphas.append(rho if opt_type_internal != "HARD_KILL" else 1.0)

    # 2. Linien zeichnen
    colors = np.zeros((len(segments), 4))
    colors[:, 3] = alphas 
    
    if segments:
        lc = LineCollection(segments, colors=colors, linewidths=linewidths, capstyle='round')
        ax.add_collection(lc)

    # 3. Knoten, Lager und Kräfte einzeichnen
    for node_id in list(structure.get_nodes()):
        node = structure.get_node(node_id)
        if any(node.fixed):
            ax.plot(node.pos[0], node.pos[1], 'r^', markersize=8, zorder=5) # zorder legt es in den Vordergrund
        elif np.linalg.norm(node.force) > 0:
            ax.plot(node.pos[0], node.pos[1], 'gv', markersize=8, zorder=5)

    # 4. Plot-Einstellungen
    ax.autoscale() 
    ax.set_aspect('equal')
    ax.invert_yaxis()
    ax.set_title(f"Topologie: {opt_type_internal} | Iteration: {iteration} (Elemente: {visible_elements})")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    
    plt.tight_layout()
    
    return fig