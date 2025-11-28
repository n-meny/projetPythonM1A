import pandas as pd
import praw
from pytz import timezone
from datetime import datetime, timezone
from Document import Document
from Authors import Author
from Corpus import Corpus
from fonctions_TD3_TD4 import td3, td4_partie1, td4_partie2

def main():

    client_id='98hIeN0Mei2sSaV3FL9W9Q'
    client_secret='kgTOjJ_slHFfJ1s8gxWma7cn5QYA3w'
    user_agent='WebScraping'
    sujet = 'MachineLearning'

    ## td3
    # td3(client_id, client_secret, user_agent, sujet)
    ## td4 partie 1
    # id2doc = td4_partie1(client_id, client_secret, user_agent, sujet) # Crée le dictionnaire id2doc avec les objets Document et créé un id par doc
    ## td4 partie 2
    #id2doc, id2aut = td4_partie2(client_id, client_secret, user_agent, sujet) # Crée le dictionnaire id2doc avec les objets Document et créé un id par doc, crée le dictionnaire id2aut avec les objets Author et les ids des documents associés
    
    
    #TD5 à 7
    
    corpus = Corpus(title=sujet)
    corpus.load_from_net(client_id, client_secret, user_agent, sujet)
    print(f"Corpus '{corpus.title}' chargé avec {len(corpus.id2document)} documents et {len(corpus.id2author)} auteurs.")

if __name__ == "__main__":
    main()