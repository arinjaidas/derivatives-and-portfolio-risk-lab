import unittest
from pricing import delta, implied_volatility, binomial_european, monte_carlo_european


class FiniteRateTests(unittest.TestCase):
    def test_nonfinite_rates_rejected_by_all_public_pricers(self):
        for function in [delta, binomial_european, monte_carlo_european]:
            for bad in [float('nan'), float('inf')]:
                with self.subTest(function=function.__name__, rate=bad):
                    with self.assertRaises(ValueError): function(100, 100, 1, bad, .2)
                with self.subTest(function=function.__name__, dividend=bad):
                    with self.assertRaises(ValueError): function(100, 100, 1, .04, .2, dividend_yield=bad)
        with self.assertRaises(ValueError): implied_volatility(10, 100, 100, 1, float('nan'))


if __name__ == '__main__': unittest.main()
