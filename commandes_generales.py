from config import (
    salutations,
    commandes_aide,
    commandes_memoire,
    commandes_activer_memoire,
    commandes_desactiver_memoire,
    commandes_basculer_memoire,
    commandes_statut_sauvegardes
)

def traiter_commande_etat_memoire(
    roy,
    message: str
) -> bool:
    commandes_actions = (
        (commandes_activer_memoire, roy.activer_memoire),
        (commandes_desactiver_memoire, roy.desactiver_memoire),
        (commandes_basculer_memoire, roy.basculer_memoire)
    )

    for formulations, action in commandes_actions:
        if message in formulations:
            action()
            return True

    return False

def traiter_commande_generale(
    roy,
    message: str
) -> bool:
    commandes_actions = (
        (
            commandes_statut_sauvegardes,
            roy.afficher_statut_sauvegardes
        ),
        (
            commandes_aide,
            roy.afficher_aide
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