import numpy as np
import networkx as nx
from core.structure import Structure

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

    def _build_distance_filter(self, item_coordinates, r_min):
        """
        Generischer räumlicher Filter. 
        Erwartet ein Dictionary mit {id: numpy_array_position} und gibt die Filtergewichte zurück.
        """
        filter_weights = {item_id: [] for item_id in item_coordinates}
        item_ids = list(item_coordinates.keys())
        n_items = len(item_ids)
        
        for i in range(n_items):
            id_i = item_ids[i]
            pos_i = item_coordinates[id_i]
            
            # Gewicht zum eigenen Element/Knoten (Distanz = 0 -> Gewicht = r_min)
            filter_weights[id_i].append((id_i, r_min))
            
            for j in range(i + 1, n_items):
                id_j = item_ids[j]
                pos_j = item_coordinates[id_j]
                
                # Distanz berechnen
                dist = np.linalg.norm(pos_i - pos_j)
                
                if dist <= r_min:
                    # Gewicht sinkt linear mit zunehmender Distanz
                    h_factor = r_min - dist
                    filter_weights[id_i].append((id_j, h_factor))
                    filter_weights[id_j].append((id_i, h_factor))
                    
        return filter_weights


class ESO_BaseOptimizer(BaseTopologyOptimizer):
    """
    Gemeinsame Basisklasse für alle knotenbasierten ESO-Optimierer (HardKill, SoftKill):
    geteilte Logik für Energieberechnung und Knotenprüfung.
    """

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
        if hasattr(self, 'soft_killed_nodes'):
            H.remove_nodes_from(self.soft_killed_nodes)
             
        H.remove_node(node_to_remove)
        
        # fängt den networkx-crash ab, falls der graph komplett leer wird
        if len(H.nodes) == 0:
            return True
            
        return nx.is_connected(H)
    
    def _calculate_removal_count(self, current_mass, target_mass, iteration, base_removal_rate=0.02):
        """
        Berechnet, wie viele Knoten in der aktuellen Iteration entfernt bzw. abgeschwächt werden sollen.
        """
        current_removal_rate = min(0.05, base_removal_rate + (iteration * 0.002))
        nodes_to_remove_count = max(1, int(current_mass * current_removal_rate))
        
        # Über Ziel hinausschießen verhindern
        if current_mass - nodes_to_remove_count < target_mass:
            nodes_to_remove_count = current_mass - target_mass
            
        return nodes_to_remove_count


class ESO_HardKill_Optimizer(ESO_BaseOptimizer):
    """
    Evolutionary Structural Optimization
    Topologieoptimierer, der Massepunkte (Knoten) basierend auf ihrer 
    Verformungsenergie entfernt.
    """
    #neumathias
    def __init__(self, structure, initial_state=None):
        # 1. Basisklasse aufrufen (erstellt self.structure, self.initial_nodes_count etc.)
        super().__init__(structure) 
        
        # 2. Leeres Set für die entfernten Knoten vorbereiten
        self.removed_nodes = set()
        
        # 3. Savegame laden, falls eins übergeben wurde
        if initial_state is not None:
            self.current_iteration = initial_state.get("iteration", 0)
            self.removed_nodes = set(initial_state.get("removed_nodes", []))
            
            # Löcher direkt in die frisch geladene Struktur stanzen
            for node_id in self.removed_nodes:
                self.structure.remove_node(node_id)

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
                break
                
            # K * u = F nach u lösen
            if not self._solve_system():
                print(f"Iteration {iteration+1}: Solver fehlgeschlagen/instabil. Abbruch.")
                break
                
            # Wichtigkeit der Massepunkte aus Verformungsenergie berechnen
            node_energies = self._calculate_node_energies()
            
            # Knoten nach Energie sortieren (aufsteigend -> geringste Energie zuerst)
            sorted_nodes = sorted(node_energies.items(), key=lambda item: item[1])
            
            # Zu entfernende Massepunkte für diese Iteration bestimmen
            nodes_to_remove_count = self._calculate_removal_count(current_mass, target_mass, iteration, base_removal_rate)
                
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
                #neumathias
                self.removed_nodes.add(node_id)
                nodes_removed_this_iter += 1
                
            new_mass = self.structure.number_of_nodes()
            print(f"Iter {iteration+1}: {nodes_removed_this_iter} Knoten entfernt. "
                  f"Verbleibend: {new_mass}/{self.initial_nodes_count} "
                  f"({(new_mass/self.initial_nodes_count)*100:.1f}%)")
            
            '''neu'''
            yield {
                "iteration": iteration,
                "removed_nodes": list(self.removed_nodes)
            }
            #yield iteration -> alt

            if nodes_removed_this_iter == 0:
                print("Abbruch: Keine weiteren Knoten können entfernt werden, "
                      "ohne die Struktur zu zerstören (Zusammenhang/Lagerverlust).")
                break


