import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from elements import Node, Spring
from structureBuilder import StructureBuilder
from optimizer import TopologyOptimizer


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
structure.get_node(idx_bottom_right).fixed = [True, True]


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

#OPTIMIERUNG
optimizer = TopologyOptimizer(structure)
optimizer.optimize(target_mass_ratio=0.5, max_iterations=100)

# LÖSEN UND VISUALISIEREN

# bereitgestellter solver
structure.solve()

# plot erstellen
fig, ax = plt.subplots(figsize=(10, 7))

# skalierungsfaktor für sehr kleine bzw. große verformungen
scale_factor = 1.0 

# UNVERFORMTE Struktur zeichen
for edge in structure.get_edges():
    spring = structure.get_graph().edges[edge]['data']
    pos_i = spring.node_i.pos
    pos_j = spring.node_j.pos
    ax.plot([pos_i[0], pos_j[0]], [pos_i[1], pos_j[1]], 'k--', linewidth=1, alpha=0.3)

"""

# VERFORMTE Struktur zeichen
for edge in structure.get_edges():
    spring = structure.get_graph().edges[edge]['data']
        
    # neue Position = alte Position + Verschiebung * Skalierungsfaktor
    pos_i_def = spring.node_i.pos + spring.node_i.displacement * scale_factor
    pos_j_def = spring.node_j.pos + spring.node_j.displacement * scale_factor
        
    ax.plot([pos_i_def[0], pos_j_def[0]], [pos_i_def[1], pos_j_def[1]], 'b-', linewidth=2, alpha=0.8)

# Konten an neuer Postion zeichen
for node_id in structure.get_nodes():
    node = structure.get_node(node_id)
    new_pos = node.pos + node.displacement * scale_factor
        
    # Farben: rot = fest, grün = Kraft drauf, sonst blau
    color = 'blue'
    if node.fixed[0] or node.fixed[1]: color = 'red'
    elif np.linalg.norm(node.force) > 0: color = 'green'
        
    ax.plot(new_pos[0], new_pos[1], marker='o', color=color, markersize=8)

"""    
        
# plot optionen
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title(f'Verformung (Skalierung: {scale_factor}x)\nRot=Fest, Grün=Kraft')
ax.grid(True, alpha=0.3)
ax.axis('equal')
    
# WICHTIG: y-achse muss nach unten zeigen!!
ax.invert_yaxis() 
    
plt.tight_layout()
plt.show()