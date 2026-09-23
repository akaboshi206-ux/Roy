import json

from pathlib import Path
from tempfile import TemporaryDirectory
from roy import Roy
from outils import formater_message_historique
from config import commandes_quitter
from main import nettoyer_message
from itertools import count
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

dossier_tests = TemporaryDirectory()
numeros_tests = count()


def creer_roy_test(**options):
    numero = next(numeros_tests)

    chemin_memoire = (
        Path(dossier_tests.name)
        / f"memoire_{numero}.json"
    )
    chemin_taches = (
        Path(dossier_tests.name)
        / f"taches_{numero}.json"
    )

    options.setdefault(
        "fichier_taches",
        str(chemin_taches)
    )

    return Roy(
        fichier_memoire=str(chemin_memoire),
        **options
    )

def recharger_roy_test(roy: Roy) -> Roy:
    return Roy(
        historique_actif=False,
        fichier_memoire=roy.fichier_memoire,
        fichier_taches=roy.fichier_taches
    )

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
    with TemporaryDirectory() as dossier:
        roy = Roy(
            historique_actif=False,
            fichier_memoire=str(Path(dossier) / "memoire_test.json")
        )
                    
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
    roy = creer_roy_test(historique_actif=False)
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
    roy = creer_roy_test(historique_actif=False)
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

        roy = creer_roy_test(fichier_historique=str(chemin))

        assert len(roy.historique) == 1
        assert roy.historique[0]["role"] == "user"
        assert roy.historique[0]["content"] == "Bonjour"

def tester_commande_historique_avec_limite():
    roy = creer_roy_test(historique_actif=False)

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

        roy = creer_roy_test(historique_actif=False)
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

        roy_vide = creer_roy_test(historique_actif=False)

        assert (
            roy_vide.exporter_historique(
                str(chemin_vide)
            )
            is False
        )

        assert not chemin_vide.exists()

def tester_executer_commande():
    roy = creer_roy_test(historique_actif=False)
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
    roy = creer_roy_test(historique_actif=False)

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
    roy = creer_roy_test(historique_actif=False)

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

def tester_memoire_configurable():
    with TemporaryDirectory() as dossier_temporaire:
        chemin = Path(dossier_temporaire) / "memoire_test.json"

        roy = Roy(
            historique_actif=False,
            fichier_memoire=str(chemin)
        )

        assert roy.memoire == {}

        assert roy.apprendre("couleur", "cyan") is True
        assert chemin.exists()

        roy_recharge = Roy(
            historique_actif=False,
            fichier_memoire=str(chemin)
        )

        assert roy_recharge.memoire["couleur"] == "cyan"

def tester_repondre():
    roy = creer_roy_test(historique_actif=False)

    roy.repondre("Réponse de test")

    assert len(roy.historique) == 1

    reponse = roy.historique[0]

    assert reponse["role"] == "assistant"
    assert reponse["content"] == "Réponse de test"
    assert "timestamp" in reponse
    assert isinstance(reponse["timestamp"], str)

def tester_mise_a_jour_etat():
    roy = creer_roy_test(historique_actif=False)

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
    roy = creer_roy_test(historique_actif=False)

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

def tester_formatage_message_historique():
    ancien_message = {
        "role": "user",
        "content": "salut"
    }
    assert formater_message_historique(ancien_message) == "Toi : salut"

    message_date = {
        "role": "assistant",
        "content": "Bonjour Cyan",
        "timestamp": "2026-09-22T08:46:28"
    }
    assert formater_message_historique(message_date) == (
        "[2026-09-22 08:46:28] Roy : Bonjour Cyan"
    )

def tester_aide_un_seul_message():
    roy = creer_roy_test(historique_actif=False)

    roy.afficher_aide()

    assert len(roy.historique) == 1
    assert "1. bonjour" in roy.historique[0]["content"]
    assert "20. quitter" in roy.historique[0]["content"]
    assert "21. ajoute une tâche : description" in roy.historique[0]["content"]
    assert "22. montre mes tâches" in roy.historique[0]["content"]
    assert "23. termine la tâche 1" in roy.historique[0]["content"]
    assert "24. supprime la tâche 1" in roy.historique[0]["content"]

def tester_recherche_ignore_nouvelle_aide():
    roy = creer_roy_test(historique_actif=False)
    roy.afficher_aide()
    roy.ajouter_historique("user", "Je veux quitter")
    roy.ajouter_historique("user", "recherche historique quitter")

    sortie = StringIO()
    with redirect_stdout(sortie):
        roy.rechercher_historique("quitter")

    texte = sortie.getvalue()
    assert "1 message(s) trouvé(s)" in texte
    assert "Je veux quitter" in texte
    assert "20. quitter" not in texte

def tester_statut_un_seul_message():
    roy = creer_roy_test(historique_actif=False)

    roy.afficher_statut()

    assert len(roy.historique) == 1
    lignes = roy.historique[0]["content"].splitlines()
    assert len(lignes) == 5
    assert lignes[0] == "Statut du système"
    assert "Système actif." in lignes
    assert "Mémoire activée." in lignes

def tester_affichage_memoire_un_seul_message():
    roy = creer_roy_test(historique_actif=False)
    roy.memoire = {"couleur": "cyan", "ville": "Paris"}

    roy.afficher_memoire()

    assert len(roy.historique) == 1
    contenu = roy.historique[0]["content"]
    assert "1. couleur : cyan" in contenu
    assert "2. ville : Paris" in contenu

def tester_echec_sauvegarde_preserve_memoire():
    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "memoire_test.json"
        chemin.write_text('{"couleur": "bleu"}', encoding="utf-8")

        roy = Roy(
            historique_actif=False,
            fichier_memoire=str(chemin)
        )
        roy.memoire["couleur"] = "cyan"

        with patch("roy.os.replace", side_effect=OSError("échec simulé")):
            assert roy.sauvegarder_memoire() is False

        assert json.loads(chemin.read_text(encoding="utf-8")) == {
            "couleur": "bleu"
        }
        assert list(Path(dossier).iterdir()) == [chemin]

def tester_gestion_taches():
    roy = creer_roy_test(historique_actif=False)

    assert roy.traiter_message(
        "ajoute une tâche : travailler sur Roy",
        "ajoute une tâche : travailler sur Roy"
    ) is True

    assert len(roy.taches) == 1
    assert roy.taches[0] == {
        "description": "travailler sur Roy",
        "terminee": False
    }

    roy = recharger_roy_test(roy)

    assert len(roy.taches) == 1

    assert roy.traiter_message(
        "termine la tâche 1",
        "termine la tâche 1"
    ) is True

    assert roy.taches[0]["terminee"] is True

    roy = recharger_roy_test(roy)

    assert roy.taches[0]["terminee"] is True

    assert roy.traiter_message(
        "supprime la tâche 1",
        "supprime la tâche 1"
    ) is True

    assert roy.taches == []

    roy = recharger_roy_test(roy)

    assert roy.taches == []

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
tester_memoire_configurable()
tester_formatage_message_historique()
tester_aide_un_seul_message()
tester_recherche_ignore_nouvelle_aide()
tester_statut_un_seul_message()
tester_echec_sauvegarde_preserve_memoire()
tester_gestion_taches()

print("Tous les tests ont réussi.")