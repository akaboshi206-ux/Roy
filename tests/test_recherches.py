from recherches import (
    creer_recherche,
    est_recherche_valide,
    est_liste_recherches_valide,
    ajouter_note,
    ajouter_source,
    formater_recherche,
    sauvegarder_recherches,
    charger_recherches
)


def tester_creation_recherche():
    recherche = creer_recherche("  Protection souple  ")

    assert recherche["titre"] == "Protection souple"
    assert recherche["notes"] == []
    assert recherche["sources"] == []
    assert est_recherche_valide(recherche)

    autre_recherche = creer_recherche("Énergie")
    recherche["notes"].append("Comparer les matériaux")

    assert autre_recherche["notes"] == []


def tester_refus_titre_recherche_vide():
    for titre in ("", "   "):
        try:
            creer_recherche(titre)
        except ValueError:
            pass
        else:
            raise AssertionError("Un titre vide a été accepté")


def tester_validation_recherche():
    assert est_recherche_valide({
        "titre": "Énergie",
        "notes": ["Comparer les rendements"],
        "sources": ["Une référence bibliographique"]
    })

    donnees_invalides = (
        None,
        {},
        {"titre": " ", "notes": [], "sources": []},
        {"titre": "Énergie", "notes": "texte", "sources": []},
        {"titre": "Énergie", "notes": [42], "sources": []},
        {"titre": "Énergie", "notes": [" "], "sources": []},
        {"titre": "Énergie", "notes": [], "sources": [None]},
        {"titre": "Énergie", "notes": [], "sources": [""]}
    )

    for donnees in donnees_invalides:
        assert not est_recherche_valide(donnees)


def tester_validation_liste_recherches():
    recherche = creer_recherche("Énergie")

    assert est_liste_recherches_valide([])
    assert est_liste_recherches_valide([recherche])
    assert not est_liste_recherches_valide(recherche)
    assert not est_liste_recherches_valide([recherche, {}])

def tester_ajout_note_recherche():
    recherche = creer_recherche("Protection souple")

    assert ajouter_note(
        recherche,
        "  Comparer les matériaux  "
    )
    assert recherche["notes"] == [
        "Comparer les matériaux"
    ]

    assert not ajouter_note(recherche, "")
    assert not ajouter_note(recherche, "   ")
    assert recherche["notes"] == [
        "Comparer les matériaux"
    ]
    assert est_recherche_valide(recherche)

def tester_ajout_source_recherche():
    recherche = creer_recherche("Énergie")

    assert ajouter_source(
        recherche,
        "  Article sur les rendements  "
    )
    assert recherche["sources"] == [
        "Article sur les rendements"
    ]

    assert not ajouter_source(
        recherche,
        "Article sur les rendements"
    )
    assert not ajouter_source(recherche, "")
    assert not ajouter_source(recherche, "   ")

    assert recherche["sources"] == [
        "Article sur les rendements"
    ]
    assert est_recherche_valide(recherche)

def tester_affichage_recherche():
    recherche = creer_recherche("Énergie")

    assert formater_recherche(recherche) == (
        "Recherche : Énergie\n\n"
        "Notes :\nAucune note.\n\n"
        "Sources :\nAucune source."
    )

    ajouter_note(recherche, "Comparer les rendements")
    ajouter_source(recherche, "Référence bibliographique")

    assert formater_recherche(recherche) == (
        "Recherche : Énergie\n\n"
        "Notes :\n1. Comparer les rendements\n\n"
        "Sources :\n1. Référence bibliographique"
    )

def tester_sauvegarde_recherches():
    import json
    from pathlib import Path
    from tempfile import TemporaryDirectory

    recherche = creer_recherche("Énergie")
    ajouter_note(recherche, "Comparer les rendements")
    ajouter_source(recherche, "Référence bibliographique")

    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "recherches.json"

        assert sauvegarder_recherches(
            str(chemin),
            [recherche]
        )

        contenu_initial = chemin.read_text(encoding="utf-8")
        assert json.loads(contenu_initial) == [recherche]

        assert not sauvegarder_recherches(
            str(chemin),
            [{"titre": "Incomplet"}]
        )
        assert chemin.read_text(
            encoding="utf-8"
        ) == contenu_initial

