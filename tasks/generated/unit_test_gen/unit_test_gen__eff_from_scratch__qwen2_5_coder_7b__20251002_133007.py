def run_task():
    return """import unittest
    
class TestAdd(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(add(2, 3), 5)
    
    def test_negative(self):
        self.assertEqual(add(-1, -4), -5)
        
    def test_edge_zero(self):
        self.assertEqual(add(0, 0), 0)

if __name__ == '__main__':
    unittest.main()
"""