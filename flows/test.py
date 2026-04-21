import onecode


def run():
    # --- LE SEUL ET UNIQUE WIDGET (Le Test de la Dernière Chance) ---
    # Cette ligne DOIT créer un slider dans la colonne 'Input' de ton appli

    sensibilite = onecode.slider(
        key="curseur_test",  # Clé unique
        value=2.0,  # Valeur par défaut
        min=1.0,  # Minimum
        max=5.0,  # Maximum
        step=0.1,  # Incrément
        label="Niveau de détection (MAD)"  # Le titre affiché
    )

    # --- LOGIQUE MINIMALE ---
    onecode.Logger.info(f"Widget détecté avec succès ! Valeur du slider : {sensibilite}")
    onecode.Logger.info("Si vous lisez ceci et ne voyez pas le slider, le problème vient du Cloud.")