import onecode

def run():
    # --- COMPARTIMENTS POUR DRAG & DROP / UPLOAD ---
    # On définit une valeur vide par défaut comme l'exige la doc
    
    f_geo = onecode.file_input(
        key="input_geochimie",
        value="", 
        label="1. Déposez votre GeoJSON ici",
        optional=True
    )

    f_mnt = onecode.file_input(
        key="input_mnt",
        value="",
        label="2. Déposez votre MNT (TIFF) ici",
        optional=True
    )

    # --- TES SLIDERS (On ne change pas ce qui marche) ---
    s1 = onecode.slider(
        key="curseur_test",
        value=2.0,
        min=1.0,
        max=5.0,
        label="3. Niveau de détection (MAD)"
    )

    s2 = onecode.slider(
        key="poids_or",
        value=0.5,
        min=0.0,
        max=1.0,
        label="4. Importance de l'Or (Au)"
    )

    onecode.Logger.info("Interface prête : Sliders et Zones d'upload activés.")
