from taches import (
    PRIORITES_VALIDES,
    ajouter_tache,
    formater_taches,
    terminer_tache,
    rouvrir_tache,
    supprimer_tache,
    modifier_tache,
    changer_priorite,
    changer_echeance,
    trier_taches_par_priorite,
    rechercher_taches,
    calculer_statistiques_taches,
    trier_taches_par_echeance,
    retirer_echeance
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

    if message == "montre mes tâches en retard":
        roy.repondre(
            formater_taches(
                roy.taches,
                en_retard=True
            )
        )
        return True

    if message == "montre mes tâches pour aujourd'hui":
        roy.repondre(
            formater_taches(
                roy.taches,
                pour_aujourdhui=True
            )
        )
        return True

    if message == "montre mes tâches à venir":
        roy.repondre(
            formater_taches(
                roy.taches,
                a_venir=True
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

def traiter_echeance_tache(
    roy,
    message: str
) -> bool:
    if not message.startswith(
        "échéance tâche "
    ):
        return False

    contenu = message.removeprefix(
        "échéance tâche "
    ).strip()

    texte_numero, separateur, echeance = (
        contenu.partition(":")
    )

    echeance = echeance.strip()

    if not separateur or not echeance:
        roy.repondre(
            "Utilise le format : "
            "échéance tâche 1 : 2026-10-05"
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

    ancienne_echeance = (
        roy.taches[numero - 1].get("echeance")
    )

    if not changer_echeance(
        roy.taches,
        numero,
        echeance
    ):
        roy.repondre(
            "Utilise une date valide au format "
            "année-mois-jour."
        )

    elif roy.sauvegarder_taches():
        roy.repondre("Échéance modifiée.")

    else:
        roy.taches[numero - 1]["echeance"] = (
            ancienne_echeance
        )
        roy.repondre(
            "La modification de l'échéance "
            "a été annulée."
        )

    return True

def traiter_retrait_echeance_tache(
    roy,
    message: str
) -> bool:
    prefixe = (
        "retire l'échéance de la tâche "
    )

    if not message.startswith(prefixe):
        return False

    texte_numero = message.removeprefix(
        prefixe
    ).strip()

    numero = roy.obtenir_numero_tache(
        texte_numero
    )

    if numero is None:
        roy.repondre(
            "Indique un numéro de tâche valide."
        )
        return True

    ancienne_echeance = (
        roy.taches[numero - 1].get(
            "echeance"
        )
    )

    if not retirer_echeance(
        roy.taches,
        numero
    ):
        roy.repondre(
            "Indique un numéro de tâche valide."
        )

    elif roy.sauvegarder_taches():
        roy.repondre(
            "Échéance retirée."
        )

    else:
        roy.taches[numero - 1][
            "echeance"
        ] = ancienne_echeance

        roy.repondre(
            "Le retrait de l'échéance "
            "a été annulé."
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

def traiter_tri_taches(
    roy,
    message: str
) -> bool:
    if message not in (
        "trie mes tâches par priorité",
        "trie mes tâches par échéance"
    ):
        return False

    ancien_ordre = roy.taches.copy()

    if message == "trie mes tâches par priorité":
        trier_taches_par_priorite(
            roy.taches
        )
        critere = "priorité"

    else:
        trier_taches_par_echeance(
            roy.taches
        )
        critere = "échéance"

    if roy.sauvegarder_taches():
        roy.repondre(
            f"Tâches triées par {critere}.\n"
            + formater_taches(roy.taches)
        )

    else:
        roy.taches[:] = ancien_ordre
        roy.repondre(
            "Le tri des tâches a été annulé."
        )

    return True

def traiter_recherche_tache(
    roy,
    message: str
) -> bool:
    if not message.startswith(
        "recherche tâche "
    ):
        return False

    recherche = message.removeprefix(
        "recherche tâche "
    ).strip()

    resultats = rechercher_taches(
        roy.taches,
        recherche
    )

    if not resultats:
        roy.repondre(
            f"Aucune tâche trouvée pour : {recherche}"
        )
        return True

    roy.repondre(
        f"{len(resultats)} tâche(s) trouvée(s) "
        f"pour : {recherche}\n"
        f"{formater_taches(resultats)}"
    )
    return True

def traiter_resume_taches(
    roy,
    message: str
) -> bool:
    if message != "résumé tâches":
        return False

    statistiques = calculer_statistiques_taches(
        roy.taches
    )

    taches_en_retard = formater_taches(
        roy.taches,
        en_retard=True
    )

    taches_du_jour = formater_taches(
        roy.taches,
        pour_aujourdhui=True
    )

    roy.repondre(
        "Résumé des tâches\n"
        f"En retard : {statistiques['en_retard']}\n"
        f"Pour aujourd'hui : "
        f"{statistiques['pour_aujourdhui']}\n"
        f"À venir : {statistiques['a_venir']}\n\n"
        "Tâches en retard :\n"
        f"{taches_en_retard}\n\n"
        "Tâches pour aujourd'hui :\n"
        f"{taches_du_jour}"
    )

    return True

def traiter_statistiques_taches(
    roy,
    message: str
) -> bool:
    if message != "statistiques tâches":
        return False
    statistiques = calculer_statistiques_taches(
        roy.taches
    )
    roy.repondre(
        "Statistiques des tâches\n"
        f"Tâches totales : {statistiques['total']}\n"
        f"À faire : {statistiques['a_faire']}\n"
        f"Terminées : {statistiques['terminees']}\n"
        f"Progression : {statistiques['pourcentage']} %\n"
        f"Priorité haute : {statistiques['hautes']}\n"
        f"Priorité normale : {statistiques['normales']}\n"
        f"Priorité basse : {statistiques['basses']}\n"
        f"En retard : {statistiques['en_retard']}\n"
        f"Pour aujourd'hui : "
        f"{statistiques['pour_aujourdhui']}\n"
        f"À venir : {statistiques['a_venir']}"
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
        traiter_echeance_tache,
        traiter_retrait_echeance_tache,
        traiter_priorite_tache,
        traiter_suppression_tache,
        traiter_tri_taches,
        traiter_resume_taches,
        traiter_statistiques_taches,
        traiter_recherche_tache,
        traiter_affichage_taches,
    )

    for gestionnaire in gestionnaires:
        if gestionnaire(roy, message):
            return True

    return False