"""
Tests package for FarmVille
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestConfig:
    """Configuração para testes"""
    VERBOSE = True
    SHOW_WARNINGS = False

def run_all_tests():
    """
    Executa todos os testes do package
    
    Returns:
        bool: True se todos os testes passaram, False caso contrário
    """
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(
        verbosity=2 if TestConfig.VERBOSE else 1,
        warnings='ignore' if not TestConfig.SHOW_WARNINGS else None
    )
    
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    print("🧪 Running all tests for FarmVille")
    print("=" * 60)
    
    success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed!")
        exit(0)
    else:
        print("\n❌ Some tests failed!")
        exit(1)