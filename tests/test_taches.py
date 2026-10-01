import json

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import date

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
    changer_echeance,
    tache_en_retard,
    tache_pour_aujourdhui,
    filtrer_taches_en_retard,
    tache_a_venir,
    formater_taches,
    convertir_echeance_en_date,
    trier_taches_par_echeance,
    retirer_echeance,
    Tache
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

def tester_conversion_echeance_en_date():
    assert convertir_echeance_en_date(
        "2026-10-05"
    ) == date(2026, 10, 5)

    assert convertir_echeance_en_date(
        "date incorrecte"
    ) is None

    assert convertir_echeance_en_date(
        None
    ) is None

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
            "priorite": "haute",
            "echeance": None
        },
        {
            "description": "Acheter du lait",
            "terminee": True,
            "priorite": "normale",
            "echeance": None
        },
        {
            "description": "Faire du sport",
            "terminee": False,
            "priorite": "basse",
            "echeance": None
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
        "basses": 1,
        "en_retard": 0,
        "pour_aujourdhui": 0,
        "a_venir": 0
    }

    assert calculer_statistiques_taches([]) == {
        "total": 0,
        "a_faire": 0,
        "terminees": 0,
        "pourcentage": 0,
        "hautes": 0,
        "normales": 0,
        "basses": 0,
        "en_retard": 0,
        "pour_aujourdhui": 0,
        "a_venir": 0
    }

def tester_statistiques_echeances():
    taches = [
        {
            "description": "Tâche en retard",
            "terminee": False,
            "priorite": "haute",
            "echeance": "2026-09-30"
        },
        {
            "description": "Tâche du jour",
            "terminee": False,
            "priorite": "normale",
            "echeance": "2026-10-01"
        },
        {
            "description": "Tâche à venir",
            "terminee": False,
            "priorite": "basse",
            "echeance": "2026-10-02"
        }
    ]

    statistiques = calculer_statistiques_taches(
        taches,
        date(2026, 10, 1)
    )

    assert statistiques["en_retard"] == 1
    assert statistiques["pour_aujourdhui"] == 1
    assert statistiques["a_venir"] == 1

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

def tester_tri_taches_par_echeance():
    taches = [
        {
            "description": "Sans échéance",
            "terminee": False,
            "priorite": "normale",
            "echeance": None
        },
        {
            "description": "Tâche future",
            "terminee": False,
            "priorite": "haute",
            "echeance": "2026-10-10"
        },
        {
            "description": "Tâche proche",
            "terminee": False,
            "priorite": "basse",
            "echeance": "2026-10-05"
        }
    ]

    trier_taches_par_echeance(taches)

    assert [
        tache["description"]
        for tache in taches
    ] == [
        "Tâche proche",
        "Tâche future",
        "Sans échéance"
    ]

def tester_commande_tri_taches_par_echeance():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.taches = [
        {
            "description": "Sans échéance",
            "terminee": False,
            "priorite": "normale",
            "echeance": None
        },
        {
            "description": "Tâche future",
            "terminee": False,
            "priorite": "haute",
            "echeance": "2026-10-10"
        },
        {
            "description": "Tâche proche",
            "terminee": False,
            "priorite": "basse",
            "echeance": "2026-10-05"
        }
    ]

    resultat = roy.traiter_message(
        "trie mes tâches par échéance",
        "trie mes tâches par échéance"
    )

    assert resultat is True

    assert [
        tache["description"]
        for tache in roy.taches
    ] == [
        "Tâche proche",
        "Tâche future",
        "Sans échéance"
    ]

    reponse = roy.historique[-1]["content"]

    assert "Tâches triées par échéance." in reponse

def tester_annulation_tri_taches_par_echeance():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.taches = [
        {
            "description": "Sans échéance",
            "terminee": False,
            "priorite": "normale",
            "echeance": None
        },
        {
            "description": "Tâche future",
            "terminee": False,
            "priorite": "haute",
            "echeance": "2026-10-10"
        },
        {
            "description": "Tâche proche",
            "terminee": False,
            "priorite": "basse",
            "echeance": "2026-10-05"
        }
    ]

    ordre_initial = [
        tache["description"]
        for tache in roy.taches
    ]

    roy.sauvegarder_taches = lambda: False

    resultat = roy.traiter_message(
        "trie mes tâches par échéance",
        "trie mes tâches par échéance"
    )

    assert resultat is True

    nouvel_ordre = [
        tache["description"]
        for tache in roy.taches
    ]

    assert nouvel_ordre == ordre_initial

    reponse = roy.historique[-1]["content"]

    assert (
        "Le tri des tâches a été annulé."
        in reponse
    )

