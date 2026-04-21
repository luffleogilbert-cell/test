import onecode
import geopandas as gpd
import rasterio
import numpy as np
import matplotlib.pyplot as plt

def run():
    # --- ENTRÉES ---
    f_geo = onecode.file_input("input_geochimie", value="", label="GeoJSON", optional=True)
    f_mnt = onecode.file_input("input_mnt", value="", label="MNT (TIFF)", optional=True)
    
    # Poids des éléments (sliders)
    w_au = onecode.slider("poids_au", 0.4)
    w_as = onecode.slider("poids_as", 0.2)
    w_w  = onecode.slider("poids_w", 0.2)
    w_bi = onecode.slider("poids_bi", 0.2)

    if f_geo and f_mnt and len(str(f_geo)) > 5:
        try:
            # 1. Chargement des données
            data = gpd.read_file(f_geo)
            
            # 2. Calcul du Score (normalisation Z-score comme dans le notebook)
            for el in ['Au_ppb', 'As_ppm', 'W_ppm', 'Bi_ppm']:
                if el in data.columns:
                    data[f'{el}_z'] = (data[el] - data[el].mean()) / data[el].std()
            
            data['score'] = (data.get('Au_ppb_z', 0) * w_au + 
                             data.get('As_ppm_z', 0) * w_as + 
                             data.get('W_ppm_z', 0) * w_w + 
                             data.get('Bi_ppm_z', 0) * w_bi)

            # 3. Préparation du graphique
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Lecture du MNT et extraction des coordonnées exactes (Crucial !)
            with rasterio.open(f_mnt) as src:
                mnt_data = src.read(1).astype(float)
                # Gestion des valeurs nulles
                mnt_data[mnt_data == src.nodata] = np.nan
                # Définition de l'étendue : [gauche, droite, bas, haut]
                extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
                
                # Affichage du fond de carte (MNT)
                ax.imshow(mnt_data, cmap='terrain', extent=extent, origin='upper', alpha=0.6)

            # 4. Affichage des points (Scatter)
            # Utilisation de vmin/vmax basés sur les quantiles pour le contraste
            sc = ax.scatter(data.geometry.x, data.geometry.y, 
                            c=data['score'], 
                            cmap='hot_r', 
                            s=25, 
                            alpha=0.8,
                            vmin=data['score'].quantile(0.1), 
                            vmax=data['score'].quantile(0.95),
                            zorder=4)
            
            plt.colorbar(sc, ax=ax, label='Score de potentiel', shrink=0.8)
            
            # Calage final des limites de vue sur le MNT
            ax.set_xlim(extent[0], extent[1])
            ax.set_ylim(extent[2], extent[3])
            
            ax.set_title(f"Carte de Potentiel : Au({w_au}) + As({w_as}) + W({w_w}) + Bi({w_bi})")
            ax.set_xlabel("X (Lambert 93)")
            ax.set_ylabel("Y (Lambert 93)")

            # --- SORTIE ---
            output_path = onecode.file_output("carte_resultat", "carte_potentiel.png")
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
        except Exception as e:
            onecode.Logger.error(f"Erreur lors du traitement : {str(e)}")
