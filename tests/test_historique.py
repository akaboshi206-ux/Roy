import json

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from roy import Roy

from outils import (
    formater_message_historique,
    est_message_historique_valide
)

from tests.aides import (
    dossier_tests,
    creer_roy_test
)


def tester_historique():
    with TemporaryDirectory() as dossier:
        roy = Roy(
            historique_actif=False,
            fichier_memoire=str(
                Path(dossier) / "memoire_test.json"
            )
        )

    assert roy.historique == []

    roy.ajouter_historique(
        "user",
        "bonjour"
    )

    assert len(roy.historique) == 1

    premier_message = roy.historique[0]

    assert premier_message["role"] == "user"
    assert (
        premier_message["content"]
        == "bonjour"
    )
    assert "timestamp" in premier_message
    assert isinstance(
        premier_message["timestamp"],
        str
    )

    for numero in range(25):
        roy.ajouter_historique(
            "user",
            f"message {numero}"
        )

    assert len(roy.historique) == 26
    assert (
        roy.historique[0]["content"]
        == "bonjour"
    )
    assert (
        roy.historique[-1]["content"]
        == "message 24"
    )


def tester_recherche_historique():
    roy = creer_roy_test(
        historique_actif=False
    )
    roy.etat["systeme"]["actif"] = True

    roy.ajouter_historique(
        "user",
        "Bonjour Cyan"
    )
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
    assert (
        roy.historique[0]["content"]
        == "Bonjour Cyan"
    )

def tester_statistiques_historique():
    roy = creer_roy_test(
        historique_actif=False
    )
    roy.etat["systeme"]["actif"] = True

    roy.ajouter_historique(
        "user",
        "bonjour"
    )
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
    assert (
        roy.historique[0]["role"]
        == "user"
    )
    assert (
        roy.historique[1]["role"]
        == "assistant"
    )


def tester_chargement_historique_invalide():
    with TemporaryDirectory() as dossier_temporaire:
        chemin = (
            Path(dossier_temporaire)
            / "historique_test.json"
        )

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

        with open(
            chemin,
            "w",
            encoding="utf-8"
        ) as fichier:
            json.dump(
                donnees,
                fichier,
                ensure_ascii=False,
                indent=4
            )

        roy = creer_roy_test(
            fichier_historique=str(chemin)
        )

        assert len(roy.historique) == 1
        assert (
            roy.historique[0]["role"]
            == "user"
        )
        assert (
            roy.historique[0]["content"]
            == "Bonjour"
        )

        assert roy.historique_sauvegardable is False
        assert roy.sauvegarder_historique() is False

        with open(chemin, "r", encoding="utf-8") as fichier:
            assert json.load(fichier) == donnees

def tester_commande_historique_avec_limite():
    roy = creer_roy_test(
        historique_actif=False
    )

    assert (
        roy.traiter_historique("statut")
        is False
    )
    assert (
        roy.traiter_historique("historique")
        is True
    )
    assert (
        roy.traiter_historique("historique 3")
        is True
    )
    assert (
        roy.traiter_historique(
            "historique banane"
        )
        is True
    )

    assert roy.historique[-1]["content"] == (
        "Utilise un nombre, par exemple : "
        "historique 5"
    )

    assert (
        roy.traiter_historique("historique 0")
        is True
    )

    assert roy.historique[-1]["content"] == (
        "Le nombre de messages doit être "
        "supérieur à zéro."
    )

    assert (
        roy.traiter_historique("historique -5")
        is True
    )


