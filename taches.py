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

def formater_taches(taches: list[dict]) -> str:
    if not taches:
        return "Tu n'as aucune tâche."

    lignes = []
    for numero, tache in enumerate(taches, start=1):
        etat = "✓" if tache["terminee"] else "○"
        priorite = tache.get("priorite", "normale")
        lignes.append(
            f"{numero}. {etat} [{priorite}] "
            f"{tache['description']}"
        )

    return "\n".join(lignes)

def terminer_tache(taches: list[dict], numero: int) -> bool:
    if not 1 <= numero <= len(taches):
        return False

    taches[numero - 1]["terminee"] = True
    return True

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