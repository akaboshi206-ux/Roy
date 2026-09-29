import json

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from roy import Roy

from tests.aides import (
    creer_roy_test,
    dossier_tests,
    recharger_roy_test
)

from taches import (
    est_tache_valide,
    rechercher_taches,
    calculer_statistiques_taches,
    date_echeance_valide,
    changer_echeance
)

def tester_validation_tache():
    assert est_tache_valide({
        "description": "travailler sur Roy",
        "terminee": False,
        "priorite": "normale"
    }) is True

    assert est_tache_valide({
        "description": "ancienne tâche",
        "terminee": False
    }) is True

    assert est_tache_valide({
        "description": 42,
        "terminee": False
    }) is False

    assert est_tache_valide({
        "description": "tâche invalide",
        "terminee": "non"
    }) is False

    assert est_tache_valide({
        "description": "tâche invalide",
        "terminee": False,
        "priorite": "urgente"
    }) is False

    assert est_tache_valide(
        "pas une tâche"
    ) is False


def tester_echeances_taches():
    assert date_echeance_valide(
        "2026-10-05"
    ) is True

    assert date_echeance_valide(
        "2026-02-30"
    ) is False

    assert date_echeance_valide(
        "05-10-2026"
    ) is False

    taches = [
        {
            "description": "Apprendre Python",
            "terminee": False,
            "priorite": "haute",
            "echeance": None
        }
    ]

    assert changer_echeance(
        taches,
        1,
        "2026-10-05"
    ) is True

    assert (
        taches[0]["echeance"]
        == "2026-10-05"
    )

    assert changer_echeance(
        taches,
        1,
        "2026-02-30"
    ) is False

    assert (
        taches[0]["echeance"]
        == "2026-10-05"
    )

def tester_recherche_taches():
    taches = [
        {
            "description": "Apprendre Python",
            "terminee": False,
            "priorite": "haute"
        },
        {
            "description": "Acheter du lait",
            "terminee": False,
            "priorite": "normale"
        },
        {
            "description": "Continuer le projet Python",
            "terminee": True,
            "priorite": "basse"
        }
    ]

    resultats = rechercher_taches(
        taches,
        "PYTHON"
    )

    assert len(resultats) == 2
    assert (
        resultats[0]["description"]
        == "Apprendre Python"
    )
    assert (
        resultats[1]["description"]
        == "Continuer le projet Python"
    )

    assert rechercher_taches(
        taches,
        "Java"
    ) == []

    assert rechercher_taches(
        taches,
        "   "
    ) == []


def tester_statistiques_taches():
    taches = [
        {
            "description": "Apprendre Python",
            "terminee": False,
            "priorite": "haute"
        },
        {
            "description": "Acheter du lait",
            "terminee": True,
            "priorite": "normale"
        },
        {
            "description": "Faire du sport",
            "terminee": False,
            "priorite": "basse"
        }
    ]

    statistiques = calculer_statistiques_taches(
        taches
    )

    assert statistiques == {
        "total": 3,
        "a_faire": 2,
        "terminees": 1,
        "pourcentage": 33,
        "hautes": 1,
        "normales": 1,
        "basses": 1
    }

    assert calculer_statistiques_taches([]) == {
        "total": 0,
        "a_faire": 0,
        "terminees": 0,
        "pourcentage": 0,
        "hautes": 0,
        "normales": 0,
        "basses": 0
    }

def tester_commande_recherche_tache():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.taches = [
        {
            "description": "Apprendre Python",
            "terminee": False,
            "priorite": "haute"
        },
        {
            "description": "Acheter du lait",
            "terminee": False,
            "priorite": "normale"
        },
        {
            "description": "Continuer Python",
            "terminee": True,
            "priorite": "basse"
        }
    ]

    sortie = StringIO()

    with redirect_stdout(sortie):
        assert roy.traiter_message(
            "recherche tâche python",
            "recherche tâche python"
        ) is True

    texte = sortie.getvalue()

    assert "2 tâche(s) trouvée(s)" in texte
    assert "Apprendre Python" in texte
    assert "Continuer Python" in texte
    assert "Acheter du lait" not in texte


