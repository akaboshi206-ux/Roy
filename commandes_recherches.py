def traiter_commande_recherche(
    roy,
    message: str,
    message_original: str
) -> bool:
    formats_incomplets = {
        "montre la recherche": "montre la recherche 1",
        "export recherche": "export recherche 1",
        "note recherche": "note recherche 1 : texte"
    }

    if message in formats_incomplets:
        roy.repondre(
            f"Utilise le format : {formats_incomplets[message]}"
        )
        return True
    
    if message == "répare mes recherches":
        roy.reparer_recherches()
        return True
    
    if message == "montre mes recherches":
        roy.afficher_recherches()
        return True

    if message.startswith("montre la recherche "):
        texte_numero = message.removeprefix(
            "montre la recherche "
        ).strip()

        try:
            numero = int(texte_numero)
        except ValueError:
            roy.repondre(
                "Utilise le format : montre la recherche 1"
            )
            return True

        roy.afficher_recherche(numero)
        return True

    if (
        message == "cherche recherche"
        or message.startswith("cherche recherche ")
    ):
        mot = message.removeprefix(
            "cherche recherche"
        ).strip()

        roy.rechercher_recherches(mot)
        return True

    if message.startswith("export recherche "):
        texte_numero = message.removeprefix(
            "export recherche "
        ).strip()

        try:
            numero = int(texte_numero)
        except ValueError:
            roy.repondre(
                "Utilise le format : export recherche 1"
            )
            return True

        roy.exporter_recherche(numero)
        return True
    
    commande, separateur, contenu = message.partition(":")

    if commande.strip().startswith("note recherche "):
        texte_numero = commande.strip().removeprefix(
            "note recherche "
        ).strip()

        if not separateur:
            roy.repondre(
                "Utilise le format : note recherche 1 : texte"
            )
            return True

        try:
            numero = int(texte_numero)
        except ValueError:
            roy.repondre(
                "Utilise le format : note recherche 1 : texte"
            )
            return True

        texte = message_original.partition(":")[2].strip()
        roy.ajouter_note_recherche(numero, texte)
        return True

    if commande.strip().startswith("source recherche "):
        texte_numero = commande.strip().removeprefix(
            "source recherche "
        ).strip()

        if not separateur:
            roy.repondre(
                "Utilise le format : source recherche 1 : référence"
            )
            return True

        try:
            numero = int(texte_numero)
        except ValueError:
            roy.repondre(
                "Utilise le format : source recherche 1 : référence"
            )
            return True

        texte = message_original.partition(":")[2].strip()
        roy.ajouter_source_recherche(numero, texte)
        return True

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