def tester_chargement_recherches():
    from pathlib import Path
    from tempfile import TemporaryDirectory

    recherche = creer_recherche("Énergie")
    ajouter_note(recherche, "Comparer les rendements")
    ajouter_source(recherche, "Référence bibliographique")

    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "recherches.json"

        assert sauvegarder_recherches(
            str(chemin),
            [recherche]
        )

        donnees, erreur, recuperation, erreur_reparation = (
            charger_recherches(str(chemin))
        )

        assert donnees == [recherche]
        assert erreur is None
        assert recuperation is False
        assert erreur_reparation is None

def tester_recuperation_recherches():
    import json
    from pathlib import Path
    from tempfile import TemporaryDirectory

    recherche = creer_recherche("Énergie")
    ajouter_note(recherche, "Comparer les rendements")

    with TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "recherches.json"
        sauvegarde = Path(f"{chemin}.bak")

        sauvegarde.write_text(
            json.dumps([recherche], ensure_ascii=False),
            encoding="utf-8"
        )

        chemin.write_text(
            "{invalide",
            encoding="utf-8"
        )

        donnees, erreur, recuperation, erreur_reparation = (
            charger_recherches(str(chemin))
        )

        assert donnees == [recherche]
        assert erreur is None
        assert recuperation is True
        assert erreur_reparation is None

        assert json.loads(
            chemin.read_text(encoding="utf-8")
        ) == [recherche]

        assert json.loads(
            sauvegarde.read_text(encoding="utf-8")
        ) == [recherche]

def tester_carnet_recherches_roy():
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)

        chemins = {
            "historique_actif": False,
            "fichier_historique": str(
                dossier_test / "historique.json"
            ),
            "fichier_memoire": str(
                dossier_test / "memoire.json"
            ),
            "fichier_taches": str(
                dossier_test / "taches.json"
            ),
            "fichier_recherches": str(
                dossier_test / "recherches.json"
            )
        }

        roy = Roy(**chemins)

        assert roy.recherches == []
        assert roy.recherches_sauvegardables is True

        recherche = creer_recherche("Énergie")
        ajouter_note(recherche, "Comparer les rendements")
        ajouter_source(recherche, "Référence bibliographique")

        roy.recherches.append(recherche)

        assert roy.sauvegarder_recherches() is True

        roy_recharge = Roy(**chemins)

        assert roy_recharge.recherches == [recherche]
        assert roy_recharge.recherches_sauvegardables is True

def tester_blocage_carnet_endommage_roy():
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)
        chemin = dossier_test / "recherches.json"
        contenu_endommage = "{invalide"

        chemin.write_text(
            contenu_endommage,
            encoding="utf-8"
        )

        roy = Roy(
            historique_actif=False,
            fichier_historique=str(
                dossier_test / "historique.json"
            ),
            fichier_memoire=str(
                dossier_test / "memoire.json"
            ),
            fichier_taches=str(
                dossier_test / "taches.json"
            ),
            fichier_recherches=str(chemin)
        )

        assert roy.recherches == []
        assert roy.recherches_sauvegardables is False
        assert roy.sauvegarder_recherches() is False

        assert chemin.read_text(
            encoding="utf-8"
        ) == contenu_endommage

        assert not Path(f"{chemin}.bak").exists()

def tester_ajout_recherche_roy():
    import json
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)
        chemin = dossier_test / "recherches.json"

        roy = Roy(
            historique_actif=False,
            fichier_historique=str(
                dossier_test / "historique.json"
            ),
            fichier_memoire=str(
                dossier_test / "memoire.json"
            ),
            fichier_taches=str(
                dossier_test / "taches.json"
            ),
            fichier_recherches=str(chemin)
        )

        assert roy.ajouter_recherche("  Énergie  ") is True

        attendu = [{
            "titre": "Énergie",
            "notes": [],
            "sources": []
        }]

        assert roy.recherches == attendu
        assert json.loads(
            chemin.read_text(encoding="utf-8")
        ) == attendu

        contenu_initial = chemin.read_text(
            encoding="utf-8"
        )

        assert roy.ajouter_recherche("   ") is False
        assert roy.recherches == attendu
        assert chemin.read_text(
            encoding="utf-8"
        ) == contenu_initial

