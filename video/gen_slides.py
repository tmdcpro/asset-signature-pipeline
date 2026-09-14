"""Generate syntax-highlighted HTML code slides + a terminal-style output slide."""
import os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

OUT_DIR = "/home/user/workspace/video/slides"
os.makedirs(OUT_DIR, exist_ok=True)

formatter = HtmlFormatter(style="monokai", nowrap=True)
pygments_css = formatter.get_style_defs('.code')

BASE_CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  width:1920px; height:1080px;
  background: linear-gradient(135deg, #0f1420 0%, #1a2035 100%);
  font-family: 'Noto Sans', 'DejaVu Sans', sans-serif;
  display:flex; flex-direction:column;
  color: #e8e8e8;
  overflow:hidden;
}}
.header {{
  padding: 56px 80px 24px 80px;
}}
.eyebrow {{
  color: #7dd3fc; font-size: 26px; font-weight:600; letter-spacing: 3px; text-transform:uppercase;
  margin-bottom: 14px;
}}
.title {{
  font-size: 52px; font-weight:800; color: #ffffff; line-height:1.2;
}}
.subtitle {{
  font-size: 28px; color: #a8b3cc; margin-top:14px; max-width:1600px; line-height:1.4;
}}
.panel-wrap {{
  flex:1; padding: 10px 80px 70px 80px; display:flex; align-items:flex-start;
}}
.editor {{
  width:100%; background:#1e1f29; border-radius:16px; box-shadow: 0 30px 80px rgba(0,0,0,0.5);
  overflow:hidden; border: 1px solid #33364a;
}}
.editor-bar {{
  background:#2b2d3d; padding:16px 24px; display:flex; align-items:center; gap:10px;
}}
.dot {{ width:16px; height:16px; border-radius:50%; }}
.dot.red {{ background:#ff5f56; }}
.dot.yellow {{ background:#ffbd2e; }}
.dot.green {{ background:#27c93f; }}
.filename {{ margin-left:16px; color:#8b91a8; font-size:20px; font-family: monospace; }}
.code {{
  font-family: 'DejaVu Sans Mono', monospace;
  font-size: 25px;
  line-height: 1.55;
  padding: 34px 40px;
  white-space: pre;
  overflow: hidden;
}}
{pygments_css}
.code .c1 {{ font-style: italic; }}
.footer-tag {{
  position:absolute; bottom:40px; right:80px; color:#5b6480; font-size:20px; font-family:monospace;
}}
"""

def make_code_slide(filename, eyebrow, title, subtitle, code, editor_label):
    highlighted = highlight(code, PythonLexer(), formatter)
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{BASE_CSS}</style></head>
<body>
  <div class="header">
    <div class="eyebrow">{eyebrow}</div>
    <div class="title">{title}</div>
    <div class="subtitle">{subtitle}</div>
  </div>
  <div class="panel-wrap">
    <div class="editor">
      <div class="editor-bar">
        <div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div>
        <div class="filename">{editor_label}</div>
      </div>
      <div class="code">{highlighted}</div>
    </div>
  </div>
  <div class="footer-tag">signature_pipeline.py</div>
</body></html>"""
    with open(os.path.join(OUT_DIR, filename), "w") as f:
        f.write(html)


def make_title_slide(filename):
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  width:1920px; height:1080px;
  background: radial-gradient(circle at 30% 20%, #1c2540 0%, #0a0e1a 70%);
  font-family: 'Noto Sans', sans-serif;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  color:#fff;
}}
.badge {{
  color:#7dd3fc; font-size:28px; font-weight:700; letter-spacing:6px; text-transform:uppercase; margin-bottom:36px;
}}
.big-title {{
  font-size:88px; font-weight:800; text-align:center; line-height:1.15; max-width:1500px;
  background: linear-gradient(90deg,#ffffff,#9fd8ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}}
.sub {{
  font-size:32px; color:#a8b3cc; margin-top:36px; text-align:center; max-width:1300px; line-height:1.5;
}}
.pill-row {{ display:flex; gap:20px; margin-top:56px; }}
.pill {{
  background:#161b2e; border:1px solid #333a55; color:#9fd8ff; padding:14px 28px; border-radius:999px;
  font-size:22px; font-family: monospace;
}}
</style></head>
<body>
  <div class="badge">Python Pipeline Walkthrough</div>
  <div class="big-title">Asset Signature<br/>Vector Pipeline</div>
  <div class="sub">Turning price history into a multi-dimensional financial fingerprint</div>
  <div class="pill-row">
    <div class="pill">yfinance</div>
    <div class="pill">GARCH</div>
    <div class="pill">Black-Scholes</div>
    <div class="pill">Duration &amp; Convexity</div>
  </div>
</body></html>"""
    with open(os.path.join(OUT_DIR, filename), "w") as f:
        f.write(html)


def make_outro_slide(filename):
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* { margin:0; padding:0; box-sizing:border-box; }
body {
  width:1920px; height:1080px;
  background: radial-gradient(circle at 70% 80%, #1c2540 0%, #0a0e1a 70%);
  font-family: 'Noto Sans', sans-serif;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  color:#fff;
}
.big-title {
  font-size:72px; font-weight:800; text-align:center; line-height:1.2; max-width:1500px;
  background: linear-gradient(90deg,#ffffff,#9fd8ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.sub {
  font-size:30px; color:#a8b3cc; margin-top:32px; text-align:center; max-width:1300px; line-height:1.5;
}
.file-chip {
  margin-top:56px; background:#161b2e; border:1px solid #333a55; color:#7dd3fc; padding:18px 36px;
  border-radius:14px; font-size:26px; font-family:monospace;
}
</style></head>
<body>
  <div class="big-title">Your turn: swap tickers,<br/>extend the metrics</div>
  <div class="sub">One CSV row per asset &mdash; ready for clustering, comparison, or your own OSINT-style cross-referencing</div>
  <div class="file-chip">asset_signatures.csv</div>
</body></html>"""
    with open(os.path.join(OUT_DIR, filename), "w") as f:
        f.write(html)


def make_terminal_slide(filename):
    table_text = """=== ASSET SIGNATURE VECTORS ===
           cagr  ann_vol  sharpe  sortino  max_dd  calmar  skew   kurt   beta    alpha   hurst  garch_a
AAPL     0.2450   0.2675  0.6756   0.9102  -0.334  0.7344  0.287   9.74  1.044   0.132  0.911    0.063
SPY      0.2110   0.1527  1.0009   1.3054  -0.188  1.1248  0.609  18.34  1.002  -0.000  0.808    0.108
BTC-USD  0.4379   0.3897  0.5404   0.7983  -0.531  0.8253  0.153   3.54  1.011  -0.061  1.074    0.118
TLT     -0.0038   0.1348 -0.3254  -0.4914  -0.148 -0.0260 -0.142   0.84  0.141  -0.002  0.738    0.020
GLD      0.3014   0.2153  1.0466   1.2920  -0.264  1.1414 -0.965   7.20  0.311   0.140  0.950    0.127
NVDA     0.6898   0.4684  1.0427   1.4844  -0.369  1.8703 -0.098   4.72  2.013   0.270  0.967    0.079

=== BOND SIGNATURE (5y, 4% coupon, 4.5% YTM) ===
price: 977.83   macaulay_duration: 4.58   modified_duration: 4.47   convexity: 23.35

=== OPTION SIGNATURE (call, S=100, K=100, T=0.5y, r=4%, vol=25%) ===
price: 8.01   delta: 0.580   gamma: 0.022   theta: -8.91   vega: 27.64   rho: 24.99
$ _"""
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  width:1920px; height:1080px;
  background: linear-gradient(135deg, #0f1420 0%, #1a2035 100%);
  font-family:'Noto Sans', sans-serif; color:#e8e8e8; display:flex; flex-direction:column; overflow:hidden;
}}
.header {{ padding: 56px 80px 24px 80px; }}
.eyebrow {{ color:#7dd3fc; font-size:26px; font-weight:600; letter-spacing:3px; text-transform:uppercase; margin-bottom:14px; }}
.title {{ font-size:52px; font-weight:800; color:#fff; }}
.subtitle {{ font-size:28px; color:#a8b3cc; margin-top:14px; max-width:1650px; line-height:1.4; }}
.panel-wrap {{ flex:1; padding: 10px 80px 70px 80px; }}
.term {{
  width:100%; height:100%; background:#0b0d14; border-radius:16px; box-shadow:0 30px 80px rgba(0,0,0,0.5);
  overflow:hidden; border:1px solid #2a2d3d;
}}
.term-bar {{ background:#1a1d2b; padding:16px 24px; display:flex; align-items:center; gap:10px; }}
.dot {{ width:16px; height:16px; border-radius:50%; }}
.dot.red {{ background:#ff5f56; }} .dot.yellow {{ background:#ffbd2e; }} .dot.green {{ background:#27c93f; }}
.termname {{ margin-left:16px; color:#7a8296; font-size:20px; font-family:monospace; }}
.term-body {{
  font-family:'DejaVu Sans Mono', monospace; font-size:24px; line-height:1.5; color:#8ef58e;
  padding:36px 44px; white-space:pre;
}}
.term-body .hl {{ color:#7dd3fc; }}
</style></head>
<body>
  <div class="header">
    <div class="eyebrow">Live Run</div>
    <div class="title">python3 signature_pipeline.py</div>
    <div class="subtitle">Real output from a basket of six assets, plus example bond and option signatures</div>
  </div>
  <div class="panel-wrap">
    <div class="term">
      <div class="term-bar"><div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div>
        <div class="termname">terminal</div></div>
      <div class="term-body">{table_text}</div>
    </div>
  </div>
</body></html>"""
    with open(os.path.join(OUT_DIR, filename), "w") as f:
        f.write(html)


# ---- Slide content ----

make_title_slide("01_intro.html")

make_code_slide(
    "02_config.html",
    "Step 1 &middot; Setup",
    "Configure & Fetch Data",
    "Pick your tickers and benchmark, then pull adjusted price history and convert it to log returns.",
    '''TICKERS = ["AAPL", "SPY", "BTC-USD", "TLT", "GLD", "NVDA"]
BENCHMARK = "SPY"
PERIOD = "3y"
RISK_FREE_ANNUAL = 0.04
TRADING_DAYS = 252

def fetch_prices(tickers, period=PERIOD):
    raw = yf.download(tickers, period=period,
                       auto_adjust=True, progress=False)
    close = raw["Close"]
    return close.dropna(how="all")

def to_log_returns(price_series):
    return np.log(price_series / price_series.shift(1)).dropna()''',
    "signature_pipeline.py — config & ingestion",
)

make_code_slide(
    "03_returnrisk.html",
    "Step 2 &middot; Layer One",
    "Return & Risk Metrics",
    "CAGR, volatility, Sharpe, Sortino, drawdown, and Calmar describe performance and pain.",
    '''def cagr(price_series):
    n_years = (price_series.index[-1]
               - price_series.index[0]).days / 365.25
    return (price_series.iloc[-1]
            / price_series.iloc[0]) ** (1/n_years) - 1

def sharpe_ratio(returns, rf_annual=RISK_FREE_ANNUAL):
    rf_daily = rf_annual / TRADING_DAYS
    excess = returns - rf_daily
    return (excess.mean() / returns.std()) * np.sqrt(TRADING_DAYS)

def max_drawdown(price_series):
    cum_max = price_series.cummax()
    drawdown = price_series / cum_max - 1
    return drawdown.min()''',
    "signature_pipeline.py — return & risk",
)

make_code_slide(
    "04_shape.html",
    "Step 3 &middot; Layer Two",
    "Distribution Shape",
    "Skewness, kurtosis, and tail thickness describe the personality of an asset's returns.",
    '''def distribution_shape(returns):
    return {
        "skewness": stats.skew(returns),
        "excess_kurtosis": stats.kurtosis(returns),
    }

def tail_index_hill(returns, tail_fraction=0.05):
    losses = -returns[returns < 0]
    losses_sorted = np.sort(losses)[::-1]
    k = max(int(len(losses_sorted) * tail_fraction), 5)
    top = losses_sorted[:k]
    xmin = losses_sorted[k - 1]
    return 1 / np.mean(np.log(top / xmin))''',
    "signature_pipeline.py — distribution shape",
)

make_code_slide(
    "05_beta.html",
    "Step 4 &middot; Layer Three",
    "Market Sensitivity",
    "Beta and alpha measure co-movement with a benchmark and the return left over after that.",
    '''def beta_alpha(asset_returns, benchmark_returns,
               rf_annual=RISK_FREE_ANNUAL):
    rf_daily = rf_annual / TRADING_DAYS
    df = pd.concat([asset_returns - rf_daily,
                     benchmark_returns - rf_daily], axis=1).dropna()
    df.columns = ["asset", "bench"]

    cov = np.cov(df["asset"], df["bench"])[0, 1]
    var = np.var(df["bench"])
    beta = cov / var

    alpha_daily = df["asset"].mean() - beta * df["bench"].mean()
    alpha_annual = alpha_daily * TRADING_DAYS
    return beta, alpha_annual''',
    "signature_pipeline.py — beta & alpha",
)

make_code_slide(
    "06_dynamics.html",
    "Step 5 &middot; Layer Four",
    "Time-Series Dynamics",
    "Hurst exponent, autocorrelation, and a fitted GARCH model reveal memory and volatility clustering.",
    '''def hurst_exponent(price_series, max_lag=100):
    ts = np.log(price_series.dropna().values)
    lags = range(2, min(max_lag, len(ts)//2))
    tau = [np.std(ts[l:] - ts[:-l]) for l in lags]
    poly = np.polyfit(np.log(list(lags)), np.log(tau), 1)
    return poly[0] * 2

def garch_params(returns):
    model = arch_model(returns * 100, vol="Garch", p=1, q=1)
    res = model.fit(disp="off")
    return (res.params["omega"], res.params["alpha[1]"],
            res.params["beta[1]"])''',
    "signature_pipeline.py — dynamics & GARCH",
)

make_code_slide(
    "07_bondoption.html",
    "Step 6 &middot; Structural Signatures",
    "Bonds & Options",
    "Contract-level instruments get their own signature from coupon/yield or strike/volatility inputs.",
    '''def bond_signature(face_value, coupon_rate,
                    years_to_maturity, ytm, freq=2):
    # ... discounts cash flows, then returns:
    return {"price": price,
            "macaulay_duration": macaulay_duration,
            "modified_duration": modified_duration,
            "convexity": convexity}

def option_signature(S, K, T, r, sigma, option_type="call"):
    # Black-Scholes d1, d2 ...
    return {"price": price, "delta": delta, "gamma": gamma,
            "theta_annual": theta, "vega": vega, "rho": rho}''',
    "signature_pipeline.py — bond & option signatures",
)

make_terminal_slide("08_run.html")
make_outro_slide("09_outro.html")

print("Slides generated:", os.listdir(OUT_DIR))
