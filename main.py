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

    #results_search = corpus.search("learning")
    # print(results_search)
    # results_concorde = corpus.concorde("learning", taille_context=50)
    # print(results_concorde)
    # corpus.search("learning")
    # print(corpus._full_text[:500])  # afficher les 500 premiers caractères du texte complet du corpus
    # text_propre = corpus.nettoyer_texte_full_text()
    # print(text_propre[:500])  # afficher les 500 premiers caractères du texte nettoyé

    #freq = corpus.vocabulaire(True) # True en parametre pour afficher un graphique
    # print(f"Vocabulaire du corpus ({len(freq)} mots) :")
    # print(freq)
    # mat_TF_IDF = corpus.construire_matrice_tfidf() # Construction d'une matrice mot x document TF-IDF
    # print(mat_TF_IDF)


    ## Test de la classe Search Engine
    search_engine = SearchEngine(corpus)
    search_engine.load_from_pickle(f'{sujet}_corpus.pkl')
    mots_cle = input("Entrez un ou plusieurs mot clé pour la recherche: ")

    results = search_engine.search(mots_cle, nb_doc_retour=3)
    print(type(results))










if __name__ == "__main__":
    main()