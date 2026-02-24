from core.elements import Node, Spring
import networkx as nx
import numpy as np
from core.solver import solve


class Structure:
    """
    Wrapper um NetworkX Graph mit zusätzlicher Funktionalität.
    Verhält sich wie ein NetworkX Graph.
    """
    def __init__(self):
        self._graph = nx.Graph()
    
    def add_node(self, node_id, node_obj: Node):
        """Fügt einen Node hinzu"""
        self._graph.add_node(node_id, data=node_obj)
    
    def add_spring(self, node_id_i, node_id_j, spring_obj: Spring):
        """Fügt eine Feder/Edge hinzu"""
        self._graph.add_edge(node_id_i, node_id_j, data=spring_obj)
    
    def get_node(self, node_id) -> Node:
        """Gibt Node-Objekt zurück"""
        return self._graph.nodes[node_id]['data']
    
    def get_spring(self, node_id_i, node_id_j) -> Spring:
        """Gibt Spring-Objekt zurück"""
        return self._graph.edges[node_id_i, node_id_j]['data']
    
    def remove_node(self, node_id):
        """Entfernt einen Knoten und alle verbundenen Federn"""
        self._graph.remove_node(node_id)

    def get_nodes(self):
            """Zugriff auf Graph Nodes"""
            return self._graph.nodes
        
    def get_edges(self):
        """Zugriff auf Graph Edges"""
        return self._graph.edges
        
    def get_graph(self):
        """Direkter Zugriff auf NetworkX Graph"""
        return self._graph
    
    def number_of_nodes(self):
        """Anzahl der Nodes"""
        return self._graph.number_of_nodes()
    
    def number_of_edges(self):
        """Anzahl der Edges"""
        return self._graph.number_of_edges()
    
    def to_dict(self):
        """
        Konvertiert die Struktur in ein Dictionary
        """
        result = {
            'nodes': [],
            'springs': []
        }
        
        # Nodes hinzufügen
        for node_id in self._graph.nodes():
            node_obj = self._graph.nodes[node_id]['data']
            result['nodes'].append({
                'id': node_obj.id,
                'pos': node_obj.pos.tolist()
            })
        
        # Springs hinzufügen
        for edge in self._graph.edges():
            spring_obj = self._graph.edges[edge]['data']
            result['springs'].append({
                'node_i': spring_obj.node_i.id,
                'node_j': spring_obj.node_j.id
            })
        
        return result
    
    def assemble_system(self):
            """
            Erstellt die globale Steifigkeitsmatrix K und den Kraftvektor F.
            (nach Folien 11-16)
            """
            n_nodes = self.number_of_nodes()
            # mapping von node_id zu Matrix-Index (nötig, falls IDs nicht 0,1,2... sind oder Knoten gelöscht werden)
            sorted_nodes = sorted(list(self.get_nodes()))
            id_to_idx = {node_id: i for i, node_id in enumerate(sorted_nodes)}

            n_dof = 2 * n_nodes  # 2 Freiheitsgrade pro Knoten (x, z)
            
            # Globale Matrix und Vektor initialisieren
            K_global = np.zeros((n_dof, n_dof))
            F_global = np.zeros(n_dof)
            
            # Kraftvektor F aufbauen
            for node_id in self.get_nodes():
                node = self.get_node(node_id)
                idx = id_to_idx[node_id]
                
                # Indizes im globalen Vektor: 2*idx für x, 2*idx+1 für y
                idx_x = 2 * idx
                idx_y = 2 * idx + 1
                
                F_global[idx_x] = node.force[0]
                F_global[idx_y] = node.force[1]

            # Steifigkeitsmatrix K aufbauen
            for edge in self.get_edges():
                spring = self.get_graph().edges[edge]['data']
                i = spring.node_i
                j = spring.node_j
                
                # 4x4 Matrix direkt aus dem Element
                K_elem_global = spring.K_global()
                
                # Indizes für die globale Matrix finden
                idx_i = id_to_idx[i.id]
                idx_j = id_to_idx[j.id]
                
                # ...4 FHG für Verschiebung pro Feder: [uix, uiy, ujx, ujy]
                indices = [2*idx_i, 2*idx_i+1, 2*idx_j, 2*idx_j+1]
                
                # Einsortieren in die globale Matrix (Superposition... Folie 16) 
                for row_local, row_global in enumerate(indices):
                    for col_local, col_global in enumerate(indices):
                        K_global[row_global, col_global] += K_elem_global[row_local, col_local]
                        
            return K_global, F_global, id_to_idx
    
    def solve(self):
            """Löst das Gleichungssystem K*u = F"""
            # System aufstellen
            K, F, id_to_idx = self.assemble_system()
            
            # Fixierte Indizes ermitteln (Randbedingungen)
            fixed_indices = []
            for node_id in self.get_nodes():
                node = self.get_node(node_id)
                idx = id_to_idx[node_id]
                if node.fixed[0]: fixed_indices.append(2 * idx)     # x fest
                if node.fixed[1]: fixed_indices.append(2 * idx + 1) # y fest
                
            # Solver callen
            u_vec = solve(K, F, fixed_indices)
            
            if u_vec is None:
                print("System ist singulär/nicht lösbar!")
                return None
            
            # Ergebnisse zurück in die Nodes schreiben
            for node_id in self.get_nodes():
                node = self.get_node(node_id)
                idx = id_to_idx[node_id]
                idx_x = 2 * idx
                idx_y = 2 * idx + 1
                node.displacement = np.array([u_vec[idx_x], u_vec[idx_y]])
                
            return u_vec