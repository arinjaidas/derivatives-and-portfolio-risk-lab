import unittest
from math import exp
from pricing import black_scholes, delta, implied_volatility, binomial_european, monte_carlo_european, payoff_profiles


class PricingChecks(unittest.TestCase):
    def test_put_call_parity(self):
        for q in [0, .02]:
            call=black_scholes(100,105,1,.04,.25,dividend_yield=q)
            put=black_scholes(100,105,1,.04,.25,'put',q)
            self.assertAlmostEqual(call-put,100*exp(-q)-105*exp(-.04),places=10)

    def test_expiry_and_zero_volatility(self):
        self.assertEqual(black_scholes(100,90,0,.04,.25),10)
        self.assertAlmostEqual(black_scholes(100,90,1,.04,0),100-90*exp(-.04))

    def test_implied_volatility_round_trip(self):
        for kind in ['call','put']:
            for vol in [.1,.25,.6]:
                price=black_scholes(100,105,1,.04,vol,kind)
                self.assertAlmostEqual(implied_volatility(price,100,105,1,.04,kind),vol,places=8)

    def test_invalid_option_price_is_rejected(self):
        with self.assertRaises(ValueError): implied_volatility(110,100,105,1,.04)

    def test_delta_matches_price_derivative(self):
        h=.001
        numerical=(black_scholes(100+h,105,1,.04,.25)-black_scholes(100-h,105,1,.04,.25))/(2*h)
        self.assertAlmostEqual(delta(100,105,1,.04,.25),numerical,places=7)

    def test_independent_numerical_methods(self):
        exact=black_scholes(100,105,1,.04,.25)
        self.assertLess(abs(binomial_european(100,105,1,.04,.25,steps=800)-exact),.03)
        mc=monte_carlo_european(100,105,1,.04,.25,paths=150000)
        self.assertLess(abs(mc['price']-exact),4*mc['standard_error'])

    def test_protective_put_floor(self):
        p=payoff_profiles()
        self.assertLess(p.loc[p.terminal_spot<=100,'protective_put_pnl'].max()-p.loc[p.terminal_spot<=100,'protective_put_pnl'].min(),1e-10)


if __name__=='__main__': unittest.main()
