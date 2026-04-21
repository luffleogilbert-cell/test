import onecode
import geopandas as gpd
import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def run():
    # --- 1. INPUTS (Selon la Doc) ---
    f_geo = onecode.file_input("input_geochimie", value="", label="GeoJSON des points", optional=True)
    f_mnt = onecode.file_input("input_mnt", value="", label="MNT (TIFF)", optional=True)
    
    w_au = onecode.slider("poids_au", 0.4, min=0.0, max=1.0, label="Poids Or (Au)")
    w_as = onecode.slider("poids_as", 0.2, min=0.0, max=1.0, label="Poids Arsenic (As)")
    w_w  = onecode.slider("poids_w", 0.2, min=0.0, max=1.0, label="Poids Tungstène (W)")
    w_bi = onecode.slider("poids_bi", 0.2, min=0.0, max=1.0, label="Poids Bismuth (Bi)")

    # Vérification que les fichiers sont bien présents
    if f_geo and f_mnt and len(str(f_geo)) > 5:
        try:
            onecode.Logger.info("Début de l'analyse...")
            
            # Lecture des données
            data = gpd.read_file(f_geo)
            
            # Calcul des scores (Z-score)
            for el in ['Au', 'As', 'W', 'Bi']:
                if el in data.columns:
                    val_mean = data[el].mean()
                    val_std = data[el].std()
                    data[f'{el}_z'] = (data[el] - val_mean) / val_std if val_std > 0 else 0
            
            data['score'] = (data.get('Au_z', 0) * w_au + data.get('As_z', 0) * w_as + 
                             data.get('W_z', 0) * w_w + data.get('Bi_z', 0) * w_bi)

            # --- 2. CRÉATION DU VISUEL ---
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Affichage du MNT
            with rasterio.open(f_mnt) as src:
                extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
                ax.imshow(src.read(1), cmap='terrain', extent=extent, alpha=0.5)
            
            # Affichage des points géochimiques
            sc = ax.scatter(data.geometry.x, data.geometry.y, c=data['score'], 
                            cmap='hot_r', s=25, alpha=0.8)
            plt.colorbar(sc, ax=ax, label='Score de potentiel')
            ax.set_title("Carte de Potentiel Minéral - Ambazac")

            # --- 3. OUTPUTS (Selon la Doc) ---
            # file_output définit le chemin où OneCode attend le fichier
            output_path = onecode.file_output("carte_resultat", "carte_potentiel.png")
            
            # Sauvegarde de la figure matplotlib au chemin défini par OneCode
            plt.savefig(output_path, dpi=150)
            plt.close(fig)
            
            onecode.Logger.info(f"✅ Analyse terminée. Fichier enregistré sous : {output_path}")

        except Exception as e:
            onecode.Logger.error(f"❌ Erreur lors de l'exécution : {str(e)}")
    else:
        onecode.Logger.info("⚠️ Veuillez uploader le GeoJSON et le MNT dans l'interface.")
