import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

#Dummy Daten
nx = 200
ny = 25
L, W = 1.0, 0.1

x_init = np.linspace(0, L, nx)
y_init = np.linspace(-W/2, W/2, ny)
X, Y = np.meshgrid(x_init, y_init)

biegung = -0 * np.sin(np.pi * X / L) 
Y_neu = Y + biegung

x_plot = X.flatten()
y_plot = Y_neu.flatten()

farb_werte = biegung.flatten()

# Visualisierungsfunktion
def plot_dense_beam(x, y, colors):
    fig, ax = plt.subplots(figsize=(10, 3))

    sc = ax.scatter(
        x, y, 
        c=colors,      
        s=1,              
        edgecolor='none',   
        cmap='turbo',       
        alpha=0.9         
    )


    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label('Vertikale Verschiebung (m)')


    draw_support(ax, x_pos=0, y_bottom=-W/2, support_type="Festlager", size=0.05)

    draw_support(ax, x_pos=L, y_bottom=-W/2, support_type="Loslager", size=0.05)
    ax.set_aspect('equal') 
    ax.set_title(f"Visualisierung mit {len(x)} diskreten Massepunkten")

    # Zoom-Bereich etwas größer als der Balken
    ax.set_xlim(-0.5, L + 0.5)
    ax.set_ylim(np.min(y)-0.5, np.max(y)+0.5)

    return fig

def draw_support(ax, x_pos, y_bottom, support_type="Festlager", size=0.01):
    """
    Zeichnet ein mechanisches Lager an die Position x_pos, y_bottom.
    size: Skalierungsfaktor für die Größe des Symbols relative zum Plot
    """
    # Dreieck für Lager
    # Punkte: Spitze oben, Ecke links unten, Ecke rechts unten
    triangle_points = [
        [x_pos, y_bottom], 
        [x_pos - size/2, y_bottom - size], 
        [x_pos + size/2, y_bottom - size]
    ]
    
    # Dreieck zeichnen
    triangle = Polygon(triangle_points, closed=True, facecolor='gray', edgecolor='black', zorder=10)
    ax.add_patch(triangle)
    
    
    ground_y = y_bottom - size # Wo der Boden beginnt
    
    if support_type == "Festlager":
        ax.plot([x_pos - size, x_pos + size], [ground_y, ground_y], color='black', linewidth=2)
        
        for i in range(-2, 3):
            offset = i * (size / 3)
            ax.plot([x_pos + offset, x_pos + offset - size/4], 
                    [ground_y, ground_y - size/3], color='black', linewidth=1)
            
    elif support_type == "Loslager":
        gap = size / 4
        floor_y = ground_y - gap
        
    
        ax.plot([x_pos - size, x_pos + size], [floor_y, floor_y], color='black', linewidth=2)

