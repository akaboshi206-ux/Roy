import json

from outils import nettoyer_texte, extraire_cle
from config import (
    salutations,
    commandes_memoire,
    formes_connaitre,
    formes_question,
    formes_rappeler,
    formes_oublie,
    formes_apprendre,
    mots_inutiles,
    cles_feminines,
    commandes_aide
)

class Roy:
    def __init__(self):
        self.nom = "Roy"
        self.charger_memoire()

    def se_presenter(self):
        print("Bonjour ! Je m'appelle", self.nom + ".")

    def verifier_texte(self, texte):
        if not texte.strip():
            raise ValueError("Le texte ne peut pas être vide.")

    def charger_memoire(self):
        try:
            with open("memoire.json", "r", encoding="utf-8") as fichier:
                self.memoire = json.load(fichier)                
        except FileNotFoundError:
            self.memoire = {}
        except json.JSONDecodeError as erreur:
            print("Roy : Ma mémoire semble endommagée.")
            print(erreur)
            self.memoire = {}        

    def saluer(self):
        print("Roy : Bonjour", self.memoire.get("nom", "utilisateur"), "!")

    def se_presenter_utilisateur(self):
        print("Enchanté", self.memoire.get("nom", "utilisateur"), "!")

    def reagir_humeur(self):
        humeur = self.memoire.get("humeur")
        
        if humeur is None:
            print("Roy : Je ne connais pas encore ton humeur")
        elif humeur == "bien":
            print("Roy : Je suis content de l'apprendre !")
        elif humeur == "mal":
            print("Roy : Désolé de l'apprendre. J'espère que ça ira mieux.")
        elif humeur == "fatigué":
            print("Roy : Tu devrais peut-être te reposer un peu.")
        else:
            print("Roy : D'accord, merci de me l'avoir dit.")

    def sauvegarder_memoire(self):                              
        try:
            with open("memoire.json", "w", encoding="utf-8") as fichier:
                json.dump(self.memoire, fichier, ensure_ascii=False, indent=4)
            return True
        except OSError:
            print("Roy : Impossible de sauvegarder ma mémoire.")
            return False
        
    def apprendre(self, cle, valeur):
        cle_existait = cle in self.memoire

        if cle_existait:
            ancienne_valeur = self.memoire[cle]

            if ancienne_valeur == valeur:
                print("Roy : Je connaissais déjà exactement cette information.")
                return

            print("Roy : J'ai remplacé", ancienne_valeur, "par", valeur)
        else:
            print("Roy : J'ai appris une nouvelle information.")

        self.memoire[cle] = valeur

        if self.sauvegarder_memoire():
            print("Roy : Mémoire sauvegardée")
            return True
        
        if cle_existait:
            self.memoire[cle] = ancienne_valeur
        else:
            del self.memoire[cle]

        print("Roy : La modification a été annulée.")
        return False

    def rappeler(self, cle):
        if cle in self.memoire:
            print("Roy :", self.memoire[cle])
        else:
            print("Roy : Je n'ai aucune information sur", cle)

    def oublier(self, cle):
        if cle in self.memoire:
            while True:
                reponse = nettoyer_texte(
                   input("Roy : Es-tu sûr de vouloir oublier " + cle + " ? ")
                )

                if reponse == "oui": 
                    ancienne_valeur = self.memoire[cle]   
                    del self.memoire[cle]

                    if self.sauvegarder_memoire():                        
                        print("Roy : J'ai oublié", cle)                    
                        break
                    else:
                        self.memoire[cle] = ancienne_valeur
                        print("Roy : Oublie de l'information échoué.")
                        break

                elif reponse == "non":
                    print("Roy : D'accord, je garde cette information.")
                    break

                else:
                    print("Roy : Réponds par oui ou non.")
        
        else:
            print("Roy : Je ne connaissais pas", cle)

    def afficher_memoire(self):
        print("Roy : Voici ce que je sais sur toi :")
        for numero, (cle, valeur) in enumerate(self.memoire.items(), start=1):
            print(numero, cle, ":", valeur)

    def compter_memoire(self):
        nombre = self.obtenir_nombre_informations()

        if nombre == 1:
            print("Roy : Je connais 1 information sur toi.")
        else:
            print("Roy : Je connais", nombre, "informations sur toi.")

    def obtenir_nombre_informations(self):
        return len(self.memoire)

    def connaitre(self, cle):
        if cle in self.memoire:
            valeur = self.memoire[cle]

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
                   self.apprendre(cle, valeur)
                   break
            
               elif reponse == "non":
                   print("Roy : D'accord, je n'apprendrai pas cette information.")
                   break
            
               else:
                   print("Roy : Je n'ai pas compris. Réponds par oui ou non.")

    def traiter_apprentissage(self, information):
        if "=" not in information:
            print("Roy : Utilise le format : clé = valeur")
            return

        cle, valeur = information.split("=", 1)
        cle = cle.strip()
        valeur = valeur.strip()

        if cle == "" or valeur == "":
            print("Roy : la clé et la valeur ne peuvent pas être vides.")
            return

        self.apprendre(cle, valeur)

    def traiter_message(self, message, message_original):

        try:
            self.verifier_texte(message)
        except ValueError as erreur:
            print("Roy :", erreur)
            return True

        if message in commandes_aide:
            print("Roy : Je peux saluer, apprendre, rappeler, oublier et afficher ma mémoire.")
            return True
    
        if message in salutations:
            self.saluer()
            return True

        elif message == "comment vas-tu":
            print("Roy : Je vais bien, merci !")
            return True

        elif "mon nom" in message:
            print("Roy : Ton nom est", self.memoire.get("nom", "utilisateur"))
            return True

        elif "mon humeur" in message:
            print("Roy : Tu m'as dit que ton humeur était", self.memoire.get("humeur", "inconnue"))
            return True

        elif message in commandes_memoire:
            self.afficher_memoire()
            return True

        elif message == "combien d'informations connais-tu":
            self.compter_memoire()
            return True

        elif any(forme in message for forme in formes_rappeler):
            cle = extraire_cle(message, formes_rappeler, mots_inutiles)

            if cle is None:
                print("Roy : Quelle information veux-tu que je te rappelle ?")
            else:
                self.rappeler(cle)

            return True

        elif any(forme in message for forme in formes_oublie):
            cle = extraire_cle(message, formes_oublie, mots_inutiles)

            if cle is None:
                print("Roy : Quelle information veux-tu que j'oublie ?")
            else:
                self.oublier(cle)

            return True

        elif any(forme in message for forme in formes_connaitre):
            cle = extraire_cle(message, formes_connaitre, mots_inutiles)

            if cle is None:
                print("Roy : Dis-moi ce que tu veux savoir si je connais.")
                return True
        
            self.connaitre(cle)
            return True

        elif any(forme in message for forme in formes_question):
            cle = extraire_cle(message, formes_question, mots_inutiles)

            if cle is None:
                print("Roy : Je n'ai pas trouvé ce que tu veux connaître.")
                return True
        
            self.connaitre(cle)
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

            self.traiter_apprentissage(message_sans_roy)
            return True
             
        return False      