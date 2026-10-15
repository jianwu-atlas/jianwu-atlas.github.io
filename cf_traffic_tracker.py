#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cf_traffic_tracker.py
---------------------------------
用于 GitHub Actions 定期调用：拉取 Cloudflare Web Analytics 数据，
生成/更新月度趋势图、月度汇总 CSV，以及 shields.io 兼容的 badge.json，
全部写入仓库内的 traffic_report/ 目录，由 workflow 自动 commit + push。

与 fetch_github_traffic.py（jwtools 仓库用）的差异：
    - 数据源是 Cloudflare GraphQL Analytics API 而不是 GitHub Traffic API
    - Cloudflare 数据本身不受 14 天限制，但依然按月归档，
      一方面防止账号/站点变更导致历史数据丢失，另一方面方便直接
      在网站首页 embed 展示。

依赖:
    pip install requests pandas matplotlib --break-system-packages

用法（本地测试）:
    export CF_API_TOKEN="..."
    python cf_traffic_tracker.py \
        --account-id <Account ID> \
        --site-tag <Web Analytics Site Tag> \
        --months 3 \
        --outdir traffic_report \
        --site-label "jackng88.github.io"
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
import matplotlib.pyplot as plt

GRAPHQL_URL = "https://api.cloudflare.com/client/v4/graphql"

QUERY = """
query MonthlyWebAnalytics($accountTag: String!, $siteTag: String!, $since: Time!, $until: Time!, $limit: Int!) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      rumPageloadEventsAdaptiveGroups(
        limit: $limit
        filter: { siteTag: $siteTag, datetime_geq: $since, datetime_lt: $until }
        orderBy: [date_ASC]
      ) {
        dimensions {
          date
        }
        count
        sum {
          visits
        }
      }
    }
  }
}
"""


def fetch_daily_data_chunk(api_token: str, account_id: str, site_tag: str,
                           since: datetime, until: datetime) -> pd.DataFrame:
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    variables = {
        "accountTag": account_id,
        "siteTag": site_tag,
        "since": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "until": until.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": 10000,
    }
    resp = requests.post(
        GRAPHQL_URL, headers=headers,
        json={"query": QUERY, "variables": variables}, timeout=60,
    )
    resp.raise_for_status()
    payload = resp.json()

    if payload.get("errors"):
        raise RuntimeError(f"Cloudflare GraphQL 返回错误: {payload['errors']}")

    accounts = payload["data"]["viewer"]["accounts"]
    if not accounts:
        raise RuntimeError("未查询到该 accountTag 下的数据，请检查 --account-id 是否正确、"
                            "以及 API Token 是否有 Account Analytics: Read 权限。")

    groups = accounts[0]["rumPageloadEventsAdaptiveGroups"]
    rows = [{"date": g["dimensions"]["date"], "page_views": g["count"],
             "visits": g["sum"]["visits"]} for g in groups]

    df = pd.DataFrame(rows)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


def fetch_daily_data(api_token: str, account_id: str, site_tag: str,
                     since: datetime, until: datetime, chunk_days: int = 90) -> pd.DataFrame:
    chunks = []
    chunk_start = since
    while chunk_start < until:
        chunk_end = min(chunk_start + timedelta(days=chunk_days), until)
        chunk_df = fetch_daily_data_chunk(api_token, account_id, site_tag, chunk_start, chunk_end)
        if not chunk_df.empty:
            chunks.append(chunk_df)
        chunk_start = chunk_end

    if not chunks:
        return pd.DataFrame(columns=["date", "page_views", "visits"])

    daily = pd.concat(chunks, ignore_index=True)
    daily = daily.drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)
    return daily


def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["month", "page_views", "visits", "month_label"])
    monthly = (
        df.set_index("date").resample("MS").sum(numeric_only=True).reset_index()
        .rename(columns={"date": "month"})
    )
    monthly["month_label"] = monthly["month"].dt.strftime("%Y-%m")
    return monthly


def plot_trend(monthly: pd.DataFrame, outpath: str, site_label: str):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(monthly["month_label"], monthly["page_views"], marker="o",
            linewidth=2, color="#2b6cb0", label="Page Views")
    ax.plot(monthly["month_label"], monthly["visits"], marker="s",
            linewidth=2, color="#dd6b20", label="Visits")

    for x, y in zip(monthly["month_label"], monthly["page_views"]):
        ax.annotate(str(int(y)), (x, y), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=9, color="#2b6cb0")
    for x, y in zip(monthly["month_label"], monthly["visits"]):
        ax.annotate(str(int(y)), (x, y), textcoords="offset points",
                    xytext=(0, -14), ha="center", fontsize=9, color="#dd6b20")

    ax.set_title(f"{site_label} — Monthly Web Analytics Trend", fontsize=14, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Count")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="upper left")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def generate_badges(monthly: pd.DataFrame, outdir: str):
    """生成最近一个自然月的 Page Views / Visits shields.io badge.json。"""
    if monthly.empty:
        return
    latest = monthly.iloc[-1]
    views_badge = {"schemaVersion": 1, "label": f"page views ({latest['month_label']})",
                   "message": str(int(latest["page_views"])), "color": "blue"}
    visits_badge = {"schemaVersion": 1, "label": f"visits ({latest['month_label']})",
                    "message": str(int(latest["visits"])), "color": "orange"}

    with open(os.path.join(outdir, "badge_pageviews.json"), "w") as f:
        json.dump(views_badge, f)
    with open(os.path.join(outdir, "badge_visits.json"), "w") as f:
        json.dump(visits_badge, f)
    print(f"徽章 JSON 已生成: page_views={int(latest['page_views'])}, visits={int(latest['visits'])}")


def main():
    parser = argparse.ArgumentParser(description="拉取 Cloudflare Web Analytics 数据并生成月度趋势图（供 GitHub Action 定期调用）")
    parser.add_argument("--account-id", required=True)
    parser.add_argument("--site-tag", required=True)
    parser.add_argument("--months", type=int, default=3,
                         help="回溯多少个月（默认3；Cloudflare单次查询时间跨度上限约为13周2天/93天，"
                              "超过会报错 'time range wider than 13w2d'，因此不要设置超过约3个月）")
    parser.add_argument("--outdir", default="traffic_report")
    parser.add_argument("--site-label", default="jackng88.github.io")
    args = parser.parse_args()

    api_token = os.environ.get("CF_API_TOKEN")
    if not api_token:
        sys.exit("错误: 请先设置环境变量 CF_API_TOKEN")

    os.makedirs(args.outdir, exist_ok=True)

    until = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    since = until - timedelta(days=31 * args.months)

    print(f"拉取数据区间: {since.date()} ~ {until.date()} ...")
    daily_df = fetch_daily_data(api_token, args.account_id, args.site_tag, since, until)
    print(f"拉取到 {len(daily_df)} 天的数据。")

    daily_df.to_csv(os.path.join(args.outdir, "daily_raw.csv"), index=False)

    monthly_df = aggregate_monthly(daily_df)
    monthly_df.to_csv(os.path.join(args.outdir, "monthly_summary.csv"), index=False)
    print(monthly_df[["month_label", "page_views", "visits"]].to_string(index=False))

    if not monthly_df.empty:
        plot_trend(monthly_df, os.path.join(args.outdir, "monthly_trend.png"), args.site_label)
        generate_badges(monthly_df, args.outdir)
    else:
        print("没有数据可绘图。")


if __name__ == "__main__":
    main()