def tester_retrait_echeance():
    taches: list[Tache] = [
        {
            "description": "Expérience",
            "terminee": False,
            "priorite": "haute",
            "echeance": "2026-10-05"
        }
    ]

    assert retirer_echeance(
        taches,
        1
    ) is True

    assert taches[0]["echeance"] is None

    assert retirer_echeance(
        taches,
        0
    ) is False

    assert retirer_echeance(
        taches,
        2
    ) is False

def tester_commande_retrait_echeance():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.taches = [
        {
            "description": "Expérience",
            "terminee": False,
            "priorite": "haute",
            "echeance": "2026-10-05"
        }
    ]

    resultat = roy.traiter_message(
        "retire l'échéance de la tâche 1",
        "retire l'échéance de la tâche 1"
    )

    assert resultat is True
    assert roy.taches[0]["echeance"] is None

    reponse = roy.historique[-1]["content"]

    assert "Échéance retirée." in reponse

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

def tester_tache_a_venir():
    date_reference = date(2026, 10, 1)

    assert tache_a_venir(
        {
            "description": "Tâche future",
            "terminee": False,
            "priorite": "haute",
            "echeance": "2026-10-02"
        },
        date_reference
    ) is True

    assert tache_a_venir(
        {
            "description": "Tâche du jour",
            "terminee": False,
            "priorite": "normale",
            "echeance": "2026-10-01"
        },
        date_reference
    ) is False

    assert tache_a_venir(
        {
            "description": "Tâche passée",
            "terminee": False,
            "priorite": "basse",
            "echeance": "2026-09-30"
        },
        date_reference
    ) is False

def tester_formatage_taches_a_venir():
    taches = [
        {
            "description": "Ancienne tâche",
            "terminee": False,
            "priorite": "normale",
            "echeance": "2000-01-01"
        },
        {
            "description": "Tâche future",
            "terminee": False,
            "priorite": "haute",
            "echeance": "2999-01-01"
        },
        {
            "description": "Tâche future terminée",
            "terminee": True,
            "priorite": "basse",
            "echeance": "2999-01-01"
        }
    ]

    resultat = formater_taches(
        taches,
        a_venir=True
    )

    assert "2." in resultat
    assert "Tâche future" in resultat
    assert "Ancienne tâche" not in resultat
    assert "Tâche future terminée" not in resultat

    resultat_vide = formater_taches(
        [taches[0]],
        a_venir=True
    )

    assert resultat_vide == (
        "Tu n'as aucune tâche à venir."
    )

def tester_commande_taches_a_venir():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.taches = [
        {
            "description": "Ancienne tâche",
            "terminee": False,
            "priorite": "normale",
            "echeance": "2000-01-01"
        },
        {
            "description": "Tâche future",
            "terminee": False,
            "priorite": "haute",
            "echeance": "2999-01-01"
        },
        {
            "description": "Tâche future terminée",
            "terminee": True,
            "priorite": "basse",
            "echeance": "2999-01-01"
        }
    ]

    resultat = roy.traiter_message(
        "montre mes tâches à venir",
        "montre mes tâches à venir"
    )

    assert resultat is True

    reponse = roy.historique[-1]["content"]

    assert "2." in reponse
    assert "Tâche future" in reponse
    assert "Ancienne tâche" not in reponse
    assert "Tâche future terminée" not in reponse

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

def tester_tache_en_retard():
    date_reference = date(
        2026,
        9,
        30
    )

    tache_retard = {
        "description": "Réviser Python",
        "terminee": False,
        "priorite": "haute",
        "echeance": "2026-09-29"
    }

    tache_aujourdhui = {
        "description": "Faire du sport",
        "terminee": False,
        "priorite": "normale",
        "echeance": "2026-09-30"
    }

    tache_terminee = {
        "description": "Acheter du lait",
        "terminee": True,
        "priorite": "basse",
        "echeance": "2026-09-20"
    }

    tache_sans_echeance = {
        "description": "Ranger le bureau",
        "terminee": False,
        "priorite": "normale",
        "echeance": None
    }

    assert tache_en_retard(
        tache_retard,
        date_reference
    ) is True

    assert tache_en_retard(
        tache_aujourdhui,
        date_reference
    ) is False

    assert tache_en_retard(
        tache_terminee,
        date_reference
    ) is False

    assert tache_en_retard(
        tache_sans_echeance,
        date_reference
    ) is False

def tester_filtrage_taches_en_retard():
    taches = [
        {
            "description": "Tâche en retard",
            "terminee": False,
            "priorite": "haute",
            "echeance": "2026-09-20"
        },
        {
            "description": "Tâche future",
            "terminee": False,
            "priorite": "normale",
            "echeance": "2026-10-05"
        },
        {
            "description": "Tâche déjà terminée",
            "terminee": True,
            "priorite": "basse",
            "echeance": "2026-09-10"
        }
    ]

    resultat = filtrer_taches_en_retard(
        taches,
        date(2026, 9, 30)
    )

    assert len(resultat) == 1
    assert (
        resultat[0]["description"]
        == "Tâche en retard"
    )

