import onecode
import geopandas as gpd
import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def run():
    # --- 1. INTERFACE ---
    f_geo = onecode.file_input("input_geochimie", value="", label="GeoJSON des points", optional=True)
    f_mnt = onecode.file_input("input_mnt", value="", label="MNT (TIFF)", optional=True)
    
    w_au = onecode.slider("poids_au", 0.4, min=0.0, max=1.0, label="Poids Or (Au)")
    w_as = onecode.slider("poids_as", 0.2, min=0.0, max=1.0, label="Poids Arsenic (As)")
    w_w  = onecode.slider("poids_w", 0.2, min=0.0, max=1.0, label="Poids Tungstène (W)")
    w_bi = onecode.slider("poids_bi", 0.2, min=0.0, max=1.0, label="Poids Bismuth (Bi)")

    if f_geo and f_mnt and len(str(f_geo)) > 4:
        try:
            onecode.Logger.info("Lecture et calcul des scores...")
            data = gpd.read_file(f_geo)
            
            for el in ['Au', 'As', 'W', 'Bi']:
                if el in data.columns:
                    std = data[el].std()
                    data[f'{el}_z'] = (data[el] - data[el].mean()) / std if std > 0 else 0
            
            data['score'] = (data.get('Au_z', 0) * w_au + data.get('As_z', 0) * w_as + 
                             data.get('W_z', 0) * w_w + data.get('Bi_z', 0) * w_bi)

            # --- 2. GÉNÉRATION DE LA CARTE ---
            fig, ax = plt.subplots(figsize=(10, 8))
            with rasterio.open(f_mnt) as src:
                extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
                ax.imshow(src.read(1), cmap='terrain', extent=extent, alpha=0.5)
            
            sc = ax.scatter(data.geometry.x, data.geometry.y, c=data['score'], 
                            cmap='hot_r', s=25, alpha=0.8)
            plt.colorbar(sc, ax=ax, label='Score de potentiel')
            ax.set_title("Analyse Potentiel Ambazac")

            # --- 3. SORTIE OFFICIELLE ONECODE ---
            # On utilise image_output pour que OneCode l'ajoute au ZIP et à l'interface
            onecode.image_output(
                key="ma_carte_finale",
                value=fig,
                path="carte_potentiel.png"
            )
            
            plt.close(fig)
            onecode.Logger.info("✅ Carte déclarée dans les sorties OneCode.")

        except Exception as e:
            onecode.Logger.error(f"❌ ERREUR : {str(e)}")
    else:
        onecode.Logger.info("⚠️ En attente des fichiers...")
