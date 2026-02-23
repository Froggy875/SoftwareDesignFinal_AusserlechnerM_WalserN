import numpy as np
import matplotlib.pyplot as plt
from structureBuilder import StructureBuilder
from optimizer import ESO_HardKill_Optimizer, ESO_SoftKill_Optimizer


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
optimizer_type = "SOFT_KILL"

if optimizer_type == "HARD_KILL":
    print("Initialisiere Hard-Kill Optimierer...")
    opt = ESO_HardKill_Optimizer(structure)
    opt.optimize(target_mass_ratio=0.4, max_iterations=100)

elif optimizer_type == "SOFT_KILL":
    print("Initialisiere Soft-Kill Optimierer...")
    opt = ESO_SoftKill_Optimizer(structure)
    opt.optimize(target_mass_ratio=0.4, max_iterations=100, r_min=1.5)

print(f"Optimierung ({optimizer_type}) abgeschlossen.")



# VISUALISIEREN

# ...Optimierer abhängiges provisorium

fig, ax = plt.subplots(figsize=(10, 5))
visible_elements = 0

for u, v in list(structure.get_edges()):
    edge_key = tuple(sorted((u, v)))
    
    # Standardwert 1.0 für den Hard-Kill
    rho = 1.0 
    
    if optimizer_type == "SOFT_KILL":
        # Bei Soft-Kill hängt die Feder vom schwächsten anliegenden Knoten ab
        rho = min(opt.node_states.get(u, 1.0), opt.node_states.get(v, 1.0))

    # Filter
    if rho < 0.1:
        continue
    
    visible_elements += 1
    
    node_i = structure.get_node(u)
    node_j = structure.get_node(v)
    
    p1 = node_i.pos
    p2 = node_j.pos
    
    # Transparenz (alpha) und Dicke angepasst plotten
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 
            color='black', 
            linewidth=2.5 * rho, 
            solid_capstyle='round',
            alpha=rho if optimizer_type != "HARD_KILL" else 1.0)

# Lager und Kräfte zeichnen
for node_id in list(structure.get_nodes()):
    node = structure.get_node(node_id)
    
    if any(node.fixed):
        ax.plot(node.pos[0], node.pos[1], 'r^', markersize=8, label='Festlager')
    elif np.linalg.norm(node.force) > 0:
        ax.plot(node.pos[0], node.pos[1], 'gv', markersize=8, label='Last')

# Achsen formatieren
ax.set_aspect('equal')
ax.invert_yaxis()
ax.set_title(f"Topologie: {optimizer_type} (Sichtbare Elemente: {visible_elements})")
ax.set_xlabel("x")
ax.set_ylabel("y")

# Plot settings
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys())

plt.tight_layout()
plt.show()