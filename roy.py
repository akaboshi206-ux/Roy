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
    formes_renommer,
    commandes_historique
)

class Roy:
    def __init__(self, historique_actif: bool = True):
        self.nom = "Roy"        
        self.historique_actif = historique_actif
        self.etat = {
            "memoire": {
                "active": True
            },
            "systeme": {
                "actif": True
            }
        }
        self.historique = []
        self.charger_memoire()
        if self.historique_actif:
            self.charger_historique()

    def ajouter_historique(self, role: str, contenu: str) -> None:
        message = {
            "role": role,
            "content": contenu
        }
        self.historique.append(message)

    def repondre(self, contenu: str) -> None:
        self.ajouter_historique("assistant", contenu)
        self.sauvegarder_historique()
        print(f"Roy : {contenu}")

    def charger_historique(self) -> None:
        try:
            with open("historique.json", "r", encoding="utf-8") as fichier:
                self.historique = json.load(fichier)
        except FileNotFoundError:
            self.historique = []
        except json.JSONDecodeError as erreur:
            print("Roy : Mon historique semble endommagé.")
            print(erreur)
            self.historique = []

    def sauvegarder_historique(self) -> bool:
        if not self.historique_actif:
            return True

        try:
            with open("historique.json", "w", encoding="utf-8") as fichier:
                json.dump(
                    self.historique,
                    fichier,
                    ensure_ascii=False,
                    indent=4
                )
            return True
        except OSError:
            print("Roy : Impossible de sauvegarder mon historique.")
            return False        

    def afficher_historique(self) -> None:
        if not self.historique:
            print("Roy : L'historique est vide.")
            return

        print("Roy : Historique de la conversation :")

        for message in self.historique:
            auteur = "Toi" if message["role"] == "user" else "Roy"
            print(f"{auteur} : {message['content']}")

    def se_presenter(self):
        self.repondre(f"Bonjour ! Je m'appelle {self.nom}.")

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
        self.repondre(f"Bonjour {self.memoire.get('nom', 'utilisateur')} !")

    def se_presenter_utilisateur(self):
        self.repondre(f"Enchanté {self.memoire.get('nom', 'utilisateur')} !")

    def reagir_humeur(self):
        humeur = self.memoire.get("humeur")
        
        if humeur is None:
            self.repondre("Je ne connais pas encore ton humeur")
        elif humeur == "bien":
            self.repondre("Je suis content de l'apprendre !")
        elif humeur == "mal":
            self.repondre("Désolé de l'apprendre. J'espère que ça ira mieux.")
        elif humeur == "fatigué":
            self.repondre("Tu devrais peut-être te reposer un peu.")
        else:
            self.repondre("D'accord, merci de me l'avoir dit.")

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
                self.repondre("Je connaissais déjà exactement cette information.")
                return 
        
        self.memoire[cle] = valeur

        if self.sauvegarder_memoire():
            if cle_existait:
                self.repondre(f"J'ai remplacé {ancienne_valeur} par {valeur}")
            else:
                self.repondre("J'ai appris une nouvelle information.")

            self.repondre("Mémoire sauvegardée")
            return True
        
        if cle_existait:
            self.memoire[cle] = ancienne_valeur
        else:
            del self.memoire[cle]

        self.repondre("La modification a été annulée.")
        return False

    def rappeler(self, cle):
        if not self.verifier_memoire_active():
            return
        
        if cle in self.memoire:
            self.repondre(str(self.memoire[cle]))
        else:
            self.repondre(f"Je n'ai aucune information sur {cle}")

    def renommer_information(self, ancienne_cle: str, nouvelle_cle: str):
        if not self.verifier_memoire_active():
            return
        
        if ancienne_cle in self.memoire:

            if nouvelle_cle in self.memoire:
                self.repondre("Une information porte déjà ce nom.")
                return
            
            ancienne_valeur = self.memoire[ancienne_cle]
            self.memoire[nouvelle_cle] = ancienne_valeur
            del self.memoire[ancienne_cle]
            if self.sauvegarder_memoire():
                self.repondre(f"J'ai renommé {ancienne_cle} en {nouvelle_cle}.")
                return

            self.memoire[ancienne_cle] = ancienne_valeur
            del self.memoire[nouvelle_cle]
            self.repondre("Le renommage a échoué. La modification a été annulée.")

        else:
            self.repondre("Je ne connais aucune information portant ce nom.")

    def demander_confirmation(self, question: str) -> bool:
        self.repondre(question)

        while True:
            reponse = nettoyer_texte(input("Toi : "))
            if reponse == "oui":
                return True
            elif reponse == "non":
                return False
            else:
                self.repondre("Réponds par oui ou non.")

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
            self.repondre(f"Je ne connais pas : {', '.join(elements_inconnus)}")
            return
                    
        nombre_total = len(self.memoire)
        nombre_gardes = len(nouvelle_memoire)
        nombre_supprimes = nombre_total - nombre_gardes
        
        self.repondre(f"Je vais conserver : {elements_a_garder}")
        self.repondre(f"{nombre_supprimes} informations seront supprimées.")
        
        if self.demander_confirmation(
            f"Es-tu sûr de vouloir tout oublier sauf {elements_a_garder} ?"
        ):
            ancienne_memoire = self.memoire.copy()
            self.memoire = nouvelle_memoire
            if self.sauvegarder_memoire():
                self.repondre("J'ai oublié tout sauf les informations que tu voulais garder.")
                return
        
            self.memoire = ancienne_memoire
            self.repondre("L'effacement a échoué. La mémoire a été restaurée.")
            return
        
        self.repondre("D'accord, je garde toute ma mémoire.")
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
                    self.repondre("Toute ma mémoire a été effacée.")
                    return

                self.memoire = ancienne_memoire
                self.repondre("L'effacement a échoué. La mémoire a été restaurée.")
                return

            return
        
        if cle in self.memoire:
            if self.demander_confirmation(f"Es-tu sûr de vouloir oublier {cle} ?"):
                ancienne_valeur = self.memoire[cle]
                del self.memoire[cle]

                if self.sauvegarder_memoire():
                    self.repondre(f"J'ai oublié {cle}")
                    return

                self.memoire[cle] = ancienne_valeur
                self.repondre("L'oubli de l'information a échoué.")
                return

            else:
                self.repondre("D'accord, je garde cette information.")
                return

        else:
            self.repondre(f"Je ne connaissais pas {cle}")

    def afficher_memoire(self):
        if not self.verifier_memoire_active():
            return

        self.repondre("Voici ce que je sais sur toi :")
        for numero, (cle, valeur) in enumerate(self.memoire.items(), start=1):
            self.repondre(f"{numero}. {cle} : {valeur}")

    def compter_memoire(self):
        nombre = self.obtenir_nombre_informations()

        if nombre == 1:
            self.repondre("Je connais 1 information sur toi.")
        else:
            self.repondre(f"Je connais {nombre} informations sur toi.")

    def mettre_a_jour_etat(self, categorie, changements) -> bool:
        if not isinstance(categorie, str):
            self.repondre("La catégorie doit être du texte.")
            return False

        if not isinstance(changements, dict):
            self.repondre("Les changements doivent être un dictionnaire.")
            return False

        if categorie not in self.etat:
            self.repondre(f"Catégorie d'état inconnue : {categorie}")
            return False
        
        for cle, valeur in changements.items():
            if cle not in self.etat[categorie]:
                self.repondre(f"Clé d'état inconnue : {cle}")
                return False

            if not isinstance(valeur, type(self.etat[categorie][cle])):
                self.repondre(f"Type incorrect pour la clé : {cle}")
                return False
            
        self.etat[categorie].update(changements)
        return True

    def afficher_etat(self) -> None:
        if self.etat["systeme"]["actif"]:
            self.repondre("Système actif.")
        else:
            self.repondre("Système désactivé.")

        if self.etat["memoire"]["active"]:
            self.repondre("Mémoire activée.")
        else:
            self.repondre("Mémoire désactivée.")

    def obtenir_nombre_informations(self) -> int:
        return len(self.memoire)

    def connaitre(self, cle: str) -> None:
        if cle in self.memoire:
            valeur = self.memoire[cle]

            if cle in cles_feminines:
                possessif = "ta"
            else:
                possessif = "ton"
            
            self.repondre(f"Oui, {possessif} {cle} est {valeur}.")
        else:
            self.repondre(f"Non, je ne connais encore aucune information sur {cle}.")
            self.repondre("Veux-tu me l'apprendre ?")
            
            while True:
               reponse = nettoyer_texte(input("Toi : "))
            
               if reponse == "oui":
                   self.repondre("Quelle est l'information ?")
                   valeur = nettoyer_texte(
                        input("Toi : "),
                        False
                   )
                   self.apprendre(cle, valeur)
                   break
            
               elif reponse == "non":
                   self.repondre("D'accord, je n'apprendrai pas cette information.")
                   break
            
               else:
                   self.repondre("Je n'ai pas compris. Réponds par oui ou non.")

    def traiter_apprentissage(self, information):
        if "=" not in information:
            self.repondre("Utilise le format : clé = valeur")
            return

        cle, valeur = information.split("=", 1)
        cle = cle.strip()
        valeur = valeur.strip()

        if cle == "" or valeur == "":
            self.repondre("La clé et la valeur ne peuvent pas être vides.")
            return

        self.apprendre(cle, valeur)

    def afficher_aide(self) -> None:
        self.repondre("Voici ce que je peux faire :")
        commandes = [
            "bonjour",
            "retiens que clé = valeur",
            "rappelle-moi clé",
            "oublie clé",
            "montre ta mémoire",
            "statut",
            "active ta mémoire",
            "désactive ta mémoire",
            "bascule ta mémoire",
            "active le système",
            "désactive le système",
            "bascule le système",
            "quitter"
        ]
        for numero, commande in enumerate(commandes, start=1):
            self.repondre(f"{numero}. {commande}")
    
    @property
    def etat_memoire(self):
            if self.etat["memoire"]["active"]:
                return "active"
            else:
                return "désactivée"

    def afficher_statut(self) -> None:
        self.repondre("Statut du système")
        self.repondre(f"Nom : {self.nom}")
        self.repondre(f"Informations en mémoire : {self.obtenir_nombre_informations()}")
        self.afficher_etat()
        
    def desactiver_memoire(self):
        if not self.etat["memoire"]["active"]:
            self.repondre("Ma mémoire est déjà désactivée.")
            return

        if self.mettre_a_jour_etat("memoire", {"active": False}):
            self.repondre("Mémoire désactivée.")

    def basculer_memoire(self):
        if self.mettre_a_jour_etat(
            "memoire",
            {"active": not self.etat["memoire"]["active"]}
        ):
            if self.etat["memoire"]["active"]:
                self.repondre("Mémoire activée.")
            else:
                self.repondre("Mémoire désactivée.")

    def activer_memoire(self):
        if self.etat["memoire"]["active"]:
            self.repondre("Ma mémoire est déjà activée.")
            return
                
        if self.mettre_a_jour_etat("memoire", {"active": True}):
            self.repondre("Mémoire activée.")

    def verifier_memoire_active(self):
        if not self.etat["memoire"]["active"]:
            self.repondre("Ma mémoire est désactivée.")
            return False

        return True

    def desactiver_systeme(self):
        if not self.etat["systeme"]["actif"]:
            self.repondre("Le système est déjà désactivé.")
            return

        if self.mettre_a_jour_etat("systeme", {"actif": False}):
            self.repondre("Système désactivé.")

    def activer_systeme(self):
        if self.etat["systeme"]["actif"]:
            self.repondre("Le système est déjà actif.")
            return

        if self.mettre_a_jour_etat("systeme", {"actif": True}):
            self.repondre("Système activé.")

    def basculer_systeme(self):
        if self.mettre_a_jour_etat(
            "systeme",
            {"actif": not self.etat["systeme"]["actif"]}
        ):
            if self.etat["systeme"]["actif"]:
                self.repondre("Système activé.")
            else:
                self.repondre("Système désactivé.")

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
                            self.repondre("Les deux noms doivent être renseignés.")
                            return True
                        self.renommer_information(ancienne_cle, nouvelle_cle)
                        return True
                    else:
                        self.repondre("Utilise le format : renomme ancienne_clé en nouvelle_clé")
                        return True
        return False

    def traiter_message(self, message, message_original):

        try:
            self.verifier_texte(message)
        except ValueError as erreur:
            self.repondre(str(erreur))
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

        if message in commandes_statut:
            self.afficher_statut()
            return True
        
        if not self.etat["systeme"]["actif"]:
            self.repondre("Le système est désactivé. Réactive-le pour continuer.")
            return True        

        if message in commandes_aide:
            self.afficher_aide()
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

        if message in commandes_historique:
            self.afficher_historique()
            return True 
        
        if self.traiter_renommage(message):
            return True
        
        if message in salutations:
            self.saluer()
            return True

        elif message == "comment vas-tu":
            self.repondre("Je vais bien, merci !")
            return True

        elif "mon nom" in message:
            self.repondre(f"Ton nom est {self.memoire.get('nom', 'utilisateur')}")
            return True

        elif "mon humeur" in message:
            self.repondre(
                f"Tu m'as dit que ton humeur était "
                f"{self.memoire.get('humeur', 'inconnue')}"
            )
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
                self.repondre("Quelle information veux-tu que je te rappelle ?")
            else:
                self.rappeler(cle)

            return True

        elif any(forme in message for forme in formes_oublie):
            cle = extraire_cle(message, formes_oublie, mots_inutiles)

            if cle is None:
                self.repondre("Quelle information veux-tu que j'oublie ?")
            else:
                self.oublier(cle)

            return True

        elif any(forme in message for forme in formes_connaitre):
            cle = extraire_cle(message, formes_connaitre, mots_inutiles)

            if cle is None:
                self.repondre("Dis-moi ce que tu veux savoir si je connais.")
                return True
        
            self.connaitre(cle)
            return True

        elif any(forme in message for forme in formes_question):
            cle = extraire_cle(message, formes_question, mots_inutiles)

            if cle is None:
                self.repondre("Je n'ai pas trouvé ce que tu veux connaître.")
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
