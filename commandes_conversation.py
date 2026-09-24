def traiter_commande_conversation(
    roy,
    message: str
) -> bool:
    if message == "comment vas-tu":
        roy.repondre("Je vais bien, merci !")
        return True

    if "mon nom" in message:
        nom = roy.memoire.get(
            "nom",
            "utilisateur"
        )
        roy.repondre(f"Ton nom est {nom}")
        return True

    if "mon humeur" in message:
        humeur = roy.memoire.get(
            "humeur",
            "inconnue"
        )
        roy.repondre(
            f"Tu m'as dit que ton humeur était {humeur}"
        )
        return True

    if message == "combien d'informations connais-tu":
        roy.compter_memoire()
        return True

    return False