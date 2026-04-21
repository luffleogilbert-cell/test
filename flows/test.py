import onecode

def run():
    # TEST : On utilise des clés simples sans imports complexes
    f_geo = onecode.file_input(
        key="input_geochimie",
        label="1. Chargez vos points (GeoJSON)"
    )

    f_mnt = onecode.file_input(
        key="input_mnt",
        label="2. Chargez votre MNT (TIFF)"
    )

    # Tes sliders qui marchent
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

    onecode.Logger.info("Vérification de l'affichage des champs d'upload...")
