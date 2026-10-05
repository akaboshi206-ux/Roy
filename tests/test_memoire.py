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

def tester_reparation_memoire_conserve_donnees_actuelles():
    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "memoire.json"
        chemin_sauvegarde = Path(f"{chemin}.bak")

        copie = {"couleur": "cyan"}

        chemin.write_text(
            "{json invalide",
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

        assert roy.memoire_sauvegardable is False

        roy.memoire["ville"] = "Paris"
        memoire_actuelle = roy.memoire.copy()

        assert roy.reparer_memoire() is True
        assert roy.memoire_sauvegardable is True
        assert roy.memoire == memoire_actuelle

        assert json.loads(
            chemin.read_text(encoding="utf-8")
        ) == copie

        assert json.loads(
            chemin_sauvegarde.read_text(encoding="utf-8")
        ) == copie

        assert set(Path(dossier).iterdir()) == {
            chemin,
            chemin_sauvegarde
        }

        assert roy.sauvegarder_memoire() is True

        assert json.loads(
            chemin.read_text(encoding="utf-8")
        ) == memoire_actuelle

        assert json.loads(
            chemin_sauvegarde.read_text(encoding="utf-8")
        ) == copie

def tester_echec_reparation_memoire_preserve_donnees():
    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "memoire.json"
        chemin_sauvegarde = Path(f"{chemin}.bak")

        principale = "{json invalide"
        copie = {"couleur": "cyan"}

        chemin.write_text(
            principale,
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

        roy.memoire["ville"] = "Paris"
        memoire_actuelle = roy.memoire.copy()
        contenu_copie = chemin_sauvegarde.read_bytes()

        with patch(
            "outils.os.replace",
            side_effect=OSError("Fichier inaccessible")
        ):
            assert roy.reparer_memoire() is False

        assert roy.memoire_sauvegardable is False
        assert roy.memoire == memoire_actuelle
        assert roy.sauvegarder_memoire() is False

        assert chemin.read_text(
            encoding="utf-8"
        ) == principale

        assert chemin_sauvegarde.read_bytes() == contenu_copie

        assert set(Path(dossier).iterdir()) == {
            chemin,
            chemin_sauvegarde
        }

def tester_reparation_memoire_refuse_copie_invalide():
    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "memoire.json"
        chemin_sauvegarde = Path(f"{chemin}.bak")

        principale = "{json invalide"

        chemin.write_text(
            principale,
            encoding="utf-8"
        )
        chemin_sauvegarde.write_text(
            json.dumps({"couleur": "cyan"}),
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

        roy.memoire["ville"] = "Paris"
        memoire_actuelle = roy.memoire.copy()

        chemin_sauvegarde.write_text(
            json.dumps({"couleur": 123}),
            encoding="utf-8"
        )
        contenu_copie = chemin_sauvegarde.read_bytes()

        assert roy.reparer_memoire() is False
        assert roy.memoire_sauvegardable is False
        assert roy.memoire == memoire_actuelle

        assert chemin.read_text(
            encoding="utf-8"
        ) == principale

        assert chemin_sauvegarde.read_bytes() == contenu_copie

        assert set(Path(dossier).iterdir()) == {
            chemin,
            chemin_sauvegarde
        }

def tester_commande_reparation_memoire():
    roy = creer_roy_test(
        historique_actif=False
    )

    for commande in (
        "répare ta mémoire",
        "repare ta memoire"
    ):
        for resultat_reparation in (True, False):
            with patch.object(
                roy,
                "reparer_memoire",
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
        "reparer_memoire"
    ) as reparation:
        resultat = roy.traiter_message(
            "commande inconnue",
            "commande inconnue"
        )

    assert resultat is False
    reparation.assert_not_called()

def tester_reparation_memoire_refuse_copie_absente():
    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "memoire.json"
        principale = "{json invalide"

        chemin.write_text(
            principale,
            encoding="utf-8"
        )

        roy = creer_roy_test(
            historique_actif=False,
            fichier_memoire=str(chemin)
        )

        roy.memoire["ville"] = "Paris"
        memoire_actuelle = roy.memoire.copy()

        assert roy.memoire_sauvegardable is False
        assert roy.reparer_memoire() is False
        assert roy.memoire_sauvegardable is False
        assert roy.memoire == memoire_actuelle

        assert chemin.read_text(
            encoding="utf-8"
        ) == principale

        assert set(Path(dossier).iterdir()) == {
            chemin
        }

def tester_statut_sauvegardes_sans_ecriture():
    roy = creer_roy_test()

    lignes = roy.obtenir_statut_sauvegardes()

    assert "Mémoire : sauvegarde autorisée." in lignes
    assert "Historique : sauvegarde autorisée." in lignes
    assert "Tâches : sauvegarde autorisée." in lignes

    roy.memoire_sauvegardable = False
    roy.historique_sauvegardable = False
    roy.taches_sauvegardables = False

    lignes = roy.obtenir_statut_sauvegardes()

    assert (
        "Mémoire : sauvegarde bloquée. "
        "Utilise : répare ta mémoire."
    ) in lignes
    assert (
        "Historique : sauvegarde bloquée. "
        "Utilise : répare ton historique."
    ) in lignes
    assert (
        "Tâches : sauvegarde bloquée. "
        "Utilise : répare mes tâches."
    ) in lignes

    historique_avant = [
        message.copy()
        for message in roy.historique
    ]

    with patch.object(
        roy,
        "sauvegarder_historique"
    ) as sauvegarde:
        for commande in (
            "statut sauvegardes",
            "statut des sauvegardes"
        ):
            assert roy.traiter_message(
                commande,
                commande
            ) is True

    sauvegarde.assert_not_called()
    assert roy.historique == historique_avant

    roy.historique_actif = False
    lignes = roy.obtenir_statut_sauvegardes()

    assert "Historique : désactivé." in lignes
    assert not any(
        "répare ton historique" in ligne
        for ligne in lignes
    )

def tester_apprentissage_echoue_sans_annoncer_succes():
    roy = creer_roy_test(
        historique_actif=False
    )
    roy.memoire = {"couleur": "cyan"}

    for cle, valeur in (
        ("ville", "Paris"),
        ("couleur", "bleu")
    ):
        memoire_avant = roy.memoire.copy()

        with patch.object(
            roy,
            "sauvegarder_memoire",
            return_value=False
        ) as sauvegarde:
            with patch.object(
                roy,
                "repondre"
            ) as reponse:
                resultat = roy.apprendre(cle, valeur)

        assert resultat is False
        assert roy.memoire == memoire_avant
        sauvegarde.assert_called_once_with()
        reponse.assert_called_once_with(
            "La modification a été annulée."
        )

def tester_renommage_echoue_preserve_memoire():
    roy = creer_roy_test(
        historique_actif=False
    )
    roy.memoire = {
        "couleur": "cyan",
        "ville": "Paris"
    }
    memoire_avant = roy.memoire.copy()

    with patch.object(
        roy,
        "sauvegarder_memoire",
        return_value=False
    ) as sauvegarde:
        with patch.object(
            roy,
            "repondre"
        ) as reponse:
            roy.renommer_information(
                "couleur",
                "couleur_preferee"
            )

    assert roy.memoire == memoire_avant
    assert "couleur_preferee" not in roy.memoire

    sauvegarde.assert_called_once_with()
    reponse.assert_called_once_with(
        "Le renommage a échoué. "
        "La modification a été annulée."
    )

def tester_oubli_echoue_preserve_memoire():
    roy = creer_roy_test(historique_actif=False)
    roy.memoire = {"couleur": "cyan", "ville": "Paris"}
    memoire_avant = roy.memoire.copy()

    with patch.object(
        roy, "demander_confirmation", return_value=True
    ):
        with patch.object(
            roy, "sauvegarder_memoire", return_value=False
        ) as sauvegarde:
            with patch.object(roy, "repondre") as reponse:
                roy.oublier("couleur")

    assert roy.memoire == memoire_avant
    sauvegarde.assert_called_once_with()
    reponse.assert_called_once_with(
        "L'oubli de l'information a échoué."
    )

def tester_oubli_total_echoue_preserve_memoire():
    roy = creer_roy_test(historique_actif=False)
    roy.memoire = {"couleur": "cyan", "ville": "Paris"}
    memoire_avant = roy.memoire.copy()

    with patch.object(
        roy, "demander_confirmation", return_value=True
    ):
        with patch.object(
            roy, "sauvegarder_memoire", return_value=False
        ) as sauvegarde:
            with patch.object(roy, "repondre") as reponse:
                roy.oublier("tout")

    assert roy.memoire == memoire_avant
    sauvegarde.assert_called_once_with()
    reponse.assert_called_once_with(
        "L'effacement a échoué. La mémoire a été restaurée."
    )

def tester_oubli_partiel_echoue_preserve_memoire():
    roy = creer_roy_test(historique_actif=False)
    roy.memoire = {"couleur": "cyan", "ville": "Paris"}
    memoire_avant = roy.memoire.copy()

    with patch.object(
        roy, "demander_confirmation", return_value=True
    ):
        with patch.object(
            roy, "sauvegarder_memoire", return_value=False
        ) as sauvegarde:
            with patch.object(roy, "repondre") as reponse:
                roy.oublier("tout sauf couleur")

    assert roy.memoire == memoire_avant
    sauvegarde.assert_called_once_with()
    reponse.assert_called_with(
        "L'effacement a échoué. La mémoire a été restaurée."
    )

def tester_information_inconnue_ne_demande_pas_de_saisie():
    roy = creer_roy_test(historique_actif=False)
    roy.memoire = {"nom": "Cyan"}
    memoire_avant = roy.memoire.copy()

    with patch(
        "builtins.input",
        side_effect=AssertionError("Saisie inattendue")
    ):
        with patch.object(roy, "repondre") as reponse:
            roy.connaitre("animal")

    assert roy.memoire == memoire_avant
    reponse.assert_called_once_with(
        "Je ne connais encore aucune information sur animal. "
        "Tu peux me dire : retiens que animal = valeur"
    )

def tester_commandes_memoire_refusent_cle_vide():
    from commandes_memoire import (
        traiter_rappel_memoire,
        traiter_oubli_memoire,
        traiter_connaissance_memoire,
        traiter_question_memoire
    )
    from config import (
        formes_rappeler,
        formes_oublie,
        formes_connaitre,
        formes_question
    )

    cas = (
        (
            traiter_rappel_memoire,
            formes_rappeler[0],
            "rappeler"
        ),
        (
            traiter_oubli_memoire,
            formes_oublie[0],
            "oublier"
        ),
        (
            traiter_connaissance_memoire,
            formes_connaitre[0],
            "connaitre"
        ),
        (
            traiter_question_memoire,
            formes_question[0],
            "connaitre"
        )
    )

    roy = creer_roy_test(historique_actif=False)

    for gestionnaire, commande, methode in cas:
        with patch(
            "commandes_memoire.extraire_cle",
            return_value=""
        ):
            with patch.object(roy, methode) as action:
                with patch.object(roy, "repondre") as reponse:
                    resultat = gestionnaire(roy, commande)

        assert resultat is True, commande
        action.assert_not_called()
        reponse.assert_called_once()