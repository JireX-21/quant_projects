"""Risk-neutral European call prices with zero dividends.

Time is in years, rates and volatilities are decimals, and Heston v0 and
theta are annualized variances. Merton jump sizes are in log-price units.
"""

import numpy as np
from scipy.integrate import quad_vec
from scipy.optimize import brentq
from scipy.special import ndtr
from scipy.stats import poisson


def bs_call(spot, strike, maturity, rate, volatility):
    """Black–Scholes call price. Strike and volatility can be arrays."""
    discounted_strike = np.asarray(strike, dtype=float) * np.exp(-rate * maturity)
    scale = np.asarray(volatility, dtype=float) * np.sqrt(maturity)
    safe_scale = np.where(scale == 0, 1.0, scale)
    d1 = np.log(spot / discounted_strike) / safe_scale + scale / 2
    return np.where(
        scale == 0,
        np.maximum(spot - discounted_strike, 0),
        spot * ndtr(d1) - discounted_strike * ndtr(d1 - scale),
    )


def implied_volatility(price, spot, strike, maturity, rate):
    """Recover Black–Scholes annualized volatility from one or more calls."""
    if maturity <= 0:
        raise ValueError("Implied volatility requires positive time to expiry.")
    prices, strikes = np.broadcast_arrays(price, strike)
    result = np.empty(prices.shape)
    for index in np.ndindex(prices.shape):
        premium, k = prices[index], strikes[index]
        floor = float(bs_call(spot, k, maturity, rate, 0))
        if premium < floor - 1e-10 or premium >= spot:
            raise ValueError(f"Call price {premium:g} violates bounds for strike {k:g}.")
        if premium <= floor:
            result[index] = 0
            continue
        upper_vol = 1.0
        while bs_call(spot, k, maturity, rate, upper_vol) < premium:
            upper_vol *= 2
        result[index] = brentq(
            lambda vol: float(bs_call(spot, k, maturity, rate, vol)) - premium,
            0.0,
            upper_vol,
        )
    return result.item() if result.ndim == 0 else result


def heston_logreturn_cf(u, maturity, rate, *, v0, kappa, theta, xi, rho):
    """Characteristic function of log(S_T/S_0) in the Heston model."""
    u = np.asarray(u, dtype=complex)
    iu = 1j * u
    if xi == 0:
        integrated_var = v0 * maturity if kappa == 0 else (
            theta * maturity + (v0 - theta) * (-np.expm1(-kappa * maturity)) / kappa
        )
        return np.exp(iu * rate * maturity - 0.5 * (u**2 + iu) * integrated_var)

    # In the decaying-exponential representation, Re(d) >= 0.
    beta = kappa - rho * xi * iu
    d = np.sqrt(beta**2 + xi**2 * (u**2 + iu))
    one_minus_decay = -np.expm1(-d * maturity)
    # Rationalize beta - d and cancel beta + d in the log denominator.
    # This also avoids losing the first-order xi**2 term for small vol of vol.
    martingale_points = (u == 0) | (u == -1j)
    beta_plus_d = np.where(martingale_points, 1, beta + d)
    scaled_difference = -(u**2 + iu) / beta_plus_d
    g = xi**2 * scaled_difference / beta_plus_d
    log_term = np.log1p(g * one_minus_decay / (1 - g))
    c = iu * rate * maturity + kappa * theta * (
        scaled_difference * maturity - 2 * log_term / xi**2
    )
    variance_coefficient = scaled_difference * one_minus_decay / (
        1 - g * np.exp(-d * maturity)
    )
    return np.exp(c + v0 * variance_coefficient)


def heston_call(spot, strike, maturity, rate, *, v0, kappa, theta, xi, rho):
    """Price calls by integrating the Heston characteristic function."""
    strikes = np.asarray(strike, dtype=float)
    if maturity == 0:
        return np.maximum(spot - strikes, 0)
    if xi == 0:
        integrated_var = v0 * maturity if kappa == 0 else (
            theta * maturity + (v0 - theta) * (-np.expm1(-kappa * maturity)) / kappa
        )
        return bs_call(spot, strikes, maturity, rate, np.sqrt(integrated_var / maturity))

    log_strike = np.log(strikes / spot)

    # P1 uses the stock-numeraire tilt. P2 is the Q probability of exercise.
    def integrand(u):
        params = dict(v0=v0, kappa=kappa, theta=theta, xi=xi, rho=rho)
        phase = np.exp(-1j * u * log_strike) / (1j * u)
        p1 = np.exp(-rate * maturity) * heston_logreturn_cf(u - 1j, maturity, rate, **params)
        p2 = heston_logreturn_cf(u, maturity, rate, **params)
        return np.stack([(phase * p1).real, (phase * p2).real])

    integral, _ = quad_vec(integrand, 0, np.inf, epsabs=1e-9, epsrel=1e-9)
    p1, p2 = 0.5 + integral / np.pi
    return spot * p1 - strikes * np.exp(-rate * maturity) * p2


def merton_call(spot, strike, maturity, rate, *, volatility, intensity, jump_mean, jump_vol):
    """Price calls as a Poisson mixture of conditional Black–Scholes calls."""
    strikes = np.asarray(strike, dtype=float)
    if maturity == 0 or intensity == 0:
        return bs_call(spot, strikes, maturity, rate, volatility)

    log_jump_multiplier = jump_mean + 0.5 * jump_vol**2
    original_count_mean = intensity * maturity
    tilted_count_mean = original_count_mean * np.exp(log_jump_multiplier)
    max_count = int(poisson.isf(1e-13, max(original_count_mean, tilted_count_mean)))
    counts = np.arange(max_count + 1)
    effective_vol = np.sqrt(volatility**2 + counts * jump_vol**2 / maturity)
    effective_rate = rate - intensity * np.expm1(log_jump_multiplier)
    effective_rate += counts * log_jump_multiplier / maturity
    # Tilting the Poisson weights lets each conditional call use the same spot.
    weights = poisson.pmf(counts, tilted_count_mean)
    terms = bs_call(spot, strikes[..., None], maturity, effective_rate, effective_vol)
    return terms @ weights
