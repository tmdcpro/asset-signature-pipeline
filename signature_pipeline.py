"""
Asset Signature Vector Pipeline
================================
Computes a multi-dimensional "signature vector" for any priced financial
asset (equities, ETFs, indexes, crypto, FX) from historical price data,
plus optional structural signatures for bonds and options given contract
parameters.

Usage:
    python3 signature_pipeline.py

Edit the CONFIG section below to change tickers, benchmark, date range,
or risk-free rate.
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
TICKERS = ["AAPL", "SPY", "BTC-USD", "TLT", "GLD", "NVDA"]  # basket to profile
BENCHMARK = "SPY"          # used for beta/alpha
PERIOD = "3y"              # lookback window for yfinance
RISK_FREE_ANNUAL = 0.04    # annualized risk-free rate assumption
TRADING_DAYS = 252


# ---------------------------------------------------------------------------
# 1. DATA INGESTION
# ---------------------------------------------------------------------------
def fetch_prices(tickers, period=PERIOD):
    """Download adjusted close prices for a list of tickers."""
    raw = yf.download(tickers, period=period, auto_adjust=True, progress=False)
    close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
    close = close.dropna(how="all")
    return close


def to_log_returns(price_series):
    return np.log(price_series / price_series.shift(1)).dropna()


# ---------------------------------------------------------------------------
# 2. RETURN / RISK METRICS
# ---------------------------------------------------------------------------
def cagr(price_series):
    n_years = (price_series.index[-1] - price_series.index[0]).days / 365.25
    if n_years <= 0:
        return np.nan
    return (price_series.iloc[-1] / price_series.iloc[0]) ** (1 / n_years) - 1


def annualized_vol(returns):
    return returns.std() * np.sqrt(TRADING_DAYS)


def sharpe_ratio(returns, rf_annual=RISK_FREE_ANNUAL):
    rf_daily = rf_annual / TRADING_DAYS
    excess = returns - rf_daily
    if returns.std() == 0:
        return np.nan
    return (excess.mean() / returns.std()) * np.sqrt(TRADING_DAYS)


def sortino_ratio(returns, rf_annual=RISK_FREE_ANNUAL):
    rf_daily = rf_annual / TRADING_DAYS
    excess = returns - rf_daily
    downside = excess[excess < 0]
    dd_std = downside.std()
    if dd_std == 0 or np.isnan(dd_std):
        return np.nan
    return (excess.mean() / dd_std) * np.sqrt(TRADING_DAYS)


def max_drawdown(price_series):
    cum_max = price_series.cummax()
    drawdown = price_series / cum_max - 1
    return drawdown.min()


def calmar_ratio(price_series, returns):
    mdd = max_drawdown(price_series)
    if mdd == 0:
        return np.nan
    return cagr(price_series) / abs(mdd)


# ---------------------------------------------------------------------------
# 3. DISTRIBUTIONAL SHAPE
# ---------------------------------------------------------------------------
def distribution_shape(returns):
    return {
        "skewness": stats.skew(returns),
        "excess_kurtosis": stats.kurtosis(returns),  # Fisher definition, normal=0
    }


def tail_index_hill(returns, tail_fraction=0.05):
    """Hill estimator for the tail index of the loss distribution."""
    losses = -returns[returns < 0]
    if len(losses) < 20:
        return np.nan
    losses_sorted = np.sort(losses)[::-1]
    k = max(int(len(losses_sorted) * tail_fraction), 5)
    top = losses_sorted[:k]
    xmin = losses_sorted[k - 1]
    if xmin <= 0:
        return np.nan
    hill = 1 / np.mean(np.log(top / xmin))
    return hill


# ---------------------------------------------------------------------------
# 4. MARKET SENSITIVITY (BETA / ALPHA)
# ---------------------------------------------------------------------------
def beta_alpha(asset_returns, benchmark_returns, rf_annual=RISK_FREE_ANNUAL):
    rf_daily = rf_annual / TRADING_DAYS
    df = pd.concat([asset_returns - rf_daily, benchmark_returns - rf_daily], axis=1).dropna()
    df.columns = ["asset", "bench"]
    if len(df) < 30 or df["bench"].var() == 0:
        return np.nan, np.nan
    cov = np.cov(df["asset"], df["bench"])[0, 1]
    var = np.var(df["bench"])
    beta = cov / var
    alpha_daily = df["asset"].mean() - beta * df["bench"].mean()
    alpha_annual = alpha_daily * TRADING_DAYS
    return beta, alpha_annual


# ---------------------------------------------------------------------------
# 5. TIME-SERIES MEMORY / DYNAMICS
# ---------------------------------------------------------------------------
def hurst_exponent(price_series, max_lag=100):
    """Rescaled-range style Hurst exponent via variance-of-differences method."""
    ts = np.log(price_series.dropna().values)
    lags = range(2, min(max_lag, len(ts) // 2))
    tau = [np.std(ts[lag:] - ts[:-lag]) for lag in lags]
    lags = list(lags)
    valid = [(l, t) for l, t in zip(lags, tau) if t > 0]
    if len(valid) < 2:
        return np.nan
    lags_v, tau_v = zip(*valid)
    poly = np.polyfit(np.log(lags_v), np.log(tau_v), 1)
    return poly[0] * 2  # slope*2 approximates the Hurst exponent


def autocorrelation(returns, lag=1):
    return returns.autocorr(lag=lag)


def vol_clustering_autocorr(returns, lag=1):
    """Autocorrelation of squared returns = volatility clustering signature."""
    sq = returns ** 2
    return sq.autocorr(lag=lag)


def garch_params(returns):
    """Fit a GARCH(1,1) and return (omega, alpha, beta) describing volatility dynamics."""
    try:
        from arch import arch_model
        scaled = returns * 100  # arch works better on percentage returns
        model = arch_model(scaled, vol="Garch", p=1, q=1, dist="normal", rescale=False)
        res = model.fit(disp="off")
        omega = res.params.get("omega", np.nan)
        alpha1 = res.params.get("alpha[1]", np.nan)
        beta1 = res.params.get("beta[1]", np.nan)
        return omega, alpha1, beta1
    except Exception:
        return np.nan, np.nan, np.nan


# ---------------------------------------------------------------------------
# 6. COMPOSITE SIGNATURE VECTOR (price-based assets)
# ---------------------------------------------------------------------------
def build_signature(ticker, price_series, benchmark_returns):
    returns = to_log_returns(price_series)
    shape = distribution_shape(returns)
    beta, alpha = beta_alpha(returns, benchmark_returns)
    omega, g_alpha, g_beta = garch_params(returns)

    return {
        "ticker": ticker,
        "cagr": cagr(price_series),
        "ann_volatility": annualized_vol(returns),
        "sharpe": sharpe_ratio(returns),
        "sortino": sortino_ratio(returns),
        "max_drawdown": max_drawdown(price_series),
        "calmar": calmar_ratio(price_series, returns),
        "skewness": shape["skewness"],
        "excess_kurtosis": shape["excess_kurtosis"],
        "tail_index_hill": tail_index_hill(returns),
        "beta": beta,
        "alpha_annual": alpha,
        "hurst_exponent": hurst_exponent(price_series),
        "autocorr_lag1": autocorrelation(returns, 1),
        "vol_clustering_autocorr_lag1": vol_clustering_autocorr(returns, 1),
        "garch_omega": omega,
        "garch_alpha": g_alpha,
        "garch_beta": g_beta,
    }


# ---------------------------------------------------------------------------
# 7. OPTIONAL: BOND STRUCTURAL SIGNATURE
# ---------------------------------------------------------------------------
def bond_signature(face_value, coupon_rate, years_to_maturity, ytm, freq=2):
    """
    Macaulay duration, modified duration, and convexity for a plain-vanilla
    fixed-coupon bond. Rates are annual decimals (e.g. 0.05 for 5%).
    """
    periods = int(years_to_maturity * freq)
    coupon = face_value * coupon_rate / freq
    y = ytm / freq

    t = np.arange(1, periods + 1)
    cash_flows = np.full(periods, coupon)
    cash_flows[-1] += face_value

    disc_factors = 1 / (1 + y) ** t
    pv_cf = cash_flows * disc_factors
    price = pv_cf.sum()

    macaulay_duration = (t * pv_cf).sum() / price / freq
    modified_duration = macaulay_duration / (1 + y)
    convexity = ((t * (t + 1) * pv_cf).sum() / (price * (1 + y) ** 2)) / (freq ** 2)

    return {
        "price": price,
        "macaulay_duration": macaulay_duration,
        "modified_duration": modified_duration,
        "convexity": convexity,
    }


# ---------------------------------------------------------------------------
# 8. OPTIONAL: OPTION GREEKS SIGNATURE (Black-Scholes)
# ---------------------------------------------------------------------------
def option_signature(S, K, T, r, sigma, option_type="call"):
    """Black-Scholes Greeks: delta, gamma, theta, vega, rho."""
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    pdf_d1 = stats.norm.pdf(d1)
    if option_type == "call":
        delta = stats.norm.cdf(d1)
        theta = (-S * pdf_d1 * sigma / (2 * np.sqrt(T))
                 - r * K * np.exp(-r * T) * stats.norm.cdf(d2))
        rho = K * T * np.exp(-r * T) * stats.norm.cdf(d2)
        price = S * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d2)
    else:
        delta = stats.norm.cdf(d1) - 1
        theta = (-S * pdf_d1 * sigma / (2 * np.sqrt(T))
                 + r * K * np.exp(-r * T) * stats.norm.cdf(-d2))
        rho = -K * T * np.exp(-r * T) * stats.norm.cdf(-d2)
        price = K * np.exp(-r * T) * stats.norm.cdf(-d2) - S * stats.norm.cdf(-d1)

    gamma = pdf_d1 / (S * sigma * np.sqrt(T))
    vega = S * pdf_d1 * np.sqrt(T)

    return {
        "price": price,
        "delta": delta,
        "gamma": gamma,
        "theta_annual": theta,
        "vega": vega,
        "rho": rho,
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    all_tickers = list(dict.fromkeys(TICKERS + [BENCHMARK]))
    prices = fetch_prices(all_tickers)

    bench_returns = to_log_returns(prices[BENCHMARK])

    rows = []
    for t in TICKERS:
        if t not in prices.columns:
            print(f"Skipping {t}: no data returned")
            continue
        series = prices[t].dropna()
        if len(series) < 60:
            print(f"Skipping {t}: insufficient history ({len(series)} rows)")
            continue
        rows.append(build_signature(t, series, bench_returns))

    sig_df = pd.DataFrame(rows).set_index("ticker")
    sig_df.to_csv("/home/user/workspace/asset_signatures.csv")
    print("\n=== ASSET SIGNATURE VECTORS ===")
    print(sig_df.round(4).to_string())

    # ---- example bond signature ----
    print("\n=== EXAMPLE BOND SIGNATURE (5y, 4% coupon, 4.5% YTM) ===")
    bond = bond_signature(face_value=1000, coupon_rate=0.04, years_to_maturity=5, ytm=0.045)
    for k, v in bond.items():
        print(f"{k}: {v:.4f}")

    # ---- example option signature ----
    print("\n=== EXAMPLE OPTION SIGNATURE (call, S=100,K=100,T=0.5,r=0.04,sigma=0.25) ===")
    opt = option_signature(S=100, K=100, T=0.5, r=0.04, sigma=0.25, option_type="call")
    for k, v in opt.items():
        print(f"{k}: {v:.4f}")

    return sig_df


if __name__ == "__main__":
    main()
