import numpy as np
import pandas as pd
from Corpus import Corpus

class SearchEngine:
    def __init__(self, corpus: Corpus):

        self.corpus = corpus
        self.matriceRecherche = corpus.construire_matrice_tfidf()
        self.vocabulaire = corpus._construire_dictionnaire_vocab()




    # On reprend les fonctions du corpus pour que ca soit plus propre à l'utilisation
    def load_from_pickle(self, filepath):
        self.corpus.load_from_pickle(filepath)
    
    def load_from_net(self, client_id, client_secret, user_agent):
        self.corpus.load_from_net(client_id, client_secret, user_agent)


    def search(self, mots_cle, nb_doc_retour=5) :

        resultat = pd.DataFrame()
        matrice_csr = self.matriceRecherche.tocsr() # On reconverti la matrice pour la recherche
        

        mots_cle = mots_cle.lower().strip()
        for mot in mots_cle.split():
            vecteur_mot_cle = self.encodage_vecteur(mot).reshape(1, -1) # On shape pour avoir un vecteur ligne et 
                                                                        # pouvoir l'utiliser dans le calcul de similarité
            #Vectorisation du mot clé
            similarites = []
            for i in range(self.matriceRecherche.shape[0]): #On parcourt chaque document
                # On extrait le vecteur du document i de la matrice TF-IDF
                vecteur_doc = matrice_csr[i, :].toarray().reshape(-1, 1) # Extraction du vecteur du document i
                # Calcul de la similarité cosinus entre le vecteur du mot clé et le vecteur du document
                sim = self._cosinus(vecteur_mot_cle, vecteur_doc)
                similarites.append(sim)
            # Ajout des similarités au DataFrame des résultats
            if resultat.empty:
                resultat = pd.DataFrame({'doc_id': list(self.corpus.id2document.keys()), 'similarity': similarites})
            else:
                resultat['similarity'] += similarites  
        # Tri des résultats par similarité décroissante
        resultat = resultat.sort_values(by='similarity', ascending=False)
        return resultat.head(nb_doc_retour)

    
    


    # calcul similarité cosinus entre vecteur mot clé et chaque document
    def _cosinus(self, vec1, vec2):
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        vec2 = np.array(vec2).reshape(-1)
        norm_vec2 = np.linalg.norm(vec2)
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0
        return dot_product / (norm_vec1 * norm_vec2)
    

    # transformer les mots clés en vecteur TF-IDF
    def encodage_vecteur(self, mot):
        # Le vecteur doit prendre des 0 jusqua l'id du mot dans le vocabulaire qui doit etre a 1
        if mot in self.vocabulaire:
            index_mot = self.vocabulaire[mot]['id']
            vecteur_mot_cle = np.zeros(len(self.vocabulaire)) # On mets des 0 partout
            vecteur_mot_cle[index_mot] = 1 # On mets un 1 a l'index du mot clé
        else:
            vecteur_mot_cle = np.zeros(len(self.vocabulaire)) # On mets des 0 partout
        
        return vecteur_mot_cle
        

        
        
# création matrice --> OK
# encodage des mots clés en vecteur --> OK
    # calcul similarité cosinus entre vecteur mot clé et chaque document
    # trier les documents par similarité décroissante
