import json

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from roy import Roy
from outils import est_memoire_valide
from tests.aides import (
    dossier_tests,
    creer_roy_test
)

def tester_memoire_configurable():
    with TemporaryDirectory() as dossier_temporaire:
        chemin = (
            Path(dossier_temporaire)
            / "memoire_test.json"
        )

        roy = Roy(
            historique_actif=False,
            fichier_memoire=str(chemin)
        )

        assert roy.memoire == {}

        assert (
            roy.apprendre(
                "couleur",
                "cyan"
            )
            is True
        )
        assert chemin.exists()

        roy_recharge = Roy(
            historique_actif=False,
            fichier_memoire=str(chemin)
        )

        assert (
            roy_recharge.memoire["couleur"]
            == "cyan"
        )


def tester_validation_memoire():
    assert est_memoire_valide({
        "couleur": "cyan",
        "ville": "Paris"
    }) is True

    assert est_memoire_valide({}) is True

    assert est_memoire_valide({
        42: "cyan"
    }) is False

    assert est_memoire_valide({
        "age": 20
    }) is False

    assert est_memoire_valide(
        ["cyan", "Paris"]
    ) is False

def tester_echec_sauvegarde_preserve_memoire():
    with TemporaryDirectory() as dossier:
        chemin = (
            Path(dossier) / "memoire_test.json"
        )

        chemin.write_text(
            '{"couleur": "bleu"}',
            encoding="utf-8"
        )

        roy = Roy(
            historique_actif=False,
            fichier_memoire=str(chemin)
        )
        roy.memoire["couleur"] = "cyan"

        with patch(
            "outils.os.replace",
            side_effect=OSError("échec simulé")
        ):
            assert (
                roy.sauvegarder_memoire()
                is False
            )

        contenu = chemin.read_text(
            encoding="utf-8"
        )

        assert json.loads(contenu) == {
            "couleur": "bleu"
        }

        chemin_sauvegarde = Path(
            f"{chemin}.bak"
        )

        contenu_sauvegarde = (
            chemin_sauvegarde.read_text(
                encoding="utf-8"
            )
        )

        assert json.loads(
            contenu_sauvegarde
        ) == {
            "couleur": "bleu"
        }

        assert set(
            Path(dossier).iterdir()
        ) == {
            chemin,
            chemin_sauvegarde
        }


def tester_apprentissage_conserve_majuscules():
    roy = creer_roy_test(
        historique_actif=False
    )

    resultat = roy.traiter_message(
        "retiens que ville = paris",
        "retiens que ville = Paris"
    )

    assert resultat is True
    assert (
        roy.memoire["ville"]
        == "Paris"
    )

def tester_chargement_memoire_json():
    fichier_memoire = (
        Path(dossier_tests.name)
        / "memoire_chargement.json"
    )

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
        fichier_memoire=str(
            fichier_memoire
        )
    )

    assert roy.memoire == {
        "ville": "Paris",
        "couleur": "cyan"
    }

    assert roy.memoire_sauvegardable is True

def tester_recuperation_memoire_depuis_copie_securite():
    with TemporaryDirectory() as dossier:
        chemin = (
            Path(dossier)
            / "memoire_test.json"
        )

        chemin.write_text(
            "{json invalide",
            encoding="utf-8"
        )

        chemin_sauvegarde = Path(
            f"{chemin}.bak"
        )

        chemin_sauvegarde.write_text(
            json.dumps({
                "couleur": "cyan"
            }),
            encoding="utf-8"
        )

        roy = Roy(
            historique_actif=False,
            fichier_memoire=str(chemin)
        )

        assert roy.memoire == {
            "couleur": "cyan"
        }

        assert (
            roy.memoire_sauvegardable
            is True
        )

def tester_recuperation_memoire_format_invalide():
    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "memoire_test.json"
        memoire_valide = {"couleur": "cyan"}

        with open(chemin, "w", encoding="utf-8") as fichier:
            json.dump({"couleur": 123}, fichier)

        with open(f"{chemin}.bak", "w", encoding="utf-8") as fichier:
            json.dump(memoire_valide, fichier)

        roy = creer_roy_test(
            fichier_memoire=str(chemin)
        )

        assert roy.memoire == memoire_valide
        assert roy.memoire_sauvegardable is True

        with open(chemin, "r", encoding="utf-8") as fichier:
            assert json.load(fichier) == memoire_valide

def tester_reparation_memoire_echouee_bloque_sauvegarde():
    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "memoire.json"
        chemin_sauvegarde = Path(f"{chemin}.bak")

        principale = {"couleur": 123}
        copie = {"couleur": "cyan"}

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
                historique_actif=False,
                fichier_memoire=str(chemin)
            )

        assert roy.memoire == copie
        assert roy.memoire_sauvegardable is False

        roy.memoire["ville"] = "Paris"
        assert roy.sauvegarder_memoire() is False

        assert json.loads(
            chemin.read_text(encoding="utf-8")
        ) == principale

        assert json.loads(
            chemin_sauvegarde.read_text(encoding="utf-8")
        ) == copie

        assert roy.memoire["ville"] == "Paris"