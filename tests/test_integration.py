# ============================================
# TESTS D'INTÉGRATION
# ============================================

import unittest
import pandas as pd
import numpy as np
from datetime import datetime
from Document import RedditDocument
from Corpus import Corpus
from SearchEngine import SearchEngine

class TestIntegration(unittest.TestCase):
    """Tests d'intégration complets"""
    
    def setUp(self):
        """Initialiser pour les tests d'intégration"""
        Corpus._instance = None
        self.corpus = Corpus("MachineLearning")
        
        # Créer un corpus avec plusieurs documents
        docs = [
            ("Article sur ML", "Alice", "machine learning algorithms classification", datetime(2025, 1, 15)),
            ("Article sur DL", "Bob", "deep learning neural networks training", datetime(2025, 3, 20)),
            ("Article sur NLP", "Charlie", "natural language processing transformers", datetime(2025, 6, 10)),
            ("Article sur RL", "Diana", "reinforcement learning agents deep learning", datetime(2025, 9, 5)),
        ]
        
        for i, (title, author, text, date) in enumerate(docs, 1):
            doc = RedditDocument(
                title=title,
                authors=author,
                text=text,
                published=date,
                link=f"http://test{i}.com",
                comments_count=i*10,
                subreddit="MachineLearning"
            )
            self.corpus.id2document[i] = doc
        
        self.corpus.ndoc = len(docs)
        self.search_engine = SearchEngine(self.corpus)
    
    def test_end_to_end_search(self):
        """Test complet de recherche"""
        results = self.search_engine.search2("learning", nb_doc_retour=10)
        self.assertGreater(len(results), 0)
        self.assertLess(len(results), 5)
    
    def test_corpus_statistics(self):
        """Test des statistiques du corpus"""
        stats = self.corpus.get_stats()
        self.assertEqual(stats["num_documents"], 4)
        self.assertGreater(stats["average_document_length"], 0)
    
    def test_vocabulary_building(self):
        """Test de la construction du vocabulaire"""
        vocab = self.corpus.vocabulaire(display=False)
        self.assertGreater(len(vocab), 0)
