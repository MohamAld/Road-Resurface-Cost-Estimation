import unittest
from useful_functions import inBBOX, haversine



class MyTestCase(unittest.TestCase):
    def test_something(self):
       # self.assertEqual(True, False)

         #Unit Testing of Haversine
         self.assertAlmostEqual(round(haversine(-38.2485653, 145.659277, -38.2483678, 145.6590903) * 1000), 27)
         self.assertAlmostEqual(round(haversine(-38.2514967, 145.6592619,   -38.2482551, 145.6587403) * 1000), 363)


         #Unit Testing of inBBOX
         bbox = [-38.00657835288609, 145.2217483520508, -37.99812418578717, 145.230331420898]

         self.assertFalse(inBBOX(bbox,[-38.00461849, 145.22132219]))

         self.assertTrue(inBBOX(bbox, [-38.005436266 ,145.2256142]))

         self.assertTrue(inBBOX(bbox,[-37.9996089, 145.2240466]))

         self.assertFalse(inBBOX(bbox, [20,100]))








if __name__ == '__main__':
    unittest.main()
