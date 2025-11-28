import pandas as pd
from datetime import datetime, timezone
from Document import Document
from Authors import Author

import praw
import urllib.request
import xmltodict



## TD3
def scrap_reddit(client_id, client_secret, user_agent, sujet):
    import praw


    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    ml_subreddit = reddit.subreddit(sujet)

    docs = []
    for submission in ml_subreddit.hot(limit=1000):
        text = submission.selftext.replace('\n', '')
        if text != "" :
            docs.append(text)

    return pd.DataFrame(docs, columns=["selftext"]).assign(source="reddit_" + sujet)
def scrap_arxiv(sujet):
    import urllib.request
    import xmltodict



    url = f"http://export.arxiv.org/api/query?search_query=all:{sujet}&start=0&max_results=10000"

    with urllib.request.urlopen(url) as response:
        xml_data = response.read()

    data_dict = xmltodict.parse(xml_data)

    docs = []
    for entry in data_dict['feed']['entry']:
        docs.append(entry['summary'].replace('\n', ' '))

    return pd.DataFrame(docs, columns=["selftext"]).assign(source="arxiv_" + sujet)
def creation_export(client_id, client_secret, user_agent, sujet, csvpath):

    import os
    

    if os.path.exists(csvpath):
        pass   
    else :
        docs_reddit = scrap_reddit(client_id, client_secret, user_agent, sujet)
        docs_arxiv = scrap_arxiv(sujet)
        combined_docs = pd.concat([docs_reddit, docs_arxiv], ignore_index=True)
        print(combined_docs)
        combined_docs = combined_docs.reset_index(drop=True)
        combined_docs.insert(0, "id", combined_docs.index + 1)
        combined_docs.to_csv('scraped_documents.csv', index=False, sep='\t')
        combined_docs.to_pickle('scraped_documents.pkl')
        combined_docs.to_json('scraped_documents.json', orient='records', force_ascii=False, indent=2)
def analyse_statistiques(combined_docs):
    
    ### statistiques
    print("Nombre de documents scrappés :", len(combined_docs))
    print("Aperçu des documents scrappés :")
    print(combined_docs.head()) 
    #taille des documents
    combined_docs['taille'] = combined_docs['selftext'].apply(len)
    print("Taille moyenne des documents scrappés :", round(combined_docs['taille'].mean(),2), "caractères")
    print("Taille maximale des documents scrappés :", combined_docs['taille'].max(), "caractères")
    print("Taille minimale des documents scrappés :", combined_docs['taille'].min(), "caractères")
    # nombre de phrases (split au point '.')
    combined_docs['n_sentences'] = combined_docs['selftext'].apply(
        lambda s: len([seg for seg in s.split('.') if seg.strip() != ""])
    )

    # nombre de mots (split à l'espace)
    combined_docs['n_words'] = combined_docs['selftext'].apply(
        lambda s: len([w for w in s.split(' ') if w.strip() != ""])
    )

    print("Nombre total de phrases :", combined_docs['n_sentences'].sum())
    print("Nombre moyen de phrases par document :", round(combined_docs['n_sentences'].mean(), 2))
    print("Nombre minimal de phrases par document :", combined_docs['n_sentences'].min())
    print("Nombre maximal de phrases par document :", combined_docs['n_sentences'].max())

    print("Nombre total de mots :", combined_docs['n_words'].sum())
    print("Nombre moyen de mots par document :", round(combined_docs['n_words'].mean(), 2))
    print("Nombre minimal de mots par document :", combined_docs['n_words'].min())
    print("Nombre maximal de mots par document :", combined_docs['n_words'].max())
    print("Statistiques descriptives des tailles des documents scrappés :")
    print(combined_docs['taille'].describe())
    # histogramme des tailles
    import matplotlib.pyplot as plt 
    plt.hist(combined_docs['taille'], bins=50, color='blue', alpha=0.7)
    plt.hist(combined_docs['n_words'], bins=50, color='red', alpha=0.7)
    plt.hist(combined_docs['n_sentences'], bins=50, color='green', alpha=0.7)
    plt.legend(['Taille (caractères)', 'Nombre de mots', 'Nombre de phrases'])
    plt.grid(axis='y', alpha=0.75)
    plt.title('Histogramme des tailles des documents scrappés')
    plt.xlabel('Taille des documents (en caractères)')
    plt.ylabel('Nombre de documents')
    plt.show()

