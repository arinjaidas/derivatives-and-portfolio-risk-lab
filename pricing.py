"""Clean public demonstration of the documented derivatives coursework.

European options, continuous compounding and constant volatility. This file
was reconstructed in October 2026; it is not the unrecovered 2024 source.
"""
from math import erf, exp, log, sqrt
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def normal_cdf(x): return .5 * (1 + erf(x / sqrt(2)))


def validate(spot, strike, maturity, volatility, kind):
    if not all(np.isfinite([spot, strike, maturity, volatility])):
        raise ValueError('Inputs must be finite.')
    if spot <= 0 or strike <= 0 or maturity < 0 or volatility < 0:
        raise ValueError('Positive spot/strike and nonnegative maturity/volatility required.')
    if kind not in ['call', 'put']: raise ValueError('Kind must be call or put.')


def black_scholes(spot, strike, maturity, rate, volatility, kind='call', dividend_yield=0.0):
    validate(spot, strike, maturity, volatility, kind)
    if not np.isfinite([rate, dividend_yield]).all(): raise ValueError('Rates must be finite.')
    ds, dk = spot * exp(-dividend_yield * maturity), strike * exp(-rate * maturity)
    if maturity == 0 or volatility == 0:
        return max(ds - dk, 0.0) if kind == 'call' else max(dk - ds, 0.0)
    d1 = (log(spot / strike) + (rate - dividend_yield + .5 * volatility ** 2) * maturity) / (volatility * sqrt(maturity))
    d2 = d1 - volatility * sqrt(maturity)
    if kind == 'call': return ds * normal_cdf(d1) - dk * normal_cdf(d2)
    return dk * normal_cdf(-d2) - ds * normal_cdf(-d1)


def delta(spot, strike, maturity, rate, volatility, kind='call', dividend_yield=0.0):
    validate(spot, strike, maturity, volatility, kind)
    if not np.isfinite([rate, dividend_yield]).all(): raise ValueError('Rates must be finite.')
    if maturity == 0 or volatility == 0: raise ValueError('Delta requires positive maturity and volatility.')
    d1 = (log(spot / strike) + (rate - dividend_yield + .5 * volatility ** 2) * maturity) / (volatility * sqrt(maturity))
    return exp(-dividend_yield * maturity) * (normal_cdf(d1) - (kind == 'put'))


def implied_volatility(price, spot, strike, maturity, rate, kind='call', dividend_yield=0.0):
    validate(spot, strike, maturity, 0, kind)
    if not np.isfinite([rate, dividend_yield]).all(): raise ValueError('Rates must be finite.')
    if not np.isfinite(price) or maturity == 0: raise ValueError('Finite price and positive maturity required.')
    ds, dk = spot * exp(-dividend_yield * maturity), strike * exp(-rate * maturity)
    lower = max(ds - dk, 0.0) if kind == 'call' else max(dk - ds, 0.0)
    upper = ds if kind == 'call' else dk
    if price < lower - 1e-10 or price >= upper:
        raise ValueError('Price violates finite-volatility European option bounds.')
    if abs(price - lower) <= 1e-10: return 0.0
    def objective(vol): return black_scholes(spot, strike, maturity, rate, vol, kind, dividend_yield) - price
    high = 1.0
    while objective(high) < 0 and high < 32: high *= 2
    if objective(high) < 0: raise ValueError('Could not bracket implied volatility.')
    return float(brentq(objective, 0.0, high, xtol=1e-12))


def binomial_european(spot, strike, maturity, rate, volatility, kind='call', steps=400, dividend_yield=0.0):
    validate(spot, strike, maturity, volatility, kind)
    if not np.isfinite([rate, dividend_yield]).all(): raise ValueError('Rates must be finite.')
    if not isinstance(steps, int) or steps < 1: raise ValueError('Positive integer step count required.')
    if maturity == 0 or volatility == 0:
        return black_scholes(spot, strike, maturity, rate, volatility, kind, dividend_yield)
    dt = maturity / steps
    up = exp(volatility * sqrt(dt)); down = 1 / up
    prob = (exp((rate - dividend_yield) * dt) - down) / (up - down)
    if not 0 <= prob <= 1: raise ValueError('Tree probability invalid; increase the step count.')
    terminal = spot * up ** np.arange(steps + 1) * down ** (steps - np.arange(steps + 1))
    values = np.maximum(terminal - strike, 0) if kind == 'call' else np.maximum(strike - terminal, 0)
    for _ in range(steps): values = exp(-rate * dt) * (prob * values[1:] + (1 - prob) * values[:-1])
    return float(values[0])


