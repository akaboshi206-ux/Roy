from typing import (
    Literal,
    TypedDict,
    cast
)

from datetime import date, datetime

Priorite = Literal[
    "basse",
    "normale",
    "haute"
]


class Tache(TypedDict):
    description: str
    terminee: bool
    priorite: Priorite
    echeance: str | None

PRIORITES_VALIDES: set[Priorite] = {
    "basse",
    "normale",
    "haute"
}

ORDRE_PRIORITES: dict[Priorite, int] = {
    "haute": 0,
    "normale": 1,
    "basse": 2
}

def date_echeance_valide(
    echeance: str
) -> bool:
    return (
        convertir_echeance_en_date(echeance)
        is not None
    )

def convertir_echeance_en_date(
    echeance: object
) -> date | None:
    if not isinstance(echeance, str):
        return None

    try:
        return datetime.strptime(
            echeance,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return None

def tache_en_retard(
    tache: Tache,
    date_reference=None
) -> bool:
    if tache.get("terminee", False):
        return False

    date_echeance = convertir_echeance_en_date(
        tache.get("echeance")
    )

    if date_echeance is None:
        return False

    if date_reference is None:
        date_reference = date.today()

    return date_echeance < date_reference

def tache_pour_aujourdhui(
    tache: Tache,
    date_reference=None
) -> bool:
    if tache.get("terminee", False):
        return False

    date_echeance = convertir_echeance_en_date(
        tache.get("echeance")
    )

    if date_echeance is None:
        return False

    if date_reference is None:
        date_reference = date.today()

    return date_echeance == date_reference

def tache_a_venir(
    tache: Tache,
    date_reference=None
) -> bool:
    if tache.get("terminee", False):
        return False

    date_echeance = convertir_echeance_en_date(
        tache.get("echeance")
    )

    if date_echeance is None:
        return False

    if date_reference is None:
        date_reference = date.today()

    return date_echeance > date_reference

def filtrer_taches_en_retard(
    taches: list[Tache],
    date_reference=None
) -> list[Tache]:
    return [
        tache
        for tache in taches
        if tache_en_retard(
            tache,
            date_reference
        )
    ]

def changer_echeance(
    taches: list[Tache],
    numero: int,
    echeance: str
) -> bool:
    echeance = echeance.strip()

    if (
        not 1 <= numero <= len(taches)
        or not date_echeance_valide(echeance)
    ):
        return False

    taches[numero - 1]["echeance"] = echeance
    return True

def retirer_echeance(
    taches: list[Tache],
    numero: int
) -> bool:
    if not 1 <= numero <= len(taches):
        return False

    taches[numero - 1]["echeance"] = None
    return True

def trier_taches_par_priorite(taches: list[Tache]) -> None:
    taches.sort(
        key=lambda tache: ORDRE_PRIORITES[
            tache["priorite"]
        ]
    )

def trier_taches_par_echeance(
    taches: list[Tache]
) -> None:
    taches.sort(
        key=lambda tache: (
            convertir_echeance_en_date(
                tache.get("echeance")
            )
            or date.max
        )
    )

def est_tache_valide(tache: object) -> bool:
    if not isinstance(tache, dict):
        return False

    return (
        isinstance(
            tache.get("description"),
            str
        )
        and isinstance(
            tache.get("terminee"),
            bool
        )
        and tache.get(
            "priorite",
            "normale"
        ) in PRIORITES_VALIDES
        and (
            tache.get("echeance") is None
            or (
                isinstance(
                    tache.get("echeance"),
                    str
                )
                and date_echeance_valide(
                    tache["echeance"]
                )
            )
        )
    )

def est_liste_taches_valide(donnees: object) -> bool:
    if not isinstance(donnees, list):
        return False

    for tache in donnees:
        if not est_tache_valide(tache):
            return False

    return True

def ajouter_tache(taches: list[Tache], description: str) -> bool:
    description = description.strip()

    if not description:
        return False

    taches.append({
        "description": description,
        "terminee": False,
        "priorite": "normale",
        "echeance": None
    })
    return True

def formater_taches(
    taches: list[Tache],
    priorite: str | None = None,
    terminee: bool | None = None,
    en_retard: bool = False,
    pour_aujourdhui: bool = False,
    a_venir: bool = False
) -> str:
    if not taches:
        return "Tu n'as aucune tâche."

    lignes = []

    for numero, tache in enumerate(taches, start=1):
        priorite_tache = tache.get("priorite", "normale")

        if (en_retard and not tache_en_retard(tache)):
            continue

        if (pour_aujourdhui and not tache_pour_aujourdhui(tache)):
            continue

        if a_venir and not tache_a_venir(tache):
            continue

        if (priorite is not None and priorite_tache != priorite):
            continue

        if (terminee is not None and tache["terminee"] != terminee):
            continue    

        etat = "✓" if tache["terminee"] else "○"

        echeance = tache.get("echeance")

        texte_echeance = (
            f" [échéance : {echeance}]"
            if echeance
            else ""
        )

        lignes.append(
            f"{numero}. {etat} "
            f"[{priorite_tache}]"
            f"{texte_echeance} "
            f"{tache['description']}"
        )

    if lignes:
        return "\n".join(lignes)

    if en_retard:
        return "Tu n'as aucune tâche en retard."

    if pour_aujourdhui:
        return "Tu n'as aucune tâche prévue aujourd'hui."

    if a_venir:
        return "Tu n'as aucune tâche à venir."

    if priorite is not None:
        return ("Tu n'as aucune tâche de priorité " f"{priorite}.")

    if terminee is True:
        return "Tu n'as aucune tâche terminée."

    return "Tu n'as aucune tâche à faire."
   
def changer_etat_tache(taches: list[Tache], numero: int, terminee: bool) -> bool:
    if (
        not 1 <= numero <= len(taches)
        or not isinstance(terminee, bool)
    ):
        return False

    taches[numero - 1]["terminee"] = terminee
    return True


def terminer_tache(
    taches: list[Tache],
    numero: int
) -> bool:
    return changer_etat_tache(
        taches,
        numero,
        True
    )


def rouvrir_tache(
    taches: list[Tache],
    numero: int
) -> bool:
    return changer_etat_tache(
        taches,
        numero,
        False
    )

def supprimer_tache(taches: list[Tache], numero: int) -> bool:
    if not 1 <= numero <= len(taches):
        return False

    taches.pop(numero - 1)
    return True

def modifier_tache(taches: list[Tache], numero: int, nouvelle_description: str) -> bool:
    nouvelle_description = nouvelle_description.strip()

    if (
        not 1 <= numero <= len(taches)
        or not nouvelle_description
    ):
        return False

    taches[numero - 1]["description"] = nouvelle_description
    return True

def changer_priorite(taches: list[Tache], numero: int, priorite: str) -> bool:
    priorite = priorite.strip().lower()

    if (
        not 1 <= numero <= len(taches)
        or priorite not in PRIORITES_VALIDES
    ):
        return False

    taches[numero - 1]["priorite"] = cast(
        Priorite,
        priorite
    )
    return True

def rechercher_taches(
    taches: list[Tache],
    recherche: str
) -> list[Tache]:
    recherche = recherche.strip().lower()

    if not recherche:
        return []

    resultats: list[Tache] = []

    for tache in taches:
        if recherche in tache["description"].lower():
            resultats.append(tache)

    return resultats

def calculer_statistiques_taches(
    taches: list[Tache],
    date_reference=None
) -> dict[str, int]:
    total = len(taches)

    terminees = sum(
        1 for tache in taches
        if tache["terminee"]
    )

    a_faire = total - terminees

    pourcentage = round(
        terminees / total * 100
    ) if total > 0 else 0

    hautes = sum(
        1 for tache in taches
        if tache["priorite"] == "haute"
    )

    normales = sum(
        1 for tache in taches
        if tache["priorite"] == "normale"
    )

    basses = sum(
        1 for tache in taches
        if tache["priorite"] == "basse"
    )

    en_retard = sum(
        tache_en_retard(
            tache,
            date_reference
        )
        for tache in taches
    )

    pour_aujourdhui = sum(
        tache_pour_aujourdhui(
            tache,
            date_reference
        )
        for tache in taches
    )

    a_venir = sum(
        tache_a_venir(
            tache,
            date_reference
        )
        for tache in taches
    )

    return {
        "total": total,
        "a_faire": a_faire,
        "terminees": terminees,
        "hautes": hautes,
        "pourcentage": pourcentage,
        "normales": normales,
        "basses": basses,
        "en_retard": en_retard,
        "pour_aujourdhui": pour_aujourdhui,
        "a_venir": a_venir
    }