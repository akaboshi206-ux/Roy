import json

from pathlib import Path
from unittest.mock import patch
from tempfile import TemporaryDirectory

from roy import Roy

from outils import charger_json

from tests.aides import dossier_tests


def tester_charger_json():
    fichier_valide = (
        Path(dossier_tests.name)
        / "chargement_valide.json"
    )

    fichier_valide.write_text(
        json.dumps(
            {"nom": "Cyan"}
        ),
        encoding="utf-8"
    )

    donnees_valides, erreur_valide = (
        charger_json(
            str(fichier_valide),
            {}
        )
    )

    fichier_absent = (
        Path(dossier_tests.name)
        / "chargement_absent.json"
    )

    donnees_absentes, erreur_absente = (
        charger_json(
            str(fichier_absent),
            {}
        )
    )

    fichier_invalide = (
        Path(dossier_tests.name)
        / "chargement_invalide.json"
    )

    fichier_invalide.write_text(
        "{json invalide",
        encoding="utf-8"
    )

    donnees_invalides, erreur_invalide = (
        charger_json(
            str(fichier_invalide),
            []
        )
    )

    assert donnees_valides == {
        "nom": "Cyan"
    }
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


def tester_charger_json_erreur_lecture():
    with patch(
        "builtins.open",
        side_effect=PermissionError(
            "accès refusé"
        )
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
