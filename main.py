from roy import Roy

if __name__ == "__main__":
    roy = Roy()
    
    roy.se_presenter()
    roy.reagir_humeur()
    roy.se_presenter_utilisateur()

    while True:
        message_original = input("Toi : ")
        message = message_original.lower()
        if message.startswith("roy "):
            message = message.removeprefix("roy ")

        if message == "quitter":
            print("Roy : À bientôt !")
            break

        if roy.traiter_message(message, message_original):
            continue

        print("Roy : Je ne sais pas encore quoi répondre.")