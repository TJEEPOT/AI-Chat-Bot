import unittest
from context import services


class MyTestCase(unittest.TestCase):
    def test_build_ga_intercity(self):
        n = services.get_network("ga_intercity")
        stations = n.get_all_stations()
        self.assertEqual("ga_intercity", n.get_name())
        self.assertEqual("NRCH", stations[0])
        self.assertEqual("DISS", n.get_station("DISS").get_id())  # get_station for object, get_id for name string
        self.assertEqual("STWMRKT", [x.id for x in n.get_station("DISS").get_connections()][0])
        self.assertEqual("0400", n.get_station("DISS").get_peak(n.get_station("STWMRKT"))[0][0])  # start peak
        self.assertEqual("0815", n.get_station("DISS").get_peak(n.get_station("STWMRKT"))[0][1])  # end peak

    def test_ga_intercity_paths(self):
        n = services.get_network("ga_intercity")
        path = n.find_path("NRCH", "STWMRKT")
        for station in path:
            print(station.get_id(), "connects to")
            cons = station.get_connections()
            for key in cons:
                print(key.get_id())
            print("---")
        self.assertEqual("NRCH", path[0].get_id())
        self.assertEqual("DISS", path[1].get_id())
        self.assertEqual("STWMRKT", path[2].get_id())

    def test_ga_intercity_paths_rev(self):
        n = services.get_network("ga_intercity")
        path = n.find_path("STWMRKT", "NRCH")
        for station in path:
            print(station.get_id(), "connects to")
            cons = station.get_connections()
            for key in cons:
                print(key.get_id())
            print("---")
        self.assertEqual("STWMRKT", path[0].get_id())
        self.assertEqual("DISS", path[1].get_id())
        self.assertEqual("NRCH", path[2].get_id())

    def test_ga_intercity_paths_wrong(self):
        n = services.get_network("ga_intercity")
        self.assertRaises(ValueError, n.find_path, "NRCH", "k")


if __name__ == '__main__':
    unittest.main()
