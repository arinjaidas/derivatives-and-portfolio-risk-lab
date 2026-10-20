# Results walkthrough

All values below are synthetic or illustrative workflow results.

| Calculation | Illustrative value |
| --- | --- |
| Analytical call | 9.55626 |
| Analytical put | 10.4391 |
| Binomial call | 9.55194 |
| Monte Carlo call | 9.57773 |
| Monte Carlo standard error | 0.0529321 |
| Recovered volatility | 0.25 |

The numerical and analytical call estimates are close under the common assumed model. Simulation error is distinct from uncertainty about the model itself.

![Results preview](../demo_output/payoffs.svg)

The numerical files in [demo_output](../demo_output/) are the authoritative bundled artifacts. Re-run the entry command to reproduce the workflow. Figure metadata can differ across renders even when the underlying numerical example is unchanged.
