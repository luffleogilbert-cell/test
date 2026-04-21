import onecode
import geopandas as gpd
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def run():
    f_geo = onecode.file_input("input_geochimie", value="", label="GeoJSON", optional=True)
    f_mnt = onecode.file_input("input_mnt", value="", label="MNT (TIFF)", optional=True)
    
    elements = ['Au_ppb', 'As_ppm', 'W_ppm', 'Bi_ppm']
    w_au = onecode.slider("poids_au", 0.4, min=0.0, max=1.0)
    w_as = onecode.slider("poids_as", 0.2, min=0.0, max=1.0)
    w_w  = onecode.slider("poids_w", 0.2, min=0.0, max=1.0)
    w_bi = onecode.slider("poids_bi", 0.2, min=0.0, max=1.0)

    if f_geo and f_mnt and len(str(f_geo)) > 5:
        try:
            data = gpd.read_file(f_geo)
            poids = [w_au, w_as, w_w, w_bi]
            sum_poids = sum(poids)

            df_el = data[elements].copy()
            scaler = StandardScaler()
            z_scores = scaler.fit_transform(df_el)
            
            for i, el in enumerate(elements):
                data[f'{el}_z'] = z_scores[:, i]
            
            if sum_poids > 0:
                data['score'] = (data['Au_ppb_z'] * w_au + 
                                 data['As_ppm_z'] * w_as + 
                                 data['W_ppm_z'] * w_w + 
                                 data['Bi_ppm_z'] * w_bi) / sum_poids
            else:
                data['score'] = 0

            # Generation de la carte de potentiel
            fig1, ax1 = plt.subplots(figsize=(10, 8))
            with rasterio.open(f_mnt) as src:
                mnt_data = src.read(1).astype(float)
                mnt_data[mnt_data == src.nodata] = np.nan
                extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
                ax1.imshow(mnt_data, cmap='terrain', extent=extent, origin='upper', alpha=0.6)
            
            sc = ax1.scatter(data.geometry.x, data.geometry.y, c=data['score'], 
                            cmap='hot_r', s=25, vmin=data['score'].quantile(0.1), 
                            vmax=data['score'].quantile(0.95))
            plt.colorbar(sc, ax=ax1, label='Score')
            ax1.set_xlim(extent[0], extent[1])
            ax1.set_ylim(extent[2], extent[3])
            
            path_map = onecode.file_output("carte_potentiel", "carte_potentiel.png")
            fig1.savefig(path_map, dpi=150, bbox_inches='tight')
            plt.close(fig1)

            # Analyse en Composantes Principales
            pca = PCA(n_components=2)
            pca.fit(z_scores)
            fig2, ax2 = plt.subplots(figsize=(8, 8))
            ax2.add_artist(plt.Circle((0,0), 1, color='blue', fill=False))
            for i, el in enumerate(elements):
                ax2.arrow(0, 0, pca.components_[0, i], pca.components_[1, i], 
                         head_width=0.05, color='red')
                ax2.text(pca.components_[0, i]*1.1, pca.components_[1, i]*1.1, el)
            ax2.set_xlim(-1.2, 1.2)
            ax2.set_ylim(-1.2, 1.2)
            ax2.grid(True)
            
            path_pca = onecode.file_output("graph_acp", "analyse_acp.png")
            fig2.savefig(path_pca, dpi=120)
            plt.close(fig2)

            # Histogrammes de distribution
            fig3, axes = plt.subplots(2, 2, figsize=(12, 10))
            for i, el in enumerate(elements):
                curr_ax = axes[i//2, i%2]
                sns.histplot(data[el], kde=True, ax=curr_ax)
                curr_ax.set_title(el)
            
            path_hist = onecode.file_output("histogrammes", "distributions.png")
            fig3.savefig(path_hist, dpi=120)
            plt.close(fig3)

        except Exception as e:
            onecode.Logger.error(f"Erreur execution: {str(e)}")
