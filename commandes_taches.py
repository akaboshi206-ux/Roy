from taches import (
    PRIORITES_VALIDES,
    ajouter_tache,
    formater_taches,
    terminer_tache,
    rouvrir_tache,
    supprimer_tache,
    modifier_tache,
    changer_priorite
)


def traiter_affichage_taches(
    roy,
    message: str
) -> bool:
    if message == "montre mes tâches":
        roy.repondre(
            formater_taches(roy.taches)
        )
        return True

    if message == "montre mes tâches à faire":
        roy.repondre(
            formater_taches(
                roy.taches,
                terminee=False
            )
        )
        return True

    if message == "montre mes tâches terminées":
        roy.repondre(
            formater_taches(
                roy.taches,
                terminee=True
            )
        )
        return True

    if message.startswith(
        "montre mes tâches de priorité "
    ):
        priorite = message.removeprefix(
            "montre mes tâches de priorité "
        ).strip()

        if priorite not in PRIORITES_VALIDES:
            roy.repondre(
                "Choisis une priorité : "
                "basse, normale ou haute."
            )
            return True

        roy.repondre(
            formater_taches(
                roy.taches,
                priorite=priorite
            )
        )
        return True

    return False

def traiter_ajout_tache(
    roy,
    message: str
) -> bool:
    if not message.startswith(
        "ajoute une tâche :"
    ):
        return False

    description = message.removeprefix(
        "ajoute une tâche :"
    ).strip()

    if not ajouter_tache(
        roy.taches,
        description
    ):
        roy.repondre(
            "Indique la tâche à ajouter."
        )

    elif roy.sauvegarder_taches():
        roy.repondre("Tâche ajoutée.")

    else:
        roy.taches.pop()
        roy.repondre(
            "L'ajout de la tâche a été annulé."
        )

    return True

def traiter_fin_tache(
    roy,
    message: str
) -> bool:
    if not message.startswith(
        "termine la tâche "
    ):
        return False

    numero = roy.obtenir_numero_tache(
        message.removeprefix(
            "termine la tâche "
        )
    )

    if numero is None:
        roy.repondre(
            "Indique un numéro de tâche valide."
        )
        return True

    if roy.appliquer_etat_tache(
        numero,
        terminer_tache
    ):
        roy.repondre("Tâche terminée.")

    else:
        roy.repondre(
            "La modification de la tâche "
            "a été annulée."
        )

    return True

def traiter_reouverture_tache(
    roy,
    message: str
) -> bool:
    if not message.startswith(
        "rouvre la tâche "
    ):
        return False

    numero = roy.obtenir_numero_tache(
        message.removeprefix(
            "rouvre la tâche "
        )
    )

    if numero is None:
        roy.repondre(
            "Indique un numéro de tâche valide."
        )
        return True

    if roy.appliquer_etat_tache(
        numero,
        rouvrir_tache
    ):
        roy.repondre("Tâche rouverte.")

    else:
        roy.repondre(
            "La modification de la tâche "
            "a été annulée."
        )

    return True

def traiter_modification_tache(
    roy,
    message: str
) -> bool:
    if not message.startswith(
        "modifie la tâche "
    ):
        return False

    contenu = message.removeprefix(
        "modifie la tâche "
    ).strip()

    texte_numero, separateur, nouvelle_description = (
        contenu.partition(":")
    )

    nouvelle_description = (
        nouvelle_description.strip()
    )

    if not separateur or not nouvelle_description:
        roy.repondre(
            "Utilise le format : "
            "modifie la tâche 1 : nouvelle description"
        )
        return True

    numero = roy.obtenir_numero_tache(
        texte_numero
    )

    if numero is None:
        roy.repondre(
            "Indique un numéro de tâche valide."
        )
        return True

    ancienne_description = (
        roy.taches[numero - 1]["description"]
    )

    if not modifier_tache(
        roy.taches,
        numero,
        nouvelle_description
    ):
        roy.repondre(
            "Numéro de tâche invalide."
        )

    elif roy.sauvegarder_taches():
        roy.repondre("Tâche modifiée.")

    else:
        roy.taches[numero - 1]["description"] = (
            ancienne_description
        )
        roy.repondre(
            "La modification de la tâche "
            "a été annulée."
        )

    return True

def traiter_priorite_tache(
    roy,
    message: str
) -> bool:
    if not message.startswith(
        "priorité tâche "
    ):
        return False

    contenu = message.removeprefix(
        "priorité tâche "
    ).strip()

    texte_numero, separateur, priorite = (
        contenu.partition(":")
    )

    priorite = priorite.strip()

    if (
        not separateur
        or priorite not in PRIORITES_VALIDES
    ):
        roy.repondre(
            "Utilise le format : "
            "priorité tâche 1 : haute"
        )
        return True

    numero = roy.obtenir_numero_tache(
        texte_numero
    )

    if numero is None:
        roy.repondre(
            "Indique un numéro de tâche valide."
        )
        return True

    ancienne_priorite = (
        roy.taches[numero - 1]["priorite"]
    )

    if not changer_priorite(
        roy.taches,
        numero,
        priorite
    ):
        roy.repondre(
            "Numéro de tâche invalide."
        )

    elif roy.sauvegarder_taches():
        roy.repondre("Priorité modifiée.")

    else:
        roy.taches[numero - 1]["priorite"] = (
            ancienne_priorite
        )
        roy.repondre(
            "La modification de la priorité "
            "a été annulée."
        )

    return True

def traiter_suppression_tache(
    roy,
    message: str
) -> bool:
    if not message.startswith(
        "supprime la tâche "
    ):
        return False

    numero = roy.obtenir_numero_tache(
        message.removeprefix(
            "supprime la tâche "
        )
    )

    if numero is None:
        roy.repondre(
            "Indique un numéro de tâche valide."
        )
        return True

    ancienne_tache = (
        roy.taches[numero - 1].copy()
    )

    supprimer_tache(
        roy.taches,
        numero
    )

    if roy.sauvegarder_taches():
        roy.repondre("Tâche supprimée.")

    else:
        roy.taches.insert(
            numero - 1,
            ancienne_tache
        )
        roy.repondre(
            "La suppression de la tâche "
            "a été annulée."
        )

    return True

def traiter_commande_tache(
    roy,
    message: str
) -> bool:
    gestionnaires = (
        traiter_ajout_tache,
        traiter_fin_tache,
        traiter_reouverture_tache,
        traiter_modification_tache,
        traiter_priorite_tache,
        traiter_suppression_tache,
        traiter_affichage_taches
    )

    for gestionnaire in gestionnaires:
        if gestionnaire(roy, message):
            return True

    return False