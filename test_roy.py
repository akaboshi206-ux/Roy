import json

from pathlib import Path
from tempfile import TemporaryDirectory
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

    assert len(roy.historique) == 1

    premier_message = roy.historique[0]

    assert premier_message["role"] == "user"
    assert premier_message["content"] == "bonjour"
    assert "timestamp" in premier_message
    assert isinstance(premier_message["timestamp"], str)

    for numero in range(25):
        roy.ajouter_historique("user", f"message {numero}")

    assert len(roy.historique) == 26
    assert roy.historique[0]["content"] == "bonjour"
    assert roy.historique[-1]["content"] == "message 24"

def tester_recherche_historique():
    roy = Roy(historique_actif=False)
    roy.etat["systeme"]["actif"] = True

    roy.ajouter_historique("user", "Bonjour Cyan")
    roy.ajouter_historique(
        "user",
        "recherche historique cyan"
    )

    resultat = roy.traiter_message(
        "recherche historique cyan",
        "recherche historique Cyan"
    )

    assert resultat is True
    assert len(roy.historique) == 2
    assert roy.historique[0]["content"] == "Bonjour Cyan"

def tester_statistiques_historique():
    roy = Roy(historique_actif=False)
    roy.etat["systeme"]["actif"] = True

    roy.ajouter_historique("user", "bonjour")
    roy.ajouter_historique(
        "assistant",
        "Bonjour Cyan !"
    )

    resultat = roy.traiter_message(
        "statistiques historique",
        "statistiques historique"
    )

    assert resultat is True
    assert len(roy.historique) == 2
    assert roy.historique[0]["role"] == "user"
    assert roy.historique[1]["role"] == "assistant"

def tester_chargement_historique_invalide():
    with TemporaryDirectory() as dossier_temporaire:
        chemin = Path(dossier_temporaire) / "historique_test.json"

        donnees = [
            {
                "role": "user",
                "content": "Bonjour"
            },
            {
                "role": "user"
            },
            42
        ]

        with open(chemin, "w", encoding="utf-8") as fichier:
            json.dump(donnees, fichier, ensure_ascii=False, indent=4)

        roy = Roy(fichier_historique=str(chemin))

        assert len(roy.historique) == 1
        assert roy.historique[0]["role"] == "user"
        assert roy.historique[0]["content"] == "Bonjour"

def tester_commande_historique_avec_limite():
    roy = Roy(historique_actif=False)

    assert roy.traiter_historique("statut") is False
    assert roy.traiter_historique("historique") is True
    assert roy.traiter_historique("historique 3") is True
    assert roy.traiter_historique("historique banane") is True
    assert roy.historique[-1]["content"] == ("Utilise un nombre, par exemple : historique 5")
    assert roy.traiter_historique("historique 0") is True
    assert roy.historique[-1]["content"] == ("Le nombre de messages doit être supérieur à zéro.")
    assert roy.traiter_historique("historique -5") is True

def tester_export_historique():
    with TemporaryDirectory() as dossier_temporaire:
        chemin = Path(dossier_temporaire) / "conversation_test.txt"

        roy = Roy(historique_actif=False)
        roy.historique = [
            {
                "role": "user",
                "content": "Bonjour",
                "timestamp": "2026-09-20T10:00:00"
            },
            {
                "role": "assistant",
                "content": "Salut Cyan",
                "timestamp": None
            }
        ]

        resultat = roy.exporter_historique(str(chemin))

        assert resultat is True
        assert chemin.exists()

        contenu = chemin.read_text(encoding="utf-8")

        assert (
            "[2026-09-20 10:00:00] Toi : Bonjour"
            in contenu
        )
        assert (
            "[date inconnue] Roy : Salut Cyan"
            in contenu
        )
        chemin_vide = (
            Path(dossier_temporaire)
            / "conversation_vide.txt"
        )

        roy_vide = Roy(historique_actif=False)

        assert (
            roy_vide.exporter_historique(
                str(chemin_vide)
            )
            is False
        )

        assert not chemin_vide.exists()

def tester_executer_commande():
    roy = Roy(historique_actif=False)
    appels = []

    def action_test():
        appels.append("ok")

    commandes = [
        (
            {"test"},
            action_test
        )
    ]

    resultat_connu = roy.executer_commande(
        "test",
        commandes
    )

    assert resultat_connu is True
    assert appels == ["ok"]

    resultat_inconnu = roy.executer_commande(
        "inconnue",
        commandes
    )

    assert resultat_inconnu is False
    assert appels == ["ok"]

def tester_commandes_centralisees():
    roy = Roy(historique_actif=False)

    resultat_historique = roy.traiter_message(
        "historique",
        "historique"
    )
    assert resultat_historique is True

    resultat_salutation = roy.traiter_message(
        "bonjour",
        "bonjour"
    )
    assert resultat_salutation is True

    resultat_statut = roy.traiter_message(
        "statut",
        "statut"
    )
    assert resultat_statut is True

def tester_reactivation_systeme():
    roy = Roy(historique_actif=False)

    resultat_desactivation = roy.traiter_message(
        "désactive le système",
        "désactive le système"
    )

    assert resultat_desactivation is True
    assert roy.etat["systeme"]["actif"] is False

    resultat_reactivation = roy.traiter_message(
        "active le système",
        "active le système"
    )

    assert resultat_reactivation is True
    assert roy.etat["systeme"]["actif"] is True

def tester_repondre():
    roy = Roy(historique_actif=False)

    roy.repondre("Réponse de test")

    assert len(roy.historique) == 1

    reponse = roy.historique[0]

    assert reponse["role"] == "assistant"
    assert reponse["content"] == "Réponse de test"
    assert "timestamp" in reponse
    assert isinstance(reponse["timestamp"], str)

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
tester_recherche_historique()
tester_statistiques_historique()
tester_chargement_historique_invalide()
tester_commande_historique_avec_limite()
tester_export_historique()
tester_executer_commande()
tester_commandes_centralisees()
tester_reactivation_systeme()   
tester_repondre()
tester_mise_a_jour_etat()
tester_statut()

print("Tous les tests ont réussi.")
