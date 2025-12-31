
import unittest
import pandas as pd

from datetime import datetime
from Document import RedditDocument
from Corpus import Corpus




# ============================================
# TESTS POUR Corpus.py
# ============================================

class TestCorpus(unittest.TestCase):
    """Tests pour la classe Corpus"""
    
    def setUp(self):
        """Initialiser un corpus pour les tests"""
        # Reset singleton
        Corpus._instance = None
        
        self.corpus = Corpus("MachineLearning")
        
        # Ajouter des documents de test
        doc1 = RedditDocument(
            title="Article 1",
            authors="Author1",
            text="machine learning is great and powerful",
            published=datetime(2025, 12, 25),
            link="http://test1.com",
            comments_count=10,
            subreddit="MachineLearning"
        )
        
        doc2 = RedditDocument(
            title="Article 2",
            authors="Author2",
            text="deep learning neural networks machine",
            published=datetime(2025, 12, 28),
            link="http://test2.com",
            comments_count=20,
            subreddit="MachineLearning"
        )
        
        self.corpus.id2document[1] = doc1
        self.corpus.id2document[2] = doc2
        self.corpus.ndoc = 2
    
    def test_corpus_creation(self):
        """Tester la création d'un corpus"""
        self.assertEqual(self.corpus.title, "MachineLearning")
        self.assertEqual(self.corpus.ndoc, 2)
    
    def test_search_method(self):
        """Tester la méthode search du corpus"""
        results = self.corpus.search("machine")
        self.assertGreater(len(results), 0)
    
    def test_search_case_insensitive(self):
        """Tester que la recherche est insensible à la casse"""
        results_lower = self.corpus.search("machine")
        results_upper = self.corpus.search("MACHINE")
        self.assertEqual(len(results_lower), len(results_upper))
    
    def test_get_stats(self):
        """Tester la méthode get_stats"""
        stats = self.corpus.get_stats()
        self.assertIn("num_documents", stats)
        self.assertIn("average_document_length", stats)
        self.assertEqual(stats["num_documents"], 2)
    
    def test_get_document_stats(self):
        """Tester la méthode get_document_stats"""
        stats = self.corpus.get_document_stats()
        self.assertIn(1, stats)
        self.assertIn("title", stats[1])
        self.assertIn("length", stats[1])
    
    def test_vocabulaire(self):
        """Tester la construction du vocabulaire"""
        vocab = self.corpus.vocabulaire(display=False)
        self.assertIsInstance(vocab, pd.DataFrame)
        self.assertIn("mot", vocab.columns)
        self.assertIn("frequence", vocab.columns)
    
    def test_construire_matrice_tf(self):
        """Tester la construction de la matrice TF"""
        mat_tf = self.corpus.construire_matrice_tf()
        self.assertEqual(mat_tf.shape[0], 2)  # 2 documents
        self.assertGreater(mat_tf.shape[1], 0)  # Au moins 1 mot
    
    def test_construire_matrice_tfidf(self):
        """Tester la construction de la matrice TF-IDF"""
        mat_tfidf = self.corpus.construire_matrice_tfidf()
        self.assertEqual(mat_tfidf.shape[0], 2)  # 2 documents
        self.assertGreater(mat_tfidf.shape[1], 0)  # Au moins 1 mot
    
    def test_get_all_publication_dates(self):
        """Tester la récupération des dates de publication"""
        dates = self.corpus.get_all_publication_dates()
        self.assertEqual(len(dates), 2)
        self.assertIn(datetime(2025, 12, 25), dates)
    
    def test_concorde(self):
        """Tester la méthode concorde"""
        results = self.corpus.concorde("machine", taille_context=30)
        self.assertIsInstance(results, pd.DataFrame)
        if len(results) > 0:
            self.assertIn("contexteGauche", results.columns)
            self.assertIn("keyword", results.columns)
            self.assertIn("contexteDroite", results.columns)

