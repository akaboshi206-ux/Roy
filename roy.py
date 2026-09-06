import json
with open("memoire.json", "r", encoding="utf-8") as fichier:
    memoire = json.load(fichier)

print("Mémoire chargée :", memoire)

print("Bonjour ! Je m'appelle Roy.")

nom = memoire["nom"]

print("Enchanté", nom, "!")
humeur = memoire["humeur"]

if humeur == "bien":
    print("Je suis content de l'apprendre !")

elif humeur == "mal":
    print("Désolé de l'apprendre. J'espère que ça ira mieux.")

elif humeur == "fatigué":
    print("Tu devrais peut-être te reposer un peu.")

else:
    print("D'accord, merci de me l'avoir dit.") 

def saluer(nom):
    print("Roy : Bonjour", nom, "!") 

def sauvegarder_memoire():
    with open("memoire.json", "w", encoding="utf-8") as fichier:
        json.dump(memoire, fichier, ensure_ascii=False, indent=4)

def apprendre(cle, valeur):
    if cle in memoire:
        ancienne_valeur = memoire[cle]

        if ancienne_valeur == valeur:
            print("Roy : Je connaissais déjà exactement cette information.")
            return
       
        print("Roy : J'ai remplacé", ancienne_valeur, "par", valeur)
    else:
        print("Roy : J'ai appris une nouvelle information.")

    memoire[cle] = valeur
    sauvegarder_memoire()

def rappeler(cle):
    if cle in memoire:
        print("Roy :", memoire[cle])
    else:
        print("Roy : Je n'ai aucune information sur", cle)

def oublier(cle):
    if cle in memoire:
        while True:
            reponse = nettoyer_texte(
               input("Roy : Es-tu sûr de vouloir oublier " + cle + " ? ")
            )

            if reponse == "oui":    
                del memoire[cle]
                sauvegarder_memoire()
                print("Roy : J'ai oublié", cle)
                break

            elif reponse == "non":
                print("Roy : D'accord, je garde cette information.")
                break

            else:
                print("Roy : Réponds par oui ou non.")
        
    else:
        print("Roy : Je ne connaissais pas", cle)

def afficher_memoire():
    print("Roy : Voici ce que je sais sur toi :")
    for cle, valeur in memoire.items():
        print("-", cle, ":", valeur)

def compter_memoire():
    nombre = obtenir_nombre_informations()

    if nombre == 1:
        print("Roy : Je connais 1 information sur toi.")
    else:
        print("Roy : Je connais", nombre, "informations sur toi.")

def obtenir_nombre_informations():
    return len(memoire)

def connaitre(cle):
    if cle in memoire:
        valeur = memoire[cle]

        if cle in cles_feminines:
            possessif = "ta"
        else:
            possessif = "ton"

        print(f"Roy : Oui, {possessif} {cle} est {valeur}.")
    else:
        print(f"Roy : Non, je ne connais encore aucune information sur {cle}.")
        print("Roy : Veux-tu me l'apprendre ?")

        while True:
           reponse = nettoyer_texte(input("Toi : "))

           if reponse == "oui":
               valeur = nettoyer_texte(
                   input("Roy : Quelle est l'information ? "),
                   False
                )
               apprendre(cle, valeur)
               break

           elif reponse == "non":
               print("Roy : D'accord, je n'apprendrai pas cette information.")
               break

           else:
               print("Roy : Je n'ai pas compris. Réponds par oui ou non.")

def nettoyer_texte(texte, minuscules=True):
    texte_nettoye = texte.strip()

    if minuscules:
        texte_nettoye = texte_nettoye.lower()

    return texte_nettoye

def extraire_cle(message, formes):
    for forme in formes:
        if forme in message:
            cle = message.replace(forme, "").strip()

            for mot in mots_inutiles:
                cle = cle.removeprefix(mot).strip()
                cle = cle.removeprefix("mon ").removeprefix("ma ").removeprefix("mes ")

            cle = cle.replace("?", "").strip()
            return cle

    return None
            
