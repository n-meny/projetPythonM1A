import re
from datetime import datetime, timezone

class Document:
    def __init__(self, title, authors, text, published, link, source="unknown"):
        self.title = title
        self.authors = authors
        self.text = text
        self.published = published
        self.link = link
        self.source = source

    @property 
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not isinstance(value, str):
            raise TypeError("title must be a string")
        self._title = value.strip()

    @property
    def authors(self):
        return str(self._authors)

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

        # formatted = None

        # # numeric values
        # if isinstance(value, (int, float)):
        #     num = int(value)
        #     if num > 9999:
        #         try:
        #             dt = datetime.fromtimestamp(num, timezone.utc)
        #             formatted = dt.strftime("%d-%m-%Y")
        #         except (OverflowError, OSError, ValueError):
        #             formatted = str(value)
        #     else:
        #         # likely a year like 2015
        #         formatted = str(num)

        # # string values
        # else:
        #     s = value.strip()
        #     # pure numeric string (timestamp or year)
        #     if re.fullmatch(r"\d+(\.\d+)?", s):
        #         try:
        #             num = int(float(s))
        #             if num > 9999:
        #                 try:
        #                     dt = datetime.fromtimestamp(num, timezone.utc)
        #                     formatted = dt.strftime("%d-%m-%Y")
        #                 except (OverflowError, OSError, ValueError):
        #                     formatted = s
        #             else:
        #                 formatted = str(num)
        #         except Exception:
        #             formatted = s
        #     else:
        #         # try ISO 8601 and other common datetime formats
        #         parsed = False
        #         try:
        #             iso = s.replace("Z", "+00:00")
        #             dt = datetime.fromisoformat(iso)
        #             formatted = dt.strftime("%d-%m-%Y")
        #             parsed = True
        #         except Exception:
        #             parsed = False

        #         if not parsed:
        #             for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        #                 try:
        #                     dt = datetime.strptime(s, fmt)
        #                     formatted = dt.strftime("%d-%m-%Y")
        #                     parsed = True
        #                     break
        #                 except Exception:
        #                     continue

        #         if not parsed:
        #             # fallback: keep original string
        #             formatted = s

        # self._published = formatted

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

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        if not isinstance(value, str):
            raise TypeError("source must be a string")
        self._source = value.strip()
    
    
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