from recherches import (
    creer_recherche,
    est_recherche_valide,
    est_liste_recherches_valide,
    ajouter_note,
    ajouter_source,
    formater_recherche,
    sauvegarder_recherches
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