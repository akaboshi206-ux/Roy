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
