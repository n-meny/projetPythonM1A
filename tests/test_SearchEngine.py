
import unittest
import pandas as pd
import numpy as np
from datetime import datetime
from Document import RedditDocument
from Corpus import Corpus
from SearchEngine import SearchEngine



# ============================================
# TESTS POUR SearchEngine.py
# ============================================

class TestSearchEngine(unittest.TestCase):
    """Tests pour la classe SearchEngine"""
    
    def setUp(self):
        """Initialiser un moteur de recherche avec corpus de test"""
        # Reset singleton
        Corpus._instance = None
        
        self.corpus = Corpus("MachineLearning")
        
        # Ajouter des documents de test
        doc1 = RedditDocument(
            title="Article 1",
            authors="Author1",
            text="machine learning is great powerful algorithm",
            published=datetime(2025, 12, 25),
            link="http://test1.com",
            comments_count=10,
            subreddit="MachineLearning"
        )
        
        doc2 = RedditDocument(
            title="Article 2",
            authors="Author2",
            text="deep learning neural networks data science",
            published=datetime(2025, 12, 28),
            link="http://test2.com",
            comments_count=20,
            subreddit="MachineLearning"
        )
        
        doc3 = RedditDocument(
            title="Article 3",
            authors="Author3",
            text="machine learning classification regression",
            published=datetime(2025, 12, 29),
            link="http://test3.com",
            comments_count=5,
            subreddit="MachineLearning"
        )
        
        self.corpus.id2document[1] = doc1
        self.corpus.id2document[2] = doc2
        self.corpus.id2document[3] = doc3
        self.corpus.ndoc = 3
        
        self.search_engine = SearchEngine(self.corpus)
    
    def test_search_engine_creation(self):
        """Tester la création d'un moteur de recherche"""
        self.assertIsNotNone(self.search_engine.corpus)
        self.assertIsNotNone(self.search_engine.matriceRecherche)
        self.assertIsNotNone(self.search_engine.vocabulaire)
    
    def test_encodage_vecteur(self):
        """Tester l'encodage d'un mot en vecteur"""
        # Mot existant
        vecteur = self.search_engine.encodage_vecteur("machine")
        self.assertEqual(len(vecteur), len(self.search_engine.vocabulaire))
        self.assertEqual(sum(vecteur), 1)  # Un seul 1 dans le vecteur
        
        # Mot inexistant
        vecteur_unknown = self.search_engine.encodage_vecteur("xyz123unknown")
        self.assertEqual(sum(vecteur_unknown), 0)  # Tous des 0
    
    def test_cosinus_similarity(self):
        """Tester le calcul de similarité cosinus"""
        # Vecteurs identiques → similarité = 1
        vec = np.array([1, 0, 0]) 
        sim = self.search_engine._cosinus(vec, vec)
        self.assertAlmostEqual(sim, 1.0, places=5)
        
        # Vecteurs orthogonaux → similarité = 0
        vec1 = np.array([1, 0, 0])
        vec2 = np.array([0, 1, 0])
        sim = self.search_engine._cosinus(vec1, vec2)
        self.assertAlmostEqual(sim, 0.0, places=5)


    def test_search_single_keyword(self):
        """Tester la recherche avec un seul mot-clé"""
        results = self.search_engine.search("machine", nb_doc_retour=5)
        self.assertIsInstance(results, pd.DataFrame)
        self.assertLessEqual(len(results), 5)
    
    def test_search2_single_keyword(self):
        """Tester la recherche améliorée avec un seul mot-clé"""
        results = self.search_engine.search2("machine", nb_doc_retour=5)
        self.assertIsInstance(results, pd.DataFrame)
        self.assertLessEqual(len(results), 5)
        # Tous les résultats doivent avoir une similarité non nulle
        if len(results) > 0:
            self.assertTrue((results['similarity'] != 0).all())
    
    def test_search2_multiple_keywords(self):
        """Tester la recherche améliorée avec plusieurs mots-clés"""
        results = self.search_engine.search2("machine learning", nb_doc_retour=5)
        self.assertIsInstance(results, pd.DataFrame)
        # Les résultats avec les deux mots doivent être mieux classés
    
    def test_search2_no_results(self):
        """Tester la recherche quand aucun document ne correspond"""
        results = self.search_engine.search2("xyzunknownword123", nb_doc_retour=5)
        self.assertEqual(len(results), 0)
    
    def test_search_result_sorting(self):
        """Tester que les résultats sont bien triés par similarité"""
        results = self.search_engine.search2("machine", nb_doc_retour=10)
        if len(results) > 1:
            # Vérifier que les similarités sont en ordre décroissant
            similarities = results['similarity'].values
            self.assertTrue(all(similarities[i] >= similarities[i+1] for i in range(len(similarities)-1)))
    
    def test_evolution_presence_mot_single_word(self):
        """Tester evolution_presence_mot avec un seul mot"""
        resultats = self.search_engine.evolution_presence_mot("machine")
        self.assertIsInstance(resultats, dict)
        self.assertIn("machine", resultats)
        self.assertGreater(len(resultats["machine"]), 0)
    
    def test_evolution_presence_mot_multiple_words(self):
        """Tester evolution_presence_mot avec plusieurs mots"""
        resultats = self.search_engine.evolution_presence_mot(["machine", "learning"])
        self.assertIsInstance(resultats, dict)
        self.assertIn("machine", resultats)
        self.assertIn("learning", resultats)
    
    def test_evolution_presence_mot_not_found(self):
        """Tester evolution_presence_mot quand le mot n'existe pas"""
        resultats = self.search_engine.evolution_presence_mot("xyzunknown")
        self.assertIsInstance(resultats, dict)
        # Le mot doit être dans le dictionnaire avec 0 occurrences
        if "xyzunknown" in resultats:
            total_occ = sum(resultats["xyzunknown"].values())
            self.assertEqual(total_occ, 0)
    
    def test_load_from_pickle(self):
        """Tester le chargement à partir d'un pickle"""
        # Sauvegarder
        print("debug")
        self.corpus.save_pickle("tests/tmp/test_corpus.pkl")
        
        # Réinitialiser
        Corpus._instance = None
        corpus_reload = Corpus("test")
        
        # Charger
        corpus_reload.load_from_pickle("tests/tmp/test_corpus.pkl")
        
        # Vérifier
        self.assertEqual(corpus_reload.title, "MachineLearning")
        self.assertEqual(len(corpus_reload.id2document), 3)

        # Nettoyer
        import os
        os.remove("tests/tmp/test_corpus.pkl")



