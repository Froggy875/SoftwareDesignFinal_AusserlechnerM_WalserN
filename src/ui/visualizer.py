import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

def plot_deformation(structure, scale_factor=1.0, opt=None, opt_type_internal=None):
    """
    Erstellt einen Plot der unverformten und verformten Struktur.
    Wenn 'opt' und 'opt_type_internal' übergeben werden, werden wegoptimierte 
    Elemente (Dichte < 0.1) ausgeblendet.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    
    active_nodes = set()

    # A & B) Elemente durchgehen, ggf. filtern und zeichnen
    for edge in structure.get_edges():
        u, v = edge
        edge_key = tuple(sorted((u, v)))
        rho = 1.0 
        
        # 1. Filter-Logik: Dichte berechnen, falls Optimierer übergeben wurde
        if opt is not None and opt_type_internal is not None:
            if opt_type_internal == "SIMP":
                spring = opt.structure.get_spring(*edge_key) 
                rho = spring.density
            elif opt_type_internal in ["SOFT_KILL", "BESO"]:
                rho = min(opt.node_states.get(u, 1.0), opt.node_states.get(v, 1.0))

        # 2. Unsichtbare Elemente überspringen
        if rho < 0.5:
            continue
            
        # Knoten als "aktiv" markieren
        active_nodes.add(u)
        active_nodes.add(v)
        
        spring = structure.get_graph().edges[edge]['data']
        
        # Unverformte Referenzstruktur zeichnen (Grau)
        pos_i = spring.node_i.pos
        pos_j = spring.node_j.pos
        ax.plot([pos_i[0], pos_j[0]], [pos_i[1], pos_j[1]], 'k--', linewidth=1, alpha=0.3)

        # Verformung berechnen
        pos_i_def = spring.node_i.pos + spring.node_i.displacement * scale_factor
        pos_j_def = spring.node_j.pos + spring.node_j.displacement * scale_factor
        
        # Verformtes Element zeichnen (Dicke/Transparenz anpassen, wenn optimiert)
        alpha_val = rho if (opt is not None and opt_type_internal != "HARD_KILL") else 0.8
        line_width = 2.5 * rho if opt is not None else 2.0
        
        ax.plot([pos_i_def[0], pos_j_def[0]], [pos_i_def[1], pos_j_def[1]], 'b-', linewidth=line_width, alpha=alpha_val)

    # C) Knotenpunkte zeichnen
    # Wenn wir filtern, nehmen wir nur active_nodes. Sonst alle Knoten der Struktur.
    nodes_to_plot = active_nodes if opt is not None else structure.get_nodes()

    # C) Knotenpunkte zeichnen
    for node_id in nodes_to_plot:
        node = structure.get_node(node_id)
        new_pos = node.pos + node.displacement * scale_factor
        
        # Farbe bestimmen
        color = 'blue'
        if node.fixed == [True, True]:
            color = 'red'     # Festlager
        elif node.fixed == [False, True]:
            color = 'skyblue'  # Horizontales Loslager
        elif node.fixed == [True, False]:
            color = 'orange'  # Vertikales Loslager
        elif np.linalg.norm(node.force) > 0: 
            color = 'green'   # Kraft
            
        ax.plot(new_pos[0], new_pos[1], marker='o', color=color, markersize=5, zorder=5)

    # D) Plot-Einstellungen
    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    
    # Titel dynamisch anpassen
    title_suffix = f" (Optimiert: {opt_type_internal})" if opt else ""
    ax.set_title(f'Verformung{title_suffix} (Skalierung: {scale_factor}x)\nRot=Fest, Blau=Los(h), Orange=Los(v), Grün=Kraft')    
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    ax.invert_yaxis() 
    
    plt.tight_layout()
    return fig

def plot_optimization_step(structure, opt, opt_type_internal, iteration):
    """
    Zeichnet den aktuellen Zustand der Optimierung (Dichten/Hardkill-Status).
    Gibt ein fertiges Matplotlib-Figure Objekt zurück.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
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
        # Lager und Farben unterscheiden
        if node.fixed == [True, True]:
            ax.plot(node.pos[0], node.pos[1], marker='^', color='red', markersize=8, zorder=5)     # Festlager
        elif node.fixed == [False, True]:
            ax.plot(node.pos[0], node.pos[1], marker='^', color='skyblue', markersize=8, zorder=5)  # Horizontales Loslager
        elif node.fixed == [True, False]:
            ax.plot(node.pos[0], node.pos[1], marker='^', color='orange', markersize=8, zorder=5)  # Vertikales Loslager
        elif np.linalg.norm(node.force) > 0:
            ax.plot(node.pos[0], node.pos[1], marker='v', color='green', markersize=8, zorder=5)   # Kraft

    # 4. Plot-Einstellungen
    ax.autoscale() 
    ax.set_aspect('equal')
    ax.invert_yaxis()
    ax.set_title(f"Topologie: {opt_type_internal} | Iteration: {iteration+1} (Elemente: {visible_elements})")
    ax.set_xlabel("X")
    ax.set_ylabel("Z")
    
    plt.tight_layout()
    
    return fig