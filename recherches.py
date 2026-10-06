from typing import TypedDict
from outils import (
    charger_json_avec_sauvegarde,
    sauvegarder_json_atomiquement
)


class Recherche(TypedDict):
    titre: str
    notes: list[str]
    sources: list[str]


def creer_recherche(titre: str) -> Recherche:
    titre = titre.strip()

    if not titre:
        raise ValueError(
            "Le titre de la recherche ne peut pas être vide."
        )

    return {
        "titre": titre,
        "notes": [],
        "sources": []
    }

def est_recherche_valide(donnees: object) -> bool:
    if not isinstance(donnees, dict):
        return False

    titre = donnees.get("titre")
    notes = donnees.get("notes")
    sources = donnees.get("sources")

    return (
        isinstance(titre, str)
        and bool(titre.strip())
        and isinstance(notes, list)
        and all(
            isinstance(note, str) and bool(note.strip())
            for note in notes
        )
        and isinstance(sources, list)
        and all(
            isinstance(source, str) and bool(source.strip())
            for source in sources
        )
    )


def est_liste_recherches_valide(donnees: object) -> bool:
    return (
        isinstance(donnees, list)
        and all(
            est_recherche_valide(recherche)
            for recherche in donnees
        )
    )

def ajouter_note(
    recherche: Recherche,
    texte: str
) -> bool:
    texte = texte.strip()

    if not texte:
        return False

    recherche["notes"].append(texte)
    return True

def ajouter_source(
    recherche: Recherche,
    texte: str
) -> bool:
    texte = texte.strip()

    if not texte or texte in recherche["sources"]:
        return False

    recherche["sources"].append(texte)
    return True

def formater_recherche(recherche: Recherche) -> str:
    lignes = [f"Recherche : {recherche['titre']}", "", "Notes :"]

    if recherche["notes"]:
        for numero, note in enumerate(recherche["notes"], start=1):
            lignes.append(f"{numero}. {note}")
    else:
        lignes.append("Aucune note.")

    lignes.extend(["", "Sources :"])

    if recherche["sources"]:
        for numero, source in enumerate(recherche["sources"], start=1):
            lignes.append(f"{numero}. {source}")
    else:
        lignes.append("Aucune source.")

    return "\n".join(lignes)

def sauvegarder_recherches(
    chemin: str,
    recherches: list[Recherche]
) -> bool:
    if not est_liste_recherches_valide(recherches):
        return False

    return sauvegarder_json_atomiquement(
        chemin,
        recherches
    )

def charger_recherches(
    chemin: str
) -> tuple[object, Exception | None, bool, OSError | None]:
    return charger_json_avec_sauvegarde(
        chemin,
        [],
        est_liste_recherches_valide
    )