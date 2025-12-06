from abc import ABC, abstractmethod

# Classe Document mere avec uniquement le setter authors abstrait ainsi que le constructeur
#  il devront etre reécrits dans les classes filles
class Document(ABC):
    @abstractmethod
    def __init__(self, title, authors, text, published, link, source="unknown"):
        self._title = title
        self._authors = authors
        self._text = text
        self._published = published
        self._link = link
        self._source = source

    @property
    def source(self):
        return self._source
    @source.setter
    def source(self, value):
        if not isinstance(value, str):
            raise TypeError("source must be a string")
        self._source = value.strip()
    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, value):
        if not isinstance(value, str):
            raise TypeError("title must be a string")
        self._title = value.strip()
    @property
    @abstractmethod
    def authors(self):
        return str(self._authors)
    @authors.setter
    @abstractmethod
    def authors(self, value):
        if isinstance(value, str):
            self._authors = value
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, value):
        if not isinstance(value, str):
            raise TypeError("text must be a string")
        self._text = value

    @property
    def published(self):
        return self._published
    @published.setter
    def published(self, value):
            self._published = value
            return

    @property
    def link(self):
        return self._link
    @link.setter
    def link(self, value):
        if value is None:
            self._link = ""
            return
        if not isinstance(value, str):
            raise TypeError("link must be a string or None")
        self._link = value.strip()

    def __str__(self):
        # appelé par print()
        return f"Title: {self.title}\nAuthors: {self.authors}\nPublished: {self.published}\nLink: {self.link}\n\n{self.get_summary()}"
 
    def __repr__(self):
        # appelé quand on ecrit juste le nom de l'objet
        return f"Document(title={self.title!r}, authors={self.authors!r}, published={self.published!r}, link={self.link!r}, source={self.source!r})"
    
    def get_summary(self, max_length=200):
        return self.text[:max_length] + ("..." if len(self.text) > max_length else "")
    
    def __eq__(self, other):
        if not isinstance(other, Document):
            return NotImplemented
        return (self.title == other.title and
                self.authors == other.authors and
                self.text == other.text and
                self.published == other.published and
                self.link == other.link)
     
    def get_citation(self):
        authors_str = ', '.join(self.authors)
        return f"{authors_str} ({self.published}). {self.title}. Retrieved from {self.link}"
    
# La classe RedditDocument hérite de Document et ajoute des attributs spécifiques à Reddit et leurs getters et setters
# On reécris aussi les méthodes __str__ et __repr__
class RedditDocument(Document):
    def __init__(self, title, authors, text, published, link, source="reddit", comments_count=0, subreddit=None):
        super().__init__(title, authors, text, published, link, source)
        self._comments_count = comments_count
        self._subreddit = subreddit

    @property
    def authors(self):
        return super().authors
    @authors.setter
    def authors(self, value):
        super(RedditDocument, self.__class__).authors.fset(self, value) 
        # On utilise fset pour appeler le setter de la classe mère car il est abstrait et on ne peut pas faire super().authors = value
    @property
    def comments_count(self):
        return self._comments_count

    @comments_count.setter
    def comments_count(self, value):
        if not isinstance(value, int) or value < 0:
            raise TypeError("comments_count must be a non-negative integer")
        self._comments_count = value

    @property
    def subreddit(self):
        return self._subreddit

    @subreddit.setter
    def subreddit(self, value):
        if value is None:
            self._subreddit = ""
            return
        if not isinstance(value, str):
            raise TypeError("subreddit must be a string or None")
        self._subreddit = value.strip()

    def __str__(self):
        base = super().__str__()
        extras = f"\nSubreddit: {self.subreddit}\nComments: {self.comments_count}"
        return f"{base}{extras}"
    
    def __repr__(self):
        base = super().__repr__()
        return f"{base[:-1]}, comments_count={self.comments_count!r}, subreddit={self.subreddit!r})"

# La classe ArxivDocument hérite de Document et on réécris le setter de authors pour gérer les auteurs sous forme de liste de dictionnaires /liste
class ArxivDocument(Document):
    def __init__(self, title, authors, text, published, link, source="arxiv"):
  
        # Appel du constructeur de la classe mère 
        super().__init__(title, authors, text, published, link, source)
  
    @property
    def authors(self):
        return super().authors

    @authors.setter
    def authors(self, value):
        if isinstance(value, str):
            self._authors = value
        elif isinstance(value, list):
            self._authors = ""
            for auteur in value:
                self._authors += auteur['name'] if isinstance(auteur, dict) and 'name' in auteur else str(auteur)
                self._authors += ", "
            if self._authors.endswith(", "):
                self._authors = self._authors[:-2]

        elif isinstance(value, dict):
            value = [value['name']] if 'name' in value else [str(value)]

        elif not isinstance(value, (list, tuple)):
            raise TypeError("authors must be a list/tuple of strings or a comma-separated string")


# Création d'une factory pour créer des documents en fonction de leur type, pratique pour le code dans Corpus.py
class DocumentFactory:
    @staticmethod
    def create_document(doc_type, *args, **kwargs):
        if doc_type == "reddit":
            return RedditDocument(*args, **kwargs)
        elif doc_type == "arxiv":
            return ArxivDocument(*args, **kwargs)
        else:
            raise ValueError(f"Unknown document type: {doc_type}")