from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import matplotlib.pyplot as plt
import seaborn as sns

DATA_ROOT = Path("..") / "dsa-data"
OUTPUT_DIR = Path("outputs") / "feb2025"

PLATFORMS = {
    "tiktok": "tiktok___full",
    "x": "x___full",
}

PLATFORM_LABELS = {
    "tiktok": "TikTok",
    "x": "X",
}

DATE_START = date(2025, 2, 13)
DATE_END = date(2025, 3, 2)
ELECTION_DATE = date(2025, 2, 23)

AGG_COLUMNS = [
    "category",
    "decision_ground",
    "automated_decision",
    "automated_detection",
    "created_at",
]


def date_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def iter_day_files(platform_key: str):
    base = DATA_ROOT / PLATFORMS[platform_key] / "daily_dumps_chunked"
    for day in date_range(DATE_START, DATE_END):
        folder = base / f"sor-{platform_key}-{day.isoformat()}-full"
        if not folder.exists():
            continue
        files = sorted(folder.glob("part-*.parquet"))
        if files:
            yield day, files


def process_platform(platform_key: str):
    counters = {col: Counter() for col in AGG_COLUMNS if col != "created_at"}
    daily_counter = Counter()
    total_rows = 0

    for day, files in iter_day_files(platform_key):
        for file_path in files:
            table = pq.read_table(file_path, columns=AGG_COLUMNS)
            df = table.to_pandas()
            df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
            df["created_date"] = df["created_at"].dt.date

            mask = (df["created_date"] >= DATE_START) & (df["created_date"] <= DATE_END)
            df = df.loc[mask]
            if df.empty:
                continue

            for col in counters:
                counters[col].update(df[col].fillna("UNKNOWN").tolist())
            daily_counter.update(df["created_date"].tolist())
            total_rows += len(df)

    daily_df = pd.DataFrame(
        [
            {
                "platform_name": PLATFORM_LABELS[platform_key],
                "created_date": day,
                "count": count,
            }
            for day, count in sorted(daily_counter.items())
        ]
    )
    return counters, daily_df, total_rows


def counter_to_share_df(counter: Counter, platform_label: str, col: str, total: int) -> pd.DataFrame:
    df = pd.DataFrame({col: list(counter.keys()), "count": list(counter.values())})
    df["share"] = df["count"] / total if total else 0
    df["platform_name"] = platform_label
    return df.sort_values("share", ascending=False)


def top_categories_for_plot(df: pd.DataFrame, col: str, top_n: int = 8) -> pd.DataFrame:
    total = df.groupby(col, dropna=False)["count"].sum().sort_values(ascending=False)
    top = total.head(top_n).index.tolist()
    df_plot = df.copy()
    df_plot[col] = df_plot[col].where(df_plot[col].isin(top), other="OTHER")
    return df_plot


def plot_share_bar(df: pd.DataFrame, col: str, title: str, out_path: Path):
    df_plot = top_categories_for_plot(df, col)
    df_plot = df_plot.groupby(["platform_name", col], dropna=False)["count"].sum().reset_index()
    df_plot["share"] = df_plot["count"] / df_plot.groupby("platform_name")["count"].transform("sum")

    plt.figure(figsize=(10, 5))
    sns.barplot(
        data=df_plot,
        x=col,
        y="share",
        hue="platform_name",
        dodge=True,
    )
    plt.title(title)
    plt.ylabel("Share of SoRs")
    plt.xlabel(col)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def pre_post_summary(daily: pd.DataFrame) -> pd.DataFrame:
    pre = daily[daily["created_date"] < ELECTION_DATE]
    post = daily[daily["created_date"] > ELECTION_DATE]

    def summarize(group: pd.DataFrame, label: str) -> pd.DataFrame:
        summary = (
            group.groupby("platform_name")["count"]
            .agg(["mean", "std", "min", "max"])
            .reset_index()
        )
        summary["period"] = label
        summary["cv"] = summary["std"] / summary["mean"]
        return summary

    summary_pre = summarize(pre, "pre")
    summary_post = summarize(post, "post")

    combined = pd.concat([summary_pre, summary_post], ignore_index=True)
    pivot = combined.pivot(index="platform_name", columns="period", values="mean").reset_index()
    pivot["pct_change_post_vs_pre"] = (pivot["post"] - pivot["pre"]) / pivot["pre"]

    combined = combined.merge(
        pivot[["platform_name", "pct_change_post_vs_pre"]],
        on="platform_name",
        how="left",
    )
    return combined


