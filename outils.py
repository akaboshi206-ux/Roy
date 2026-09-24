import json
import os
from tempfile import NamedTemporaryFile

def nettoyer_texte(texte, minuscules=True):
    texte_nettoye = texte.strip()

    if minuscules:
        texte_nettoye = texte_nettoye.lower()

    return texte_nettoye

def extraire_cle(message, formes, mots_inutiles):
    for forme in formes:
        if forme in message:
            cle = message.replace(forme, "").strip()

            for mot in mots_inutiles:
                mot = mot.strip()
                cle = cle.removeprefix(mot).strip()
                cle = cle.removesuffix(mot).strip()
                
            cle = cle.removeprefix("mon ").removeprefix("ma ").removeprefix("mes ")

            cle = cle.replace("?", "").strip()
            return cle

    return None

def formater_message_historique(message):
    auteur = "Toi" if message["role"] == "user" else "Roy"
    timestamp = message.get("timestamp")

    if timestamp:
        date_affichee = timestamp.replace("T", " ")
        return f"[{date_affichee}] {auteur} : {message['content']}"

    return f"{auteur} : {message['content']}"

def sauvegarder_json_atomiquement(chemin, donnees) -> bool:
    chemin_temporaire = None

    try:
        dossier = os.path.dirname(os.path.abspath(chemin))

        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=dossier,
            suffix=".tmp",
            delete=False
        ) as fichier:
            chemin_temporaire = fichier.name
            json.dump(donnees, fichier, ensure_ascii=False, indent=4)

        os.replace(chemin_temporaire, chemin)
        return True

    except (OSError, TypeError):
        if chemin_temporaire is not None:
            try:
                os.unlink(chemin_temporaire)
            except OSError:
                pass

        return False

def charger_json(
    chemin: str,
    valeur_par_defaut: object
) -> tuple[object, Exception | None]:
    try:
        with open(
            chemin,
            "r",
            encoding="utf-8"
        ) as fichier:
            donnees = json.load(fichier)

        return donnees, None

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        OSError
    ) as erreur:
        return valeur_par_defaut, erreur