def monte_carlo_european(spot, strike, maturity, rate, volatility, kind='call', paths=100000, seed=20261019, dividend_yield=0.0):
    validate(spot, strike, maturity, volatility, kind)
    if not np.isfinite([rate, dividend_yield]).all(): raise ValueError('Rates must be finite.')
    if not isinstance(paths, int) or paths < 2: raise ValueError('At least two paths required.')
    z = np.random.default_rng(seed).standard_normal(paths)
    terminal = spot * np.exp((rate - dividend_yield - .5 * volatility ** 2) * maturity + volatility * sqrt(maturity) * z)
    payoff = np.maximum(terminal - strike, 0) if kind == 'call' else np.maximum(strike - terminal, 0)
    discounted = exp(-rate * maturity) * payoff
    return {'price': float(discounted.mean()), 'standard_error': float(discounted.std(ddof=1) / sqrt(paths)), 'paths': paths}


def payoff_profiles(spot=100, strike=100, maturity=1, rate=.04, volatility=.25):
    terminal = np.linspace(0, 2 * spot, 401)
    call = black_scholes(spot, strike, maturity, rate, volatility)
    put = black_scholes(spot, strike, maturity, rate, volatility, 'put')
    # Expiry P&L here subtracts nominal initial outlay, without financing costs.
    call_payoff = np.maximum(terminal - strike, 0)
    put_payoff = np.maximum(strike - terminal, 0)
    return pd.DataFrame({'terminal_spot': terminal,
        'stock_pnl': terminal - spot,
        'covered_call_pnl': terminal - spot - call_payoff + call,
        'protective_put_pnl': terminal - spot + put_payoff - put,
        'bond70_call30_terminal_value': 70 * exp(rate * maturity) + 30 / call * call_payoff})


def run(output):
    output = Path(output); output.mkdir(exist_ok=True, parents=True)
    args = dict(spot=100, strike=105, maturity=1, rate=.04, volatility=.25)
    call = black_scholes(**args); put = black_scholes(**args, kind='put')
    mc = monte_carlo_european(**args)
    result = {'synthetic': True, 'parameters': args, 'call': call, 'put': put,
        'call_delta': delta(**args), 'implied_volatility_recovered': implied_volatility(call, 100, 105, 1, .04),
        'binomial_call': binomial_european(**args), 'monte_carlo_call': mc,
        'assumptions': ['European exercise', 'constant volatility and rates', 'illustrative inputs', 'no transaction costs'],
        'provenance': 'October 2026 public reconstruction of documented 2024 coursework methods.'}
    (output / 'pricing_summary.json').write_text(json.dumps(result, indent=2))
    payoffs = payoff_profiles(); payoffs.to_csv(output / 'payoff_profiles.csv', index=False)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    payoffs.plot(x='terminal_spot', y=['stock_pnl','covered_call_pnl','protective_put_pnl'], ax=axes[0])
    payoffs.plot(x='terminal_spot', y='bond70_call30_terminal_value', ax=axes[1], legend=False)
    axes[0].set(title='Illustrative expiry P&L; no financing costs', ylabel='P&L')
    axes[1].set(title='70 bond / 30 calls: terminal value', ylabel='Value per 100 initial capital')
    for ax in axes: ax.grid(alpha=.2); ax.set_xlabel('Terminal underlying price')
    fig.suptitle('SYNTHETIC PAYOFF DEMONSTRATION'); fig.tight_layout()
    fig.savefig(output / 'payoffs.svg'); plt.close(fig)
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',default='demo_output')
    print(json.dumps(run(parser.parse_args().output),indent=2))