def tester_commande_statistiques_taches():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.taches = [
        {
            "description": "Apprendre Python",
            "terminee": False,
            "priorite": "haute"
        },
        {
            "description": "Acheter du lait",
            "terminee": True,
            "priorite": "normale"
        },
        {
            "description": "Faire du sport",
            "terminee": False,
            "priorite": "basse"
        }
    ]

    sortie = StringIO()

    with redirect_stdout(sortie):
        assert roy.traiter_message(
            "statistiques tâches",
            "statistiques tâches"
        ) is True

    texte = sortie.getvalue()

    assert "Statistiques des tâches" in texte
    assert "Tâches totales : 3" in texte
    assert "À faire : 2" in texte
    assert "Terminées : 1" in texte
    assert "Progression : 33 %" in texte
    assert "Priorité haute : 1" in texte
    assert "Priorité normale : 1" in texte
    assert "Priorité basse : 1" in texte

def tester_tri_taches_par_priorite():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.taches = [
        {
            "description": "tâche basse",
            "terminee": False,
            "priorite": "basse"
        },
        {
            "description": "tâche haute",
            "terminee": False,
            "priorite": "haute"
        },
        {
            "description": "tâche normale",
            "terminee": False,
            "priorite": "normale"
        }
    ]

    assert roy.traiter_message(
        "trie mes tâches par priorité",
        "trie mes tâches par priorité"
    ) is True

    assert [
        tache["priorite"]
        for tache in roy.taches
    ] == [
        "haute",
        "normale",
        "basse"
    ]

    roy = recharger_roy_test(roy)

    assert [
        tache["priorite"]
        for tache in roy.taches
    ] == [
        "haute",
        "normale",
        "basse"
    ]


def tester_commande_echeance_tache():
    roy = creer_roy_test(
        historique_actif=False
    )

    assert roy.traiter_message(
        "ajoute une tâche : Apprendre Python",
        "ajoute une tâche : Apprendre Python"
    ) is True

    assert roy.traiter_message(
        "échéance tâche 1 : 2026-10-05",
        "échéance tâche 1 : 2026-10-05"
    ) is True

    assert (
        roy.taches[0]["echeance"]
        == "2026-10-05"
    )

    roy = recharger_roy_test(roy)

    assert (
        roy.taches[0]["echeance"]
        == "2026-10-05"
    )

    assert roy.traiter_message(
        "échéance tâche 1 : 2026-02-30",
        "échéance tâche 1 : 2026-02-30"
    ) is True

    assert (
        roy.taches[0]["echeance"]
        == "2026-10-05"
    )

    assert est_tache_valide(
        roy.taches[0]
    ) is True

    tache_invalide = roy.taches[0].copy()
    tache_invalide["echeance"] = "2026-02-30"

    assert est_tache_valide(
        tache_invalide
    ) is False

    ancienne_tache = {
        "description": "Ancienne tâche",
        "terminee": False,
        "priorite": "normale"
    }

    assert est_tache_valide(
        ancienne_tache
    ) is True

def tester_chargement_priorites_taches():
    with TemporaryDirectory() as dossier:
        chemin_taches = (
            Path(dossier) / "taches_test.json"
        )
        chemin_memoire = (
            Path(dossier) / "memoire_test.json"
        )

        anciennes_taches = [
            {
                "description": "ancienne tâche",
                "terminee": False
            }
        ]

        chemin_taches.write_text(
            json.dumps(
                anciennes_taches,
                ensure_ascii=False,
                indent=4
            ),
            encoding="utf-8"
        )

        roy = Roy(
            historique_actif=False,
            fichier_memoire=str(chemin_memoire),
            fichier_taches=str(chemin_taches)
        )

        assert (
            roy.taches[0]["priorite"]
            == "normale"
        )
        assert roy.taches_sauvegardables is True

        taches_invalides = [
            {
                "description": "tâche invalide",
                "terminee": False,
                "priorite": "urgente"
            }
        ]

        chemin_taches.write_text(
            json.dumps(
                taches_invalides,
                ensure_ascii=False,
                indent=4
            ),
            encoding="utf-8"
        )

        roy_invalide = Roy(
            historique_actif=False,
            fichier_memoire=str(chemin_memoire),
            fichier_taches=str(chemin_taches)
        )

        assert roy_invalide.taches == []
        assert (
            roy_invalide.taches_sauvegardables
            is False
        )


