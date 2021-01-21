import unittest
from datetime import datetime
from context import services


class MyTestCase(unittest.TestCase):
    def test_build_ga_intercity(self):
        n = services.build_ga_intercity()

        self.assertEqual("NRCH", n.get_all_stations()[0])
        self.assertEqual("DISS", n.get_station("DISS").get_id())  # get_station for object, get_id for name string
        self.assertEqual("STWMRKT", [x.id for x in n.get_station("DISS").get_connections()][0])
        self.assertEqual("0400", n.get_station("DISS").get_peak(n.get_station("STWMRKT"))[0][0])  # start peak
        self.assertEqual("0821", n.get_station("DISS").get_peak(n.get_station("STWMRKT"))[0][1])  # end peak

    def test_ga_intercity_paths(self):
        n = services.build_ga_intercity()
        path = n.find_path("NRCH", "STWMRKT")
        self.assertEqual("NRCH", path[0].get_id())
        self.assertEqual("DISS", path[1].get_id())
        self.assertEqual("STWMRKT", path[2].get_id())

    def test_ga_intercity_paths_wrong(self):
        n = services.build_ga_intercity()
        self.assertRaises(ValueError, n.find_path, "NRCH", "k")


if __name__ == '__main__':
    unittest.main()
