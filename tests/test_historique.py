import json

from pathlib import Path
from tempfile import TemporaryDirectory

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