def tester_commande_creation_recherche():
    import json
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)
        chemin = dossier_test / "recherches.json"

        roy = Roy(
            historique_actif=False,
            fichier_historique=str(
                dossier_test / "historique.json"
            ),
            fichier_memoire=str(
                dossier_test / "memoire.json"
            ),
            fichier_taches=str(
                dossier_test / "taches.json"
            ),
            fichier_recherches=str(chemin)
        )

        original = "crée une recherche : Énergie Solaire"

        assert roy.traiter_message(
            original.lower(),
            original
        ) is True

        attendu = [{
            "titre": "Énergie Solaire",
            "notes": [],
            "sources": []
        }]

        assert roy.recherches == attendu
        assert json.loads(
            chemin.read_text(encoding="utf-8")
        ) == attendu

        contenu_initial = chemin.read_text(
            encoding="utf-8"
        )

        assert roy.traiter_message(
            "crée une recherche",
            "crée une recherche"
        ) is True

        assert roy.recherches == attendu
        assert chemin.read_text(
            encoding="utf-8"
        ) == contenu_initial

def tester_commande_affichage_recherches():
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)

        roy = Roy(
            historique_actif=False,
            fichier_historique=str(
                dossier_test / "historique.json"
            ),
            fichier_memoire=str(
                dossier_test / "memoire.json"
            ),
            fichier_taches=str(
                dossier_test / "taches.json"
            ),
            fichier_recherches=str(
                dossier_test / "recherches.json"
            )
        )

        commande = "montre mes recherches"

        with patch.object(roy, "repondre") as reponse:
            assert roy.traiter_message(
                commande,
                commande
            ) is True

            reponse.assert_called_once_with(
                "Tu n'as aucune recherche enregistrée."
            )

        roy.recherches = [
            creer_recherche("Énergie"),
            creer_recherche("Matériaux")
        ]

        with patch.object(roy, "repondre") as reponse:
            assert roy.traiter_message(
                commande,
                commande
            ) is True

            reponse.assert_called_once_with(
                "Tes recherches :\n"
                "1. Énergie\n"
                "2. Matériaux"
            )

def tester_commande_affichage_recherche():
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)

        roy = Roy(
            historique_actif=False,
            fichier_historique=str(
                dossier_test / "historique.json"
            ),
            fichier_memoire=str(
                dossier_test / "memoire.json"
            ),
            fichier_taches=str(
                dossier_test / "taches.json"
            ),
            fichier_recherches=str(
                dossier_test / "recherches.json"
            )
        )

        recherche = creer_recherche("Énergie")
        ajouter_note(recherche, "Étudier le stockage.")
        ajouter_source(recherche, "Article de référence")
        roy.recherches = [recherche]

        with patch.object(roy, "repondre") as reponse:
            commande = "montre la recherche 1"

            assert roy.traiter_message(
                commande,
                commande
            ) is True

            reponse.assert_called_once_with(
                formater_recherche(recherche)
            )

        for numero in ("0", "-1", "2"):
            with patch.object(roy, "repondre") as reponse:
                commande = f"montre la recherche {numero}"

                assert roy.traiter_message(
                    commande,
                    commande
                ) is True

                reponse.assert_called_once_with(
                    "Numéro de recherche invalide."
                )

        with patch.object(roy, "repondre") as reponse:
            commande = "montre la recherche abc"

            assert roy.traiter_message(
                commande,
                commande
            ) is True

            reponse.assert_called_once_with(
                "Utilise le format : montre la recherche 1"
            )

def tester_commande_ajout_note_recherche():
    import json
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)
        chemin = dossier_test / "recherches.json"

        roy = Roy(
            historique_actif=False,
            fichier_historique=str(
                dossier_test / "historique.json"
            ),
            fichier_memoire=str(
                dossier_test / "memoire.json"
            ),
            fichier_taches=str(
                dossier_test / "taches.json"
            ),
            fichier_recherches=str(chemin)
        )

        roy.ajouter_recherche("Énergie")

        commande = (
            "note recherche 1 : "
            "Hypothèse : améliorer le stockage."
        )

        assert roy.traiter_message(
            commande.lower(),
            commande
        ) is True

        notes_attendues = [
            "Hypothèse : améliorer le stockage."
        ]

        assert roy.recherches[0]["notes"] == notes_attendues

        donnees = json.loads(
            chemin.read_text(encoding="utf-8")
        )

        assert donnees[0]["notes"] == notes_attendues

        contenu_avant = chemin.read_bytes()

        with patch(
            "roy.sauvegarder_carnet",
            return_value=False
        ):
            assert roy.ajouter_note_recherche(
                1,
                "Note à annuler."
            ) is False

        assert roy.recherches[0]["notes"] == notes_attendues
        assert chemin.read_bytes() == contenu_avant

        assert roy.ajouter_note_recherche(1, "   ") is False
        assert roy.ajouter_note_recherche(0, "Note") is False
        assert roy.ajouter_note_recherche(2, "Note") is False

        assert roy.recherches[0]["notes"] == notes_attendues
        assert chemin.read_bytes() == contenu_avant

