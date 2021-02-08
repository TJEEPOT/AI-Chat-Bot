import unittest
from context import process, services


class MyTestCase(unittest.TestCase):

    def test_transform_data_dep(self):
        data = ["201701267101240", "NRCH", "", "", "06:00", "", "", "", "", "", "06:01"]
        source, date, delay = process.entry_to_query(data)
        dest     = "DISS"
        network  = services.get_network("ga_intercity")
        path     = network.find_path(source, dest)
        stn_from = path[0]
        stn_to   = path[1]
        processed_entry    = process.query_to_input(stn_from, stn_to, date)
        self.assertEqual(["NRCH", "DISS", 4, 1, 0, 6], processed_entry)

    def test_transform_data_arrived_next_day(self):
        data = ["201810097681184", "SHENFLD", "23:54:30", "", "", "", "", "", "00:00", "", ""]
        source, date, delay = process.entry_to_query(data)
        dest     = "STFD"
        network  = services.get_network("ga_intercity")
        path     = network.find_path(source, dest)
        stn_from = path[0]
        stn_to   = path[1]
        processed_entry = process.query_to_input(stn_from, stn_to, date)

        self.assertEqual(["SHENFLD", "STFD", 2, 1, 1, 23], processed_entry)
        self.assertEqual(6, delay)

    def test_transform_data_arrived_prev_day(self):
        data = ["201810097681184", "STFD", "00:01:30", "", "", "", "", "", "23:59", "", ""]
        source, date, delay = process.entry_to_query(data)
        dest     = "LIVST"
        network  = services.get_network("ga_intercity")
        path     = network.find_path(source, dest)
        stn_from = path[0]
        stn_to   = path[1]
        processed_entry = process.query_to_input(stn_from, stn_to, date)

        self.assertEqual(["STFD", "LIVST", 2, 1, 1, 0], processed_entry)
        self.assertEqual(-2, delay)

    def test_user_to_query_adj(self):
        # testing adjacent stations
        delay = process.user_to_query("DISS", "STWMRKT", 2)
        print(delay)
        self.assertGreaterEqual(4, delay)

    def test_user_to_query_to_london(self):
        delay = process.user_to_query("STWMRKT", "STFD", 3)
        print(delay)
        self.assertGreaterEqual(8, delay)

    def test_user_to_query_to_norwich(self):
        delay = process.user_to_query("SHENFLD", "NRCH", 3)
        print(delay)
        self.assertGreaterEqual(12, delay)

    def test_user_to_query_full_journey(self):
        delay = process.user_to_query("NRCH", "LIVST", 2)
        print(delay)
        self.assertGreaterEqual(12, delay)

    def test_user_to_query_large_delay(self):
        delay = process.user_to_query("IPSWICH", "STFD", 20)
        print(delay)
        self.assertGreaterEqual(30, delay)

    def test_user_to_query_huge_delay(self):
        delay = process.user_to_query("IPSWICH", "STFD", 50)
        # might as well wait for another train.
        print(delay)
        self.assertGreaterEqual(60, delay)

    def test_user_to_query_no_delay(self):
        delay = process.user_to_query("IPSWICH", "STFD", 0)
        # might as well wait for another train.
        print(delay)
        self.assertGreaterEqual(3, delay)

    # dropping the rest of these tests for now since they need to be rewritten as above to work right now,
    # but I'll be making changes to process_data.py soon to remove the network requirement from query_to_input

    # def test_transform_data_pass(self):
    #     data = ["201701267101240", "MANRPK", "", "06:00", "", "", "", "", "", "06:01", ""]
    #     transformed_data, flag = prep.transform(data, True)
    #     self.assertEqual(["MANRPK", 4, 1, 0, 6, 1], transformed_data)
    #     self.assertEqual(True, flag)
    #
    # def test_transform_data_arr(self):
    #     data = ["201701267101240", "LIVST", "07:35", "", "", "", "", "", "07:36", "", ""]
    #     transformed_data, flag = prep.transform(data, True)
    #     self.assertEqual(["LIVST", 4, 1, 0, 7, 1], transformed_data)
    #     self.assertEqual(True, flag)
    #
    # def test_transform_data_no_time(self):
    #     data = ["201701267101240", "DISS", "07:20", "", "", "", "", "", "", "", ""]  # cancelled train
    #     transformed_data, flag = prep.transform(data)
    #     self.assertEqual(["DISS", 4, 1, 1, 7, 30], transformed_data)
    #     self.assertEqual(False, flag)
    #
    # def test_transform_negative_delay(self):
    #     data = ["201701267101240", "NRCH", "", "", "06:00", "", "", "", "", "", "05:57"]
    #     transformed_data, flag = prep.transform(data, False)  # also testing NRCH flag setting peak/off-peak
    #     self.assertEqual(["NRCH", 4, 1, 0, 6, -3], transformed_data)
    #     self.assertEqual(True, flag)
    #
    # def test_transform_saturday(self):
    #     data = ["201701287101240", "NRCH", "", "", "06:00", "", "", "", "", "", "06:10"]
    #     transformed_data, flag = prep.transform(data, False)  # test flag doesn"t set on weekend
    #     self.assertEqual(["NRCH", 6, 0, 1, 6, 10], transformed_data)
    #     self.assertEqual(False, flag)
    #
    # def test_transform_predicted_time(self):
    #     data = ["201701287101240", "BOWJ", "", "14:23", "", "", "15:26", "", "", "", ""]
    #     transformed_data, flag = prep.transform(data, False)
    #     self.assertEqual(["BOWJ", 6, 0, 1, 14, 63], transformed_data)  # also testing over one hour late and afternoon
    #     self.assertEqual(False, flag)
    #
    # def test_write_to_db_new_table(self):
    #     data = [["NRCH", 6, 0, 1, 6, 10]]
    #     added_rows = prep.write_to_db("new_table", data)
    #     self.assertEqual(1, added_rows)
    #
    # def test_write_to_db_existing_table(self):
    #     data = [["NRCH", 4, 1, 0, 6, -3], ["LIVST", 4, 1, 0, 7, 1]]
    #     added_rows = prep.write_to_db("new_table", data)
    #     self.assertEqual(2, added_rows)
    #
    # def test_drop_table(self):
    #     dropped = prep.drop_table("new_table")
    #     self.assertEqual(True, dropped)

if __name__ == "__main__":
    unittest.main()
