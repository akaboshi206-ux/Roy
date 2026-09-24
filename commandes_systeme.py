from config import (
    commandes_activer_systeme,
    commandes_desactiver_systeme,
    commandes_basculer_systeme,
    commandes_statut
)

def traiter_commande_systeme(
    roy,
    message: str
) -> bool:
    commandes_actions = (
        (
            commandes_activer_systeme,
            roy.activer_systeme
        ),
        (
            commandes_desactiver_systeme,
            roy.desactiver_systeme
        ),
        (
            commandes_basculer_systeme,
            roy.basculer_systeme
        ),
        (
            commandes_statut,
            roy.afficher_statut
        )
    )

    for formulations, action in commandes_actions:
        if message in formulations:
            action()
            return True

    return False