def tester_filtrage_taches():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.taches = [
        {
            "description": "tâche normale",
            "terminee": False,
            "priorite": "normale"
        },
        {
            "description": "tâche haute",
            "terminee": False,
            "priorite": "haute"
        },
        {
            "description": "tâche basse",
            "terminee": True,
            "priorite": "basse"
        }
    ]

    assert roy.traiter_message(
        "montre mes tâches de priorité haute",
        "montre mes tâches de priorité haute"
    ) is True

    reponse = roy.historique[-1]["content"]

    assert "2. ○ [haute] tâche haute" in reponse
    assert "tâche normale" not in reponse
    assert "tâche basse" not in reponse

    assert roy.traiter_message(
        "montre mes tâches à faire",
        "montre mes tâches à faire"
    ) is True

    reponse = roy.historique[-1]["content"]

    assert (
        "1. ○ [normale] tâche normale"
        in reponse
    )
    assert "2. ○ [haute] tâche haute" in reponse
    assert "tâche basse" not in reponse

    assert roy.traiter_message(
        "montre mes tâches terminées",
        "montre mes tâches terminées"
    ) is True

    reponse = roy.historique[-1]["content"]

    assert reponse == "3. ✓ [basse] tâche basse"

    assert roy.traiter_message(
        "montre mes tâches de priorité urgente",
        "montre mes tâches de priorité urgente"
    ) is True

    assert roy.historique[-1]["content"] == (
        "Choisis une priorité : "
        "basse, normale ou haute."
    )

def tester_gestion_taches():
    roy = creer_roy_test(
        historique_actif=False
    )

    assert roy.traiter_message(
        "ajoute une tâche : travailler sur Roy",
        "ajoute une tâche : travailler sur Roy"
    ) is True

    assert len(roy.taches) == 1

    assert roy.taches[0] == {
        "description": "travailler sur Roy",
        "terminee": False,
        "priorite": "normale",
        "echeance": None
    }

    roy = recharger_roy_test(roy)

    assert len(roy.taches) == 1
    assert (
        roy.taches[0]["description"]
        == "travailler sur Roy"
    )
    assert (
        roy.taches[0]["priorite"]
        == "normale"
    )

    assert roy.traiter_message(
        "priorité tâche 1 : haute",
        "priorité tâche 1 : haute"
    ) is True

    assert (
        roy.taches[0]["priorite"]
        == "haute"
    )

    roy = recharger_roy_test(roy)

    assert (
        roy.taches[0]["priorite"]
        == "haute"
    )

    assert roy.traiter_message(
        "termine la tâche 1",
        "termine la tâche 1"
    ) is True

    assert roy.taches[0]["terminee"] is True

    roy = recharger_roy_test(roy)

    assert roy.taches[0]["terminee"] is True
    assert (
        roy.taches[0]["priorite"]
        == "haute"
    )

    assert roy.traiter_message(
        "rouvre la tâche 1",
        "rouvre la tâche 1"
    ) is True

    assert roy.taches[0]["terminee"] is False

    roy = recharger_roy_test(roy)

    assert roy.taches[0]["terminee"] is False
    assert (
        roy.taches[0]["priorite"]
        == "haute"
    )

    assert roy.traiter_message(
        "modifie la tâche 1 : travailler sur Python",
        "modifie la tâche 1 : travailler sur Python"
    ) is True

    assert (
        roy.taches[0]["description"]
        == "travailler sur Python"
    )
    assert roy.taches[0]["terminee"] is False
    assert (
        roy.taches[0]["priorite"]
        == "haute"
    )

    roy = recharger_roy_test(roy)

    assert (
        roy.taches[0]["description"]
        == "travailler sur Python"
    )
    assert roy.taches[0]["terminee"] is False
    assert (
        roy.taches[0]["priorite"]
        == "haute"
    )

    assert roy.traiter_message(
        "supprime la tâche 1",
        "supprime la tâche 1"
    ) is True

    assert roy.taches == []

    roy = recharger_roy_test(roy)

    assert roy.taches == []

def tester_chargement_taches_json():
    fichier_taches = Path(
        dossier_tests.name
    ) / "taches_chargement.json"

    fichier_taches.write_text(
        json.dumps(
            [
                {
                    "description": "Continuer Roy",
                    "terminee": False
                }
            ]
        ),
        encoding="utf-8"
    )

    roy = creer_roy_test(
        historique_actif=False,
        fichier_taches=str(fichier_taches)
    )

    assert roy.taches == [
        {
            "description": "Continuer Roy",
            "terminee": False,
            "priorite": "normale",
            "echeance": None
        }
    ]
    assert roy.taches_sauvegardables is True