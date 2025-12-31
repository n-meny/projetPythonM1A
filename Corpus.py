
from Document import DocumentFactory
from Authors import Author
from datetime import datetime, timezone
import re 
import pandas as pd
from scipy.sparse import csr_matrix
import numpy as np
#attributs :
# nom du corpus
# dictionnaire id2document
# dictionnaire id2author
# ndoc = nombre de documents
# nauth = nombre d'auteurs
# On ne va pas s'embêter avec des getters et setters pour l'instant 
# car les attributs ne sont jamais vraiment privés en Python


class Corpus:
    # Singleton implementation pour n'avoir qu'une seule instance de Corpus
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Corpus, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, title, id2document=None, id2author=None):
        if not hasattr(self, '_initialized') or not self._initialized:
            self._initialized = True
            self.title = title
            self.id2document = id2document if id2document is not None else {}
            self.id2author = id2author if id2author is not None else {}
            self.ndoc = len(self.id2document)
            self.nauth = len(self.id2author)
            self._full_text = None  # Pour stocker la concaténation complète

    def __str__(self):
            return f"Corpus(title={self.title}, num_documents={len(self.id2document)}, num_authors={len(self.id2author)})"

    def __repr__(self):
            return f"Corpus(title={self.title!r}, id2document={self.id2document!r}, id2author={self.id2author!r})"
    
    def get_author_stats(self):
        stats = {}
        for author in self.id2author.values():
            stats[author.name] = author.statistics(self.id2document)
        return stats

    def get_document_stats(self):
        stats = {}
        for doc_id, document in self.id2document.items():
            stats[doc_id] = {
                "title": document.title,
                "length": len(document.text),
                "num_authors": len(document.authors)
            }
        return stats

    def get_stats(self):
        total_length = sum(len(doc.text) for doc in self.id2document.values())
        avg_length = total_length / len(self.id2document) if self.id2document else 0
        return {
            "title": self.title,
            "num_documents": len(self.id2document),
            "num_authors": len(self.id2author),
            "average_document_length": avg_length
        }
    
    def load_from_net(self, client_id, client_secret, user_agent):
        
        sujet = self.title
        id2doc = {}
        id2aut = {}
        id_doc_counter = 0

        ## reddit
        import praw
        reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
        ml_subreddit = reddit.subreddit(sujet)

        for i, submission in enumerate(ml_subreddit.hot(limit=1000)):
            text = submission.selftext.replace('\n', '')
            if text != "" and len(text) > 20:
                id_doc_counter += 1
                published_utc = submission.created_utc
                published_str = datetime.fromtimestamp(published_utc, timezone.utc).strftime("%d-%m-%Y")
                id2doc[id_doc_counter] = DocumentFactory.create_document("reddit",
                    title=submission.title,
                    authors=[submission.author.name] if submission.author else ["Auteur inconnu"],
                    text=text,
                    published=published_str,
                    link=submission.url,
                    comments_count=submission.num_comments,
                    subreddit=submission.subreddit.display_name,
                    source="reddit_" + sujet
                )

                author_name = submission.author.name if submission.author else "Auteur inconnu"
                if author_name in id2aut:
                    id2aut[author_name].add_publication(id_doc_counter)
                else:
                    aut = Author(name=author_name)
                    aut.add_publication(id_doc_counter)
                    id2aut[author_name] = aut
            dernierDocument = id_doc_counter



        ## arxiv
        import urllib.request
        import xmltodict
        url = f"http://export.arxiv.org/api/query?search_query=all:{sujet}&start=0&max_results=10000"
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()
        data_dict = xmltodict.parse(xml_data)

        # ajourter les documents arxiv au corpus a partir du dernier document reddit
        for i in range(dernierDocument + 1, dernierDocument + 1 + len(data_dict['feed']['entry'])):
            entry = data_dict['feed']['entry'][i - (dernierDocument + 1)]
            text = entry.get('summary', '').replace('\n', ' ')
            if text != "" and len(text) > 20:
                id_doc_counter += 1
                # On retravaille les auteurs pour avoir une liste de noms pour le dictionnaire auteurs 
                # (sinon déja géré dans le setter de ArxivDocument)
                authors = entry.get('author', [])
                if isinstance(authors, dict):
                    authors = [authors.get('name', 'Auteur inconnu')]
                else:
                    authors = [a.get('name', 'Auteur inconnu') for a in authors]
                id2doc[id_doc_counter] = DocumentFactory.create_document("arxiv",
                    title=entry.get('title', 'Titre inconnu'),
                    authors=authors,
                    text=entry.get('summary', '').replace('\n', ' '),
                    published=entry.get('published', 'Inconnu'),
                    link=entry.get('id', 'Inconnu'),
                    source="arxiv_" + sujet
                )

                for author_name in authors:
                    if author_name in id2aut:
                        id2aut[author_name].add_publication(id_doc_counter)
                    else:
                        aut = Author(name=author_name)
                        aut.add_publication(id_doc_counter)
                        id2aut[author_name] = aut

            

        self.id2document = id2doc
        self.id2author = id2aut
        self.ndoc = len(id2doc)
        self.nauth = len(id2aut)

    def save_pickle(self, filename):
        import pickle
        with open(filename, 'wb') as f:
            pickle.dump(self, f)    

    def load_from_pickle(self, filename):
        import pickle
        with open(filename, 'rb') as f:
            corpus = pickle.load(f)
        self.title = corpus.title
        self.id2document = corpus.id2document
        self.id2author = corpus.id2author

    def search(self, mot): 
 
        if self._full_text is None:
            self._full_text = " ".join(doc.text for doc in self.id2document.values())
            # self._full_text est initialisé à None et concatène tous les textes des documents la première fois que search est appelé.​
        pattern = re.compile(r'\b' + re.escape(mot) + r'\b', re.IGNORECASE)
        
        matches = pattern.findall(self._full_text)
        return matches

    def concorde(self,mot, taille_context=30):
        
        if self._full_text is None:
            self._full_text = " ".join(doc.text for doc in self.id2document.values())
            # self._full_text est initialisé à None et concatène tous les textes des documents la première fois que search est appelé.​
            # Trouver toutes les positions du mot-clé (mot entier)
        pattern = r'\b' + re.escape(mot) + r'\b'
        # On cherche toutes les occurrences du mot avec leur position
        matches = re.finditer(pattern, self._full_text, re.IGNORECASE)
        # DataFrame pour stocker les résultats
        results = pd.DataFrame(columns=["contexteGauche", "keyword", "contexteDroite"])

        for match in matches:
            start_pos = match.start()
            end_pos = match.end()

            # Recherche du début du contexte (30 caractères avant ou jusqu'à un espace) 
            context_start = max(0, start_pos - taille_context)
            # Trouver le dernier espace avant la position cible
            space_before = self._full_text.rfind(' ', context_start, start_pos -taille_context)
            if space_before != -1:
                context_start = space_before + 1

            # Recherche de la fin du contexte (30 caractères après ou jusqu'à un espace)
            context_end = min(len(self._full_text), end_pos + taille_context)
            # Trouver le prochain espace après la position cible
            space_after = self._full_text.find(' ', end_pos + taille_context, context_end)
            if space_after != -1:
                context_end = space_after

            
            # Ajouter le résultat au DataFrame
            results.loc[len(results)] = {
                "contexteGauche": self._full_text[context_start:start_pos],
                "keyword": mot,
                "contexteDroite": self._full_text[end_pos:context_end],
            }
        return results
        
            # re.escape(keyword) permet d’échapper les caractères spéciaux du mot-clé pour éviter des erreurs dans la regex.​
            # \b garantit qu’on cherche le mot entier, pas une sous-partie.​
            # re.IGNORECASE rend la recherche insensible à la casse.​
            # re.findall retourne toutes les occurrences du mot-clé.​
    
    def nettoyer_texte_full_text(self):
        """
        Nettoie une chaîne :
          - passage en minuscules
          - remplacement des retours à la ligne
          - suppression des URLs
          - suppression de la ponctuation
          - normalisation des espaces
        """
        if self._full_text is None:
            self._full_text = " ".join(doc.text for doc in self.id2document.values())
        
        texte = self._full_text

        # minuscules
        texte_nettoye = texte.lower()
        # normalisation des sauts de ligne et tabulations
        texte_nettoye = texte_nettoye.replace("\r\n", "\n").replace("\r", "\n")
        texte_nettoye = texte_nettoye.replace("\n", " ").replace("\t", " ")
        # suppression des URLs
        texte_nettoye = re.sub(r"https?://\S+|www\.\S+", "", texte_nettoye)
        # suppression de la ponctuation (conserve lettres/chiffres/espaces)
        texte_nettoye = re.sub(r"[^\w\s]", " ", texte_nettoye, flags=re.UNICODE)
        # normalisation des espaces
        texte_nettoye = re.sub(r"\s+", " ", texte_nettoye).strip()
        
        return texte_nettoye

    # méthode interne à l'objet pour nettoyer le texte de chaque document
    def _nettoyer_texte(self, texte):
        texte_nettoye = texte.lower()
        # normalisation des sauts de ligne et tabulations
        texte_nettoye = texte_nettoye.replace("\r\n", "\n").replace("\r", "\n")
        texte_nettoye = texte_nettoye.replace("\n", " ").replace("\t", " ")
        # suppression des URLs
        texte_nettoye = re.sub(r"https?://\S+|www\.\S+", "", texte_nettoye)
        # suppression de la ponctuation (conserve lettres/chiffres/espaces)
        texte_nettoye = re.sub(r"[^\w\s]", " ", texte_nettoye, flags=re.UNICODE)
        # normalisation des espaces
        texte_nettoye = re.sub(r"\s+", " ", texte_nettoye).strip()
        return texte_nettoye
    
    def vocabulaire(self, display=False):
        """
        Construit le vocabulaire unique du corpus après nettoyage des textes.
        Retourne un DataFrame avec les mots, leur fréquence et le nombre de documents où ils apparaissent.
        """

        mot_freq = {}
        # 1 boucle pour nettoyer et avoir les mots dans chaque document
        for doc_id, document in self.id2document.items():
            texte_nettoye = self._nettoyer_texte(document.text)
            mots = texte_nettoye.split()

            # 1 boucle pour compter les fréquences 
            for mot in mots:
                if mot not in mot_freq:
                    mot_freq[mot] = {"frequence": 0, "frequence_nb_doc": set()}
                mot_freq[mot]["frequence"] += 1
                mot_freq[mot]["frequence_nb_doc"].add(doc_id)

        # Construction du DataFrame
        data = []
        for mot, data_mot in mot_freq.items():
            data.append({
                "mot": mot,
                "frequence": data_mot["frequence"],
                "frequence_nb_doc": len(data_mot["frequence_nb_doc"])
            })
        freq = pd.DataFrame(data)

        if display:
            import matplotlib.pyplot as plt
            #Liste de stopwords générés couramment utilisés en anglais (on aurait pu utiliser nltk.corpus.stopwords mais pas dans les consignes)
            stopwords = {
                "the","a","an","of","in","on","and","or","to","for","from","by","is","are","was","were","be",
                "this","that","these","those","it","its","as","at","not","no","but","if","he","she","they","we","you",
                "with","i","my","your","his","her","their","our","all","any","some","such","can","will","just",
                "so","do","does","did","about","what","which","when","where","who","whom","how","there","here",
                "have","has","had","been","more","most","other","than","then","also","into","up","down",
                "out","over","under","again","further","once","only","own","same","very","s","t","d","ll","m","o","re","ve","y",
                "like","get","make","use","used","using","one","two","new","may","time","first","last","many",
                "much","even","well","good","great","see","say","said","go","going","know","known","think","thought",
                "want","wanted","way","ways","need","needed","take","taken","come","more"
                # lettres alphabet
                "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z",
                # chiffres
                "0","1","2","3","4","5","6","7","8","9"
            }

            freq_no_stop = freq[~freq["mot"].isin(stopwords)].copy()
            top10 = freq_no_stop.sort_values("frequence", ascending=False).head(10)

            plt.figure(figsize=(8,4))
            plt.bar(top10["mot"], top10["frequence"], color="steelblue")
            plt.title("Top 10 mots (hors stopwords) - Fréquence totale")
            plt.xlabel("Mot")
            plt.ylabel("Fréquence")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            plt.figure(figsize=(8,4))
            plt.bar(top10["mot"], top10["frequence_nb_doc"], color="darkorange")
            plt.title("Top 10 mots (hors stopwords) - Nombre de documents")
            plt.xlabel("Mot")
            plt.ylabel("Nombre de documents")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()


            plt.show()

        return freq
    
    #TD7 
    def _construire_dictionnaire_vocab(self):
        # Appel de la fonction précédente pour obtenir les mots et fréquences
        df_vocab = self.vocabulaire()
        df_vocab.sort_values(by="mot", inplace=True)
        vocab = {}
        for i, row in df_vocab.iterrows():
            vocab[row["mot"]] = {
                "id": i,
                "frequence": row["frequence"],
                "frequence_nb_doc": row["frequence_nb_doc"]
            }

        return vocab
    
    def construire_matrice_tf(self):

        vocab = self._construire_dictionnaire_vocab()

        # vocab est le dictionnaire avec les mots et leurs id
        num_docs = len(self.id2document)
        num_terms = len(vocab)
        
        # Préparer les listes pour csr_matrix
        data = []
        row_indices = []
        col_indices = []
        #On récupère la liste des IDs de documents et on crée un mapping ID -> index
        doc_ids = list(self.id2document.keys())
        doc_id_to_index = {doc_id: index for index, doc_id in enumerate(doc_ids)}


        for doc_id, document in self.id2document.items():
            texte_nettoye = self._nettoyer_texte(document.text)
            mots = texte_nettoye.split()
            
            # On va recalculer la fréquence des mots dans chaque document mais cette fois dans une matrice creuse
            # On utilise vocab pour obtenir l'index de chaque mot dans la matrice   
            for mot in mots:
                if mot in vocab:
                    data.append(1)  # Incrémenter pour chaque occurrence
                    row_indices.append(doc_id_to_index[doc_id])
                    col_indices.append(vocab[mot]["id"])
        
        # Créer la matrice creuse
        mat_TF = csr_matrix((data, (row_indices, col_indices)), shape=(num_docs, num_terms))
        return mat_TF

# TFxIDF(mot,document)=TF(mot,document)×log( N/NbDoc(mot))
    def construire_matrice_tfidf(self):
        #On utilise le dictionnaire vocab qui contient "mot", "frequence", "frequence_nb_doc" et "id"
        vocab = self._construire_dictionnaire_vocab()
        # On construit la matrice TF classique
        mat_TF = self.construire_matrice_tf()
        # Nombre total de documents
        N = len(self.id2document)
        # Appliquer la formule TFxIDF
        # Calculer IDF pour chaque mot
        idf = np.array([np.log(N / info["frequence_nb_doc"]) for info in vocab.values()])
        # Appliquer IDF à chaque colonne de la matrice TF
        mat_TFxIDF = mat_TF.multiply(idf)
        return mat_TFxIDF
    

    def get_all_publication_dates(self):
        dates = []
        for document in self.id2document.values():
            if document.published:
                dates.append(document.published)

        return dates