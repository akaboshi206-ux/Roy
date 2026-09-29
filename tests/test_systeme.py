from tests.aides import creer_roy_test


def tester_reactivation_systeme():
    roy = creer_roy_test(
        historique_actif=False
    )

    resultat_desactivation = (
        roy.traiter_message(
            "désactive le système",
            "désactive le système"
        )
    )

    assert resultat_desactivation is True
    assert (
        roy.etat["systeme"]["actif"]
        is False
    )

    resultat_reactivation = (
        roy.traiter_message(
            "active le système",
            "active le système"
        )
    )

    assert resultat_reactivation is True
    assert (
        roy.etat["systeme"]["actif"]
        is True
    )


def tester_mise_a_jour_etat():
    roy = creer_roy_test(
        historique_actif=False
    )

    assert roy.mettre_a_jour_etat(
        "memoire",
        {"active": True}
    ) is True

    assert (
        roy.etat["memoire"]["active"]
        is True
    )

    assert roy.mettre_a_jour_etat(
        "banane",
        {"active": True}
    ) is False

    assert roy.mettre_a_jour_etat(
        "memoire",
        {"active": "oui"}
    ) is False

    assert (
        roy.etat["memoire"]["active"]
        is True
    )

    assert roy.mettre_a_jour_etat(
        "memoire",
        {"banane": True}
    ) is False

    assert roy.mettre_a_jour_etat(
        123,
        {"active": True}
    ) is False

    assert roy.mettre_a_jour_etat(
        "memoire",
        True
    ) is False

def tester_statut():
    roy = creer_roy_test(
        historique_actif=False
    )

    assert roy.mettre_a_jour_etat(
        "systeme",
        {"actif": False}
    ) is True

    assert (
        roy.etat["systeme"]["actif"]
        is False
    )

    assert roy.traiter_message(
        "statut",
        "statut"
    ) is True

    assert roy.mettre_a_jour_etat(
        "systeme",
        {"actif": True}
    ) is True

    assert (
        roy.etat["systeme"]["actif"]
        is True
    )

def tester_statut_un_seul_message():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.afficher_statut()

    assert len(roy.historique) == 1

    lignes = (
        roy.historique[0]["content"]
        .splitlines()
    )

    assert len(lignes) == 5
    assert lignes[0] == "Statut du système"
    assert "Système actif." in lignes
    assert "Mémoire activée." in lignes

def tester_commandes_centralisees():
    roy = creer_roy_test(
        historique_actif=False
    )

    resultat_historique = (
        roy.traiter_message(
            "historique",
            "historique"
        )
    )
    assert resultat_historique is True

    resultat_salutation = (
        roy.traiter_message(
            "bonjour",
            "bonjour"
        )
    )
    assert resultat_salutation is True

    resultat_statut = (
        roy.traiter_message(
            "statut",
            "statut"
        )
    )
    assert resultat_statut is True

def tester_commande_generale():
    roy = creer_roy_test(
        historique_actif=False
    )

    resultat = roy.traiter_message(
        "désactive ta mémoire",
        "désactive ta mémoire"
    )

    assert resultat is True
    assert (
        roy.etat["memoire"]["active"]
        is False
    )