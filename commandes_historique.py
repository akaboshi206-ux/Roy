from config import (
    commandes_historique,
    commandes_rechercher_historique,
    commandes_statistiques_historique,
    commandes_exporter_historique
)


def traiter_recherche_historique(
    roy,
    message: str
) -> bool:
    for commande in commandes_rechercher_historique:
        if message.startswith(commande):
            mot_cle = message.removeprefix(
                commande
            ).strip()

            roy.rechercher_historique(
                mot_cle
            )
            return True

    return False

def traiter_affichage_historique(
    roy,
    message: str
) -> bool:
    for commande in commandes_historique:
        if message == commande:
            roy.afficher_historique()
            return True

        prefixe = commande + " "

        if message.startswith(prefixe):
            nombre_texte = message.removeprefix(
                prefixe
            ).strip()

            try:
                limite = int(nombre_texte)

            except ValueError:
                roy.repondre(
                    "Utilise un nombre, "
                    "par exemple : historique 5"
                )
                return True

            if limite <= 0:
                roy.repondre(
                    "Le nombre de messages doit être "
                    "supérieur à zéro."
                )
                return True

            roy.afficher_historique(
                limite
            )
            return True

    return False

def traiter_statistiques_historique(
    roy,
    message: str
) -> bool:
    if message in commandes_statistiques_historique:
        roy.afficher_statistiques_historique()
        return True

    return False

def traiter_export_historique(
    roy,
    message: str
) -> bool:
    if message in commandes_exporter_historique:
        roy.exporter_historique()
        return True

    return False

def traiter_commande_historique(
    roy,
    message: str
) -> bool:
    gestionnaires = (
        traiter_recherche_historique,
        traiter_affichage_historique,
        traiter_statistiques_historique,
        traiter_export_historique
    )

    for gestionnaire in gestionnaires:
        if gestionnaire(roy, message):
            return True

    return False