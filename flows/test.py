import onecode
import geopandas as gpd
import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from rasterio.plot import show
from sklearn.preprocessing import StandardScaler
import os

def run():
    # --- 1. INTERFACE (PARAMÈTRES DU NOTEBOOK) ---
    f_geo = onecode.file_input("input_geochimie", "", label="GeoJSON des points", optional=True)
    f_mnt = onecode.file_input("input_mnt", "", label="MNT (TIFF)", optional=True)
    
    # On crée des sliders pour tes pondérations du notebook
    w_au = onecode.slider("poids_au", 0.4, min=0.0, max=1.0, label="Poids Or (Au)")
    w_as = onecode.slider("poids_as", 0.2, min=0.0, max=1.0, label="Poids Arsenic (As)")
    w_w  = onecode.slider("poids_w", 0.2, min=0.0, max=1.0, label="Poids Tungstène (W)")
    w_bi = onecode.slider("poids_bi", 0.2, min=0.0, max=1.0, label="Poids Bismuth (Bi)")

    if f_geo and f_mnt:
        try:
            # --- 2. CHARGEMENT ET CALCUL (LOGIQUE NOTEBOOK) ---
            data = gpd.read_file(f_geo)
            
            # Sélection des éléments comme dans ton notebook
            elements = ['Au', 'As', 'W', 'Bi']
            
            # Normalisation (Z-score)
            scaler = StandardScaler()
            data_scaled = scaler.fit_transform(data[elements].fillna(0))
            
            # Calcul du score combiné avec les valeurs des sliders
            # Score = (Au * poids_au) + (As * poids_as) + ...
            weights = np.array([w_au, w_as, w_w, w_bi])
            data['score'] = np.dot(data_scaled, weights)

            # --- 3. GÉNÉRATION DE LA CARTE ---
            fig, ax = plt.subplots(figsize=(10, 8))
            
            with rasterio.open(f_mnt) as src:
                # Affichage du MNT
                mnt_data = src.read(1)
                extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
                ax.imshow(mnt_data, cmap='terrain', extent=extent, alpha=0.5)
            
            # Affichage des points colorés par score (hot_r comme dans ton notebook)
            sc = ax.scatter(data.geometry.x, data.geometry.y, c=data['score'], 
                            cmap='hot_r', s=25, alpha=0.8, edgecolor='none')
            
            plt.colorbar(sc, ax=ax, label='Score de potentiel minéral')
            ax.set_title("Carte de Potentiel Minéral - Ambazac")
            
            # --- 4. SAUVEGARDE ---
            output_map = os.path.join(onecode.Project().output_dir, "carte_potentiel.png")
            plt.savefig(output_map, dpi=150)
            plt.close()
            
            onecode.Logger.info("✅ Analyse terminée. Carte générée selon la méthode du Notebook.")

        except Exception as e:
            onecode.Logger.error(f"Erreur d'analyse : {e}")
    else:
        onecode.Logger.info("En attente des fichiers et paramètres...")
