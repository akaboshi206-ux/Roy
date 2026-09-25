import json

from pathlib import Path
from tempfile import TemporaryDirectory
from roy import Roy
from outils import (
    charger_json,
    formater_message_historique
)
from config import (
    commandes_quitter,
    exemples_aide
)
from commandes_conversation import (
    traiter_commande_conversation
)
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
    chemin_historique = (
        Path(dossier_tests.name)
        / f"historique_{numero}.json"
    )
    chemin_taches = (
        Path(dossier_tests.name)
        / f"taches_{numero}.json"
    )

    options.setdefault(
        "fichier_memoire",
        str(chemin_memoire)
    )

    options.setdefault(
        "fichier_historique",
        str(chemin_historique)
    )

    options.setdefault(
        "fichier_taches",
        str(chemin_taches)
    )

    return Roy(
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
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.afficher_aide()

    assert len(roy.historique) == 1

    lignes_attendues = [
        "Voici ce que je peux faire :"
    ]

    lignes_attendues.extend(
        f"{numero}. {exemple}"
        for numero, exemple in enumerate(
            exemples_aide,
            start=1
        )
    )

    resultat_attendu = "\n".join(
        lignes_attendues
    )

    assert (
        roy.historique[0]["content"]
        == resultat_attendu
    )

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

        with patch("outils.os.replace", side_effect=OSError("échec simulé")):
            assert roy.sauvegarder_memoire() is False

        assert json.loads(chemin.read_text(encoding="utf-8")) == {
            "couleur": "bleu"
        }
        assert list(Path(dossier).iterdir()) == [chemin]

def tester_chargement_priorites_taches():
    with TemporaryDirectory() as dossier:
        chemin_taches = Path(dossier) / "taches_test.json"
        chemin_memoire = Path(dossier) / "memoire_test.json"

        anciennes_taches = [
            {
                "description": "ancienne tâche",
                "terminee": False
            }
        ]

        chemin_taches.write_text(
            json.dumps(
                anciennes_taches,
                ensure_ascii=False,
                indent=4
            ),
            encoding="utf-8"
        )

        roy = Roy(
            historique_actif=False,
            fichier_memoire=str(chemin_memoire),
            fichier_taches=str(chemin_taches)
        )

        assert roy.taches[0]["priorite"] == "normale"
        assert roy.taches_sauvegardables is True

        taches_invalides = [
            {
                "description": "tâche invalide",
                "terminee": False,
                "priorite": "urgente"
            }
        ]

        chemin_taches.write_text(
            json.dumps(
                taches_invalides,
                ensure_ascii=False,
                indent=4
            ),
            encoding="utf-8"
        )

        roy_invalide = Roy(
            historique_actif=False,
            fichier_memoire=str(chemin_memoire),
            fichier_taches=str(chemin_taches)
        )

        assert roy_invalide.taches == []
        assert roy_invalide.taches_sauvegardables is False

def tester_filtrage_taches():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.taches = [
        {
            "description": "tâche normale",
            "terminee": False,
            "priorite": "normale"
        },
        {
            "description": "tâche haute",
            "terminee": False,
            "priorite": "haute"
        },
        {
            "description": "tâche basse",
            "terminee": True,
            "priorite": "basse"
        }
    ]

    assert roy.traiter_message(
        "montre mes tâches de priorité haute",
        "montre mes tâches de priorité haute"
    ) is True

    reponse = roy.historique[-1]["content"]

    assert "2. ○ [haute] tâche haute" in reponse
    assert "tâche normale" not in reponse
    assert "tâche basse" not in reponse

    assert roy.traiter_message(
        "montre mes tâches à faire",
        "montre mes tâches à faire"
    ) is True

    reponse = roy.historique[-1]["content"]

    assert "1. ○ [normale] tâche normale" in reponse
    assert "2. ○ [haute] tâche haute" in reponse
    assert "tâche basse" not in reponse

    assert roy.traiter_message(
        "montre mes tâches terminées",
        "montre mes tâches terminées"
    ) is True

    reponse = roy.historique[-1]["content"]

    assert reponse == "3. ✓ [basse] tâche basse"

    assert roy.traiter_message(
        "montre mes tâches de priorité urgente",
        "montre mes tâches de priorité urgente"
    ) is True

    assert roy.historique[-1]["content"] == (
        "Choisis une priorité : "
        "basse, normale ou haute."
    )

def tester_gestion_taches():
    roy = creer_roy_test(
        historique_actif=False
    )

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
    assert (
        roy.taches[0]["description"]
        == "travailler sur Roy"
    )

    assert roy.traiter_message(
        "priorité tâche 1 : haute",
        "priorité tâche 1 : haute"
    ) is True

    assert roy.taches[0]["priorite"] == "haute"

    roy = recharger_roy_test(roy)

    assert roy.taches[0]["priorite"] == "haute"

    assert roy.traiter_message(
        "termine la tâche 1",
        "termine la tâche 1"
    ) is True

    assert roy.taches[0]["terminee"] is True

    roy = recharger_roy_test(roy)

    assert roy.taches[0]["terminee"] is True
    assert roy.taches[0]["priorite"] == "haute"

    assert roy.traiter_message(
        "rouvre la tâche 1",
        "rouvre la tâche 1"
    ) is True

    assert roy.taches[0]["terminee"] is False

    roy = recharger_roy_test(roy)

    assert roy.taches[0]["terminee"] is False
    assert roy.taches[0]["priorite"] == "haute"

    assert roy.traiter_message(
        "modifie la tâche 1 : travailler sur Python",
        "modifie la tâche 1 : travailler sur Python"
    ) is True

    assert (
        roy.taches[0]["description"]
        == "travailler sur Python"
    )
    assert roy.taches[0]["terminee"] is False
    assert roy.taches[0]["priorite"] == "haute"

    roy = recharger_roy_test(roy)

    assert (
        roy.taches[0]["description"]
        == "travailler sur Python"
    )
    assert roy.taches[0]["terminee"] is False
    assert roy.taches[0]["priorite"] == "haute"

    assert roy.traiter_message(
        "supprime la tâche 1",
        "supprime la tâche 1"
    ) is True

    assert roy.taches == []

    roy = recharger_roy_test(roy)

    assert roy.taches == []

def tester_apprentissage_conserve_majuscules():
    roy = creer_roy_test(
        historique_actif=False
    )

    resultat = roy.traiter_message(
        "retiens que ville = paris",
        "retiens que ville = Paris"
    )

    assert resultat is True
    assert roy.memoire["ville"] == "Paris"

def tester_commande_generale():
    roy = creer_roy_test(
        historique_actif=False
    )

    resultat = roy.traiter_message(
        "désactive ta mémoire",
        "désactive ta mémoire"
    )

    assert resultat is True
    assert roy.etat["memoire"]["active"] is False

def tester_commande_conversation():
    roy = creer_roy_test(
        historique_actif=False
    )

    resultat_connu = traiter_commande_conversation(
        roy,
        "comment vas-tu"
    )

    resultat_inconnu = traiter_commande_conversation(
        roy,
        "commande inconnue"
    )

    assert resultat_connu is True
    assert resultat_inconnu is False

def tester_charger_json():
    fichier_valide = Path(
        dossier_tests.name
    ) / "chargement_valide.json"

    fichier_valide.write_text(
        json.dumps(
            {"nom": "Cyan"}
        ),
        encoding="utf-8"
    )

    donnees_valides, erreur_valide = charger_json(
        str(fichier_valide),
        {}
    )

    fichier_absent = Path(
        dossier_tests.name
    ) / "chargement_absent.json"

    donnees_absentes, erreur_absente = charger_json(
        str(fichier_absent),
        {}
    )

    fichier_invalide = Path(
        dossier_tests.name
    ) / "chargement_invalide.json"

    fichier_invalide.write_text(
        "{json invalide",
        encoding="utf-8"
    )

    donnees_invalides, erreur_invalide = charger_json(
        str(fichier_invalide),
        []
    )

    assert donnees_valides == {"nom": "Cyan"}
    assert erreur_valide is None

    assert donnees_absentes == {}
    assert isinstance(
        erreur_absente,
        FileNotFoundError
    )

    assert donnees_invalides == []
    assert isinstance(
        erreur_invalide,
        json.JSONDecodeError
    )

def tester_chargement_memoire_json():
    fichier_memoire = Path(
        dossier_tests.name
    ) / "memoire_chargement.json"

    fichier_memoire.write_text(
        json.dumps(
            {
                "ville": "Paris",
                "couleur": "cyan"
            }
        ),
        encoding="utf-8"
    )

    roy = creer_roy_test(
        historique_actif=False,
        fichier_memoire=str(fichier_memoire)
    )

    assert roy.memoire == {
        "ville": "Paris",
        "couleur": "cyan"
    }
    assert roy.memoire_sauvegardable is True

def tester_chargement_historique_json():
    fichier_historique = Path(
        dossier_tests.name
    ) / "historique_chargement.json"

    fichier_historique.write_text(
        json.dumps(
            [
                {
                    "role": "user",
                    "content": "Bonjour Roy"
                },
                {
                    "role": "assistant",
                    "content": "Bonjour Cyan"
                }
            ]
        ),
        encoding="utf-8"
    )

    roy = creer_roy_test(
        fichier_historique=str(fichier_historique)
    )

    assert roy.historique == [
        {
            "role": "user",
            "content": "Bonjour Roy"
        },
        {
            "role": "assistant",
            "content": "Bonjour Cyan"
        }
    ]
    assert roy.historique_sauvegardable is True


def tester_chargement_taches_json():
    fichier_taches = Path(
        dossier_tests.name
    ) / "taches_chargement.json"

    fichier_taches.write_text(
        json.dumps(
            [
                {
                    "description": "Continuer Roy",
                    "terminee": False
                }
            ]
        ),
        encoding="utf-8"
    )

    roy = creer_roy_test(
        historique_actif=False,
        fichier_taches=str(fichier_taches)
    )

    assert roy.taches == [
        {
            "description": "Continuer Roy",
            "terminee": False,
            "priorite": "normale"
        }
    ]
    assert roy.taches_sauvegardables is True

def tester_chargements_fichiers_absents():
    with TemporaryDirectory() as dossier:
        roy = Roy(
            fichier_memoire=str(
                Path(dossier) / "memoire_absente.json"
            ),
            fichier_historique=str(
                Path(dossier) / "historique_absent.json"
            ),
            fichier_taches=str(
                Path(dossier) / "taches_absentes.json"
            )
        )

        assert roy.memoire == {}
        assert roy.historique == []
        assert roy.taches == []

        assert roy.memoire_sauvegardable is True
        assert roy.historique_sauvegardable is True
        assert roy.taches_sauvegardables is True

def tester_chargements_json_endommages():
    with TemporaryDirectory() as dossier:
        fichier_memoire = (
            Path(dossier) / "memoire_endommagee.json"
        )
        fichier_historique = (
            Path(dossier) / "historique_endommage.json"
        )
        fichier_taches = (
            Path(dossier) / "taches_endommagees.json"
        )

        fichier_memoire.write_text(
            "{json invalide",
            encoding="utf-8"
        )
        fichier_historique.write_text(
            "{json invalide",
            encoding="utf-8"
        )
        fichier_taches.write_text(
            "{json invalide",
            encoding="utf-8"
        )

        roy = Roy(
            fichier_memoire=str(fichier_memoire),
            fichier_historique=str(fichier_historique),
            fichier_taches=str(fichier_taches)
        )

        assert roy.memoire == {}
        assert roy.historique == []
        assert roy.taches == []

        assert roy.memoire_sauvegardable is False
        assert roy.historique_sauvegardable is False
        assert roy.taches_sauvegardables is False

def tester_chargements_formats_invalides():
    with TemporaryDirectory() as dossier:
        fichier_memoire = (
            Path(dossier) / "memoire_format_invalide.json"
        )
        fichier_historique = (
            Path(dossier) / "historique_format_invalide.json"
        )
        fichier_taches = (
            Path(dossier) / "taches_format_invalide.json"
        )

        fichier_memoire.write_text(
            json.dumps([]),
            encoding="utf-8"
        )
        fichier_historique.write_text(
            json.dumps({}),
            encoding="utf-8"
        )
        fichier_taches.write_text(
            json.dumps({}),
            encoding="utf-8"
        )

        roy = Roy(
            fichier_memoire=str(fichier_memoire),
            fichier_historique=str(fichier_historique),
            fichier_taches=str(fichier_taches)
        )

        assert roy.memoire == {}
        assert roy.historique == []
        assert roy.taches == []

        assert roy.memoire_sauvegardable is False
        assert roy.historique_sauvegardable is False
        assert roy.taches_sauvegardables is False

def tester_charger_json_erreur_lecture():
    with patch(
        "builtins.open",
        side_effect=PermissionError("accès refusé")
    ):
        donnees, erreur = charger_json(
            "fichier_protege.json",
            {}
        )

    assert donnees == {}
    assert isinstance(
        erreur,
        PermissionError
    )

def lancer_tests():
    tests = [
        fonction
        for nom, fonction in globals().copy().items()
        if nom.startswith("tester_")
        and callable(fonction)
    ]

    for test in tests:
        test()

    print(
        f"{len(tests)} tests ont réussi."
    )


if __name__ == "__main__":
    lancer_tests()