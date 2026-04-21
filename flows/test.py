import onecode
import geopandas as gpd # <-- Nouvelle biblio !

def run():
    # --- LES WIDGETS D'UPLOAD (Nouveau) ---
    fichier_geo = onecode.file_input(
        key="input_geochimie",
        label="1. Chargez vos points (GeoJSON)",
        types=[("GeoJSON", ".geojson .json")]
    )

    fichier_mnt = onecode.file_input(
        key="input_mnt",
        label="2. Chargez votre MNT (TIFF)",
        types=[("GeoTIFF", ".tif .tiff")]
    )

    # --- TES SLIDERS QUI MARCHENT ---
    sensibilite = onecode.slider(
        key="curseur_test",
        value=2.0,
        min=1.0,
        max=5.0,
        label="3. Niveau de détection (MAD)"
    )

    poids_au = onecode.slider(
        key="poids_or",
        value=0.5,
        min=0.0,
        max=1.0,
        label="4. Importance de l'Or (Au)"
    )

    # --- PETIT TEST DE LECTURE ---
    if fichier_geo is not None:
        data = gpd.read_file(fichier_geo)
        onecode.Logger.info(f"Succès : {len(data)} points chargés depuis le GeoJSON !")
    else:
        onecode.Logger.info("En attente du fichier GeoJSON...")
