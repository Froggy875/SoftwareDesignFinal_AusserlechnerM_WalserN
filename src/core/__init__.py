'''import numpy as np
import matplotlib.pyplot as plt
from structureBuilder import StructureBuilder
from optimizer import ESO_HardKill_Optimizer, ESO_SoftKill_Optimizer, SIMP_Optimizer
from matplotlib.collections import LineCollection # performanter ...fix für langsamen dynamischen Plot

# --BEISPIEL VERWENDUNG--


# DIMENSIONEN
n_w = 60  # breite
n_h = 20  # höhe

# STRUKTUR
# rechteck bauen
structure = StructureBuilder.create_rectangle(n_points_w=n_w, n_points_h=n_h)

# AUFLAGER
# 1. auflagereigenschaften links und rechts

# links
idx_bottom_left = (n_h - 1) * n_w + 0
# gestperrt ja/nein: [x-koord, y-koord]
structure.get_node(idx_bottom_left).fixed = [True, True]

# rechts
idx_bottom_right = (n_h - 1) * n_w + (n_w - 1)
# gesperrt ja/nein: [x-koord, y-koord]
structure.get_node(idx_bottom_right).fixed = [False, True]


# KRAFT
idx_middle_right = n_w // 2        # Bei 4: Index 2
idx_middle_left = idx_middle_right - 1  # Bei 4: Index 1


# Kraftvektor Kraft/N [x,y] ...y nach unten!
force_vector = np.array([0.0, 0.1]) 

# 4 Kraftvektoren in der Mitte
structure.get_node(idx_middle_left).force = force_vector
structure.get_node(idx_middle_left-1).force = force_vector
structure.get_node(idx_middle_right).force = force_vector
structure.get_node(idx_middle_right+1).force = force_vector

# OPTIMIERUNG

# Provisorium zum Optimizer auswählen

print("Starte Optimierung...")
optimizer_type = "SIMP"

if optimizer_type == "SIMP":
    opt = SIMP_Optimizer(structure)
    opt_generator = opt.optimize(target_mass_ratio=0.4, max_penalty=3.0, max_iterations=40, r_min=1.5)

elif optimizer_type == "HARD_KILL":
    print("Initialisiere Hard-Kill Optimierer...")
    opt = ESO_HardKill_Optimizer(structure)
    opt_generator = opt.optimize(target_mass_ratio=0.4, max_iterations=100)

elif optimizer_type == "SOFT_KILL":
    print("Initialisiere Soft-Kill Optimierer...")
    opt = ESO_SoftKill_Optimizer(structure)
    opt_generator = opt.optimize(target_mass_ratio=0.4, max_iterations=100, r_min=1.5)


print(f"Optimierung ({optimizer_type}) abgeschlossen.")



# LIVE VISUALISIEREN
# (...performanteres Provisorium als vorher mit line collection)


# Variable zum testen, ob yield Logik funktioniert
user_pressed_stopped = False 

plt.ion() 
fig, ax = plt.subplots(figsize=(10, 5))

# "ui simulation für stop button..."
for iteration in opt_generator:
    
    # test, dass bei bestimmter iteration stop gedrückt wurde
    if iteration == 15:
        user_pressed_stopped = True
        
    if user_pressed_stopped:
        # Speicherlogik dummy
        print(f"\n---> Stand gespeichert (Iteration {iteration}) <---")
        break

    ax.clear()
    visible_elements = 0
    
    segments = []
    linewidths = []
    alphas = []
    
    # Daten sammeln statt direkt zu plotten
    for u, v in list(structure.get_edges()):
        edge_key = tuple(sorted((u, v)))
        rho = 1.0 
        
        if optimizer_type == "SIMP":
            spring = opt.structure.get_spring(*edge_key) 
            rho = spring.density
        elif optimizer_type in ["SOFT_KILL", "BESO"]:
            rho = min(opt.node_states.get(u, 1.0), opt.node_states.get(v, 1.0))

        if rho < 0.1:
            continue
            
        visible_elements += 1
        
        p1 = structure.get_node(u).pos
        p2 = structure.get_node(v).pos
        
        segments.append([p1, p2])
        linewidths.append(2.5 * rho)
        alphas.append(rho if optimizer_type != "HARD_KILL" else 1.0)

    colors = np.zeros((len(segments), 4))
    colors[:, 3] = alphas 
    
    if segments:
        lc = LineCollection(segments, colors=colors, linewidths=linewidths, capstyle='round')
        ax.add_collection(lc)

    for node_id in list(structure.get_nodes()):
        node = structure.get_node(node_id)
        if any(node.fixed):
            ax.plot(node.pos[0], node.pos[1], 'r^', markersize=8)
        elif np.linalg.norm(node.force) > 0:
            ax.plot(node.pos[0], node.pos[1], 'gv', markersize=8)

    ax.set_aspect('equal')
    ax.invert_yaxis()
    ax.set_title(f"Topologie: {optimizer_type} | Iteration: {iteration+1} (Elemente: {visible_elements})")
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    fig.canvas.flush_events() 
    plt.pause(0.001) 

plt.ioff()
plt.show()'''