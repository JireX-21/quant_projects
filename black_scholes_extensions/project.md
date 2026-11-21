# Beyond Black–Scholes

How do option prices change when volatility can move or the stock can jump? The notebook compares European call prices under Black–Scholes, Heston, and Merton, then converts them to Black–Scholes implied volatility to make the differences across strikes and expiries visible. [Open the notebook](pricing.ipynb)

## Models and inputs

All examples price the same discounted payoff under a specified risk-neutral measure. The stock starts at $100, the continuously compounded rate is 2%, and dividends are zero. The parameters are hypothetical and the paths are simulated.

- **Black–Scholes.** Constant 20% annual volatility produces normal log returns and a flat implied volatility curve. [Black and Scholes (1973)](https://doi.org/10.1086/260062)
- **Heston.** Variance starts at $v_0=0.04$ and mean reverts to $\theta=0.04$ at speed $\kappa=2$ per year. The coefficient of variance shocks is $\xi=0.5$, and their correlation with stock shocks is $\rho=-0.7$. The notebook varies $\rho$ to show how it tilts the curve across strikes. Heston calls use Fourier integration. The path example uses full truncation log-Euler with 50,000 paths, 126 steps over six months, and NumPy seed 42. [Heston (1993)](https://doi.org/10.1093/rfs/6.2.327) · [Lord, Koekkoek, and van Dijk (2010)](https://doi.org/10.1080/14697680802392496)
- **Merton.** Jumps arrive at an average rate of 0.8 per year. Log jump sizes have mean −0.12 and standard deviation 0.10. The model adjusts the drift to preserve risk-neutral expected growth and uses 14.3% diffusion volatility to match Black–Scholes annual log-return variance. Call prices average conditional Black–Scholes prices over the Poisson jump count. [Merton (1976)](https://doi.org/10.1016/0304-405X(76)90022-2)

[Pricing and implied volatility code](src/models.py) · [Path simulation code](src/paths.py)

## Findings and checks

At one month and strike $80, implied volatility was **20.00%** under Black–Scholes, **27.39%** under Heston, and **36.04%** under Merton. At strike $100, the same models gave **20.00%**, **19.65%**, and **17.13%**. In the jump example, the same annual log-return variance as Black–Scholes produces a steeper downside skew because infrequent large moves account for part of the variance.

For the six-month Heston call at strike $100, Fourier pricing gave **$5.758** and simulation gave **$5.788** with a sampling standard error of **$0.031**. The simulation also has time-step bias. Both extensions reduce to Black–Scholes when the additional source of randomness is turned off and 20% constant volatility is restored.

## Run it

From the repository root, sync the environment and open the notebook. Choose the repository’s Python kernel and run all cells.

    uv sync
    uv run jupyter lab black_scholes_extensions/pricing.ipynb
