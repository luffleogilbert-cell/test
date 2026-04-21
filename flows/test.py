import onecode
import geopandas as gpd
import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def run():
    # --- 1. INPUTS ---
    f_geo = onecode.file_input("input_geochimie", "", label="GeoJSON des points", optional=True)
    f_mnt = onecode.file_input("input_mnt", "", label="MNT (TIFF)", optional=True)
    
    w_au = onecode.slider("poids_au", 0.4, min=0.0, max=1.0, label="Poids Or (Au)")
    w_as = onecode.slider("poids_as", 0.2, min=0.0, max=1.0, label="Poids Arsenic (As)")
    w_w  = onecode.slider("poids_w", 0.2, min=0.0, max=1.0, label="Poids Tungstène (W)")
    w_bi = onecode.slider("poids_bi", 0.2, min=0.0, max=1.0, label="Poids Bismuth (Bi)")

    if f_geo and f_mnt and f_geo != "" and f_mnt != "":
        try:
            # --- 2. CALCULS ---
            data = gpd.read_file(f_geo)
            
            # Normalisation simplifiée pour éviter des bugs sklearn si données vides
            for el in ['Au', 'As', 'W', 'Bi']:
                if el in data.columns:
                    col_std = data[el].std()
                    if col_std != 0:
                        data[f'{el}_z'] = (data[el] - data[el].mean()) / col_std
                    else:
                        data[f'{el}_z'] = 0
            
            data['score'] = (data['Au_z'] * w_au + data['As_z'] * w_as + 
                             data['W_z'] * w_w + data['Bi_z'] * w_bi)

            # --- 3. PLOT ---
            fig, ax = plt.subplots(figsize=(10, 8))
            with rasterio.open(f_mnt) as src:
                mnt_data = src.read(1)
                extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
                ax.imshow(mnt_data, cmap='terrain', extent=extent, alpha=0.5)
            
            sc = ax.scatter(data.geometry.x, data.geometry.y, c=data['score'], 
                            cmap='hot_r', s=25, alpha=0.8)
            plt.colorbar(sc, ax=ax, label='Score de potentiel')
            
            # --- 4. LA SORTIE (MODIFIÉ) ---
            # Au lieu de os.path.join, on utilise onecode.image_output
            # Cela force l'enregistrement dans le manifest OneCode
            onecode.image_output("carte_finale", fig, "carte_potentiel.png")
            
            plt.close(fig)
            onecode.Logger.info("✅ Carte générée et enregistrée dans les sorties.")

        except Exception as e:
            onecode.Logger.error(f"Erreur d'analyse : {e}")
    else:
        onecode.Logger.info("En attente des fichiers GeoJSON et MNT...")
