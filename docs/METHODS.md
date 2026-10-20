# Methods

## Analytical valuation

For European options with continuous dividend yield q, `d1 = [ln(S/K) + (r-q+σ²/2)T] / (σ√T)` and `d2 = d1 - σ√T`. The call is `S exp(-qT) N(d1) - K exp(-rT) N(d2)`; the put uses the corresponding negative-normal probabilities. Expiry and zero-volatility cases have explicit discounted intrinsic-value limits.

Delta uses the derivative of the discounted spot term. Implied volatility is found by a bracketed Brent root search only after checking the European option bounds. Prices at an unattainable finite-volatility upper bound are rejected. Nonfinite rates and dividend yields are rejected by all public pricers.

## Independent numerical comparisons

The CRR tree uses `u=exp(σ√dt)`, `d=1/u` and risk-neutral probability `[exp((r-q)dt)-d]/(u-d)`. A probability outside zero to one is rejected rather than silently clipped. Monte Carlo samples the risk-neutral terminal lognormal distribution and discounts the payoff. Its standard error measures simulation uncertainty under the assumed model, not uncertainty about market calibration.

## Payoff interpretation

Covered-call and protective-put plots subtract nominal initial outlay. They omit financing. The 70-bond/30-call example invests 70 initial units in a growing bond and uses 30 to buy calls. Its lower payoff is the matured bond component, which need not return all 100 initial units.
