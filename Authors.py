# Name, nb publi, liste des ids des documents
import matplotlib.pyplot as plt
class Author:
    def __init__(self, name,nb_publications=0, document_ids=None):
        self.name = name
        self.nb_publications = nb_publications
        self.document_ids = document_ids if document_ids is not None else []

    def add_publication(self, document_id):
        self.nb_publications += 1
        self.document_ids.append(document_id)

    def __repr__(self):
        return f"Author(name={self.name}, nb_publications={self.nb_publications}, document_ids={self.document_ids})"
    
    def __str__(self):
        return f"{self.name} ({self.nb_publications} publications)"
    
    def statistics(self, id2doc):
        total_length = 0
        for doc_id in self.document_ids:
            doc = id2doc.get(doc_id)
            if doc:
                total_length += len(doc.text)
        avg_length = total_length / self.nb_publications if self.nb_publications > 0 else 0
        # trace graphique: nombre de publications et taille moyenne
        labels = ["Nombre de publications", "Taille moyenne des docs"]
        values = [self.nb_publications, avg_length]
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(labels, values, color=['#4C72B0', '#DD8452'])
        ax.set_title(f"Publications et taille moyenne — {self.name}")
        ax.set_ylabel("Nombre / Taille (caractères)")
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, val, f"{val:.1f}", ha='center', va='bottom')
        plt.tight_layout()
        plt.show()
        return {
            "name": self.name,
            "nb_publications": self.nb_publications,
            "taille moyenne des documents": avg_length
        }
        