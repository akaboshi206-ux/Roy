from itertools import count
from pathlib import Path
from tempfile import TemporaryDirectory

from roy import Roy


dossier_tests = TemporaryDirectory()
numeros_tests = count()


def creer_roy_test(**options):
    numero = next(numeros_tests)

    chemin_memoire = (
        Path(dossier_tests.name)
        / f"memoire_{numero}.json"
    )
    chemin_historique = (
        Path(dossier_tests.name)
        / f"historique_{numero}.json"
    )
    chemin_taches = (
        Path(dossier_tests.name)
        / f"taches_{numero}.json"
    )

    options.setdefault(
        "fichier_memoire",
        str(chemin_memoire)
    )
    options.setdefault(
        "fichier_historique",
        str(chemin_historique)
    )
    options.setdefault(
        "fichier_taches",
        str(chemin_taches)
    )

    return Roy(**options)


def recharger_roy_test(roy: Roy) -> Roy:
    return Roy(
        historique_actif=False,
        fichier_memoire=roy.fichier_memoire,
        fichier_taches=roy.fichier_taches
    )