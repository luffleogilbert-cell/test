import onecode
import geopandas as gpd
import rasterio
import numpy as np
import matplotlib.pyplot as plt

def run():
    # ENTRÉES 
    f_geo = onecode.file_input("input_geochimie", value="", label="GeoJSON", optional=True)
    f_mnt = onecode.file_input("input_mnt", value="", label="MNT (TIFF)", optional=True)
    
    # Sliders pour les poids
    w_au = onecode.slider("poids_au", 0.4, min=0.0, max=1.0, label="Poids Or (Au)")
    w_as = onecode.slider("poids_as", 0.2, min=0.0, max=1.0, label="Poids Arsenic (As)")
    w_w  = onecode.slider("poids_w", 0.2, min=0.0, max=1.0, label="Poids Tungstène (W)")
    w_bi = onecode.slider("poids_bi", 0.2, min=0.0, max=1.0, label="Poids Bismuth (Bi)")

    if f_geo and f_mnt and len(str(f_geo)) > 5:
        try:
            # 1. Chargement
            data = gpd.read_file(f_geo)
            
            # 2. Calcul du Score avec Normalisation automatique
            # On calcule la somme totale des curseurs
            total_poids = w_au + w_as + w_w + w_bi

            # Normalisation des Z-scores
            for el in ['Au_ppb', 'As_ppm', 'W_ppm', 'Bi_ppm']:
                if el in data.columns:
                    data[f'{el}_z'] = (data[el] - data[el].mean()) / data[el].std()
            
            # Calcul du score pondéré
            if total_poids > 0:
                # Si l'utilisateur a bougé des curseurs, on divise par la somme
                # pour que l'importance relative soit respectée sur une base de 100%
                data['score'] = (data.get('Au_ppb_z', 0) * w_au + 
                                 data.get('As_ppm_z', 0) * w_as + 
                                 data.get('W_ppm_z', 0) * w_w + 
                                 data.get('Bi_ppm_z', 0) * w_bi) / total_poids
            else:
                data['score'] = 0

            # 3. Graphique
            fig, ax = plt.subplots(figsize=(10, 8))
            
            with rasterio.open(f_mnt) as src:
                mnt_data = src.read(1).astype(float)
                mnt_data[mnt_data == src.nodata] = np.nan
                extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
                ax.imshow(mnt_data, cmap='terrain', extent=extent, origin='upper', alpha=0.6)

            # Scatter des points
            sc = ax.scatter(data.geometry.x, data.geometry.y, 
                            c=data['score'], 
                            cmap='hot_r', 
                            s=25, 
                            alpha=0.8,
                            vmin=data['score'].quantile(0.1), 
                            vmax=data['score'].quantile(0.95),
                            zorder=4)
            
            plt.colorbar(sc, ax=ax, label='Score normalisé', shrink=0.8)
            
            ax.set_xlim(extent[0], extent[1])
            ax.set_ylim(extent[2], extent[3])
            
            # Mise à jour dynamique du titre avec les poids relatifs réels (%)
            if total_poids > 0:
                ax.set_title(f"Potentiel : Au({w_au/total_poids:.0%}) As({w_as/total_poids:.0%}) W({w_w/total_poids:.0%}) Bi({w_bi/total_poids:.0%})")
            
            # 4. Sortie
            output_path = onecode.file_output("carte_resultat", "carte_potentiel.png")
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
        except Exception as e:
            onecode.Logger.error(f"Erreur : {str(e)}")
