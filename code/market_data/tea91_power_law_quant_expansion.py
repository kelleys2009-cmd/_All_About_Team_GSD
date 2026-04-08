from __future__ import annotations

import json
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd
import yfinance as yf


def download_close(ticker: str) -> pd.Series:
    frame = yf.download(ticker, period="max", interval="1d", auto_adjust=False, progress=False)
    if frame is None or frame.empty:
        return pd.Series(dtype=float)

    if isinstance(frame.columns, pd.MultiIndex):
        if ("Close", ticker) in frame.columns:
            close = frame[("Close", ticker)]
        elif "Close" in frame.columns.get_level_values(0):
            close = frame.xs("Close", axis=1, level=0).iloc[:, 0]
        else:
            close = frame.iloc[:, 0]
    else:
        close = frame["Close"] if "Close" in frame.columns else frame.iloc[:, 0]

    series = close.dropna().astype(float)
    return series[series > 0.0]


def fit_power(series: pd.Series) -> dict:
    y = series.values.astype(float)
    x = np.arange(1, len(y) + 1, dtype=float)
    ln_x = np.log(x)
    ln_y = np.log(y)

    slope_b, intercept_a = np.polyfit(ln_x, ln_y, 1)
    pred = intercept_a + slope_b * ln_x
    resid = ln_y - pred

    ss_res = float(np.sum((ln_y - pred) ** 2))
    ss_tot = float(np.sum((ln_y - ln_y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    q10, q50, q90 = np.quantile(np.exp(resid), [0.1, 0.5, 0.9])

    return {
        "obs": int(len(series)),
        "start": str(pd.to_datetime(series.index[0]).date()),
        "end": str(pd.to_datetime(series.index[-1]).date()),
        "exponent_b": float(slope_b),
        "intercept_a": float(intercept_a),
        "r2": float(r2),
        "latest_price": float(series.iloc[-1]),
        "price_to_model": float(np.exp(ln_y[-1] - pred[-1])),
        "resid_q10_mult": float(q10),
        "resid_q50_mult": float(q50),
        "resid_q90_mult": float(q90),
    }


def main() -> None:
    out_dir = Path("artifacts/tea-91")
    out_dir.mkdir(parents=True, exist_ok=True)

    with urlopen(
        "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=120&page=1&sparkline=false",
        timeout=30,
    ) as response:
        markets = json.loads(response.read().decode("utf-8"))

    universe_rows: list[dict] = []
    for rank, coin in enumerate(markets, start=1):
        symbol = (coin.get("symbol") or "").upper()
        if not symbol:
            continue
        universe_rows.append(
            {
                "rank": rank,
                "id": coin.get("id"),
                "symbol": symbol,
                "name": coin.get("name"),
                "market_cap_usd": coin.get("market_cap"),
                "volume_24h_usd": coin.get("total_volume"),
                "price_usd": coin.get("current_price"),
            }
        )

    universe = pd.DataFrame(universe_rows).drop_duplicates(subset=["symbol"], keep="first")

    liquidity_threshold = 10_000_000
    history_threshold = 365

    universe["passes_liquidity"] = universe["volume_24h_usd"].fillna(0) >= liquidity_threshold

    close_series_by_symbol: dict[str, pd.Series] = {}
    coverage_rows: list[dict] = []
    for row in universe.to_dict(orient="records"):
        symbol = row["symbol"]
        ticker = f"{symbol}-USD"
        close_series = download_close(ticker)
        close_series_by_symbol[symbol] = close_series

        coverage_row = dict(row)
        coverage_row["ticker"] = ticker
        coverage_row["history_obs"] = int(len(close_series))
        coverage_row["passes_history"] = len(close_series) >= history_threshold
        coverage_rows.append(coverage_row)

    coverage = pd.DataFrame(coverage_rows)
    eligible = coverage[(coverage["passes_liquidity"]) & (coverage["passes_history"])].copy()

    metric_rows: list[dict] = []
    for _, row in eligible.iterrows():
        symbol = row["symbol"]
        series = close_series_by_symbol[symbol]
        metrics = fit_power(series)
        metrics.update(
            {
                "symbol": symbol,
                "ticker": row["ticker"],
                "rank": int(row["rank"]),
                "name": row["name"],
                "market_cap_usd": float(row["market_cap_usd"]) if pd.notna(row["market_cap_usd"]) else float("nan"),
                "volume_24h_usd": float(row["volume_24h_usd"]) if pd.notna(row["volume_24h_usd"]) else float("nan"),
            }
        )
        metric_rows.append(metrics)

    metrics = pd.DataFrame(metric_rows)
    metrics = metrics[(metrics["latest_price"] < 0.97) | (metrics["latest_price"] > 1.03)].copy()

    btc_b = float(metrics.loc[metrics["symbol"] == "BTC", "exponent_b"].iloc[0])
    btc_r2 = float(metrics.loc[metrics["symbol"] == "BTC", "r2"].iloc[0])

    metrics["exp_distance_to_btc"] = (metrics["exponent_b"] - btc_b).abs()
    liquidity_component = np.clip(np.log10(metrics["volume_24h_usd"].fillna(0.0) + 1.0) / 10.0, 0.0, 1.0)
    metrics["score"] = (
        0.50 * metrics["r2"]
        + 0.30 * (1.0 / (1.0 + metrics["exp_distance_to_btc"]))
        + 0.20 * liquidity_component
    )
    metrics = metrics.sort_values(["score", "r2"], ascending=False)

    coverage_path = out_dir / "2026-04-07-power-law-coverage.csv"
    metrics_path = out_dir / "2026-04-07-power-law-quant-expansion-metrics.csv"
    meta_path = out_dir / "2026-04-07-power-law-quant-expansion-meta.json"

    coverage.to_csv(coverage_path, index=False)
    metrics.to_csv(metrics_path, index=False)

    meta = {
        "liquidity_threshold_24h_usd": liquidity_threshold,
        "history_threshold_days": history_threshold,
        "universe_rows": int(len(coverage)),
        "eligible_rows": int(len(eligible)),
        "nonstable_rows": int(len(metrics)),
        "btc_reference_exponent_b": btc_b,
        "btc_reference_r2": btc_r2,
        "generated_date": "2026-04-07",
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(coverage_path)
    print(metrics_path)
    print(meta_path)


if __name__ == "__main__":
    main()
