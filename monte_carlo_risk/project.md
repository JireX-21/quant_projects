# Monte Carlo stock risk

The notebook estimates one-day downside risk for a $10,000 investment as it expands from Apple alone to two stocks and then five stocks. [Open the Jupyter notebook](risk_simulation.ipynb).

The univariate Apple model uses 252 closing prices from January 2 through December 31, 2024, adjusted for splits and dividends. Taking the log of each price divided by the previous trading day's price gives 251 daily log returns. The fitted daily mean is 0.1212% and the sample standard deviation is 1.4063%. [Yahoo Finance data source](https://query1.finance.yahoo.com/v8/finance/chart/AAPL?period1=1704067200&period2=1735689600&interval=1d) · [Bundled price data](data/aapl_2024_adjusted_close.csv)

The notebook draws 100,000 one-day log returns from a normal distribution with the fitted mean and volatility, using NumPy seed 42. It converts each return into a dollar loss. The 95% value at risk (VaR) is the loss threshold for the worst 5% of outcomes. The 95% expected shortfall (ES) is the average loss within those outcomes.

The simulation estimates VaR at **$218.66** (2.19% of the position) and expected shortfall at **$275.47** (2.75%). The corresponding closed-form values under the same model are $216.81 and $273.99. The estimates depend on the 2024 sample and the assumption that daily log returns are normal with constant volatility.

The portfolio pairs Microsoft and Apple prices on the same 252 trading dates. Using seed 42, it simulates 100,000 pairs of daily log returns from a multivariate normal distribution fitted to the paired returns (sample correlation 0.47). Each scenario adds the losses on the two $5,000 holdings. Portfolio VaR was **$178.77** and expected shortfall was **$225.52**. Both estimates assume the historical covariance holds over the next trading day. [Bundled Microsoft prices](data/msft_2024_adjusted_close.csv)

The five-stock example adds JPMorgan Chase, Exxon Mobil, and Johnson & Johnson using the same 252 trading dates and Yahoo Finance adjusted closes. The notebook compares each holding and both portfolio rules on identical simulated days. Equal weighting gave VaR of $105.54 and ES of $133.67. Weights chosen to minimize historical simple-return variance gave VaR of $98.80 and ES of $124.10. Both rules beat all five individual stocks on these measures in the fitted model. [Price snapshots](data/)

## Run it

From the repository root, sync the shared environment and open the notebook. In JupyterLab, select **Python (Quant Finance Playground)** and choose **Run All Cells**.

```sh
uv sync
uv run jupyter lab monte_carlo_risk/risk_simulation.ipynb
```
