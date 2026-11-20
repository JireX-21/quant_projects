# Implied and realized volatility

The notebook links two ways to measure volatility for the same underlying. It first inverts hypothetical European call quotes with Black–Scholes, using a 30-day expiry and zero rates and dividends. A $3 at-the-money call on a $100 underlying implies 26.24% annualized volatility. Repricing the option at that volatility recovers the $3 quote. Repeating the inversion across strikes shows a skew and a smile side by side in two synthetic chains. [Jupyter notebook](implied_volatility.ipynb) · [Pricing and inversion code](src/options.py) · [Black and Scholes (1973)](https://doi.org/10.1086/260062)

The historical exercise matches VIX and S&P 500 index closes on common trading dates from December 2017 through January 2025. For each month-end observation from 2018 through 2024, it compares the VIX with the S&P 500 volatility realized over the following 30 calendar days. Annualized realized volatility is the square root of the sum of squared daily log returns multiplied by 365/30. The trailing 30-day estimate uses closes available by the observation date and provides a persistence baseline. Close-to-close returns include overnight moves and give a coarser estimate than 5-minute realized variance. [Bundled data](data/spx_vix_daily.csv) · [Cboe VIX history](https://www.cboe.com/tradable_products/vix/vix_historical_data) · [Yahoo Finance S&P 500 history](https://finance.yahoo.com/quote/%5EGSPC/history/)

Across 84 month-ends, VIX averaged **20.10%** and forward realized volatility averaged **16.33%**. VIX exceeded the subsequent realization on **69 of 84** dates. Its root mean squared error was **9.40 volatility points**, compared with **11.61** for the trailing estimate. VIX prices variance under risk-neutral weighting using multiple SPX options. The difference between VIX squared and realized variance includes both a variance risk premium and unexpected market moves. Some 30-day windows overlap, so the comparison is descriptive. [Cboe methodology](https://cdn.cboe.com/resources/indices/governance/Volatility_Index_Methodology_Cboe_Volatility_Index.pdf) · [Federal Reserve research on the variance risk premium](https://www.federalreserve.gov/pubs/feds/2007/200711/)

One worked window starts at the January 29, 2021 close with VIX at 33.09. The notebook uses the Oxford–Man Realized Library’s daily sums of squared 5-minute returns for the following 30 calendar days. That gives **12.18%** annualized volatility for the trading sessions. Adding squared overnight returns before annualizing raises it to **13.06%**. The daily close-to-close estimate over those dates is **13.58%**. [Bundled example](data/spx_intraday_example.csv) · [Oxford–Man Realized Library](https://shephard.scholars.harvard.edu/publications/realized-library)

A worked example for January 29 through February 28, 2021 uses session-level five-minute realized variance from Heber, Lunde, Shephard and Sheppard’s Oxford–Man Realized Library (v0.3). Annualized volatility was 12.18% during trading hours and 13.06% including overnight gaps, against a starting VIX of 33.09%. [Bundled observations](data/spx_intraday_example.csv) · [Archived source ZIP](https://web.archive.org/web/20220301022212id_/https://realized.oxford-man.ox.ac.uk/images/oxfordmanrealizedvolatilityindices.zip)

## Run it

From the repository root, sync the environment and open the notebook. Select the repository’s Python kernel and run all cells. The notebook uses the bundled data and requires no downloads or random seed after environment setup.

```sh
uv sync
uv run jupyter lab implied_volatility/implied_volatility.ipynb
```
