import numpy as np
import networkx as nx
from structure import Structure

class BaseTopologyOptimizer:
    """
    Basisklasse für alle Optimizer
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


class ESO_BaseOptimizer(BaseTopologyOptimizer):
    """
    Gemeinsame Basisklasse für alle knotenbasierten ESO-Optimierer (HardKill, SoftKill):
    geteilte Logik für Energieberechnung und Knotenprüfung.
    """
    def __init__(self, structure):
        super().__init__(structure)
        self.initial_nodes_count = structure.number_of_nodes()

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
        Knoten mit Lasten oder Lagerbedingungen sind ausgeschlossen.
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
        
        # prüft, ob wir im softkill-modus sind und löscht die inaktiven knoten
        if hasattr(self, 'soft_killed_nodes'): #<--
            H.remove_nodes_from(self.soft_killed_nodes)
             
        H.remove_node(node_to_remove)
        
        # fängt den networkx-crash ab, falls der graph komplett leer wird
        if len(H.nodes) == 0:
            return True
            
        return nx.is_connected(H)


class ESO_HardKill_Optimizer(ESO_BaseOptimizer):
    """
    Topologieoptimierer, der Massepunkte (Knoten) basierend auf ihrer 
    Verformungsenergie entfernt.
    """

    def __init__(self, structure):
        super().__init__(structure)

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


class ESO_SoftKill_Optimizer(ESO_BaseOptimizer):
    """
    Soft Kill Optimierung mit Filter:
    Konten werden nicht gelöscht, sondern über Density Attribut abgeschwächt.
    Filter zum glätten der Knotenenergien -> etwas gleichmäßigere Strukturen
    """
    def __init__(self, structure):
        super().__init__(structure)
        self.soft_killed_nodes = set()
        self.node_states = {node_id: 1.0 for node_id in self.structure.get_nodes()}

    def optimize(self, target_mass_ratio=0.5, max_iterations=100, soft_kill_factor=1e-4, r_min=1.5):
        print(f"Start Optimierung (Softkill). Ziel-Massenverhältnis: {target_mass_ratio*100:.1f}%")
        
        target_mass = max(1, int(self.initial_nodes_count * target_mass_ratio))
        base_removal_rate = 0.02
        
        # Filter einmalig vor der Iterationsschleife vorbereiten
        print(f"Berechne Filter-Nachbarschaften für ESO (r_min={r_min})...")
        self._prepare_filter(r_min)

        for iteration in range(max_iterations):
            # Aktuelle "Masse" = Anzahl der noch nicht abgeschwächten Knoten
            current_active_mass = self.initial_nodes_count - len(self.soft_killed_nodes)
            
            if current_active_mass <= target_mass:
                print(f"Zielmasse erreicht! {current_active_mass} aktive Knoten verbleiben.")
                return
                
            # K * u = F nach u lösen
            if not self._solve_system():
                print(f"Iteration {iteration+1}: Solver fehlgeschlagen/instabil. Abbruch.")
                return
 
            # Wichtigkeit der Massepunkte aus Verformungsenergie berechnen
            node_energies = self._calculate_node_energies()
            
            # Filter auf die Knotenenergien anwenden
            node_energies = self._apply_energy_filter(node_energies)

            # Nur noch aktive Knoten sortieren
            active_energies = {n: e for n, e in node_energies.items() if n not in self.soft_killed_nodes}
            sorted_nodes = sorted(active_energies.items(), key=lambda item: item[1])
            
            # Zu entfernende Massepunkte für diese Iteration bestimmen
            current_removal_rate = min(0.05, base_removal_rate + (iteration * 0.002))
            nodes_to_remove_count = max(1, int(current_active_mass * current_removal_rate))
            
            if current_active_mass - nodes_to_remove_count < target_mass:
                nodes_to_remove_count = current_active_mass - target_mass
                
            nodes_removed_this_iter = 0
            
            # Massepunkte entfernen mit Prüfung und neue "Ist-Masse" berechnen
            for node_id, energy in sorted_nodes:
                if nodes_removed_this_iter >= nodes_to_remove_count:
                    break
                    
                if not self._is_removable(node_id):
                    continue
                    
                # Prüfen, ob das aktive Netzwerk zusammenhängend bleibt
                if not self._check_connectivity(node_id):
                    continue
                    
                # Knoten als inaktiv markieren und Status für den Plotter setzen
                self.soft_killed_nodes.add(node_id)
                self.node_states[node_id] = soft_kill_factor
                nodes_removed_this_iter += 1
            
            # Steifigkeiten basierend auf aktiven/inaktiven Knoten updaten
            self._update_spring_stiffnesses(soft_kill_factor)
            
            # yield iteration

            new_mass = self.initial_nodes_count - len(self.soft_killed_nodes)
            print(f"Iter {iteration+1}: {nodes_removed_this_iter} Knoten abgeschwächt. "
                  f"Verbleibend: {new_mass}/{self.initial_nodes_count} "
                  f"({(new_mass/self.initial_nodes_count)*100:.1f}%)")
            
            if nodes_removed_this_iter == 0:
                print("Abbruch: Keine weiteren Knoten können abgeschwächt werden (Zusammenhang/Lagerverlust).")
                return

    def _update_spring_stiffnesses(self, factor):
            """
            Setzt die Dichte der Federn auf den Softkill-Faktor,
            sobald mindestens einer der angrenzenden Knoten 'weg' ist.
            """
            for u, v in self.structure.get_edges():
                spring = self.structure.get_spring(u, v)
                if u in self.soft_killed_nodes or v in self.soft_killed_nodes:
                    spring.density = factor
                else:
                    spring.density = 1.0

    def _prepare_filter(self, r_min):
        """Berechnet Distanzen aller Knoten zueinander vorab für schnelles Filtern."""
        self.filter_weights = {node_id: [] for node_id in self.structure.get_nodes()}
        
        node_ids = list(self.structure.get_nodes())
        n_nodes = len(node_ids)
        
        for i in range(n_nodes):
            id_i = node_ids[i]
            pos_i = self.structure.get_node(id_i).pos
            
            # Gewicht zum eigenen Knoten (Distanz = 0 -> Gewicht = r_min)
            self.filter_weights[id_i].append((id_i, r_min))
            
            for j in range(i + 1, n_nodes):
                id_j = node_ids[j]
                pos_j = self.structure.get_node(id_j).pos
                
                # Distanz zwischen den Knoten
                dist = np.linalg.norm(pos_i - pos_j)
                
                if dist <= r_min:
                    # Gewicht sinkt mit zunehmender Distanz
                    h_factor = r_min - dist
                    self.filter_weights[id_i].append((id_j, h_factor))
                    self.filter_weights[id_j].append((id_i, h_factor))

    def _apply_energy_filter(self, node_energies):
        """Wendet den Filter auf die berechneten Knotenenergien an."""
        filtered_energies = {}
        
        for id_i, neighbors in self.filter_weights.items():
            sum_h = 0.0
            sum_h_e = 0.0
            
            for id_j, h_factor in neighbors:
                # Bug gefixt? falls nicht im dict enthalten: Energie des Nachbarn = 0
                # warum auch immer?
                e_j = node_energies.get(id_j, 0.0)
                
                sum_h += h_factor
                sum_h_e += h_factor * e_j
                
            # Gefilterte Energie zuweisen und Division durch 0 abfangen
            if sum_h > 0:
                filtered_energies[id_i] = sum_h_e / sum_h
            else:
                filtered_energies[id_i] = node_energies.get(id_i, 0.0)
                
        return filtered_energies