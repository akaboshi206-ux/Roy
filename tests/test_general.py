from contextlib import redirect_stdout
from io import StringIO

from config import (
    commandes_quitter,
    exemples_aide
)
from main import nettoyer_message
from tests.aides import creer_roy_test

def tester_commandes_quitter():
    assert "quitter" in commandes_quitter
    assert "au revoir" in commandes_quitter
    assert "continuer" not in commandes_quitter

def tester_nettoyer_message():
    cas_de_test = {
        "  BONJOUR  ": "bonjour",
        "Roy statut": "statut",
        "  Roy    AU REVOIR  ": "au revoir",
        "     ": "",
        "active     ta mémoire": "active ta mémoire",
        "Roy, statut": "statut",
        "Roy : aide": "aide"
    }

    for message, resultat_attendu in cas_de_test.items():
        assert nettoyer_message(message) == resultat_attendu

def tester_repondre():
    roy = creer_roy_test(historique_actif=False)

    roy.repondre("Réponse de test")

    assert len(roy.historique) == 1

    reponse = roy.historique[0]

    assert reponse["role"] == "assistant"
    assert reponse["content"] == "Réponse de test"
    assert "timestamp" in reponse
    assert isinstance(reponse["timestamp"], str)

def tester_aide_un_seul_message():
    roy = creer_roy_test(
        historique_actif=False
    )

    roy.afficher_aide()

    assert len(roy.historique) == 1

    lignes_attendues = [
        "Voici ce que je peux faire :"
    ]

    lignes_attendues.extend(
        f"{numero}. {exemple}"
        for numero, exemple in enumerate(
            exemples_aide,
            start=1
        )
    )

    resultat_attendu = "\n".join(
        lignes_attendues
    )

    assert (
        roy.historique[0]["content"]
        == resultat_attendu
    )

def tester_recherche_ignore_nouvelle_aide():
    roy = creer_roy_test(historique_actif=False)
    roy.afficher_aide()
    roy.ajouter_historique("user", "Je veux quitter")
    roy.ajouter_historique("user", "recherche historique quitter")

    sortie = StringIO()
    with redirect_stdout(sortie):
        roy.rechercher_historique("quitter")

    texte = sortie.getvalue()
    assert "1 message(s) trouvé(s)" in texte
    assert "Je veux quitter" in texte
    assert "20. quitter" not in texte

def tester_affichage_memoire_un_seul_message():
    roy = creer_roy_test(historique_actif=False)
    roy.memoire = {"couleur": "cyan", "ville": "Paris"}

    roy.afficher_memoire()

    assert len(roy.historique) == 1
    contenu = roy.historique[0]["content"]
    assert "1. couleur : cyan" in contenu
    assert "2. ville : Paris" in contenu
