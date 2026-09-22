import json
import os
from tempfile import NamedTemporaryFile
from collections.abc import Callable, Collection
from datetime import datetime
from taches import ajouter_tache, formater_taches, terminer_tache

from outils import nettoyer_texte, extraire_cle, formater_message_historique, sauvegarder_json_atomiquement
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
    commandes_historique,
    commandes_rechercher_historique,
    commandes_statistiques_historique,
    commandes_exporter_historique,
    exemples_aide
)

CommandeAction = tuple[
    Collection[str],
    Callable[[], object]
]

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
        self.historique = []
        self.taches = []
        self.fichier_taches = fichier_taches
        self.taches_sauvegardables = True
        self.charger_taches()
        self.fichier_historique = fichier_historique
        self.fichier_memoire = fichier_memoire
        self.memoire_sauvegardable = True
        self.charger_memoire()

        self.historique_sauvegardable = True
        if self.historique_actif:
            self.charger_historique()
        self.commandes_systeme = [
            (
                commandes_activer_systeme,
                self.activer_systeme
            ),
            (
                commandes_desactiver_systeme,
                self.desactiver_systeme
            ),
            (
                commandes_basculer_systeme,
                self.basculer_systeme
            ),
            (
                commandes_statut,
                self.afficher_statut
            )
        ]
        self.commandes_simples = [
            (
                commandes_aide,
                self.afficher_aide
            ),
            (
                commandes_desactiver_memoire,
                self.desactiver_memoire
            ),
            (
                commandes_basculer_memoire,
                self.basculer_memoire
            ),
            (
                commandes_activer_memoire,
                self.activer_memoire
            ),
            (
                commandes_exporter_historique,
                self.exporter_historique
            ),
            (
                commandes_statistiques_historique,
                self.afficher_statistiques_historique
            ),
            (
                salutations,
                self.saluer
            ),
            (
                commandes_memoire,
                self.afficher_memoire
            ),
            (
                commandes_historique,
                self.afficher_historique
            ),
        ]

    def ajouter_historique(self, role: str, contenu: str) -> None:
        date_message = datetime.now().isoformat(timespec="seconds")

        message = {
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
        try:
            with open(self.fichier_taches, "r", encoding="utf-8") as fichier:
                donnees = json.load(fichier)

            if not isinstance(donnees, list) or any(
                not isinstance(tache, dict)
                or not isinstance(tache.get("description"), str)
                or not isinstance(tache.get("terminee"), bool)
                for tache in donnees
            ):
                print("Roy : Le format des tâches est invalide.")
                self.taches_sauvegardables = False
                return

            self.taches = donnees

        except FileNotFoundError:
            pass  # Première utilisation : la liste reste vide.
        except (json.JSONDecodeError, OSError) as erreur:
            print("Roy : Impossible de charger mes tâches.")
            print(erreur)
            self.taches_sauvegardables = False

    def sauvegarder_taches(self) -> bool:
        if not self.taches_sauvegardables:
            print("Roy : Sauvegarde bloquée : le fichier des tâches est endommagé.")
            return False

        if sauvegarder_json_atomiquement(self.fichier_taches, self.taches):
            return True

        print("Roy : Impossible de sauvegarder mes tâches.")
        return False

    def charger_historique(self) -> None:
        try:
            with open(self.fichier_historique, "r", encoding="utf-8") as fichier:
                donnees = json.load(fichier)

            if not isinstance(donnees, list):
                print("Roy : Le format de l'historique est invalide.")
                self.historique_sauvegardable = False
                self.historique = []
                return

            historique_valide = []
            for message in donnees:
                if (
                    isinstance(message, dict)
                    and isinstance(message.get("role"), str)
                    and isinstance(message.get("content"), str)
                ):
                    historique_valide.append(message)
                else:
                    self.historique_sauvegardable = False

            self.historique = historique_valide

        except FileNotFoundError:
            self.historique = []

        except json.JSONDecodeError as erreur:
            print("Roy : Mon historique semble endommagé.")
            print(erreur)
            self.historique_sauvegardable = False
            self.historique = []

        except OSError as erreur:
            print("Roy : Impossible de charger mon historique.")
            print(erreur)
            self.historique_sauvegardable = False
            self.historique = []

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
        for commande in commandes_historique:
            if message == commande:
                self.afficher_historique()
                return True

            prefixe = commande + " "

            if message.startswith(prefixe):
                nombre_texte = message.removeprefix(prefixe).strip()

                try:
                    limite = int(nombre_texte)
                except ValueError:
                    self.repondre(
                        "Utilise un nombre, par exemple : historique 5"
                    )
                    return True

                if limite <= 0:
                    self.repondre(
                        "Le nombre de messages doit être supérieur à zéro."
                    )
                    return True

                self.afficher_historique(limite)
                return True

        return False

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
        try:
            with open(self.fichier_memoire, "r", encoding="utf-8") as fichier:
                self.memoire = json.load(fichier)  

            if not isinstance(self.memoire, dict):
                print("Roy : Le format de ma mémoire est invalide.")
                self.memoire_sauvegardable = False
                self.memoire = {}              
        except FileNotFoundError:
            self.memoire = {}
        except json.JSONDecodeError as erreur:
            print("Roy : Ma mémoire semble endommagée.")
            self.memoire_sauvegardable = False
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

    def executer_commande(self, message: str, commandes_actions: list[CommandeAction]) -> bool:
        for formulations, action in commandes_actions:
            if message in formulations:
                action()
                return True

        return False

    def traiter_message(self, message, message_original):

        try:
            self.verifier_texte(message)
        except ValueError as erreur:
            self.repondre(str(erreur))
            return True
                
        if self.executer_commande(
            message,
            self.commandes_systeme
        ):
            return True
                
        if not self.etat["systeme"]["actif"]:
            self.repondre("Le système est désactivé. Réactive-le pour continuer.")
            return True     
           
        if self.executer_commande(
            message,
            self.commandes_simples
        ):
            return True

        if message.startswith("ajoute une tâche :"):
            description = message.removeprefix("ajoute une tâche :").strip()

            if not ajouter_tache(self.taches, description):
                self.repondre("Indique la tâche à ajouter.")
            elif self.sauvegarder_taches():
                self.repondre("Tâche ajoutée.")
            else:
                self.taches.pop()
                self.repondre("L'ajout de la tâche a été annulé.")
            return True

        if message.startswith("termine la tâche "):
            texte_numero = message.removeprefix("termine la tâche ").strip()

            if not texte_numero.isdecimal():
                self.repondre("Indique un numéro de tâche valide.")
                return True

            numero = int(texte_numero)
            if not 1 <= numero <= len(self.taches):
                self.repondre("Indique un numéro de tâche valide.")
                return True

            ancien_etat = self.taches[numero - 1]["terminee"]
            terminer_tache(self.taches, numero)

            if self.sauvegarder_taches():
                self.repondre("Tâche terminée.")
            else:
                self.taches[numero - 1]["terminee"] = ancien_etat
                self.repondre("La modification de la tâche a été annulée.")
            return True

        if message == "montre mes tâches":
            self.repondre(formater_taches(self.taches))
            return True

        for commande in commandes_rechercher_historique:
            if message.startswith(commande):
                mot_cle = message.removeprefix(commande).strip()
                self.rechercher_historique(mot_cle)
                return True 

        if self.traiter_historique(message):
            return True 
                
        if self.traiter_renommage(message):
            return True
              
        if message == "comment vas-tu":
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
