import argparse
import json
import os
from typing import Any

import numpy as np
import pandas as pd


def table_summary(df: pd.DataFrame, name: str, key_cols: list[str] | None = None) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "table": name,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "top_missing_columns": (
            (df.isna().mean() * 100)
            .sort_values(ascending=False)
            .head(15)
            .round(2)
            .to_dict()
        ),
    }

    if key_cols:
        for key in key_cols:
            if key in df.columns:
                summary[f"{key}_nunique"] = int(df[key].nunique(dropna=True))
                summary[f"{key}_duplicate_rows"] = int(df.duplicated(subset=[key]).sum())

    return summary


def application_checks(df: pd.DataFrame) -> dict[str, Any]:
    return {
        "target_default_rate_pct": round(float(df["TARGET"].mean() * 100), 2),
        "days_employed_365243_count": int((df["DAYS_EMPLOYED"] == 365243).sum()),
        "days_birth_positive_count": int((df["DAYS_BIRTH"] > 0).sum()),
        "negative_income_count": int((df["AMT_INCOME_TOTAL"] < 0).sum()),
        "credit_less_than_annuity_count": int((df["AMT_CREDIT"] < df["AMT_ANNUITY"]).sum()),
    }


def bureau_checks(df: pd.DataFrame) -> dict[str, Any]:
    return {
        "rows_with_credit_day_overdue_gt_0": int((df["CREDIT_DAY_OVERDUE"] > 0).sum()),
        "rows_with_debt_gt_credit_sum": int((df["AMT_CREDIT_SUM_DEBT"] > df["AMT_CREDIT_SUM"]).sum()),
        "active_credit_share_pct": round(float((df["CREDIT_ACTIVE"] == "Active").mean() * 100), 2),
        "closed_credit_share_pct": round(float((df["CREDIT_ACTIVE"] == "Closed").mean() * 100), 2),
        "avg_bureau_records_per_client": round(float(df.groupby("SK_ID_CURR").size().mean()), 2),
    }


def previous_application_checks(df: pd.DataFrame) -> dict[str, Any]:
    out = {
        "approved_share_pct": round(float((df["NAME_CONTRACT_STATUS"] == "Approved").mean() * 100), 2),
        "refused_share_pct": round(float((df["NAME_CONTRACT_STATUS"] == "Refused").mean() * 100), 2),
        "canceled_share_pct": round(float((df["NAME_CONTRACT_STATUS"] == "Canceled").mean() * 100), 2),
        "unused_offer_share_pct": round(float((df["NAME_CONTRACT_STATUS"] == "Unused offer").mean() * 100), 2),
        "avg_previous_applications_per_client": round(float(df.groupby("SK_ID_CURR").size().mean()), 2),
        "rows_with_application_gt_credit": int((df["AMT_APPLICATION"] > df["AMT_CREDIT"]).sum()),
    }
    if "NFLAG_LAST_APPL_IN_DAY" in df.columns:
        out["rows_not_last_application_in_day"] = int((df["NFLAG_LAST_APPL_IN_DAY"] == 0).sum())
    return out


def make_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Отчёт по качеству данных",
        "",
        "## Общая сводка",
        ""
    ]

    for table_name, table_summary_dict in summary["tables"].items():
        lines.append(f"### {table_name}")
        lines.append(f"- строк: {table_summary_dict['rows']}")
        lines.append(f"- колонок: {table_summary_dict['columns']}")
        for k, v in table_summary_dict.items():
            if k.endswith("_duplicate_rows"):
                lines.append(f"- {k}: {v}")
        lines.append("- топ колонок по доле пропусков:")
        for col, pct in table_summary_dict["top_missing_columns"].items():
            lines.append(f"  - {col}: {pct}%")
        lines.append("")

    lines.extend([
        "## Проверки и наблюдения",
        "",
        "### application_train.csv",
    ])
    for k, v in summary["checks"]["application_train"].items():
        lines.append(f"- {k}: {v}")

    lines.extend([
        "",
        "### bureau.csv",
    ])
    for k, v in summary["checks"]["bureau"].items():
        lines.append(f"- {k}: {v}")

    if "previous_application" in summary["checks"]:
        lines.extend([
            "",
            "### previous_application.csv",
        ])
        for k, v in summary["checks"]["previous_application"].items():
            lines.append(f"- {k}: {v}")

    lines.extend([
        "",
        "## Интерпретация",
        "",
        "- `application_train.csv` является главной таблицей витрины: `1 строка = 1 заявка`, ключ — `SK_ID_CURR`.",
        "- В `application_train.csv` нет дублей по `SK_ID_CURR`.",
        "- Значение `DAYS_EMPLOYED = 365243` выглядит как технический код аномалии, а не реальный стаж; его стоит выносить в отдельный флаг и заменять на `NaN` для расчётов.",
        "- В `bureau.csv` одна заявка / клиент может иметь несколько записей по внешним кредитам; это слой `1:N`, который нужно агрегировать перед объединением с базовой заявкой.",
        "- В `previous_application.csv` один клиент может иметь несколько прошлых заявок; это второй важный слой `1:N`, который нужно агрегировать до уровня клиента/текущей заявки.",
        "- Существенные пропуски наблюдаются в жилищных признаках `application_train.csv`, в финансовых колонках `bureau.csv` и части стоимостных полей `previous_application.csv`, поэтому витрина должна явно фиксировать стратегию обработки пропусков.",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    app = pd.read_csv(os.path.join(args.data_dir, "application_train.csv"), low_memory=False)
    bureau = pd.read_csv(os.path.join(args.data_dir, "bureau.csv"), low_memory=False)

    summary = {
        "tables": {
            "application_train": table_summary(app, "application_train", ["SK_ID_CURR"]),
            "bureau": table_summary(bureau, "bureau", ["SK_ID_BUREAU", "SK_ID_CURR"]),
        },
        "checks": {
            "application_train": application_checks(app),
            "bureau": bureau_checks(bureau),
        }
    }

    prev_path = os.path.join(args.data_dir, "previous_application.csv")
    if os.path.exists(prev_path):
        prev = pd.read_csv(prev_path, low_memory=False)
        summary["tables"]["previous_application"] = table_summary(prev, "previous_application", ["SK_ID_PREV", "SK_ID_CURR"])
        summary["checks"]["previous_application"] = previous_application_checks(prev)

    json_path = os.path.join(args.output_dir, "data_quality_summary.json")
    md_path = os.path.join(args.output_dir, "data_quality_report.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(make_markdown(summary))

    print(f"Saved: {json_path}")
    print(f"Saved: {md_path}")


if __name__ == "__main__":
    main()
