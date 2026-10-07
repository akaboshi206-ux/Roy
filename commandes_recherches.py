def traiter_commande_recherche(
    roy,
    message: str,
    message_original: str
) -> bool:
    commande, separateur, contenu = message.partition(":")

    if commande.strip() not in (
        "crée une recherche",
        "cree une recherche"
    ):
        return False

    if not separateur:
        roy.repondre(
            "Utilise le format : crée une recherche : titre"
        )
        return True

    titre = message_original.partition(":")[2].strip()
    roy.ajouter_recherche(titre)
    return True