salutations = ["bonjour", "salut", "hello", "coucou"]

commandes_memoire = [
    "montre ta mémoire",
    "montre moi ta mémoire",
    "affiche ta mémoire",
    "affiche la mémoire",
    "présente la mémoire"
]

formes_connaitre = [
    "connais-tu",
    "connais tu",
    "est-ce que tu connais",
    "est ce que tu connais",
    "tu connais",
    "tu sais",
    "tu te souviens de",
    "tu te rappelles de"
]

formes_question = [
    "quelle est ma ",
    "quel est mon ",
    "c'est quoi mon ",
    "c'est quoi ma "
]

formes_rappeler = [
    "rappelle-moi ",
    "rappelle moi ",
    "rappelle "
]

formes_oublie = [
    "oublie-moi ",
    "oublie "
]

formes_apprendre = [
    "souviens-toi que ",
    "souviens toi que ",
    "retiens que ",
    "retiens "
]

mots_inutiles = [
    "s'il te plaît ",
    "s'il te plait ",
    "stp ",
    "svp"
]

cles_feminines = [
    "couleur",
    "voiture",
    "musique",
    "ville",
    "magie"
]

def traiter_apprentissage(information):
    if "=" not in information:
        print("Roy : Utilise le format : clé = valeur")
        return

    cle, valeur = information.split("=", 1)
    cle = cle.strip()
    valeur = valeur.strip()

    if cle == "" or valeur == "":
        print("Roy : la clé et la valeur ne peuvent pas être vides.")
        return

    apprendre(cle, valeur)

def traiter_message(message, message_original):
    
    if message in salutations:
        saluer(nom)
        return True

    elif message == "comment vas-tu":
        print("Roy : Je vais bien, merci !")
        return True

    elif "mon nom" in message:
        print("Roy : Ton nom est", memoire["nom"])
        return True

    elif "mon humeur" in message:
        print("Roy : Tu m'as dit que ton humeur était", memoire["humeur"])
        return True

    elif message in commandes_memoire:
        afficher_memoire()
        return True

    elif message == "combien d'informations connais-tu":
        compter_memoire()
        return True

    elif any(forme in message for forme in formes_rappeler):
        cle = extraire_cle(message, formes_rappeler)

        if cle is None:
            print("Roy : Quelle information veux-tu que je te rappelle ?")
        else:
            rappeler(cle)

        return True

    elif any(forme in message for forme in formes_oublie):
        cle = extraire_cle(message, formes_oublie)

        if cle is None:
            print("Roy : Quelle information veux-tu que j'oublie ?")
        else:
            oublier(cle)

        return True

    elif any(forme in message for forme in formes_connaitre):
        cle = extraire_cle(message, formes_connaitre)

        if cle is None:
            print("Roy : Dis-moi ce que tu veux savoir si je connais.")
            return True
        
        connaitre(cle)
        return True

    elif any(forme in message for forme in formes_question):
        cle = extraire_cle(message, formes_question)

        if cle is None:
            print("Roy : Je n'ai pas trouvé ce que tu veux connaître.")
            return True
        
        connaitre(cle)
        return True

    elif any(forme in message for forme in formes_apprendre):
        if message_original.lower().startswith("roy "):
            message_sans_roy = message_original[4:]
        else:
            message_sans_roy = message_original
        for forme in formes_apprendre:
            if forme in message:
                message_sans_roy = message_sans_roy.removeprefix(forme)
                break

        traiter_apprentissage(message_sans_roy)
        return True
             
    return False

while True:
    message_original = input("Toi : ")
    message = message_original.lower()
    if message.startswith("roy "):
        message = message.removeprefix("roy ")

    if message == "quitter":
        print("Roy : À bientôt !")
        break

    if traiter_message(message, message_original):
        continue

    print("Roy : Je ne sais pas encore quoi répondre.")