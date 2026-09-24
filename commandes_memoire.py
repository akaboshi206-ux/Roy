from config import (
    formes_connaitre,
    formes_question,
    formes_rappeler,
    formes_oublie,
    formes_apprendre,
    mots_inutiles
)

from outils import (
    extraire_cle
)

def traiter_rappel_memoire(
    roy,
    message: str
) -> bool:
    if not any(
        forme in message
        for forme in formes_rappeler
    ):
        return False

    cle = extraire_cle(
        message,
        formes_rappeler,
        mots_inutiles
    )

    if cle is None:
        roy.repondre(
            "Quelle information veux-tu "
            "que je te rappelle ?"
        )
    else:
        roy.rappeler(cle)

    return True

def traiter_oubli_memoire(
    roy,
    message: str
) -> bool:
    if not any(
        forme in message
        for forme in formes_oublie
    ):
        return False

    cle = extraire_cle(
        message,
        formes_oublie,
        mots_inutiles
    )

    if cle is None:
        roy.repondre(
            "Quelle information veux-tu "
            "que j'oublie ?"
        )
    else:
        roy.oublier(cle)

    return True

def traiter_connaissance_memoire(
    roy,
    message: str
) -> bool:
    if not any(
        forme in message
        for forme in formes_connaitre
    ):
        return False

    cle = extraire_cle(
        message,
        formes_connaitre,
        mots_inutiles
    )

    if cle is None:
        roy.repondre(
            "Dis-moi ce que tu veux savoir "
            "si je connais."
        )
    else:
        roy.connaitre(cle)

    return True

def traiter_question_memoire(
    roy,
    message: str
) -> bool:
    if not any(
        forme in message
        for forme in formes_question
    ):
        return False

    cle = extraire_cle(
        message,
        formes_question,
        mots_inutiles
    )

    if cle is None:
        roy.repondre(
            "Je n'ai pas trouvé ce que "
            "tu veux connaître."
        )
    else:
        roy.connaitre(cle)

    return True

def traiter_apprentissage_memoire(
    roy,
    message: str,
    message_original: str
) -> bool:
    if not any(
        forme in message
        for forme in formes_apprendre
    ):
        return False

    message_sans_roy = message_original.strip()

    if message_sans_roy.lower().startswith("roy "):
        message_sans_roy = message_sans_roy[4:]

    message_minuscule = message_sans_roy.lower()

    for forme in formes_apprendre:
        position = message_minuscule.find(forme)

        if position != -1:
            message_sans_roy = message_sans_roy[
                position + len(forme):
            ]
            break

    roy.traiter_apprentissage(
        message_sans_roy.strip()
    )
    return True

def traiter_commande_memoire(
    roy,
    message: str,
    message_original: str
) -> bool:
    gestionnaires = (
        traiter_rappel_memoire,
        traiter_oubli_memoire,
        traiter_connaissance_memoire,
        traiter_question_memoire
    )

    for gestionnaire in gestionnaires:
        if gestionnaire(roy, message):
            return True

    if traiter_apprentissage_memoire(
        roy,
        message,
        message_original
    ):
        return True

    return False