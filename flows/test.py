import onecode
import geopandas as gpd
import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def run():
    # --- 1. INTERFACE (CONFORME DOC) ---
    f_geo = onecode.file_input("input_geochimie", value="", label="GeoJSON des points", optional=True)
    f_mnt = onecode.file_input("input_mnt", value="", label="MNT (TIFF)", optional=True)
    
    w_au = onecode.slider("poids_au", 0.4, min=0.0, max=1.0, label="Poids Or (Au)")
    w_as = onecode.slider("poids_as", 0.2, min=0.0, max=1.0, label="Poids Arsenic (As)")
    w_w  = onecode.slider("poids_w", 0.2, min=0.0, max=1.0, label="Poids Tungstène (W)")
    w_bi = onecode.slider("poids_bi", 0.2, min=0.0, max=1.0, label="Poids Bismuth (Bi)")

    # --- 2. DIAGNOSTIC ET CALCULS ---
    onecode.Logger.info(f"Vérification des fichiers : GeoJSON={f_geo}, MNT={f_mnt}")

    if f_geo and f_mnt and len(str(f_geo)) > 4:
        try:
            onecode.Logger.info("Chargement du GeoJSON...")
            data = gpd.read_file(f_geo)
            
            # Calcul Z-Score (Logique Notebook)
            for el in ['Au', 'As', 'W', 'Bi']:
                if el in data.columns:
                    std = data[el].std()
                    data[f'{el}_z'] = (data[el] - data[el].mean()) / std if std > 0 else 0
            
            data['score'] = (data.get('Au_z', 0) * w_au + data.get('As_z', 0) * w_as + 
                             data.get('W_z', 0) * w_w + data.get('Bi_z', 0) * w_bi)

            onecode.Logger.info("Préparation de la carte...")
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Affichage MNT
            with rasterio.open(f_mnt) as src:
                extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
                ax.imshow(src.read(1), cmap='terrain', extent=extent, alpha=0.5)
            
            # Affichage Points
            sc = ax.scatter(data.geometry.x, data.geometry.y, c=data['score'], 
                            cmap='hot_r', s=25, alpha=0.8)
            plt.colorbar(sc, ax=ax, label='Score de potentiel')
            ax.set_title(f"Potentiel : Au({w_au}) As({w_as}) W({w_w}) Bi({w_bi})")

            # --- 3. SAUVEGARDE CRITIQUE ---
            # On force le chemin vers le dossier de sortie officiel du projet
            out_dir = onecode.Project().output_dir
            if not os.path.exists(out_dir):
                os.makedirs(out_dir, exist_ok=True)
            
            filename = "carte_potentiel.png"
            filepath = os.path.join(out_dir, filename)
            
            plt.savefig(filepath, dpi=120)
            plt.close(fig)
            
            # On vérifie si le fichier existe bien sur le disque après sauvegarde
            if os.path.exists(filepath):
                onecode.Logger.info(f"✅ CARTE GÉNÉRÉE AVEC SUCCÈS : {filepath}")
            else:
                onecode.Logger.error("❌ ERREUR : Le fichier n'a pas été écrit sur le disque.")

        except Exception as e:
            onecode.Logger.error(f"❌ ERREUR DURANT L'ANALYSE : {str(e)}")
    else:
        onecode.Logger.info("⚠️ En attente des fichiers GeoJSON et MNT...")
