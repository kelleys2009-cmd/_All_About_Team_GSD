from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class CoinSpec:
    symbol: str
    ticker: str
    genesis_date: str


COINS = [
    CoinSpec("BTC", "BTC-USD", "2009-01-03"),
    CoinSpec("ETH", "ETH-USD", "2015-07-30"),
    CoinSpec("XRP", "XRP-USD", "2012-06-02"),
    CoinSpec("SOL", "SOL-USD", "2020-03-16"),
    CoinSpec("DOGE", "DOGE-USD", "2013-12-06"),
]


def download_close_series(ticker: str) -> pd.Series:
    frame = yf.download(ticker, period="max", interval="1d", auto_adjust=False, progress=False)
    if frame.empty:
        raise RuntimeError(f"No data returned for {ticker}")

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


def fit_power_law(series: pd.Series, genesis_date: str) -> tuple[dict, pd.DataFrame]:
    genesis = pd.Timestamp(genesis_date, tz="UTC")
    idx = pd.to_datetime(series.index, utc=True)
    age_days = (idx - genesis).days.astype(float)

    mask = age_days > 0
    idx = idx[mask]
    age_days = age_days[mask]
    prices = series[mask]

    ln_age = np.log(age_days)
    ln_price = np.log(prices.values)

    slope_b, intercept_a = np.polyfit(ln_age, ln_price, 1)
    pred_ln = intercept_a + slope_b * ln_age
    residual = ln_price - pred_ln

    ss_res = float(np.sum((ln_price - pred_ln) ** 2))
    ss_tot = float(np.sum((ln_price - np.mean(ln_price)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    age_multiplier_for_double = float(2.0 ** (1.0 / slope_b))
    doubling_age_pct = age_multiplier_for_double - 1.0

    latest_age = float(age_days[-1])
    implied_days_to_double_now = doubling_age_pct * latest_age

    model_fair = float(np.exp(pred_ln[-1]))
    latest_price = float(prices.iloc[-1])

    q10, q50, q90 = np.quantile(np.exp(residual), [0.1, 0.5, 0.9])
    residual_percentile = float((residual <= residual[-1]).mean())

    metrics = {
        "start": str(idx[0].date()),
        "end": str(idx[-1].date()),
        "obs": int(len(prices)),
        "exponent_b": float(slope_b),
        "intercept_a": float(intercept_a),
        "r2": float(r2),
        "doubling_age_pct": float(doubling_age_pct),
        "implied_days_to_double_now": float(implied_days_to_double_now),
        "latest_price": float(latest_price),
        "model_fair_value": float(model_fair),
        "price_to_fair": float(latest_price / model_fair),
        "residual_percentile": float(residual_percentile),
        "residual_q10_mult": float(q10),
        "residual_q50_mult": float(q50),
        "residual_q90_mult": float(q90),
    }

    series_df = pd.DataFrame(
        {
            "date": idx.tz_convert(None),
            "price": prices.values,
            "age_days": age_days,
            "ln_price": ln_price,
            "ln_age": ln_age,
            "pred_ln": pred_ln,
            "residual_ln": residual,
        }
    )
    return metrics, series_df


def trailing_returns(price_panel: pd.DataFrame, horizons: list[int]) -> pd.DataFrame:
    rows: list[dict] = []
    for symbol, group in price_panel.groupby("symbol"):
        group = group.sort_values("date").reset_index(drop=True)
        for days in horizons:
            if len(group) <= days:
                continue
            r = float(group.loc[len(group) - 1, "price"] / group.loc[len(group) - 1 - days, "price"] - 1.0)
            rows.append({"symbol": symbol, "horizon_days": days, "return": r})
    return pd.DataFrame(rows)


def main() -> None:
    out_dir = Path("artifacts/tea-88")
    out_dir.mkdir(parents=True, exist_ok=True)

    metric_rows = []
    panel_rows = []

    for coin in COINS:
        close_series = download_close_series(coin.ticker)
        metrics, series_df = fit_power_law(close_series, coin.genesis_date)
        metrics["symbol"] = coin.symbol
        metrics["ticker"] = coin.ticker
        metrics["genesis_date"] = coin.genesis_date
        metric_rows.append(metrics)

        series_df["symbol"] = coin.symbol
        panel_rows.append(series_df)

    metrics_df = pd.DataFrame(metric_rows).sort_values("symbol").reset_index(drop=True)
    panel_df = pd.concat(panel_rows, ignore_index=True)

    horizons = [365, 730, 1095]
    ret_df = trailing_returns(panel_df[["date", "symbol", "price"]], horizons)

    metrics_path = out_dir / "2026-04-06-power-law-cross-asset-metrics.csv"
    panel_path = out_dir / "2026-04-06-power-law-cross-asset-panel.csv"
    returns_path = out_dir / "2026-04-06-power-law-cross-asset-returns.csv"
    summary_path = out_dir / "2026-04-06-power-law-cross-asset-summary.json"

    metrics_df.to_csv(metrics_path, index=False)
    panel_df.to_csv(panel_path, index=False)
    ret_df.to_csv(returns_path, index=False)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "OLS on log(price) vs log(age_days_since_genesis)",
        "symbols": [c.symbol for c in COINS],
        "metrics": metrics_df.to_dict(orient="records"),
        "trailing_returns": ret_df.to_dict(orient="records"),
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(str(metrics_path))
    print(str(panel_path))
    print(str(returns_path))
    print(str(summary_path))


if __name__ == "__main__":
    main()
