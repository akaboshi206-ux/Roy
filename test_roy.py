from roy import Roy
from config import commandes_quitter
from main import nettoyer_message

def tester_commandes_quitter():
    assert "quitter" in commandes_quitter
    assert "au revoir" in commandes_quitter
    assert "continuer" not in commandes_quitter

def tester_nettoyer_message():
    cas_de_test = {
        "  BONJOUR  ": "bonjour",
        "Roy statut": "statut",
        "  Roy    AU REVOIR  ": "au revoir",
        "     ": "",
        "active     ta mémoire": "active ta mémoire",
        "Roy, statut": "statut",
        "Roy : aide": "aide"
    }

    for message, resultat_attendu in cas_de_test.items():
        assert nettoyer_message(message) == resultat_attendu

def tester_historique():
    roy = Roy(historique_actif=False)
    
    assert roy.historique == []

    roy.ajouter_historique("user", "bonjour")

    assert roy.historique == [
        {
            "role": "user",
            "content": "bonjour"
        }
    ]
    for numero in range(25):
        roy.ajouter_historique("user", f"message {numero}")

    assert len(roy.historique) == 26
    assert roy.historique[0]["content"] == "bonjour"
    assert roy.historique[-1]["content"] == "message 24"

def tester_repondre():
    roy = Roy(historique_actif=False)

    roy.repondre("Réponse de test")

    assert roy.historique == [
        {
            "role": "assistant",
            "content": "Réponse de test"
        }
    ]

def tester_mise_a_jour_etat():
    roy = Roy(historique_actif=False)

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
    roy = Roy(historique_actif=False)

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


tester_commandes_quitter()
tester_nettoyer_message()
tester_historique()
tester_repondre()
tester_mise_a_jour_etat()
tester_statut()

print("Tous les tests ont réussi.")
