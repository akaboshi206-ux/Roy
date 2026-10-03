import json
import os

from tempfile import TemporaryDirectory

from outils import (
    charger_json_avec_sauvegarde,
    sauvegarder_json_atomiquement
)

def tester_creation_copie_securite():
    with TemporaryDirectory() as dossier:
        chemin = os.path.join(
            dossier,
            "donnees.json"
        )

        premiere_version = {
            "version": 1
        }

        deuxieme_version = {
            "version": 2
        }

        assert sauvegarder_json_atomiquement(
            chemin,
            premiere_version
        ) is True

        assert not os.path.exists(
            f"{chemin}.bak"
        )

        assert sauvegarder_json_atomiquement(
            chemin,
            deuxieme_version
        ) is True

        with open(
            chemin,
            "r",
            encoding="utf-8"
        ) as fichier:
            donnees_actuelles = json.load(
                fichier
            )

        with open(
            f"{chemin}.bak",
            "r",
            encoding="utf-8"
        ) as fichier:
            donnees_sauvegardees = json.load(
                fichier
            )

        assert donnees_actuelles == (
            deuxieme_version
        )

        assert donnees_sauvegardees == (
            premiere_version
        )

def tester_chargement_copie_securite():
    with TemporaryDirectory() as dossier:
        chemin = os.path.join(
            dossier,
            "donnees.json"
        )

        with open(
            chemin,
            "w",
            encoding="utf-8"
        ) as fichier:
            fichier.write("{json invalide")

        chemin_sauvegarde = (
            f"{chemin}.bak"
        )

        with open(
            chemin_sauvegarde,
            "w",
            encoding="utf-8"
        ) as fichier:
            json.dump(
                {"version": 1},
                fichier
            )

        donnees, erreur, recuperation = (
            charger_json_avec_sauvegarde(
                chemin,
                {}
            )
        )

        assert donnees == {
            "version": 1
        }

        assert erreur is None
        assert recuperation is True

        with open(
            chemin,
            "r",
            encoding="utf-8"
        ) as fichier:
            donnees_reparees = json.load(
                fichier
            )

        assert donnees_reparees == {
            "version": 1
        }