def tester_commande_ajout_source_recherche():
    import json
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)
        chemin = dossier_test / "recherches.json"

        roy = Roy(
            historique_actif=False,
            fichier_historique=str(
                dossier_test / "historique.json"
            ),
            fichier_memoire=str(
                dossier_test / "memoire.json"
            ),
            fichier_taches=str(
                dossier_test / "taches.json"
            ),
            fichier_recherches=str(chemin)
        )

        roy.ajouter_recherche("Énergie")

        source = "https://exemple.org/Article"
        commande = f"source recherche 1 : {source}"

        assert roy.traiter_message(
            commande.lower(),
            commande
        ) is True

        assert roy.recherches[0]["sources"] == [source]

        donnees = json.loads(
            chemin.read_text(encoding="utf-8")
        )

        assert donnees[0]["sources"] == [source]

        contenu_avant = chemin.read_bytes()

        assert roy.ajouter_source_recherche(
            1,
            source
        ) is False

        with patch(
            "roy.sauvegarder_carnet",
            return_value=False
        ):
            assert roy.ajouter_source_recherche(
                1,
                "Autre référence"
            ) is False

        assert roy.ajouter_source_recherche(
            1,
            "   "
        ) is False

        assert roy.ajouter_source_recherche(
            0,
            "Référence"
        ) is False

        assert roy.recherches[0]["sources"] == [source]
        assert chemin.read_bytes() == contenu_avant

def tester_commande_recherche_par_mot():
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)

        roy = Roy(
            historique_actif=False,
            fichier_historique=str(
                dossier_test / "historique.json"
            ),
            fichier_memoire=str(
                dossier_test / "memoire.json"
            ),
            fichier_taches=str(
                dossier_test / "taches.json"
            ),
            fichier_recherches=str(
                dossier_test / "recherches.json"
            )
        )

        energie = creer_recherche("Énergie")
        materiaux = creer_recherche("Matériaux")
        transports = creer_recherche("Transports")

        ajouter_note(
            materiaux,
            "Étudier le STOCKAGE."
        )
        ajouter_source(
            transports,
            "Article sur le stockage"
        )

        roy.recherches = [
            energie,
            materiaux,
            transports
        ]

        cas = (
            (
                "cherche recherche stockage",
                "Recherches trouvées :\n"
                "2. Matériaux\n"
                "3. Transports"
            ),
            (
                "cherche recherche ÉNERGIE",
                "Recherches trouvées :\n"
                "1. Énergie"
            ),
            (
                "cherche recherche introuvable",
                "Aucune recherche trouvée."
            ),
            (
                "cherche recherche",
                "Indique un mot à rechercher."
            )
        )

        for commande, resultat_attendu in cas:
            with patch.object(roy, "repondre") as reponse:
                assert roy.traiter_message(
                    commande.lower(),
                    commande
                ) is True

                reponse.assert_called_once_with(
                    resultat_attendu
                )

def tester_commandes_recherche_invalides():
    from copy import deepcopy
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)
        chemin = dossier_test / "recherches.json"

        roy = Roy(
            historique_actif=False,
            fichier_historique=str(
                dossier_test / "historique.json"
            ),
            fichier_memoire=str(
                dossier_test / "memoire.json"
            ),
            fichier_taches=str(
                dossier_test / "taches.json"
            ),
            fichier_recherches=str(chemin)
        )

        assert roy.ajouter_recherche("Énergie") is True

        recherches_avant = deepcopy(roy.recherches)
        fichier_avant = chemin.read_bytes()

        cas = (
            (
                "note recherche 1",
                "Utilise le format : note recherche 1 : texte"
            ),
            (
                "note recherche abc : texte",
                "Utilise le format : note recherche 1 : texte"
            ),
            (
                "note recherche 1 :   ",
                "La note ne peut pas être vide."
            ),
            (
                "note recherche 0 : texte",
                "Numéro de recherche invalide."
            ),
            (
                "source recherche 1",
                "Utilise le format : source recherche 1 : référence"
            ),
            (
                "source recherche abc : référence",
                "Utilise le format : source recherche 1 : référence"
            ),
            (
                "source recherche 1 :   ",
                "La source est vide ou déjà enregistrée."
            ),
            (
                "source recherche 2 : référence",
                "Numéro de recherche invalide."
            )
        )

        for commande, resultat_attendu in cas:
            with patch.object(roy, "repondre") as reponse:
                assert roy.traiter_message(
                    commande.lower().strip(),
                    commande
                ) is True

                reponse.assert_called_once_with(
                    resultat_attendu
                )

            assert roy.recherches == recherches_avant
            assert chemin.read_bytes() == fichier_avant

