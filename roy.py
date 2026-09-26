import json
from collections.abc import Callable
from datetime import datetime
from typing import cast

from taches import (
    Tache,
    est_tache_valide  
)

from commandes_historique import (
    traiter_affichage_historique,
    traiter_commande_historique
)

from commandes_memoire import (
    traiter_commande_memoire
)

from commandes_systeme import (
    traiter_commande_systeme
)

from commandes_generales import (
    traiter_commande_generale
)

from commandes_conversation import (
    traiter_commande_conversation
)

from commandes_taches import (
    traiter_commande_tache
)

from outils import (
    charger_json,
    nettoyer_texte,
    formater_message_historique,
    sauvegarder_json_atomiquement,
    MessageHistorique,
    RoleHistorique,
    est_message_historique_valide,
    Memoire,
    est_memoire_valide
)

from config import (
    cles_feminines,
    commandes_rechercher_historique,    
    exemples_aide
)

class Roy:
    def __init__(
        self,
        historique_actif: bool = True,
        fichier_historique: str = "historique.json",
        fichier_memoire: str = "memoire.json",
        fichier_taches: str = "taches.json"
    ):
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
        self.historique: list[MessageHistorique] = []
        self.taches: list[Tache] = []
        self.fichier_taches = fichier_taches
        self.taches_sauvegardables = True
        self.charger_taches()
        self.fichier_historique = fichier_historique
        self.fichier_memoire = fichier_memoire
        self.memoire_sauvegardable = True
        self.memoire: Memoire = {}
        self.charger_memoire()

        self.historique_sauvegardable = True
        if self.historique_actif:
            self.charger_historique()

    def ajouter_historique(self, role: RoleHistorique, contenu: str) -> None:
        date_message = datetime.now().isoformat(
            timespec="seconds"
        )

        message: MessageHistorique = {
            "role": role,
            "content": contenu,
            "timestamp": date_message
        }

        self.historique.append(message)

    def repondre(self, contenu: str) -> None:
        self.ajouter_historique("assistant", contenu)
        self.sauvegarder_historique()
        print(f"Roy : {contenu}")

    def charger_taches(self) -> None:
        donnees, erreur = charger_json(
            self.fichier_taches,
            []
        )

        if isinstance(erreur, FileNotFoundError):
            return

        if erreur is not None:
            print("Roy : Impossible de charger mes tâches.")
            print(erreur)
            self.taches_sauvegardables = False
            return

        if (
            not isinstance(donnees, list)
            or not all(
                est_tache_valide(tache)
                for tache in donnees
            )
        ):
            print("Roy : Le format des tâches est invalide.")
            self.taches_sauvegardables = False
            return

        for tache in donnees:
            tache.setdefault(
                "priorite",
                "normale"
            )

        self.taches = cast(list[Tache], donnees)

    def sauvegarder_taches(self) -> bool:
        if not self.taches_sauvegardables:
            print("Roy : Sauvegarde bloquée : le fichier des tâches est endommagé.")
            return False

        if sauvegarder_json_atomiquement(self.fichier_taches, self.taches):
            return True

        print("Roy : Impossible de sauvegarder mes tâches.")
        return False

    def obtenir_numero_tache(self, texte_numero: str) -> int | None:
        texte_numero = texte_numero.strip()

        if not texte_numero.isdecimal():
            return None

        numero = int(texte_numero)

        if not 1 <= numero <= len(self.taches):
            return None

        return numero

    def appliquer_etat_tache(self, numero: int, action: Callable[[list[dict], int],bool]) -> bool:
        ancien_etat = self.taches[
            numero - 1
        ]["terminee"]

        if not action(self.taches, numero):
            return False

        if self.sauvegarder_taches():
            return True

        self.taches[numero - 1]["terminee"] = (
            ancien_etat
        )
        return False

    def charger_historique(self) -> None:
        donnees, erreur = charger_json(
            self.fichier_historique,
            []
        )

        if isinstance(erreur, FileNotFoundError):
            self.historique = []
            return

        if erreur is not None:
            if isinstance(erreur, json.JSONDecodeError):
                print("Roy : Mon historique semble endommagé.")
            else:
                print("Roy : Impossible de charger mon historique.")

            print(erreur)
            self.historique_sauvegardable = False
            self.historique = []
            return

        if not isinstance(donnees, list):
            print("Roy : Le format de l'historique est invalide.")
            self.historique_sauvegardable = False
            self.historique = []
            return

        historique_valide: list[MessageHistorique] = []

        for message in donnees:
            if est_message_historique_valide(message):
                historique_valide.append(
                    cast(
                        MessageHistorique,
                        message
                    )
                )
            else:
                self.historique_sauvegardable = False

        self.historique = historique_valide

    def sauvegarder_historique(self) -> bool:
        if not self.historique_actif:
            return True

        if not self.historique_sauvegardable:
            print("Roy : Sauvegarde bloquée : le fichier historique est endommagé.")
            return False

        if sauvegarder_json_atomiquement(
            self.fichier_historique,
            self.historique
        ):
            return True

        print("Roy : Impossible de sauvegarder mon historique.")
        return False    

    def afficher_historique(self, limite: int = 20) -> None:
        if not self.historique:
            print("Roy : L'historique est vide.")
            return

        print("Roy : Historique de la conversation :")

        messages_a_afficher = self.historique[-limite:]

        for message in messages_a_afficher:
            print(formater_message_historique(message))

    def traiter_historique(self, message: str) -> bool:
        return traiter_affichage_historique(self, message)

    def exporter_historique(self, nom_fichier: str = "") -> bool:
        if not self.historique:
            self.repondre("L'historique est vide.")
            return False

        if not nom_fichier:
            horodatage = datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S"
            )
            nom_fichier = (
                f"conversation_{horodatage}.txt"
            )

        try:
            with open(
                nom_fichier,
                "w",
                encoding="utf-8"
            ) as fichier:
                for message in self.historique:
                    date_brute = message.get("timestamp")

                    if isinstance(date_brute, str):
                        date = date_brute.replace("T", " ")
                    else:
                        date = "date inconnue"

                    auteur = (
                        "Toi"
                        if message["role"] == "user"
                        else "Roy"
                    )

                    contenu = message["content"]

                    fichier.write(
                        f"[{date}] {auteur} : {contenu}\n"
                    )

        except OSError:
            self.repondre(
                "Impossible d'exporter l'historique."
            )
            return False

        self.repondre(
            f"Historique exporté dans {nom_fichier}."
        )
        return True

    def rechercher_historique(self, mot_cle: str) -> None:
        mot_cle = mot_cle.strip()

        if not mot_cle:
            print("Roy : Indique un mot à rechercher.")
            return

        resultats = []

        for message in self.historique[:-1]:
            contenu = message["content"]

            if (
                message["role"] == "assistant"
                and contenu.startswith("Voici ce que je peux faire :\n")
            ):
                continue

            est_une_recherche = (
                message["role"] == "user"
                and any(
                    contenu.lower().startswith(commande)
                    for commande in commandes_rechercher_historique
                )
            )

            if est_une_recherche:
                continue

            if mot_cle.lower() in contenu.lower():
                resultats.append(message)

        if not resultats:
            print(f"Roy : Aucun message trouvé pour : {mot_cle}")
            return

        print(f"Roy : {len(resultats)} message(s) trouvé(s) pour : {mot_cle}")

        for message in resultats[-20:]:
            print(formater_message_historique(message))

    def afficher_statistiques_historique(self) -> None:
        total_messages = len(self.historique)
        messages_cyan = 0
        messages_roy = 0

        for message in self.historique:
            if message["role"] == "user":
                messages_cyan += 1

            if message["role"] == "assistant":
                messages_roy += 1

        print("Roy : Statistiques de l'historique")
        print(f"Messages totaux : {total_messages}")
        print(f"Messages de Cyan : {messages_cyan}")
        print(f"Messages de Roy : {messages_roy}")

    def se_presenter(self):
        self.repondre(f"Bonjour ! Je m'appelle {self.nom}.")

    def verifier_texte(self, texte: str) -> None:
        if not isinstance(texte, str):
            raise ValueError("Le texte doit être une chaîne de caractères.")
        if not texte.strip():
            raise ValueError("Le texte ne peut pas être vide.")

    def charger_memoire(self) -> None:
        donnees, erreur = charger_json(
            self.fichier_memoire,
            {}
        )

        if isinstance(erreur, FileNotFoundError):
            self.memoire = {}
            return

        if erreur is not None:
            if isinstance(erreur, json.JSONDecodeError):
                print("Roy : Ma mémoire semble endommagée.")
            else:
                print("Roy : Impossible de charger ma mémoire.")

            print(erreur)
            self.memoire_sauvegardable = False
            self.memoire = {}
            return

        if not est_memoire_valide(donnees):
            print("Roy : Le format de ma mémoire est invalide.")
            self.memoire_sauvegardable = False
            self.memoire = {}
            return

        self.memoire = cast(
            Memoire,
            donnees
        )

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
        if not self.memoire_sauvegardable:
            print("Roy : Sauvegarde bloquée : le fichier mémoire est endommagé.")
            return False
        
        if sauvegarder_json_atomiquement(self.fichier_memoire, self.memoire):
            return True

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

        lignes = ["Voici ce que je sais sur toi :"]

        for numero, (cle, valeur) in enumerate(self.memoire.items(), start=1):
            lignes.append(f"{numero}. {cle} : {valeur}")

        self.repondre("\n".join(lignes))

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

    def afficher_etat(self) -> list[str]:
        if self.etat["systeme"]["actif"]:
            ligne_systeme = "Système actif."
        else:
            ligne_systeme = "Système désactivé."

        if self.etat["memoire"]["active"]:
            ligne_memoire = "Mémoire activée."
        else:
            ligne_memoire = "Mémoire désactivée."

        return [ligne_systeme, ligne_memoire]
    
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
        lignes = ["Voici ce que je peux faire :"]

        for numero, commande in enumerate(exemples_aide, start=1):
            lignes.append(f"{numero}. {commande}")

        self.repondre("\n".join(lignes))
    
    @property
    def etat_memoire(self):
            if self.etat["memoire"]["active"]:
                return "active"
            else:
                return "désactivée"

    def afficher_statut(self) -> None:
        lignes = [
            "Statut du système",
            f"Nom : {self.nom}",
            f"Informations en mémoire : {self.obtenir_nombre_informations()}"
        ]

        lignes.extend(self.afficher_etat())
        self.repondre("\n".join(lignes))
        
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

    def traiter_message(self, message, message_original):

        try:
            self.verifier_texte(message)
        except ValueError as erreur:
            self.repondre(str(erreur))
            return True
                
        if traiter_commande_systeme(self, message):
            return True
                
        if not self.etat["systeme"]["actif"]:
            self.repondre("Le système est désactivé. Réactive-le pour continuer.")
            return True     
           
        if traiter_commande_generale(self, message):
            return True

        if traiter_commande_tache(self, message):
            return True

        if traiter_commande_historique(self, message):
            return True                    

        if traiter_commande_memoire(self, message, message_original):
            return True

        if traiter_commande_conversation(self, message):
            return True
        
        return False      
