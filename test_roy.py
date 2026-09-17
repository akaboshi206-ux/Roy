from roy import Roy


def tester_mise_a_jour_etat():
    roy = Roy()

    assert roy.mettre_a_jour_etat(
        "memoire",
        {"active": True}
    ) is True

    assert roy.etat["memoire"]["active"] is True

    assert roy.mettre_a_jour_etat(
        "banane",
        {"active": True}
    ) is False

    assert roy.mettre_a_jour_etat(
        "memoire",
        {"active": "oui"}
    ) is False

    assert roy.etat["memoire"]["active"] is True

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
    roy = Roy()

    assert roy.mettre_a_jour_etat(
        "systeme",
        {"actif": False}
    ) is True

    assert roy.etat["systeme"]["actif"] is False

    assert roy.traiter_message(
        "statut",
        "statut"
    ) is True

    assert roy.mettre_a_jour_etat(
        "systeme",
        {"actif": True}
    ) is True

    assert roy.etat["systeme"]["actif"] is True


tester_mise_a_jour_etat()
tester_statut()

print("Tous les tests ont réussi.")