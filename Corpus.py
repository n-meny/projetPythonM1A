
from Document import Document
from Authors import Author
from datetime import datetime, timezone

#### modifier le load car il retiere le i pour arxvis alors que reddit l'a deja fait pour les auteurs !!
### passer en static chargement ??

# Un objet corpus est une collection de documents , documents = dictonnaire { id_document : objet Document }, authors = liste des auteurs uniques dans le corpus, title = titre du corpus, last_id = entier pour générer des ids uniques pour les documentss

#attributs :
# nom du corpus
# dictionnaire id2document
# dictionnaire id2author
# ndoc = nombre de documents
# nauth = nombre d'auteurs
class Corpus:
    def __init__(self, title):
        self.title = title
        self.id2document = {}
        self.id2author = {}

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
    
    def __str__(self):
            return f"Corpus(title={self.title}, num_documents={len(self.id2document)}, num_authors={len(self.id2author)})"

    def __repr__(self):
            return f"Corpus(title={self.title!r}, id2document={self.id2document!r}, id2author={self.id2author!r})"
    
    def load_from_net(self, client_id, client_secret, user_agent, sujet):
        self.title = sujet
        id2doc = {}
        id2aut = {}


        ## reddit
        import praw
        reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
        ml_subreddit = reddit.subreddit(sujet)

        for i, submission in enumerate(ml_subreddit.hot(limit=1000)):
            text = submission.selftext.replace('\n', '')
            if text != "" and len(text) > 20:
                published_utc = submission.created_utc
                published_str = datetime.fromtimestamp(published_utc, timezone.utc).strftime("%d-%m-%Y")
                id2doc[i] = Document(
                    title=submission.title,
                    authors=[submission.author.name] if submission.author else ["Auteur inconnu"],
                    text=text,
                    published=published_str,
                    link=submission.url,
                    source="reddit_" + sujet
                )

                author_name = submission.author.name if submission.author else "Auteur inconnu"
                if author_name in id2aut:
                    id2aut[author_name].add_publication(i)
                else:
                    aut = Author(name=author_name)
                    aut.add_publication(i)
                    id2aut[author_name] = aut
            dernierDocument = i
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


                authors = entry.get('author', [])
                if isinstance(authors, dict):
                    authors = [authors.get('name', 'Auteur inconnu')]
                else:
                    authors = [a.get('name', 'Auteur inconnu') for a in authors]
                id2doc[i] = Document(
                    title=entry.get('title', 'Titre inconnu'),
                    authors=authors,
                    text=entry.get('summary', '').replace('\n', ' '),
                    published=entry.get('published', 'Inconnu'),
                    link=entry.get('id', 'Inconnu'),
                    source="arxiv_" + sujet
                )

                for author_name in authors:
                    if author_name in id2aut:
                        id2aut[author_name].add_publication(i)
                    else:
                        aut = Author(name=author_name)
                        aut.add_publication(i)
                        id2aut[author_name] = aut
            self.id2document = id2doc
            self.id2author = id2aut

    def save_pickle(self, filename):
        import pickle
        with open(filename, 'wb') as f:
            pickle.dump(self, f)    

    def save_json(self, filename):
        import json

        def obj_to_dict(obj):
            if isinstance(obj, list):
                return [obj_to_dict(i) for i in obj]
            elif hasattr(obj, '__dict__'):
                d = {}
                for k, v in vars(obj).items():
                    clean_key = k.lstrip('_')  # enlève l'underscore initial
                    d[clean_key] = obj_to_dict(v)  # récursif en cas d'objets imbriqués
                return d
            elif isinstance(obj, dict):
                return {k.lstrip('_') if isinstance(k, str) else k: obj_to_dict(v) for k, v in obj.items()}
            else:
                return obj

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(obj_to_dict(self), f, ensure_ascii=False, indent=4)


    def load_from_pickle(self, filename):
        import pickle
        with open(filename, 'rb') as f:
            corpus = pickle.load(f)
        self.title = corpus.title
        self.id2document = corpus.id2document
        self.id2author = corpus.id2author

    def load_from_json(self, filename):
        import json
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.title = data['title']
        
        self.id2document = {int(k): Document(**v) for k, v in data['id2document'].items()}
        self.id2author = {k: Author(**v) for k, v in data['id2author'].items()}

    


    # méthodes :
    #dans le principal : corpus.add_document(doc) pour ajouter un document au corpus
    # methode get_author_stats() pour obtenir les stats des auteurs
    # methode get_document_stats() pour obtenir les stats des documents
    # get_stats renvoie un dictionnaire avec des infos sur le corpus (nb doc, nb auteurs, taille moyenne des doc, etc)
    # save et load pour sauvegarder et charger un corpus depuis un fichier json/csv/pickle (au choix)
