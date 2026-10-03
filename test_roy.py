from tests import (
    test_taches,
    test_historique,
    test_memoire,
    test_systeme,
    test_conversation,
    test_json,
    test_general,
    test_outils
)

def trouver_tests(espace_noms):
    return [
        fonction
        for nom, fonction in espace_noms.items()
        if nom.startswith("tester_")
        and callable(fonction)
    ]


def lancer_tests():
    tests = trouver_tests(
        globals().copy()
    )

    modules_tests = (
        test_taches,
        test_historique,
        test_memoire,
        test_systeme,
        test_conversation,
        test_json,
        test_general,
        test_outils
    )
    for module in modules_tests:
        tests.extend(
            trouver_tests(vars(module))
        )

    for test in tests:
        test()

    print(
        f"{len(tests)} tests ont réussi."
    )


if __name__ == "__main__":
    lancer_tests()