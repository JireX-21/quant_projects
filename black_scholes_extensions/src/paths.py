"""Risk-neutral Heston paths with full truncation and log-Euler stepping."""

import numpy as np


def heston_paths(
    spot,
    maturity,
    rate,
    v0,
    theta,
    kappa,
    volvol,
    rho,
    *,
    n_paths=50_000,
    n_steps=126,
    n_sample=5,
    seed=42,
    dividend=0.0,
):
    """Return time in years, sample prices, sample volatilities, and terminal prices.

    Rates and volatilities are annualized decimals. The variance levels v0
    and theta are squared volatilities. Each sample column follows one path.
    Terminal prices include every simulation, including the sample paths.
    """
    parameters = (spot, maturity, rate, dividend, v0, theta, kappa, volvol, rho)
    if not np.all(np.isfinite(parameters)):
        raise ValueError("Model parameters must be finite.")
    if spot <= 0 or maturity <= 0:
        raise ValueError("Spot and maturity must be positive.")
    if min(v0, theta, kappa, volvol) < 0 or abs(rho) > 1:
        raise ValueError("Variance parameters must be nonnegative and rho in [-1, 1].")
    if n_steps < 1 or n_paths < 1 or not 0 <= n_sample <= n_paths:
        raise ValueError("Use positive step and path counts and retain at most n_paths samples.")

    dt = maturity / n_steps
    times = np.linspace(0.0, maturity, n_steps + 1)
    rng = np.random.default_rng(seed)
    log_spots = np.full(n_paths, np.log(spot))
    variance_state = np.full(n_paths, v0, dtype=float)
    spot_paths = np.empty((n_steps + 1, n_sample))
    vol_paths = np.empty_like(spot_paths)
    spot_paths[0] = spot
    vol_paths[0] = np.sqrt(v0)
    independent_weight = np.sqrt(1.0 - rho**2)

    for step in range(1, n_steps + 1):
        # Keep the Euler state, using its positive part in every coefficient.
        variance = np.maximum(variance_state, 0.0)
        scale = np.sqrt(variance * dt)
        variance_noise, independent_noise = rng.standard_normal((2, n_paths))
        price_noise = rho * variance_noise + independent_weight * independent_noise
        log_spots += (rate - dividend - 0.5 * variance) * dt + scale * price_noise
        variance_state += kappa * (theta - variance) * dt + volvol * scale * variance_noise
        spot_paths[step] = np.exp(log_spots[:n_sample])
        vol_paths[step] = np.sqrt(np.maximum(variance_state[:n_sample], 0.0))

    return times, spot_paths, vol_paths, np.exp(log_spots)
