import pandas as pd
from Corpus import Corpus
from SearchEngine import SearchEngine
# v2
def main():

    client_id='98hIeN0Mei2sSaV3FL9W9Q'
    client_secret='kgTOjJ_slHFfJ1s8gxWma7cn5QYA3w'
    user_agent='WebScraping'
    sujet = 'MachineLearning'

    corpus = Corpus(title=sujet) # créer un objet corpus avec le titre du sujet
    #corpus.load_from_net(client_id, client_secret, user_agent) # charger les documents depuis Reddit et Arxiv
    #corpus.save_pickle(f'{sujet}_corpus.pkl') # sauvegarder le corpus dans un fichier pickle
    corpus.load_from_pickle(f'{sujet}_corpus.pkl') # recharger le corpus depuis le fichier pickle
    print(f"Corpus '{corpus.title}' chargé avec {corpus.ndoc} documents et {corpus.nauth} auteurs.")



if __name__ == "__main__":
    main()
    # Voir Notebook pour l'interface utilisateur