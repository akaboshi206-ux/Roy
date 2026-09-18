from roy import Roy
from config import (
    commandes_quitter
)

def nettoyer_message(message_original: str) -> str:
    message = " ".join(message_original.lower().split())

    if message.startswith(("roy ", "roy,", "roy :")):
        message = message.removeprefix("roy").lstrip(" ,:")

    return message

if __name__ == "__main__":
    roy = Roy()
    
    roy.se_presenter()
    roy.reagir_humeur()
    roy.se_presenter_utilisateur()

    while True:
        message_original = input("Toi : ")
        message = nettoyer_message(message_original)
        if not message:
           roy.repondre("Écris-moi quelque chose.")
           continue

        roy.ajouter_historique("user", message_original.strip())
        roy.sauvegarder_historique()

        if message in commandes_quitter:
            roy.repondre("À bientôt !")
            break

        if roy.traiter_message(message, message_original):
            continue

        roy.repondre("Je ne sais pas encore quoi répondre.")