class ESO_SoftKill_Optimizer(ESO_BaseOptimizer):
    """
    Evolutionary Structural Optimization
    Soft Kill Optimierung mit Filter:
    Konten werden nicht gelöscht, sondern über Density Attribut abgeschwächt.
    Filter zum glätten der Knotenenergien -> etwas gleichmäßigere Strukturen
    """
    def __init__(self, structure, initial_state=None):
        super().__init__(structure)
        self.soft_killed_nodes = set()
        self.node_states = {node_id: 1.0 for node_id in self.structure.get_nodes()}

        #neu mathias
        self.current_iteration = 0
        if initial_state is not None:
            self.current_iteration = initial_state.get("iteration", 0)
            self.soft_killed_nodes = set(initial_state.get("soft_killed_nodes", []))
            
            # JSON castet Int-Keys im Dict oft zu Strings. Sicherstellen, dass es Integers bleiben:
            self.node_states = {int(k): float(v) for k, v in initial_state.get("node_states", {}).items()}
            
            # Wenn Knoten schon inaktiv sind, Federn direkt anpassen (mit Standard-Faktor 1e-4)
            if self.soft_killed_nodes:
                self._update_spring_stiffnesses(1e-4)

    def optimize(self, target_mass_ratio=0.5, max_iterations=100, soft_kill_factor=1e-4, r_min=1.5):
        print(f"Start Optimierung (Softkill). Ziel-Massenverhältnis: {target_mass_ratio*100:.1f}%")
        
        target_mass = max(1, int(self.initial_nodes_count * target_mass_ratio))
        base_removal_rate = 0.02
        
        # Filter einmalig vor der Iterationsschleife vorbereiten
        print(f"Berechne Filter-Nachbarschaften für ESO (r_min={r_min})...")
        self._prepare_filter(r_min)

        for iteration in range(self.current_iteration, max_iterations):
            #neumathias
            self.current_iteration = iteration
            # Aktuelle "Masse" = Anzahl der noch nicht abgeschwächten Knoten
            current_active_mass = self.initial_nodes_count - len(self.soft_killed_nodes)
            
            if current_active_mass <= target_mass:
                print(f"Zielmasse erreicht! {current_active_mass} aktive Knoten verbleiben.")
                break
                
            # K * u = F nach u lösen
            if not self._solve_system():
                print(f"Iteration {iteration+1}: Solver fehlgeschlagen/instabil. Abbruch.")
                break
 
            # Wichtigkeit der Massepunkte aus Verformungsenergie berechnen
            node_energies = self._calculate_node_energies()
            
            # Filter auf die Knotenenergien anwenden
            node_energies = self._apply_energy_filter(node_energies)

            # Nur noch aktive Knoten sortieren
            active_energies = {n: e for n, e in node_energies.items() if n not in self.soft_killed_nodes}
            sorted_nodes = sorted(active_energies.items(), key=lambda item: item[1])
            
            # Zu entfernende Massepunkte für diese Iteration bestimmen
            nodes_to_remove_count = self._calculate_removal_count(current_active_mass, target_mass, iteration, base_removal_rate)
                
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
            
            #yield iteration
            #neumathias
            yield {
                "iteration": iteration,
                "soft_killed_nodes": list(self.soft_killed_nodes),
                "node_states": self.node_states
            }

            new_mass = self.initial_nodes_count - len(self.soft_killed_nodes)
            print(f"Iter {iteration+1}: {nodes_removed_this_iter} Knoten abgeschwächt. "
                  f"Verbleibend: {new_mass}/{self.initial_nodes_count} "
                  f"({(new_mass/self.initial_nodes_count)*100:.1f}%)")
            
            if nodes_removed_this_iter == 0:
                print("Abbruch: Keine weiteren Knoten können abgeschwächt werden (Zusammenhang/Lagerverlust).")
                break

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
        # Sammle alle Knoten-IDs und ihre Positionen
        node_coords = {
            node_id: self.structure.get_node(node_id).pos 
            for node_id in self.structure.get_nodes()
        }
        
        # Rufe die Basis-Methode auf
        self.filter_weights = self._build_distance_filter(node_coords, r_min)

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
    
