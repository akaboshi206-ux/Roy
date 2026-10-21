from roy import Roy, ArretRoyDemande
from config import (
    commandes_quitter
)

from outils import nettoyer_message

if __name__ == "__main__":
    roy = Roy()
    
    roy.se_presenter()
    roy.reagir_humeur()
    roy.se_presenter_utilisateur()

    while True:
        message_original = roy.lire_entree("Toi : ")
        message = nettoyer_message(message_original)
        if not message:
           roy.repondre("Écris-moi quelque chose.")
           continue

        roy.ajouter_historique("user", message_original.strip())
        roy.sauvegarder_historique()

        if message in commandes_quitter:
            roy.repondre("À bientôt !")
            break

        try:
            message_traite = roy.traiter_message(
                message,
                message_original
            )
        except ArretRoyDemande:
            roy.repondre("À bientôt !")
            break

        if message_traite:
            continue
        
        roy.repondre("Je ne sais pas encore quoi répondre.")
