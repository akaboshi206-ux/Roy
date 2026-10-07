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