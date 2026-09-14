# Asset Signature Vector Pipeline

Computes a multi-dimensional "signature vector" for any priced financial asset
(equities, ETFs, indexes, crypto, FX) from historical price data, plus optional
structural signatures for bonds and options given contract parameters.

## What it computes

- **Return & risk**: CAGR, annualized volatility, Sharpe, Sortino, max drawdown, Calmar ratio
- **Distribution shape**: skewness, excess kurtosis, Hill tail-index estimator
- **Market sensitivity**: beta and annualized alpha vs. a benchmark
- **Time-series dynamics**: Hurst exponent, return autocorrelation, volatility-clustering
  autocorrelation, fitted GARCH(1,1) parameters (omega, alpha, beta)
- **Bond structural signature**: Macaulay duration, modified duration, convexity
  (given face value, coupon rate, maturity, yield to maturity)
- **Option structural signature**: Black-Scholes Greeks — delta, gamma, theta, vega, rho

## Setup

```bash
pip install -r requirements.txt
```

## Usage

Edit the `CONFIG` section at the top of `signature_pipeline.py`:

```python
TICKERS = ["AAPL", "SPY", "BTC-USD", "TLT", "GLD", "NVDA"]  # basket to profile
BENCHMARK = "SPY"          # used for beta/alpha
PERIOD = "3y"              # lookback window for yfinance
RISK_FREE_ANNUAL = 0.04    # annualized risk-free rate assumption
```

Then run:

```bash
python3 signature_pipeline.py
```

This downloads price history via `yfinance`, computes the signature vector for
each ticker, prints a summary table, and saves the full result to
`asset_signatures.csv`.

The bond and option signature functions (`bond_signature`, `option_signature`)
take explicit contract parameters rather than a ticker, since those instruments
aren't fully described by a price series alone:

```python
bond_signature(face_value=1000, coupon_rate=0.04, years_to_maturity=5, ytm=0.045)
option_signature(S=100, K=100, T=0.5, r=0.04, sigma=0.25, option_type="call")
```

## Walkthrough video

See [`video/asset_signature_pipeline_demo.mp4`](video/asset_signature_pipeline_demo.mp4)
for a narrated screencast explaining the pipeline and showing a live run.
The full production sources (slides, narration script, audio) are in
[`video/`](video/).

## Sample output

See `sample_output/asset_signatures.csv` for an example run across
AAPL, SPY, BTC-USD, TLT, GLD, and NVDA.

## Extending it

The signature vector is designed to be extended — add new metrics as functions
and fold them into `build_signature()`. Useful next steps: multi-factor loadings
(Fama-French), PCA-based clustering across a larger basket, or an implied
volatility surface for options.
