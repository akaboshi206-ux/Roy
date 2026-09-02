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
        del memoire[cle]
        sauvegarder_memoire()
        print("Roy : J'ai oublié", cle)
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
        print(f"Roy : Oui, ton {cle} est {valeur}.")
    else:
        print(f"Roy : Non, je ne connais encore aucune information sur {cle}.")
        print("Roy : Veux-tu me l'apprendre ?")
        reponse = input("Toi : ").lower()
        if reponse == "oui":
            valeur = input("Roy : Quelle est l'information ? ")
            apprendre(cle, valeur)

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
    "est-ce que tu connais"
]

while True:
    message = input("Toi : ").lower()
    if message.startswith("roy "):
        message = message.removeprefix("roy ")

    if message == "quitter":
        print("Roy : À bientôt !")
        break

    elif any(mot in message for mot in salutations):
        saluer(nom)

    elif message == "comment vas-tu":
        print("Roy : Je vais bien, merci !")
        
    elif "mon nom" in message:
        print("Roy : Ton nom est", memoire["nom"])

    elif "mon humeur" in message:
        print("Roy : Tu m'as dit que ton humeur était", memoire["humeur"])

    elif "ma couleur préférée est" in message:
        couleur = message.replace("ma couleur préférée est", "").strip()
        apprendre("couleur", couleur)
        print("Roy : D'accord, je retiens que ta couleur préférée est", couleur)

    elif "ma couleur préférée" in message:
        print("Roy : Ta couleur préférée est", memoire.get("couleur"))

    elif "mon animal préféré est" in message:
        animal = message.replace("mon animal préféré est", "").strip()
        apprendre("animal", animal)
        print("Roy : D'accord, je retiens que ton animal préféré est", animal)

    elif "mon animal préféré" in message:
        print("Roy : Ton animal préféré est", memoire.get("animal"))

    elif message.startswith("retiens "):
        information = message.replace("retiens ", "")

        if "=" not in information:
            print("Roy : Utilise le format : retiens clé = valeur")
            continue

        try:
            cle, valeur = information.split("=")
        except ValueError:
            print("Roy : Il y a un problème dans le format.")
            continue

        cle = cle.strip()
        valeur = valeur.strip()

        if cle == "" or valeur == "":
            print("Roy : La clé et la valeur ne peuvent pas être vides.")
            continue

        apprendre(cle, valeur)

    elif message.startswith("rappelle"):
        cle = message.replace("rappelle", "").strip()

        if cle == "":
            print("Roy : Dis-moi ce que tu veux que je rappelle.")
            continue

        rappeler(cle)

    elif message.startswith("oublie "):
        cle = message.replace("oublie ", "").strip()
        oublier(cle)

    elif message in commandes_memoire:
        afficher_memoire()

    elif message == "combien d'informations connais-tu":
        compter_memoire()

    elif any(message.startswith(forme) for forme in formes_connaitre):
        for forme in formes_connaitre:
            if message.startswith(forme):
                cle = message.replace(forme, "").strip()

        if cle == "":
            print("Roy : Dis-moi ce que tu veux savoir si je connais.")
            continue

        connaitre(cle)

    else:
        print("Roy : Je ne sais pas encore quoi répondre.")