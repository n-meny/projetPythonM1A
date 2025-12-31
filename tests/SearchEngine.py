import numpy as np
import pandas as pd
from tqdm import tqdm
from Corpus import Corpus
import matplotlib.pyplot as plt

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
        #vec2 = np.array(vec2).reshape(-1)
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
        

 
    def search2(self, mots_cle, nb_doc_retour=5):
        """
        Fonction de recherche améliorée qui calcule la similarité cosinus entre les mots-clés et chaque document avec une barre de progression.
        Args:
            mots_cle: str - Les mots-clés de recherche
            nb_doc_retour: int - Le nombre de documents à retourner
        Returns:
            pd.DataFrame - Un DataFrame contenant les documents triés par similarité décroissante
            (ne retourne que les documents avec une similarité non nulle)

        """
        resultat = pd.DataFrame()
        matrice_csr = self.matriceRecherche.tocsr() # On reconverti la matrice pour la recherche
        mots_cle = mots_cle.lower().strip()
        mots_cle_list = mots_cle.split()

        # Barre de progression pour les mots-clés + calcul des similarités
        for mot in mots_cle_list:
            # On encodage le mot clé en vecteur TF-IDF
            vecteur_mot_cle = self.encodage_vecteur(mot).reshape(1, -1)
            # On set up une liste pour stocker les similarités
            similarites = []

            for i in tqdm(range(self.matriceRecherche.shape[0]), desc=f"Calcul des similarités pour le mot '{mot}'", unit="doc"):  
                # On extrait le vecteur du document i de la matrice TF-IDF
                #np.array(vec2).reshape(-1)
                vecteur_doc = matrice_csr[i, :].toarray().reshape(-1, 1)
                np.array(vecteur_doc).reshape(-1)
                # Calcul de la similarité cosinus
                sim = self._cosinus(vecteur_mot_cle, vecteur_doc)
                similarites.append(sim)
            
            # Ajout des similarités au DataFrame des résultats
            if resultat.empty:
                resultat = pd.DataFrame({
                    'doc_id': list(self.corpus.id2document.keys()), 
                    'similarity': similarites
                })
            else:  
                # Si le dataframe n'est pas vide, on additionne les similarités (utile pour plusieurs mots-clés)
                resultat['similarity'] = resultat['similarity'].add(similarites, fill_value=0)

        
        # Tri des résultats par similarité décroissante
        resultat = resultat.sort_values(by='similarity', ascending=False)
        resultats_non_nuls = resultat[resultat['similarity'] != 0.0]
        # Retour des nb_doc_retour premiers documents
        return resultats_non_nuls.head(nb_doc_retour)
    

    def evolution_presence_mot(self, mots):  
        """
        Trace l'évolution de la présence d'un ou plusieurs mots dans les documents.
        Args:
            mots: str ou list - Un mot ou une liste de mots à analyser
        Returns:
            dict - Un dictionnaire avec les mots comme clés et les occurrences par date comme valeurs
        Affiche un graphique de l'évolution des occurrences au fil du temps.
        """
        # Convertir en liste si c'est un seul mot
        if isinstance(mots, str):
            mots = [mots]
        # Récupérer toutes les dates de publication (déjà en timestamp)
        dates_dt = list(self.corpus.get_all_publication_dates())
        if not dates_dt:
            print("Aucune date de publication trouvée dans le corpus")
            return
        for date in dates_dt:
            if isinstance(date, str):
                date = pd.to_datetime(date)
        # Gérer la granularité de l'axe X pour limiter le nombre de dates affichées
        max_ticks = 20
        
        # Compter le nombre de dates uniques par granularité
        days = {ts.date() for ts in dates_dt}
        months = {f"{ts.year:04d}-{ts.month:02d}" for ts in dates_dt}
        years = {f"{ts.year:04d}" for ts in dates_dt}
        
        # Choisir la granularité la plus fine qui tient dans max_ticks
        if len(days) <= max_ticks:
            normalize = lambda ts: ts.date()
        elif len(months) <= max_ticks:
            normalize = lambda ts: f"{ts.year:04d}-{ts.month:02d}"
        else:
            normalize = lambda ts: f"{ts.year:04d}"
        
        # Normaliser et trier les dates uniques du corpus
        dates_corpus = sorted(set(normalize(ts) for ts in dates_dt))
        

        # Créer un dictionnaire pour chaque mot
        resultats = {}
        
        for mot in mots:
            # Initialiser avec 0 pour TOUTES les dates
            occurrences_par_date = {date: 0 for date in dates_corpus}
            
            # Parcourir tous les documents
            for doc in self.corpus.id2document.values():
                if doc.published is None:
                    continue
                
                # Normaliser la date du document
                date = normalize(doc.published)
                
                # Vérifier si le mot est dans le document 
                if mot.lower() in doc.text.lower():
                    occurrences_par_date[date] += 1
            
            resultats[mot] = occurrences_par_date
        
        # Créer le graphique
        plt.figure(figsize=(14, 6))
        
        # Tracer une courbe par mot
        for mot in mots:
            occurrences = resultats[mot]
            counts = [occurrences[date] for date in dates_corpus]
            dates_str = [str(date) for date in dates_corpus]
            
            plt.plot(dates_str, counts, marker='o', label=mot, linewidth=2)
        
        plt.title("Évolution de la présence des mots au fil du temps : " + ", ".join(mots))
        plt.xlabel("Date")
        plt.ylabel("Nombre de documents contenant le mot")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
        
        return resultats
