"""European call prices and implied volatility with continuous dividend yield."""

import numpy as np
from scipy.optimize import brentq
from scipy.special import ndtr


def call_price(spot, strike, years, rate, dividend, volatility):
    """Black–Scholes call premium per unit of underlying, using decimal rates."""
    discounted_spot = spot * np.exp(-dividend * years)
    discounted_strike = strike * np.exp(-rate * years)
    if volatility == 0:
        return max(discounted_spot - discounted_strike, 0.0)
    scale = volatility * np.sqrt(years)
    d1 = (np.log(spot / strike) + (rate - dividend) * years) / scale + scale / 2
    return discounted_spot * ndtr(d1) - discounted_strike * ndtr(d1 - scale)


def implied_volatility(premium, spot, strike, years, rate=0.0, dividend=0.0):
    """Solve for the annualized volatility that reproduces a European call quote."""
    if min(spot, strike, years) <= 0:
        raise ValueError("Spot, strike and time to expiry must be positive.")
    args = (spot, strike, years, rate, dividend)
    floor = call_price(*args, 0)
    if not floor <= premium < spot * np.exp(-dividend * years):
        raise ValueError("Premium is outside the model's finite-volatility price range.")
    if premium == floor:
        return 0.0
    upper = 1.0
    while call_price(*args, upper) < premium:
        upper *= 2
    return brentq(lambda vol: call_price(*args, vol) - premium, 0, upper)