## TD4
def scrap_objets_document_reddit(client_id, client_secret, user_agent, sujet):
    

    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

    ml_subreddit = reddit.subreddit(sujet)

    docs = []
    for submission in ml_subreddit.hot(limit=1000):
        text = submission.selftext.replace('\n', '')
        if text != "" :
            published_utc = submission.created_utc
            published_str = datetime.fromtimestamp(published_utc, timezone.utc).strftime("%d-%m-%Y")
            doc = Document(
                title=submission.title,
                authors=[submission.author.name] if submission.author else ["Auteur inconnu"],
                text=text,
                published=published_str,
                link=submission.url,
                source="reddit_" + sujet
            )
            docs.append(doc)

    return docs
def scrap_objets_document_arxiv(sujet):

    url = f"http://export.arxiv.org/api/query?search_query=all:{sujet}&start=0&max_results=10000"

    with urllib.request.urlopen(url) as response:
        xml_data = response.read()

    data_dict = xmltodict.parse(xml_data)

    docs = []
    for entry in data_dict['feed']['entry']:

        # Gestion de la date de publication
        published_str = entry.get('published', 'Inconnu')
        if published_str != 'Inconnu':
                try:
                    # parse ISO 8601 like "2021-07-21T17:15:10Z"
                    published_dt = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
                    published_str = published_dt.strftime("%d-%m-%y")
                except ValueError:
                    try:
                        # fallback for variants; convert Z to +00:00 for fromisoformat
                        published_dt = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                        published_str = published_dt.strftime("%d-%m-%y")
                    except Exception:
                        pass 

        
        authors = entry.get('author', [])
        if isinstance(authors, dict):
            authors = [authors.get('name', 'Auteur inconnu')]
        else:
            authors = [a.get('name', 'Auteur inconnu') for a in authors]
        doc = Document(
            title=entry.get('title', 'Titre inconnu'),
            authors=authors,
            text=entry.get('summary', '').replace('\n', ' '),
            published=published_str,
            link=entry.get('id', 'Inconnu'),
            source="arxiv_" + sujet
        )
        docs.append(doc)

    return docs


def td3(client_id, client_secret, user_agent, sujet):

    csvpath = 'scraped_documents.csv'
    creation_export(client_id, client_secret, user_agent, sujet, csvpath) # Si non existant
    combined_docs = pd.read_csv('scraped_documents.csv')
    textes = combined_docs['selftext'].fillna('').str.cat(sep='.\n')
    pd.DataFrame({'textes': [textes]}).to_csv('textes_combines.txt', index=False, header=False)
    ### statistiques
    analyse_statistiques(combined_docs)
def td4_partie1(client_id, client_secret, user_agent, sujet):

    id2doc = {}
    
    docs_reddit = scrap_objets_document_reddit(client_id, client_secret, user_agent, sujet)
    docs_arxiv = scrap_objets_document_arxiv(sujet)

    for i, doc in enumerate(docs_reddit + docs_arxiv):
        id2doc[i] = doc
    
    print("Dictionnaire id2doc créé avec", len(id2doc), "documents.")

    print("Nombre d'objets Document Reddit :", len(docs_reddit))
    print("Premier document Reddit :")  
    print(docs_reddit[0])
    print("\nNombre d'objets Document Arxiv :", len(docs_arxiv))
    print("Premier document Arxiv :")  
    print(docs_arxiv[0])

    return id2doc
def td4_partie2(client_id, client_secret, user_agent, sujet):
    id2aut = {}
    id2doc = {}

    ## reddit
    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    ml_subreddit = reddit.subreddit(sujet)

    for i, submission in enumerate(ml_subreddit.hot(limit=1000)):
        text = submission.selftext.replace('\n', '')
        if text != "" :
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

    ## arxiv
    import urllib.request
    import xmltodict
    url = f"http://export.arxiv.org/api/query?search_query=all:{sujet}&start=0&max_results=10000"
    with urllib.request.urlopen(url) as response:
        xml_data = response.read()
    data_dict = xmltodict.parse(xml_data)
    for i, entry in enumerate(data_dict['feed']['entry']):
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

    print("Dictionnaire id2doc créé avec", len(id2doc), "documents.")
    print("Dictionnaire id2aut créé avec", len(id2aut), "auteurs.")
    # Affichage des statistiques pour un auteur donné
    auteur_exemple = next(iter(id2aut.values()))
    stats = auteur_exemple.statistics(id2doc)
    print("Statistiques pour l'auteur :", auteur_exemple.name)
    for key, value in stats.items():
        print(f"  {key} : {value}")

    return id2doc, id2aut

