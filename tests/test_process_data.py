import unittest
from context import process, services


class MyTestCase(unittest.TestCase):

    def test_read_from_csv(self):
        data = process.read_from_csv(r"..\data\scraped\processed\scraped0.csv")
        self.assertEqual("", data[1][2])

    def test_transform_data_dep(self):
        data = ["201701267101240", "NRCH", "", "", "06:00", "", "", "", "", "", "06:01"]
        source, date, delay = process.entry_to_query(data)
        dest     = "DISS"
        network  = services.get_network()
        path     = network.find_path(source, dest)
        stn_from = path[0]
        stn_to   = path[1]
        processed_entry    = process.query_to_input(stn_from, stn_to, date)
        self.assertEqual(["NRCH", "DISS", 4, 1, 0, 6], processed_entry)

    def test_transform_data_arrived_next_day(self):
        data = ["201810097681184", "STFD", "23:54:30", "", "", "", "", "", "00:00", "", ""]
        source, date, delay = process.entry_to_query(data)
        dest     = "BTHNLGR"
        network  = services.get_network()
        path     = network.find_path(source, dest)
        stn_from = path[0]
        stn_to   = path[1]
        processed_entry = process.query_to_input(stn_from, stn_to, date)

        self.assertEqual(["STFD", "BTHNLGR", 2, 1, 1, 23], processed_entry)
        self.assertEqual(6, delay)

    def test_transform_data_arrived_prev_day(self):
        data = ["201810097681184", "BTHNLGR", "00:01:30", "", "", "", "", "", "23:59", "", ""]
        source, date, delay = process.entry_to_query(data)
        dest     = "LIVST"
        network  = services.get_network()
        path     = network.find_path(source, dest)
        stn_from = path[0]
        stn_to   = path[1]
        processed_entry = process.query_to_input(stn_from, stn_to, date)

        self.assertEqual(["BTHNLGR", "LIVST", 2, 1, 1, 0], processed_entry)
        self.assertEqual(-2, delay)
        

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
