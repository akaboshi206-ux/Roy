import json
import os
from unittest.mock import patch

from tempfile import TemporaryDirectory

from outils import (
    charger_json_avec_sauvegarde,
    sauvegarder_json_atomiquement,
    est_memoire_valide
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

        donnees, erreur, recuperation, erreur_reparation = (
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
        assert erreur_reparation is None

def tester_recuperation_format_memoire_invalide():
    with TemporaryDirectory() as dossier:
        chemin = os.path.join(dossier, "memoire.json")
        memoire_valide = {"couleur": "cyan"}

        with open(chemin, "w", encoding="utf-8") as fichier:
            json.dump({"couleur": 123}, fichier)

        with open(f"{chemin}.bak", "w", encoding="utf-8") as fichier:
            json.dump(memoire_valide, fichier)

        donnees, erreur, recuperation, erreur_reparation = charger_json_avec_sauvegarde(
            chemin,
            {},
            validateur=est_memoire_valide
        )

        assert donnees == memoire_valide
        assert erreur is None
        assert recuperation is True

        with open(chemin, "r", encoding="utf-8") as fichier:
            assert json.load(fichier) == memoire_valide
        assert erreur_reparation is None

def tester_refus_deux_memoires_invalides():
    with TemporaryDirectory() as dossier:
        chemin = os.path.join(dossier, "memoire.json")
        principale = {"couleur": 123}
        copie = {"couleur": False}

        with open(chemin, "w", encoding="utf-8") as fichier:
            json.dump(principale, fichier)

        with open(f"{chemin}.bak", "w", encoding="utf-8") as fichier:
            json.dump(copie, fichier)

        donnees, erreur, recuperation, erreur_reparation = charger_json_avec_sauvegarde(
            chemin,
            {},
            validateur=est_memoire_valide
        )

        assert donnees == {}
        assert isinstance(erreur, ValueError)
        assert recuperation is False

        with open(chemin, "r", encoding="utf-8") as fichier:
            assert json.load(fichier) == principale

        with open(f"{chemin}.bak", "r", encoding="utf-8") as fichier:
            assert json.load(fichier) == copie
        assert erreur_reparation is None

def tester_recuperation_avec_echec_reparation():
    with TemporaryDirectory() as dossier:
        chemin = os.path.join(dossier, "memoire.json")
        principale = {"couleur": 123}
        copie = {"couleur": "cyan"}

        with open(chemin, "w", encoding="utf-8") as fichier:
            json.dump(principale, fichier)

        with open(f"{chemin}.bak", "w", encoding="utf-8") as fichier:
            json.dump(copie, fichier)

        erreur_simulee = OSError("Réparation impossible")

        with patch(
            "outils.shutil.copy2",
            side_effect=erreur_simulee
        ):
            donnees, erreur, recuperation, erreur_reparation = (
                charger_json_avec_sauvegarde(
                    chemin,
                    {},
                    validateur=est_memoire_valide
                )
            )

        assert donnees == copie
        assert erreur is None
        assert recuperation is True
        assert erreur_reparation is erreur_simulee

        with open(chemin, "r", encoding="utf-8") as fichier:
            assert json.load(fichier) == principale

        with open(f"{chemin}.bak", "r", encoding="utf-8") as fichier:
            assert json.load(fichier) == copie