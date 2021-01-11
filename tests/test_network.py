import unittest
from datetime import datetime
from context import network


class MyTestCase(unittest.TestCase):
    def test_build_ga_intercity(self):
        n = network.build_ga_intercity()

        four_am = datetime.strptime("0400", "%H%M")
        eight_twenty_one_am = datetime.strptime("0821", "%H%M")
        self.assertEqual("NRCH", n.get_all_stations()[0])
        self.assertEqual("DISS", n.get_station("DISS").get_id())  # get_station for object, get_id for name string
        self.assertEqual("STWMRKT", [x.id for x in n.get_station("DISS").get_connections()][0])
        self.assertEqual(four_am, n.get_station("DISS").get_peak(n.get_station("STWMRKT"))[0][0])  # start peak
        self.assertEqual(eight_twenty_one_am, n.get_station("DISS").get_peak(n.get_station("STWMRKT"))[0][1])  # end

    def test_ga_intercity_paths(self):
        n = network.build_ga_intercity()
        path = n.find_path("NRCH", "STWMRKT")
        self.assertEqual("NRCH", path[0].get_id())
        self.assertEqual("DISS", path[1].get_id())
        self.assertEqual("STWMRKT", path[2].get_id())

    def test_ga_intercity_paths_wrong(self):
        n = network.build_ga_intercity()
        self.assertRaises(ValueError, n.find_path, "NRCH", "k")


if __name__ == '__main__':
    unittest.main()
