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
    commandes_aide,
    commandes_statut,
    commandes_activer_memoire,
    commandes_desactiver_memoire,
    commandes_basculer_memoire,
    commandes_desactiver_systeme,
    commandes_activer_systeme,
    commandes_basculer_systeme,
    formes_renommer
)

class Roy:
    def __init__(self):
        self.nom = "Roy"        
        self.etat = {
            "memoire": {
                "active": True
            },
            "systeme": {
                "actif": True
            }
        }
        self.charger_memoire()

    def se_presenter(self):
        print("Bonjour ! Je m'appelle", self.nom + ".")

    def verifier_texte(self, texte: str) -> None:
        if not isinstance(texte, str):
            raise ValueError("Le texte doit être une chaîne de caractères.")
        if not texte.strip():
            raise ValueError("Le texte ne peut pas être vide.")

    def charger_memoire(self) -> None:
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

    def sauvegarder_memoire(self) -> bool:                              
        try:
            with open("memoire.json", "w", encoding="utf-8") as fichier:
                json.dump(self.memoire, fichier, ensure_ascii=False, indent=4)
            return True
        except OSError:
            print("Roy : Impossible de sauvegarder ma mémoire.")
            return False
        
    def apprendre(self, cle: str, valeur: str):
        if not self.verifier_memoire_active():
            return False
        
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
        if not self.verifier_memoire_active():
            return
        
        if cle in self.memoire:
            print("Roy :", self.memoire[cle])
        else:
            print("Roy : Je n'ai aucune information sur", cle)

    def renommer_information(self, ancienne_cle: str, nouvelle_cle: str):
        if not self.verifier_memoire_active():
            return
        
        if ancienne_cle in self.memoire:

            if nouvelle_cle in self.memoire:
                print("Roy : Une information porte déjà ce nom.")
                return
            
            ancienne_valeur = self.memoire[ancienne_cle]
            self.memoire[nouvelle_cle] = ancienne_valeur
            del self.memoire[ancienne_cle]
            if self.sauvegarder_memoire():
                print(f"Roy : J'ai renommé {ancienne_cle} en {nouvelle_cle}.")
                return

            self.memoire[ancienne_cle] = ancienne_valeur
            del self.memoire[nouvelle_cle]
            print("Roy : Le renommage a échoué. La modification a été annulée.")

        else:
            print("Roy : Je ne connais aucune information portant ce nom.")

    def demander_confirmation(self, question: str) -> bool:
        while True:
            reponse = nettoyer_texte(
                input("Roy : " + question + " ")
            )
            if reponse == "oui":
                return True
            elif reponse == "non":
                return False
            else:
                print("Roy : Réponds par oui ou non.")

    def oublier_tout_sauf(self, cle):
        elements = cle.removeprefix("tout sauf ").split(",")
        elements_propres = [element.strip() for element in elements]
        
        nouvelle_memoire = {}
        
        for cle in self.memoire:
            if cle in elements_propres:
                nouvelle_memoire[cle] = self.memoire[cle]
        
        elements_a_garder = ", ".join(elements_propres)
        elements_inconnus = [element for element in elements_propres if element not in self.memoire]
        
        if elements_inconnus:
            print("Roy : Je ne connais pas :", ", ".join(elements_inconnus))
            return
                    
        nombre_total = len(self.memoire)
        nombre_gardes = len(nouvelle_memoire)
        nombre_supprimes = nombre_total - nombre_gardes
        
        print("Roy : Je vais conserver :", elements_a_garder)
        print("Roy :", nombre_supprimes, "informations seront supprimées.")
        
        if self.demander_confirmation(
            f"Es-tu sûr de vouloir tout oublier sauf {elements_a_garder} ?"
        ):
            ancienne_memoire = self.memoire.copy()
            self.memoire = nouvelle_memoire
            if self.sauvegarder_memoire():
                print("Roy : J'ai oublié tout sauf les informations que tu voulais garder.")
                return
        
            self.memoire = ancienne_memoire
            print("Roy : L'effacement a échoué. La mémoire a été restaurée.")
            return
        
        print("Roy : D'accord, je garde toute ma mémoire.")
        return
    
    def oublier(self, cle):
        if not self.verifier_memoire_active():
            return

        if cle.startswith("tout sauf "):
            self.oublier_tout_sauf(cle)
            return

        if cle == "tout":
            if self.demander_confirmation("Es-tu sûr de vouloir effacer toute ma mémoire ?"):
                ancienne_memoire = self.memoire.copy()
                self.memoire.clear()

                if self.sauvegarder_memoire():
                    print("Roy : Toute ma mémoire a été effacée.")
                    return

                self.memoire = ancienne_memoire
                print("Roy : L'effacement a échoué. La mémoire a été restaurée.")
                return

            return
        
        if cle in self.memoire:
            if self.demander_confirmation(f"Es-tu sûr de vouloir oublier {cle} ?"):
                ancienne_valeur = self.memoire[cle]
                del self.memoire[cle]

                if self.sauvegarder_memoire():
                    print("Roy : J'ai oublié", cle)
                    return

                self.memoire[cle] = ancienne_valeur
                print("Roy : L'oubli de l'information a échoué.")
                return

            else:
                print("Roy : D'accord, je garde cette information.")
                return

        else:
            print("Roy : Je ne connaissais pas", cle)

    def afficher_memoire(self):
        if not self.verifier_memoire_active():
            return

        print("Roy : Voici ce que je sais sur toi :")
        for numero, (cle, valeur) in enumerate(self.memoire.items(), start=1):
            print(numero, cle, ":", valeur)

    def compter_memoire(self):
        nombre = self.obtenir_nombre_informations()

        if nombre == 1:
            print("Roy : Je connais 1 information sur toi.")
        else:
            print("Roy : Je connais", nombre, "informations sur toi.")

    def mettre_a_jour_etat(self, categorie, changements):
        if not isinstance(categorie, str):
            print("Roy : La catégorie doit être du texte.")
            return

        if not isinstance(changements, dict):
            print("Roy : Les changements doivent être un dictionnaire.")
            return

        if categorie not in self.etat:
            print(f"Roy : Catégorie d'état inconnue : {categorie}")
            return
         
        self.etat[categorie].update(changements)

    def obtenir_nombre_informations(self) -> int:
        return len(self.memoire)

    def connaitre(self, cle: str) -> None:
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

    def afficher_aide(self):
        print("Roy : Voici ce que je peux faire :")
        commandes = [
            "bonjour",
            "retiens que clé = valeur",
            "rappelle-moi clé",
            "oublie clé",
            "montre ta mémoire",
            "statut",
            "active ta mémoire",
            "désactive ta mémoire",
            "bascule ta mémoire"
        ]
        for numero, commande in enumerate(commandes, start=1):
            print(f"{numero}. {commande}")
    
    @property
    def etat_memoire(self):
            if self.etat["memoire"]["active"]:
                return "active"
            else:
                return "désactivée"

    def afficher_statut(self) -> None:
        print("Roy : Statut du système")
        print(f"Nom : {self.nom}")
        print(f"Informations en mémoire : {self.obtenir_nombre_informations()}")
        print(f"Mémoire : {self.etat_memoire}")
        
    def desactiver_memoire(self):
        if not self.etat["memoire"]["active"]:
            print("Roy : Ma mémoire est déjà désactivée.")
            return

        self.mettre_a_jour_etat("memoire", {"active": False})
        print("Roy : Mémoire désactivée.")

    def basculer_memoire(self):
        self.mettre_a_jour_etat(
            "memoire",
            {"active": not self.etat["memoire"]["active"]}
        )

        if self.etat["memoire"]["active"]:
            print("Roy : Mémoire activée.")
        else:
            print("Roy : Mémoire désactivée.")

    def activer_memoire(self):
        if self.etat["memoire"]["active"]:
            print("Roy : Ma mémoire est déjà activée.")
            return
                
        self.mettre_a_jour_etat("memoire", {"active": True})
        print("Roy : Mémoire activée.")

    def verifier_memoire_active(self):
        if not self.etat["memoire"]["active"]:
            print("Roy : Ma mémoire est désactivée.")
            return False

        return True

    def desactiver_systeme(self):
        if not self.etat["systeme"]["actif"]:
            print("Roy : Le système est déjà désactivé.")
            return

        self.mettre_a_jour_etat("systeme", {"actif": False})
        print("Roy : Système désactivé.")

    def activer_systeme(self):
        if self.etat["systeme"]["actif"]:
            print("Roy : Le système est déjà actif.")
            return

        self.mettre_a_jour_etat("systeme", {"actif": True})
        print("Roy : Système activé.")

    def basculer_systeme(self):
        self.mettre_a_jour_etat(
            "systeme",
            {"actif": not self.etat["systeme"]["actif"]}
        )

        if self.etat["systeme"]["actif"]:
            print("Roy : Système activé.")
        else:
            print("Roy : Système désactivé.")

    def traiter_renommage(self, message: str):
        information = None

        for forme in formes_renommer:
            if message.startswith(forme):
                information = message.removeprefix(forme)
                break
        if information is not None:
                    if " en " in information:
                        ancienne_cle, nouvelle_cle = information.split(" en ", 1)
                        ancienne_cle = ancienne_cle.strip()
                        nouvelle_cle = nouvelle_cle.strip()
                        if not ancienne_cle or not nouvelle_cle:
                            print("Roy : Les deux noms doivent être renseignés.")
                            return True
                        self.renommer_information(ancienne_cle, nouvelle_cle)
                        return True
                    else:
                        print("Roy : Utilise le format : renomme ancienne_clé en nouvelle_clé")
                        return True
        return False

    def traiter_message(self, message, message_original):

        try:
            self.verifier_texte(message)
        except ValueError as erreur:
            print("Roy :", erreur)
            return True

        if message in commandes_activer_systeme:
            self.activer_systeme()
            return True
        
        if message in commandes_desactiver_systeme:
            self.desactiver_systeme()
            return True
        
        if message in commandes_basculer_systeme:
            self.basculer_systeme()
            return True
        
        if not self.etat["systeme"]["actif"]:
            print("Roy : Le système est désactivé. Réactive-le pour continuer.")
            return True        

        if message in commandes_aide:
            self.afficher_aide()
            return True

        if message in commandes_statut:
            self.afficher_statut()
            return True

        if message in commandes_desactiver_memoire:
            self.desactiver_memoire()
            return True

        if message in commandes_basculer_memoire:
            self.basculer_memoire()
            return True

        if message in commandes_activer_memoire:
            self.activer_memoire()
            return True  
        
        if self.traiter_renommage(message):
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