from config import (
    salutations,
    commandes_aide,
    commandes_memoire,
    commandes_activer_memoire,
    commandes_desactiver_memoire,
    commandes_basculer_memoire
)

def traiter_commande_generale(
    roy,
    message: str
) -> bool:
    commandes_actions = (
        (
            commandes_aide,
            roy.afficher_aide
        ),
        (
            commandes_activer_memoire,
            roy.activer_memoire
        ),
        (
            commandes_desactiver_memoire,
            roy.desactiver_memoire
        ),
        (
            commandes_basculer_memoire,
            roy.basculer_memoire
        ),
        (
            salutations,
            roy.saluer
        ),
        (
            commandes_memoire,
            roy.afficher_memoire
        )
    )

    for formulations, action in commandes_actions:
        if message in formulations:
            action()
            return True

    return False