def tester_commande_taches_en_retard():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.taches = [
        {
            "description": "Tâche future",
            "terminee": False,
            "priorite": "normale",
            "echeance": "2999-01-01"
        },
        {
            "description": "Ancienne tâche",
            "terminee": False,
            "priorite": "haute",
            "echeance": "2000-01-01"
        },
        {
            "description": "Ancienne tâche terminée",
            "terminee": True,
            "priorite": "basse",
            "echeance": "2000-01-01"
        }
    ]

    resultat = roy.traiter_message(
        "montre mes tâches en retard",
        "montre mes tâches en retard"
    )

    assert resultat is True

    reponse = roy.historique[-1]["content"]

    assert "Ancienne tâche" in reponse
    assert "2. ○" in reponse
    assert "Tâche future" not in reponse
    assert "Ancienne tâche terminée" not in reponse

def tester_commande_aucune_tache_en_retard():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.taches = [
        {
            "description": "Tâche future",
            "terminee": False,
            "priorite": "normale",
            "echeance": "2999-01-01"
        }
    ]

    resultat = roy.traiter_message(
        "montre mes tâches en retard",
        "montre mes tâches en retard"
    )

    assert resultat is True

    reponse = roy.historique[-1]["content"]

    assert reponse == (
        "Tu n'as aucune tâche en retard."
    )

def tester_tache_pour_aujourdhui():
    date_reference = date(2026, 9, 30)

    tache_du_jour = {
        "description": "Tâche du jour",
        "terminee": False,
        "priorite": "haute",
        "echeance": "2026-09-30"
    }

    tache_ancienne = {
        "description": "Ancienne tâche",
        "terminee": False,
        "priorite": "normale",
        "echeance": "2026-09-29"
    }

    tache_terminee = {
        "description": "Tâche terminée",
        "terminee": True,
        "priorite": "basse",
        "echeance": "2026-09-30"
    }

    assert tache_pour_aujourdhui(
        tache_du_jour,
        date_reference
    ) is True

    assert tache_pour_aujourdhui(
        tache_ancienne,
        date_reference
    ) is False

    assert tache_pour_aujourdhui(
        tache_terminee,
        date_reference
    ) is False

def tester_commande_taches_pour_aujourdhui():
    roy = creer_roy_test(
        historique_actif=False
    )

    date_du_jour = date.today().isoformat()

    roy.taches = [
        {
            "description": "Tâche future",
            "terminee": False,
            "priorite": "normale",
            "echeance": "2999-01-01"
        },
        {
            "description": "Tâche du jour",
            "terminee": False,
            "priorite": "haute",
            "echeance": date_du_jour
        },
        {
            "description": "Tâche du jour terminée",
            "terminee": True,
            "priorite": "basse",
            "echeance": date_du_jour
        }
    ]

    resultat = roy.traiter_message(
        "montre mes tâches pour aujourd'hui",
        "montre mes tâches pour aujourd'hui"
    )

    assert resultat is True

    reponse = roy.historique[-1]["content"]

    assert "2. ○" in reponse
    assert "Tâche du jour" in reponse
    assert "Tâche future" not in reponse
    assert "Tâche du jour terminée" not in reponse

    roy.taches = [
        {
            "description": "Tâche future",
            "terminee": False,
            "priorite": "normale",
            "echeance": "2999-01-01"
        }
    ]

    roy.traiter_message(
        "montre mes tâches pour aujourd'hui",
        "montre mes tâches pour aujourd'hui"
    )

    reponse = roy.historique[-1]["content"]

    assert reponse == (
        "Tu n'as aucune tâche prévue aujourd'hui."
    )

def tester_commande_resume_taches():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.taches = [
        {
            "description": "Tâche en retard",
            "terminee": False,
            "priorite": "haute",
            "echeance": "2000-01-01"
        },
        {
            "description": "Tâche du jour",
            "terminee": False,
            "priorite": "normale",
            "echeance": date.today().isoformat()
        },
        {
            "description": "Tâche future",
            "terminee": False,
            "priorite": "basse",
            "echeance": "2999-01-01"
        }
    ]

    resultat = roy.traiter_message(
        "résumé tâches",
        "résumé tâches"
    )

    assert resultat is True

    reponse = roy.historique[-1]["content"]

    assert "Résumé des tâches" in reponse
    assert "En retard : 1" in reponse
    assert "Pour aujourd'hui : 1" in reponse
    assert "À venir : 1" in reponse
    assert "Tâche en retard" in reponse
    assert "Tâche du jour" in reponse