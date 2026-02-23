import numpy as np
import networkx as nx
from structure import Structure

class TopologyOptimizer:
    """
    Topologieoptimierer, der Massepunkte (Knoten) basierend auf ihrer 
    Verformungsenergie entfernt.
    """
    def __init__(self, structure: Structure):
        self.structure = structure
        self.initial_nodes_count = structure.number_of_nodes()

    def _solve_system(self):
        """
        Versucht das System zu lösen.
        Gibt True zurück, wenn erfolgreich gelöst wurde.
        """
        try:
            u_vec = self.structure.solve()
            if u_vec is not None:
                return True
        except Exception as e:
            print(f"Solver-Fehler: {e}")
        return False

    def _renumber_nodes(self):
        """
        Nummeriert Knoten neu (0 bis N-1) für Matrix-Assembly.
        """
        mapping = {}
        new_id = 0
        current_ids = sorted(list(self.structure.get_nodes()))

        for old_id in current_ids:
            mapping[old_id] = new_id
            self.structure.get_node(old_id).id = new_id
            new_id += 1

        nx.relabel_nodes(self.structure.get_graph(), mapping, copy=False)

    def _calculate_node_energies(self):
        """
        Holt die Verformungsenergie elementweise und teilt sie auf die Knoten auf.
        """
        energies = {node_id: 0.0 for node_id in self.structure.get_nodes()}
        
        for u, v in self.structure.get_edges():
            spring = self.structure.get_spring(u, v)
            
            # Verformungsenergie holen
            strain_energy_elem = spring.get_strain_energy()
            
            # Energie 50/50 auf die beiden verbundenen Knoten aufteilen
            energies[u] += strain_energy_elem / 2.0
            energies[v] += strain_energy_elem / 2.0
            
        return energies

    def _is_removable(self, node_id):
        """
        Prüft, ob ein Knoten entfernt werden darf.
        Knoten mit Lasten oder Lagerbedingungen (Randbedingungen) sind ausgeschlossen.
        """
        node = self.structure.get_node(node_id)
        
        # Ist Node ein Lager?
        if node.fixed[0] or node.fixed[1]:
            return False
        
        # Greift an Node eine Kraft an?
        if node.force[0] != 0 or node.force[1] != 0:
            return False
        return True
    
    def _check_connectivity(self, node_to_remove):
        """
        Prüft den Graphen für das Sub-Netzwerk der aktiven Knoten.
        """
        H = self.structure.get_graph().copy()
        H.remove_node(node_to_remove)
        
        # fängt den networkx-crash ab, falls der graph komplett leer wird
        if len(H.nodes) == 0:
            return True
            
        return nx.is_connected(H)

    def optimize(self, target_mass_ratio=0.5, max_iterations=100):
        print(f"Start Optimierung (Knoten-Entfernung). Ziel-Massenverhältnis: {target_mass_ratio*100:.1f}%")
        
        target_mass = max(1, int(self.initial_nodes_count * target_mass_ratio))
        
        # ...wie in Folien empfohlen:
        # Adaptive Entfernungsrate: Startet klein (2%), damit die Struktur sich in
        # den ersten Iterationen "setzen" kann und Lastpfade gefunden werden.
        base_removal_rate = 0.02
        
        for iteration in range(max_iterations):
            current_mass = self.structure.number_of_nodes()
            
            # Abbruchbedingung (laut UML: Ist-Masse <= Soll-Masse)
            if current_mass <= target_mass:
                print(f"Zielmasse erreicht! {current_mass} Knoten verbleiben.")
                return
                
            # K * u = F nach u lösen
            if not self._solve_system():
                print(f"Iteration {iteration+1}: Solver fehlgeschlagen/instabil. Abbruch.")
                return
                
            # Wichtigkeit der Massepunkte aus Verformungsenergie berechnen
            node_energies = self._calculate_node_energies()
            
            # Knoten nach Energie sortieren (aufsteigend -> geringste Energie zuerst)
            sorted_nodes = sorted(node_energies.items(), key=lambda item: item[1])
            
            # Zu entfernende Massepunkte für diese Iteration bestimmen
            # Die Rate steigt pro Iteration leicht an (max. 5% pro Iteration)
            current_removal_rate = min(0.05, base_removal_rate + (iteration * 0.002))
            nodes_to_remove_count = max(1, int(current_mass * current_removal_rate))
            
            # Verhindern, dass wir über das Ziel hinausschießen
            if current_mass - nodes_to_remove_count < target_mass:
                nodes_to_remove_count = current_mass - target_mass
                
            nodes_removed_this_iter = 0
            
            # Massepunkte entfernen & neue Ist-Masse berechnen (mit Prüfungen)
            for node_id, energy in sorted_nodes:
                if nodes_removed_this_iter >= nodes_to_remove_count:
                    break
                    
                # Darf der Knoten entfernt werden? (Kein Lager/Keine Last)
                if not self._is_removable(node_id):
                    continue
                    
                # Bleibt die Struktur aus einem Stück? (Sichert Lastabtragung)
                if not self._check_connectivity(node_id):
                    continue
                    
                # Wenn alle Tests bestanden sind: Knoten sicher entfernen
                self.structure.remove_node(node_id)
                nodes_removed_this_iter += 1
                
            new_mass = self.structure.number_of_nodes()
            print(f"Iter {iteration+1}: {nodes_removed_this_iter} Knoten entfernt. "
                  f"Verbleibend: {new_mass}/{self.initial_nodes_count} "
                  f"({(new_mass/self.initial_nodes_count)*100:.1f}%)")
            
            # yield iteration

            if nodes_removed_this_iter == 0:
                print("Abbruch: Keine weiteren Knoten können entfernt werden, "
                      "ohne die Struktur zu zerstören (Zusammenhang/Lagerverlust).")
                return