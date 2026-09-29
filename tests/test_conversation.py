from commandes_conversation import (
    traiter_commande_conversation
)

from tests.aides import creer_roy_test


def tester_commande_conversation():
    roy = creer_roy_test(
        historique_actif=False
    )

    resultat_connu = (
        traiter_commande_conversation(
            roy,
            "comment vas-tu"
        )
    )

    resultat_inconnu = (
        traiter_commande_conversation(
            roy,
            "commande inconnue"
        )
    )

    assert resultat_connu is True
    assert resultat_inconnu is False
    