def tester_refus_ajout_recherche_fichier_endommage():
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)
        chemin = dossier_test / "recherches.json"

        chemin.write_text(
            "{contenu invalide",
            encoding="utf-8"
        )

        contenu_avant = chemin.read_bytes()

        roy = Roy(
            historique_actif=False,
            fichier_historique=str(
                dossier_test / "historique.json"
            ),
            fichier_memoire=str(
                dossier_test / "memoire.json"
            ),
            fichier_taches=str(
                dossier_test / "taches.json"
            ),
            fichier_recherches=str(chemin)
        )

        assert roy.recherches_sauvegardables is False

        assert roy.ajouter_recherche(
            "Énergie"
        ) is False

        assert roy.recherches == []
        assert chemin.read_bytes() == contenu_avant

        assert not Path(
            f"{chemin}.bak"
        ).exists()

def tester_recherches_recuperees_reparation_impossible():
    import json
    from copy import deepcopy
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)
        chemin = dossier_test / "recherches.json"
        sauvegarde = Path(f"{chemin}.bak")

        recherches = [creer_recherche("Énergie")]

        chemin.write_text(
            "{contenu invalide",
            encoding="utf-8"
        )

        sauvegarde.write_text(
            json.dumps(recherches, ensure_ascii=False),
            encoding="utf-8"
        )

        fichier_avant = chemin.read_bytes()
        sauvegarde_avant = sauvegarde.read_bytes()

        with patch(
            "outils.shutil.copy2",
            side_effect=OSError("Réparation impossible")
        ):
            roy = Roy(
                historique_actif=False,
                fichier_historique=str(
                    dossier_test / "historique.json"
                ),
                fichier_memoire=str(
                    dossier_test / "memoire.json"
                ),
                fichier_taches=str(
                    dossier_test / "taches.json"
                ),
                fichier_recherches=str(chemin)
            )

        assert roy.recherches == recherches
        assert roy.recherches_sauvegardables is False

        recherches_avant = deepcopy(roy.recherches)

        assert roy.ajouter_note_recherche(
            1,
            "Note à annuler."
        ) is False

        assert roy.ajouter_source_recherche(
            1,
            "Source à annuler."
        ) is False

        assert roy.recherches == recherches_avant
        assert chemin.read_bytes() == fichier_avant
        assert sauvegarde.read_bytes() == sauvegarde_avant

def tester_commande_reparation_recherches():
    import json
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)
        chemin = dossier_test / "recherches.json"
        sauvegarde = Path(f"{chemin}.bak")
        recherches = [creer_recherche("Énergie")]

        chemin.write_text(
            "{contenu invalide",
            encoding="utf-8"
        )
        sauvegarde.write_text(
            json.dumps(recherches, ensure_ascii=False),
            encoding="utf-8"
        )
        sauvegarde_avant = sauvegarde.read_bytes()

        with patch(
            "outils.shutil.copy2",
            side_effect=OSError("Réparation impossible")
        ):
            roy = Roy(
                historique_actif=False,
                fichier_historique=str(
                    dossier_test / "historique.json"
                ),
                fichier_memoire=str(
                    dossier_test / "memoire.json"
                ),
                fichier_taches=str(
                    dossier_test / "taches.json"
                ),
                fichier_recherches=str(chemin)
            )

        assert roy.recherches_sauvegardables is False

        assert roy.traiter_message(
            "répare mes recherches",
            "répare mes recherches"
        ) is True

        assert roy.recherches_sauvegardables is True
        assert roy.recherches == recherches
        assert json.loads(
            chemin.read_text(encoding="utf-8")
        ) == recherches
        assert sauvegarde.read_bytes() == sauvegarde_avant

        assert roy.ajouter_note_recherche(
            1,
            "Note après réparation."
        ) is True

        assert json.loads(
            chemin.read_text(encoding="utf-8")
        )[0]["notes"] == ["Note après réparation."]

