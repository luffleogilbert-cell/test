import onecode

def run():
    # Ton premier widget qui marche
    sensibilite = onecode.slider(
        key="curseur_test",
        value=2.0,
        min=1.0,
        max=5.0,
        step=0.1,
        label="Niveau de détection (MAD)"
    )

    # --- LE NOUVEAU WIDGET ---
    poids_au = onecode.slider(
        key="poids_or",
        value=0.5,
        min=0.0,
        max=1.0,
        step=0.05,
        label="Importance de l'Or (Au)"
    )

    onecode.Logger.info(f"Sliders détectés : MAD={sensibilite}, Or={poids_au}")