def plot_daily_counts(daily: pd.DataFrame, out_path: Path):
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=daily, x="created_date", y="count", hue="platform_name", marker="o")
    plt.axvline(ELECTION_DATE, color="black", linestyle="--", linewidth=1)
    plt.title("Daily SoRs (window around election)")
    plt.ylabel("SoR count")
    plt.xlabel("Date")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def write_report(
    report_path: Path,
    rq1_category: pd.DataFrame,
    rq1_ground: pd.DataFrame,
    rq2_summary: pd.DataFrame,
    rq3_decision: pd.DataFrame,
    rq3_detection: pd.DataFrame,
):
    def top_n_by_platform(df: pd.DataFrame, col: str, n: int = 5) -> pd.DataFrame:
        return (
            df.sort_values("share", ascending=False)
            .groupby("platform_name", dropna=False)
            .head(n)[["platform_name", col, "count", "share"]]
        )

    lines = []
    lines.append("# Feb 2025 Snippet Report (TikTok vs X)\n")
    lines.append("Window (created_at): 2025-02-13 to 2025-03-02 (election on 2025-02-23, Germany)\n")
    lines.append("Normalization: shares within platform (total SoRs in window)\n")

    lines.append("## RQ1: Moderation profiles (category and decision ground)\n")
    lines.append("Top categories by share (per platform):\n")
    lines.append(top_n_by_platform(rq1_category, "category").to_markdown(index=False))
    lines.append("")
    lines.append("Top decision grounds by share (per platform):\n")
    lines.append(top_n_by_platform(rq1_ground, "decision_ground").to_markdown(index=False))
    lines.append("")

    lines.append("## RQ2: Event dynamics around election\n")
    lines.append("Pre vs post daily counts (mean, std, cv, pct change):\n")
    lines.append(rq2_summary.to_markdown(index=False))
    lines.append("")

    lines.append("## RQ3: Automation reliance\n")
    lines.append("Automated decision shares:\n")
    lines.append(rq3_decision.head(12).to_markdown(index=False))
    lines.append("")
    lines.append("Automated detection shares:\n")
    lines.append(rq3_detection.head(12).to_markdown(index=False))
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_category = []
    all_ground = []
    all_decision = []
    all_detection = []
    daily_frames = []

    for platform_key in PLATFORMS:
        counters, daily_df, total_rows = process_platform(platform_key)
        label = PLATFORM_LABELS[platform_key]

        all_category.append(counter_to_share_df(counters["category"], label, "category", total_rows))
        all_ground.append(counter_to_share_df(counters["decision_ground"], label, "decision_ground", total_rows))
        all_decision.append(
            counter_to_share_df(counters["automated_decision"], label, "automated_decision", total_rows)
        )
        all_detection.append(
            counter_to_share_df(counters["automated_detection"], label, "automated_detection", total_rows)
        )
        daily_frames.append(daily_df)

    rq1_category = pd.concat(all_category, ignore_index=True)
    rq1_ground = pd.concat(all_ground, ignore_index=True)
    rq3_decision = pd.concat(all_decision, ignore_index=True)
    rq3_detection = pd.concat(all_detection, ignore_index=True)
    daily = pd.concat(daily_frames, ignore_index=True)

    rq1_category.to_csv(OUTPUT_DIR / "rq1_category_share.csv", index=False)
    rq1_ground.to_csv(OUTPUT_DIR / "rq1_decision_ground_share.csv", index=False)
    rq3_decision.to_csv(OUTPUT_DIR / "rq3_automated_decision_share.csv", index=False)
    rq3_detection.to_csv(OUTPUT_DIR / "rq3_automated_detection_share.csv", index=False)
    daily.to_csv(OUTPUT_DIR / "rq2_daily_counts.csv", index=False)

    rq2_summary = pre_post_summary(daily)
    rq2_summary.to_csv(OUTPUT_DIR / "rq2_pre_post_summary.csv", index=False)

    plot_share_bar(
        rq1_category,
        "category",
        "Category share by platform (top categories)",
        OUTPUT_DIR / "fig_category_share.png",
    )
    plot_share_bar(
        rq1_ground,
        "decision_ground",
        "Decision ground share by platform (top grounds)",
        OUTPUT_DIR / "fig_decision_ground_share.png",
    )
    plot_daily_counts(daily, OUTPUT_DIR / "fig_daily_counts.png")

    write_report(
        OUTPUT_DIR / "report.md",
        rq1_category,
        rq1_ground,
        rq2_summary,
        rq3_decision,
        rq3_detection,
    )


if __name__ == "__main__":
    main()
