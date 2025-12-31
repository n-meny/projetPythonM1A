
# ============================================
# TESTS POUR Document.py
# ============================================
import unittest
from datetime import datetime
from Document import RedditDocument, ArxivDocument, DocumentFactory



class TestRedditDocument(unittest.TestCase):
    """Tests pour la classe RedditDocument"""
    
    def setUp(self):
        """Initialiser un document Reddit pour les tests"""
        self.doc = RedditDocument(
            title="Test Article",
            authors="TestAuthor",
            text="Ceci est un test de texte pour le document Reddit",
            published=datetime(2025, 12, 29),
            link="https://reddit.com/test",
            comments_count=42,
            subreddit="MachineLearning"
        )
    
    def test_creation(self):
        """Tester la création d'un document Reddit"""
        self.assertEqual(self.doc.title, "Test Article")
        self.assertEqual(self.doc.authors, "TestAuthor")
        self.assertEqual(self.doc.comments_count, 42)
        self.assertEqual(self.doc.subreddit, "MachineLearning")
    
    def test_title_property(self):
        """Tester le setter de title"""
        self.doc.title = "Nouveau titre"
        self.assertEqual(self.doc.title, "Nouveau titre")
    
    def test_title_type_error(self):
        """Tester que title lève une exception si ce n'est pas un string"""
        with self.assertRaises(TypeError):
            self.doc.title = 123
    
    def test_comments_count_property(self):
        """Tester le setter de comments_count"""
        self.doc.comments_count = 100
        self.assertEqual(self.doc.comments_count, 100)
    
    def test_comments_count_negative_error(self):
        """Tester que comments_count ne peut pas être négatif"""
        with self.assertRaises(TypeError):
            self.doc.comments_count = -5
    
    def test_subreddit_property(self):
        """Tester le setter de subreddit"""
        self.doc.subreddit = "Python"
        self.assertEqual(self.doc.subreddit, "Python")
    
    def test_get_summary(self):
        """Tester la méthode get_summary"""
        summary = self.doc.get_summary(max_length=10)
        self.assertTrue(len(summary) <= 13)  # 10 + "..."
    
    def test_equality(self):
        """Tester l'égalité entre deux documents"""
        doc2 = RedditDocument(
            title="Test Article",
            authors="TestAuthor",
            text="Ceci est un test de texte pour le document Reddit",
            published=datetime(2025, 12, 29),
            link="https://reddit.com/test",
            comments_count=100,  # Différent mais pas comparé
            subreddit="MachineLearning"
        )
        self.assertEqual(self.doc, doc2)


class TestArxivDocument(unittest.TestCase):
    """Tests pour la classe ArxivDocument"""
    
    def setUp(self):
        """Initialiser un document ArXiv pour les tests"""
        self.doc = ArxivDocument(
            title="Test Paper",
            authors=[{"name": "Author1"}, {"name": "Author2"}],
            text="Résumé du papier arXiv",
            published="2025-12-29",
            link="https://arxiv.org/abs/test"
        )
    
    def test_creation(self):
        """Tester la création d'un document ArXiv"""
        self.assertEqual(self.doc.title, "Test Paper")
        self.assertIn("Author1", self.doc.authors)
        self.assertIn("Author2", self.doc.authors)
    
    def test_authors_from_list(self):
        """Tester que les auteurs sont bien gérés comme liste"""
        authors_str = self.doc.authors
        self.assertIsInstance(authors_str, str)
        self.assertIn("Author1", authors_str)
    
    def test_document_factory_reddit(self):
        """Tester la factory pour créer un document Reddit"""
        doc = DocumentFactory.create_document(
            "reddit",
            title="Test",
            authors="Author",
            text="Text",
            published="2025-12-29",
            link="http://test.com",
            comments_count=10
        )
        self.assertIsInstance(doc, RedditDocument)
    
    def test_document_factory_arxiv(self):
        """Tester la factory pour créer un document ArXiv"""
        doc = DocumentFactory.create_document(
            "arxiv",
            title="Test",
            authors="Author",
            text="Text",
            published="2025-12-29",
            link="http://test.com"
        )
        self.assertIsInstance(doc, ArxivDocument)