def tester_echec_reparation_recherches():
    import json
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    from roy import Roy

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)
        chemin = dossier_test / "recherches.json"
        sauvegarde = Path(f"{chemin}.bak")
        recherches = [creer_recherche("Énergie")]

        chemin.write_text(
            "{contenu invalide",
            encoding="utf-8"
        )
        sauvegarde.write_text(
            json.dumps(recherches, ensure_ascii=False),
            encoding="utf-8"
        )

        fichier_avant = chemin.read_bytes()
        sauvegarde_avant = sauvegarde.read_bytes()

        with patch(
            "outils.shutil.copy2",
            side_effect=OSError("Fichier inaccessible")
        ):
            roy = Roy(
                historique_actif=False,
                fichier_historique=str(
                    dossier_test / "historique.json"
                ),
                fichier_memoire=str(
                    dossier_test / "memoire.json"
                ),
                fichier_taches=str(
                    dossier_test / "taches.json"
                ),
                fichier_recherches=str(chemin)
            )

            with patch(
                "roy.reparer_json_depuis_sauvegarde",
                return_value=OSError("Fichier inaccessible")
            ):
                assert roy.reparer_recherches() is False

        assert roy.recherches_sauvegardables is False
        assert roy.recherches == recherches
        assert roy.ajouter_note_recherche(
            1,
            "Note à annuler."
        ) is False
        assert roy.recherches == recherches
        assert chemin.read_bytes() == fichier_avant
        assert sauvegarde.read_bytes() == sauvegarde_avant

def tester_export_recherche():
    from copy import deepcopy
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from roy import Roy
    from recherches import formater_recherche

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)

        roy = Roy(
            historique_actif=False,
            fichier_historique=str(
                dossier_test / "historique.json"
            ),
            fichier_memoire=str(
                dossier_test / "memoire.json"
            ),
            fichier_taches=str(
                dossier_test / "taches.json"
            ),
            fichier_recherches=str(
                dossier_test / "recherches.json"
            )
        )

        roy.recherches = [
            {
                "titre": "Stockage d'énergie",
                "notes": ["Comparer : batteries et hydrogène."],
                "sources": ["https://Exemple.org/Étude"]
            }
        ]
        recherches_avant = deepcopy(roy.recherches)
        chemin = dossier_test / "export.txt"

        assert roy.exporter_recherche(
            1,
            str(chemin)
        ) is True

        contenu = chemin.read_text(encoding="utf-8")

        assert contenu == (
            formater_recherche(roy.recherches[0]) + "\n"
        )
        assert "Stockage d'énergie" in contenu
        assert "Comparer : batteries et hydrogène." in contenu
        assert "https://Exemple.org/Étude" in contenu

        chemin.write_text(
            "Contenu à conserver.",
            encoding="utf-8"
        )

        assert roy.exporter_recherche(
            1,
            str(chemin)
        ) is False

        assert chemin.read_text(
            encoding="utf-8"
        ) == "Contenu à conserver."

        for numero in (0, -1, 2):
            chemin_invalide = dossier_test / f"invalide_{numero}.txt"

            assert roy.exporter_recherche(
                numero,
                str(chemin_invalide)
            ) is False

            assert not chemin_invalide.exists()

        assert roy.recherches == recherches_avant

def tester_export_recherche_automatique():
    from copy import deepcopy
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from roy import Roy
    from recherches import formater_recherche

    with TemporaryDirectory() as dossier:
        dossier_test = Path(dossier)

        roy = Roy(
            historique_actif=False,
            fichier_historique=str(
                dossier_test / "historique.json"
            ),
            fichier_memoire=str(
                dossier_test / "memoire.json"
            ),
            fichier_taches=str(
                dossier_test / "taches.json"
            ),
            fichier_recherches=str(
                dossier_test / "recherches.json"
            )
        )

        roy.recherches = [
            {
                "titre": "Énergie",
                "notes": ["Comparer les moyens de stockage."],
                "sources": ["Référence de démonstration"]
            }
        ]

        recherches_avant = deepcopy(roy.recherches)
        dossier_exports = dossier_test / "exports"

        assert not dossier_exports.exists()

        assert roy.traiter_message(
            "export recherche 1",
            "export recherche 1"
        ) is True

        fichiers = list(
            dossier_exports.glob("recherche_1_*.txt")
        )

        assert len(fichiers) == 1
        assert fichiers[0].read_text(
            encoding="utf-8"
        ) == formater_recherche(roy.recherches[0]) + "\n"

        assert roy.recherches == recherches_avant
        assert not list(
            dossier_test.glob("recherche_*.txt")
        )