class SIMP_Optimizer(BaseTopologyOptimizer):
    """
    Solid Isotropic Material with Penalization (SIMP).
    Steifigkeit der Ferdern kontinuierlich variiert.
    -> Minimierung der Nachgiebigkeit bei gegebenem Zielvolumen.
    """
    #neumathias
    def __init__(self, structure, initial_state=None):
        super().__init__(structure)
        self.current_iteration = 0
        self.current_penalty = 1.0
        self.old_densities = {}

        if initial_state is not None:
            self.current_iteration = initial_state.get("iteration", 0)
            self.current_penalty = initial_state.get("current_penalty", 1.0)
            
            # Dichten laden und direkt in die Federn schreiben
            for key_str, rho in initial_state.get("densities", {}).items():
                u, v = map(int, key_str.split('_'))
                spring = self.structure.get_spring(u, v)
                spring.density = rho
                spring.penalty = self.current_penalty
                    
            # Alte Dichten laden (als Tuples für den Konvergenzvergleich)
            self.old_densities = {tuple(map(int, k.split('_'))): v for k, v in initial_state.get("old_densities", {}).items()}

    def optimize(self, target_mass_ratio=0.5, max_penalty=3.0, max_iterations=50, min_density=0.001, r_min=1.5):
        print(f"Start SIMP Optimierung (Ziel: {target_mass_ratio*100:.1f}%)")
        
        self._renumber_nodes()
        n_springs = self.structure.number_of_edges()
        
        # Start Dichte direkt in den Elementen speichern, wenn Opiemierungsstand nicht geladen wird
        #neumathias
        if self.current_iteration == 0:
            for u, v in self.structure.get_edges():
                self.structure.get_spring(u, v).density = target_mass_ratio

        print("Berechne Filter-Nachbarschaften (passiert nur einmal)...")
        self._prepare_filter(r_min)
        print("Filter vorbereitet. Starte Iterationen.")

        current_penalty = 1.0
        #neumathias -> iteration von current iteration bis max
        for iteration in range(self.current_iteration, max_iterations):
            # Penalty-Faktor p wird von 1 auf max_penalty langsam erhöht
            # -> verhindert, dass der Algorithmus zu früh in lokalen Minima stecken bleibt...
            if current_penalty < max_penalty:
                step = (max_penalty - 1.0) / (max_iterations * 0.5)
                current_penalty = min(max_penalty, current_penalty + step)

            # Materialeigenschaften an die Federn übergeben
            for u, v in self.structure.get_edges():
                spring = self.structure.get_spring(u, v)
                spring.density = max(spring.density, min_density)
                spring.penalty = current_penalty  # Penalty ans Element übergeben

            # Berechnung K * u = f
            if not self._solve_system():
                print("SIMP: Solver instabil. Abbruch.")
                break
            
            # Sensitivitätsanalyse
            sensitivities = {}
            total_strain_energy = 0.0
            
            for u, v in self.structure.get_edges():
                edge_key = tuple(sorted((u, v)))
                spring = self.structure.get_spring(u, v)
                rho = max(spring.density, min_density)
                
                strain_energy_elem = spring.get_strain_energy()
                total_strain_energy += strain_energy_elem
                
                # Ableitung der Compliance nach der Dichte dC/drho.
                # Da U_elem bereits mit rho^p penalty bekommen hat, folgt die Rückrechnung:
                # dC/drho = p * rho^(p-1) * (U_elem / rho^p)
                dc_drho = current_penalty * (rho ** (current_penalty - 1)) * (strain_energy_elem / (rho**current_penalty))
                sensitivities[edge_key] = dc_drho

            # Filter um "zu harte Kanten/Pfade" zu vermeiden
            sensitivities = self._apply_sensitivity_filter(sensitivities)

            # Aktualisierung der Dichten unter Einhaltung der Massenbedingung
            self._update_densities_oc(sensitivities, target_mass_ratio, n_springs)
            
            # Ausgabe
            change = self._calculate_change()
            print(f"Iter {iteration+1} (p={current_penalty:.2f}): Energie={total_strain_energy:.4f}, Change={change:.4f}")
            
            #yield iteration
            yield {
                "iteration": iteration,
                "current_penalty": self.current_penalty,
                "densities": {f"{u}_{v}": self.structure.get_spring(u, v).density for u, v in self.structure.get_edges()},
                "old_densities": {f"{u}_{v}": val for (u, v), val in self.old_densities.items()}
            }

            # Konvergenzkriterium: Dichten ändert sich kaum noch und p hat sein Maximum erreicht hat
            if change < 0.01 and current_penalty == max_penalty:
                print("Konvergenz erreicht.")
                break

    def _prepare_filter(self, r_min):
            """Berechnet Distanzen aller Federn zueinander vorab für schnelles Filtern."""
            edge_coords = {}
            
            # Sammle alle Kanten-IDs (Tupel) und berechne ihre Mittelpunkte
            for u, v in self.structure.get_edges():
                edge_key = tuple(sorted((u, v)))
                node_i = self.structure.get_node(u)
                node_j = self.structure.get_node(v)
                edge_coords[edge_key] = (node_i.pos + node_j.pos) / 2.0
                
            # Rufe die Basis-Methode auf
            self.filter_weights = self._build_distance_filter(edge_coords, r_min)

    def _apply_sensitivity_filter(self, sensitivities):
            filtered_sensitivities = {}
            for key_i, neighbors in self.filter_weights.items():
                sum_h = 0.0
                sum_hs_rho = 0.0
                rho_i = max(self.structure.get_spring(*key_i).density, 1e-6) 
                
                # Gewichtete Summe der Sensitivitäten der Nachbarn
                # (Summe(H_j * rho_j * sens_j)) / (rho_i * Summe(H_j))
                for key_j, h_factor in neighbors:
                    rho_j = self.structure.get_spring(*key_j).density
                    sens_j = sensitivities[key_j]
                    sum_h += h_factor
                    sum_hs_rho += h_factor * rho_j * sens_j
                    
                filtered_sensitivities[key_i] = sum_hs_rho / (rho_i * sum_h)
            return filtered_sensitivities

    def _update_densities_oc(self, sensitivities, target_ratio, n_elements):
            move = 0.2     # "move limit:" Maximale Änderung der Dichte pro Iteration
            damping = 0.5  # Dämpfungsfaktor
            
            # Bisektionsverfahren zur Bestimmung des Lagrange-Multiplikators (l_mid)
            # ...sucht l_mid, bei dem das Zielvolumen exakt erreicht wird
            l1 = 0.0
            l2 = 100000.0
            target_sum = n_elements * target_ratio
            new_densities = {}
            
            # Solange das Intervall [l1, l2] groß ist, halbiere weiter
            while (l2 - l1) / (l2 + l1 + 1e-10) > 1e-3:
                l_mid = 0.5 * (l2 + l1)
                current_sum = 0.0
                temp_densities = {}
                
                for u, v in self.structure.get_edges():
                    edge_key = tuple(sorted((u, v)))
                    spring = self.structure.get_spring(u, v)
                    rho = spring.density
                    sens = sensitivities[edge_key]
                    
                    # Dichte Anpassen
                    # rho_neu = rho * (Sensitivität / Lagrange-Multiplikator)^Dämpfung
                    factor = (sens / l_mid) ** damping
                    val = rho * factor
                    
                    # bergrenzt die Änderung auf das Move Limit von oben und den gültigen Bereich [0.001, 1.0]
                    val = max(1e-3, max(rho - move, min(1.0, min(rho + move, val))))
                    
                    temp_densities[edge_key] = val
                    current_sum += val
                
                # Ist die berechnete Masse zu groß, muss der Multiplikator l_mid steigen (l1 anheben)
                if current_sum > target_sum:
                    l1 = l_mid
                else:
                    l2 = l_mid
                    new_densities = temp_densities 
            
            # Alte Dichten merken und neue Dichten in die Elemente schreiben
            self.old_densities = {}
            for u, v in self.structure.get_edges():
                edge_key = tuple(sorted((u, v)))
                spring = self.structure.get_spring(u, v)
                self.old_densities[edge_key] = spring.density
                spring.density = new_densities[edge_key]

    def _calculate_change(self):
        # Berechnet die maximale Dichteänderung (L-unendlich Norm) für das Konvergenzkriterium
        
        # hasattr() verhindert einen Fehler beim ersten Durchlauf, da die Variable für den 
        # Vergleich der Dichten erst am Ende der ersten Iteration erstellt wird...
        if not hasattr(self, 'old_densities'): return 1.0
        max_diff = 0.0
        for u, v in self.structure.get_edges():
            edge_key = tuple(sorted((u, v)))
            current_rho = self.structure.get_spring(u, v).density
            diff = abs(current_rho - self.old_densities.get(edge_key, 0))
            if diff > max_diff: max_diff = diff
        return max_diff