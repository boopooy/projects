import unittest

import pandas as pd

from geyser_analysis import filter_data, fit_linear_regression


class FilterDataTests(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame(
            {
                "duration": [2.0, 4.0, 3.0],
                "waiting": [50, 80, 70],
                "kind": ["short", "long", "long"],
            }
        )

    def test_filters_by_type_and_inclusive_ranges(self):
        filtered = filter_data(
            self.data,
            ["short", "long"],
            (2.0, 3.0),
            (50.0, 70.0),
        )

        self.assertEqual(filtered.index.tolist(), [0, 2])

    def test_empty_type_selection_returns_no_rows(self):
        filtered = filter_data(self.data, [], (1.0, 5.0), (40.0, 90.0))

        self.assertTrue(filtered.empty)


class LinearRegressionTests(unittest.TestCase):
    def test_fits_duration_from_waiting_time(self):
        data = pd.DataFrame(
            {
                "waiting": [1.0, 2.0, 3.0],
                "duration": [3.0, 5.0, 7.0],
            }
        )

        slope, intercept, r_squared = fit_linear_regression(data)

        self.assertAlmostEqual(slope, 2.0)
        self.assertAlmostEqual(intercept, 1.0)
        self.assertAlmostEqual(r_squared, 1.0)

    def test_rejects_constant_waiting_time(self):
        data = pd.DataFrame(
            {
                "waiting": [5.0, 5.0],
                "duration": [1.0, 2.0],
            }
        )

        with self.assertRaises(ValueError):
            fit_linear_regression(data)


if __name__ == "__main__":
    unittest.main()
