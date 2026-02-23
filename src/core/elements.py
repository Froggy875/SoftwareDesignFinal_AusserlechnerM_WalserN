import numpy as np

class Node:
    """Klasse für Massenpunkt"""
    def __init__(self, node_id, pos: np.array): 
        self.id = node_id
        self.pos = np.array(pos)
        # Kraftvektor [Fx, Fy]
        self.force = np.zeros(2) 
        # Fixierung [Fix_x, Fix_y] (True = fest, False = beweglich)
        self.fixed = [False, False] 
        # Verschiebung nach Berechnung [ux, uy]
        self.displacement = np.zeros(2)
        

class Spring:
    """Klasse für Feder/Verbindung von Massepunkten"""
    def __init__(self, node_i: Node, node_j: Node):
        self.node_i = node_i
        self.node_j = node_j
        self.density = 1.0 # für SoftKillOptimizer
        self.penalty = 1.0  # für SIMP_Optimizer
        
        # Berechnung von k (Folie 24)
        dist = np.linalg.norm(node_j.pos - node_i.pos)
        # Wenn Distanz ca. 1 (horizontal/vertikal bei Grid=1) -> k=1
        if dist <= 1.0:
            self.k = 1.0
        
        # Wenn Distanz > 1 (diagonal) -> k=1/sqrt(2)
        else:
            self.k = 1.0 / np.sqrt(2.0)

    def get_direction(self):
        """Berechnet den Einheitsvektor und die Länge der Feder"""
        vec = self.node_j.pos - self.node_i.pos
        length = np.linalg.norm(vec)
        if length == 0:
            return np.zeros(2), 0.0
        return vec / length, length

    def K_local(self):
        """
        Elementsteifigkeitsmatrix im lokalen System (1D).
        Ergibt eine 2x2 Matrix für die Federsteifigkeit k.
        """
        # für SIMP und Softkill: k_eff = k0 * (rho^p)
        k_eff = self.k * (max(self.density, 1e-9) ** self.penalty)

        return k_eff * np.array([[1.0, -1.0], [-1.0, 1.0]])

    def K_global(self):
        """
        Transformiert die lokale Steifigkeitsmatrix in das globale System.
        Rückgabe ist eine 4x4 Matrix (für 2 Knoten mit je 2 Freiheitsgraden).
        """
        # Richtungsvektor holen
        e_n, length = self.get_direction()
        
        # Transformationsmatrix O = n * n^T (Folie 13)
        O = np.outer(e_n, e_n)
        
        # Lokale Matrix
        K_loc = self.K_local()
        
        # Transformation ins globale System (Kronecker-Produkt)
        # ...ähnlich, wie in solver.py: Ko = np.kron(K, O)
        return np.kron(K_loc, O)
    
    def get_strain_energy(self):
        """
        Berechnet die elementare Dehnungsenergie der Feder.
        Formel: 0.5 * u^T * K * u
        """
        # Globale Steifigkeitsmatrix für dieses Element abrufen
        K_elem = self.K_global()
        
        # Verschiebungsvektor für dieses Element (4 Einträge) aus den Knoten holen
        u_vec = np.concatenate((self.node_i.displacement, self.node_j.displacement))
        
        # Energie berechnen und zurückgeben
        return 0.5 * (u_vec.T @ K_elem @ u_vec)