PRIORITES_VALIDES = {"basse", "normale", "haute"}

def ajouter_tache(taches: list[dict], description: str) -> bool:
    description = description.strip()

    if not description:
        return False

    taches.append({
        "description": description,
        "terminee": False
    })
    return True

def formater_taches(taches: list[dict], priorite: str | None = None, terminee: bool | None = None) -> str:
    if not taches:
        return "Tu n'as aucune tâche."

    lignes = []

    for numero, tache in enumerate(taches, start=1):
        priorite_tache = tache.get("priorite", "normale")

        if (priorite is not None and priorite_tache != priorite):
            continue

        if (terminee is not None and tache["terminee"] != terminee):
            continue

        etat = "✓" if tache["terminee"] else "○"

        lignes.append(
            f"{numero}. {etat} "
            f"[{priorite_tache}] "
            f"{tache['description']}"
        )

    if lignes:
        return "\n".join(lignes)

    if priorite is not None:
        return ("Tu n'as aucune tâche de priorité " f"{priorite}.")

    if terminee is True:
        return "Tu n'as aucune tâche terminée."

    return "Tu n'as aucune tâche à faire."
   
def changer_etat_tache(taches: list[dict], numero: int, terminee: bool) -> bool:
    if (
        not 1 <= numero <= len(taches)
        or not isinstance(terminee, bool)
    ):
        return False

    taches[numero - 1]["terminee"] = terminee
    return True


def terminer_tache(
    taches: list[dict],
    numero: int
) -> bool:
    return changer_etat_tache(
        taches,
        numero,
        True
    )


def rouvrir_tache(
    taches: list[dict],
    numero: int
) -> bool:
    return changer_etat_tache(
        taches,
        numero,
        False
    )

def supprimer_tache(taches: list[dict], numero: int) -> bool:
    if not 1 <= numero <= len(taches):
        return False

    taches.pop(numero - 1)
    return True

def modifier_tache(taches: list[dict], numero: int, nouvelle_description: str) -> bool:
    nouvelle_description = nouvelle_description.strip()

    if (
        not 1 <= numero <= len(taches)
        or not nouvelle_description
    ):
        return False

    taches[numero - 1]["description"] = nouvelle_description
    return True

def changer_priorite(taches: list[dict], numero: int, priorite: str) -> bool:
    priorite = priorite.strip().lower()

    if (
        not 1 <= numero <= len(taches)
        or priorite not in PRIORITES_VALIDES
    ):
        return False

    taches[numero - 1]["priorite"] = priorite
    return True