def tester_export_historique():
    with TemporaryDirectory() as dossier_temporaire:
        chemin = (
            Path(dossier_temporaire)
            / "conversation_test.txt"
        )

        roy = creer_roy_test(
            historique_actif=False
        )
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

        resultat = roy.exporter_historique(
            str(chemin)
        )

        assert resultat is True
        assert chemin.exists()

        contenu = chemin.read_text(
            encoding="utf-8"
        )

        assert (
            "[2026-09-20 10:00:00] "
            "Toi : Bonjour"
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

        roy_vide = creer_roy_test(
            historique_actif=False
        )

        assert (
            roy_vide.exporter_historique(
                str(chemin_vide)
            )
            is False
        )

        assert not chemin_vide.exists()

def tester_formatage_message_historique():
    ancien_message = {
        "role": "user",
        "content": "salut"
    }

    assert (
        formater_message_historique(
            ancien_message
        )
        == "Toi : salut"
    )

    message_date = {
        "role": "assistant",
        "content": "Bonjour Cyan",
        "timestamp": "2026-09-22T08:46:28"
    }

    assert (
        formater_message_historique(
            message_date
        )
        == (
            "[2026-09-22 08:46:28] "
            "Roy : Bonjour Cyan"
        )
    )

def tester_validation_message_historique():
    assert est_message_historique_valide({
        "role": "user",
        "content": "Bonjour",
        "timestamp": "2026-09-26T11:00:00"
    }) is True

    assert est_message_historique_valide({
        "role": "assistant",
        "content": "Bonjour Cyan"
    }) is True

    assert est_message_historique_valide({
        "role": "inconnu",
        "content": "Bonjour"
    }) is False

    assert est_message_historique_valide({
        "role": "user",
        "content": 42
    }) is False

    assert est_message_historique_valide({
        "role": "user",
        "content": "Bonjour",
        "timestamp": 42
    }) is False

    assert est_message_historique_valide(
        "pas un message"
    ) is False

def tester_chargement_historique_json():
    fichier_historique = (
        Path(dossier_tests.name)
        / "historique_chargement.json"
    )

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
        fichier_historique=str(
            fichier_historique
        )
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

    assert (
        roy.historique_sauvegardable
        is True
    )

def tester_recuperation_historique_depuis_copie_securite():
    with TemporaryDirectory() as dossier:
        chemin = (
            Path(dossier)
            / "historique_test.json"
        )

        chemin.write_text(
            "{json invalide",
            encoding="utf-8"
        )

        historique_sauvegarde = [
            {
                "role": "user",
                "content": "Bonjour Roy",
                "timestamp": (
                    "2026-10-02T13:00:00"
                )
            }
        ]

        chemin_sauvegarde = Path(
            f"{chemin}.bak"
        )

        chemin_sauvegarde.write_text(
            json.dumps(
                historique_sauvegarde
            ),
            encoding="utf-8"
        )

        roy = Roy(
            historique_actif=True,
            fichier_historique=str(chemin)
        )

        assert roy.historique == (
            historique_sauvegarde
        )

        assert (
            roy.historique_sauvegardable
            is True
        )

        donnees_reparees = json.loads(
            chemin.read_text(
                encoding="utf-8"
            )
        )

        assert donnees_reparees == (
            historique_sauvegarde
        )

def tester_recuperation_historique_format_invalide():
    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "historique_test.json"

        historique_valide = [
            {"role": "user", "content": "Bonjour Cyan"}
        ]

        with open(chemin, "w", encoding="utf-8") as fichier:
            json.dump(
                [{"role": "user", "content": 123}],
                fichier
            )

        with open(f"{chemin}.bak", "w", encoding="utf-8") as fichier:
            json.dump(historique_valide, fichier)

        roy = creer_roy_test(
            fichier_historique=str(chemin)
        )

        assert roy.historique == historique_valide
        assert roy.historique_sauvegardable is True

        with open(chemin, "r", encoding="utf-8") as fichier:
            assert json.load(fichier) == historique_valide

def tester_reparation_historique_echouee_bloque_sauvegarde():
    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "historique.json"
        chemin_sauvegarde = Path(f"{chemin}.bak")

        principale = [
            {"role": "user", "content": 123}
        ]
        copie = [
            {"role": "user", "content": "Bonjour Cyan"}
        ]

        chemin.write_text(
            json.dumps(principale),
            encoding="utf-8"
        )
        chemin_sauvegarde.write_text(
            json.dumps(copie),
            encoding="utf-8"
        )

        with patch(
            "outils.shutil.copy2",
            side_effect=OSError("Réparation impossible")
        ):
            roy = creer_roy_test(
                fichier_historique=str(chemin)
            )

        assert roy.historique == copie
        assert roy.historique_sauvegardable is False

        roy.historique.append(
            {"role": "assistant", "content": "Bonjour !"}
        )
        assert roy.sauvegarder_historique() is False

        assert json.loads(
            chemin.read_text(encoding="utf-8")
        ) == principale

        assert json.loads(
            chemin_sauvegarde.read_text(encoding="utf-8")
        ) == copie

        assert len(roy.historique) == 2
        assert roy.historique[-1]["content"] == "Bonjour !"

def tester_reparation_historique_conserve_messages_actuels():
    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "historique.json"
        chemin_sauvegarde = Path(f"{chemin}.bak")

        copie = [
            {"role": "user", "content": "Bonjour Cyan"}
        ]

        chemin.write_text(
            "{json invalide",
            encoding="utf-8"
        )
        chemin_sauvegarde.write_text(
            json.dumps(copie),
            encoding="utf-8"
        )
        contenu_copie = chemin_sauvegarde.read_bytes()

        with patch(
            "outils.shutil.copy2",
            side_effect=OSError("Réparation impossible")
        ):
            roy = creer_roy_test(
                fichier_historique=str(chemin)
            )

        assert roy.historique_sauvegardable is False

        roy.ajouter_historique(
            "assistant",
            "Bonjour !"
        )
        historique_actuel = roy.historique.copy()

        assert roy.reparer_historique() is True
        assert roy.historique_sauvegardable is True
        assert roy.historique == historique_actuel

        assert json.loads(
            chemin.read_text(encoding="utf-8")
        ) == copie

        assert chemin_sauvegarde.read_bytes() == contenu_copie

        assert set(Path(dossier).iterdir()) == {
            chemin,
            chemin_sauvegarde
        }

        assert roy.sauvegarder_historique() is True

        assert json.loads(
            chemin.read_text(encoding="utf-8")
        ) == historique_actuel

        assert json.loads(
            chemin_sauvegarde.read_text(encoding="utf-8")
        ) == copie

def tester_echec_reparation_historique_preserve_messages():
    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "historique.json"
        chemin_sauvegarde = Path(f"{chemin}.bak")

        principale = "{json invalide"
        copie = [
            {"role": "user", "content": "Bonjour Cyan"}
        ]

        chemin.write_text(
            principale,
            encoding="utf-8"
        )
        chemin_sauvegarde.write_text(
            json.dumps(copie),
            encoding="utf-8"
        )
        contenu_copie = chemin_sauvegarde.read_bytes()

        with patch(
            "outils.shutil.copy2",
            side_effect=OSError("Réparation impossible")
        ):
            roy = creer_roy_test(
                fichier_historique=str(chemin)
            )

        roy.ajouter_historique(
            "assistant",
            "Bonjour !"
        )
        historique_actuel = roy.historique.copy()

        with patch(
            "outils.os.replace",
            side_effect=OSError("Fichier inaccessible")
        ):
            assert roy.reparer_historique() is False

        assert roy.historique_sauvegardable is False
        assert roy.historique == historique_actuel
        assert roy.sauvegarder_historique() is False

        assert chemin.read_text(
            encoding="utf-8"
        ) == principale

        assert chemin_sauvegarde.read_bytes() == contenu_copie

        assert set(Path(dossier).iterdir()) == {
            chemin,
            chemin_sauvegarde
        }

def tester_commande_reparation_historique():
    roy = creer_roy_test()

    for commande in (
        "répare ton historique",
        "repare ton historique"
    ):
        for resultat_reparation in (True, False):
            with patch.object(
                roy,
                "reparer_historique",
                return_value=resultat_reparation
            ) as reparation:
                resultat = roy.traiter_message(
                    commande,
                    commande
                )

            assert resultat is True
            reparation.assert_called_once_with()

    with patch.object(
        roy,
        "reparer_historique"
    ) as reparation:
        resultat = roy.traiter_message(
            "commande inconnue",
            "commande inconnue"
        )

    assert resultat is False
    reparation.assert_not_called()

def tester_reponse_avec_sortie_remplacable():
    from unittest.mock import patch

    roy = creer_roy_test(historique_actif=True)
    roy.historique = []

    with patch.object(
        roy,
        "sauvegarder_historique",
        return_value=True
    ) as sauvegarde:
        with patch.object(roy, "afficher_sortie") as sortie:
            with patch(
                "builtins.print",
                side_effect=AssertionError("Affichage direct inattendu")
            ):
                roy.repondre("Bonjour Cyan")

    sortie.assert_called_once_with("Bonjour Cyan")
    sauvegarde.assert_called_once_with()
    assert len(roy.historique) == 1
    assert roy.historique[0]["role"] == "assistant"
    assert roy.historique[0]["content"] == "Bonjour Cyan"