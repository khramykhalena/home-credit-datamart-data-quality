import argparse
import os
import numpy as np
import pandas as pd


BASE_APP_COLS = [
    "SK_ID_CURR", "TARGET", "NAME_CONTRACT_TYPE", "CODE_GENDER", "FLAG_OWN_CAR",
    "FLAG_OWN_REALTY", "CNT_CHILDREN", "AMT_INCOME_TOTAL", "AMT_CREDIT",
    "AMT_ANNUITY", "AMT_GOODS_PRICE", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE",
    "NAME_FAMILY_STATUS", "NAME_HOUSING_TYPE", "REGION_POPULATION_RELATIVE",
    "DAYS_BIRTH", "DAYS_EMPLOYED", "DAYS_REGISTRATION", "DAYS_ID_PUBLISH",
    "CNT_FAM_MEMBERS", "REGION_RATING_CLIENT", "REGION_RATING_CLIENT_W_CITY",
    "WEEKDAY_APPR_PROCESS_START", "HOUR_APPR_PROCESS_START", "ORGANIZATION_TYPE",
    "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "DAYS_LAST_PHONE_CHANGE",
    "AMT_REQ_CREDIT_BUREAU_YEAR"
]

BUREAU_COLS = [
    "SK_ID_CURR", "SK_ID_BUREAU", "CREDIT_ACTIVE", "CREDIT_CURRENCY",
    "DAYS_CREDIT", "CREDIT_DAY_OVERDUE", "DAYS_CREDIT_ENDDATE",
    "DAYS_ENDDATE_FACT", "AMT_CREDIT_MAX_OVERDUE", "CNT_CREDIT_PROLONG",
    "AMT_CREDIT_SUM", "AMT_CREDIT_SUM_DEBT", "AMT_CREDIT_SUM_LIMIT",
    "AMT_CREDIT_SUM_OVERDUE", "CREDIT_TYPE", "DAYS_CREDIT_UPDATE", "AMT_ANNUITY"
]


def safe_div(a: pd.Series, b: pd.Series) -> pd.Series:
    return np.where((b.notna()) & (b != 0), a / b, np.nan)


def load_application(data_dir: str) -> pd.DataFrame:
    app = pd.read_csv(os.path.join(data_dir, "application_train.csv"), usecols=BASE_APP_COLS, low_memory=False)

    days_employed_clean = app["DAYS_EMPLOYED"].replace({365243: np.nan})

    app["age_years"] = np.abs(app["DAYS_BIRTH"]) / 365.25
    app["employment_years"] = np.abs(days_employed_clean) / 365.25
    app["days_employed_anom_flag"] = (app["DAYS_EMPLOYED"] == 365243).astype(int)
    app["credit_income_ratio"] = safe_div(app["AMT_CREDIT"], app["AMT_INCOME_TOTAL"])
    app["annuity_income_ratio"] = safe_div(app["AMT_ANNUITY"], app["AMT_INCOME_TOTAL"])
    app["credit_goods_ratio"] = safe_div(app["AMT_CREDIT"], app["AMT_GOODS_PRICE"])
    app["employment_age_ratio"] = safe_div(np.abs(days_employed_clean), np.abs(app["DAYS_BIRTH"]))

    return app


def build_bureau_agg(data_dir: str) -> pd.DataFrame:
    path = os.path.join(data_dir, "bureau.csv")
    if not os.path.exists(path):
        raise FileNotFoundError("bureau.csv not found")

    bureau = pd.read_csv(path, usecols=BUREAU_COLS, low_memory=False)

    tmp = bureau.copy()
    tmp["is_active_credit"] = (tmp["CREDIT_ACTIVE"] == "Active").astype(int)
    tmp["is_closed_credit"] = (tmp["CREDIT_ACTIVE"] == "Closed").astype(int)
    tmp["is_bad_debt_credit"] = (tmp["CREDIT_ACTIVE"] == "Bad debt").astype(int)
    tmp["is_sold_credit"] = (tmp["CREDIT_ACTIVE"] == "Sold").astype(int)
    tmp["has_overdue"] = (tmp["CREDIT_DAY_OVERDUE"] > 0).astype(int)
    tmp["credit_sum_debt_filled"] = tmp["AMT_CREDIT_SUM_DEBT"].fillna(0)
    tmp["credit_sum_filled"] = tmp["AMT_CREDIT_SUM"].fillna(0)
    tmp["credit_sum_overdue_filled"] = tmp["AMT_CREDIT_SUM_OVERDUE"].fillna(0)
    tmp["credit_limit_filled"] = tmp["AMT_CREDIT_SUM_LIMIT"].fillna(0)
    tmp["annuity_filled"] = tmp["AMT_ANNUITY"].fillna(0)
    tmp["max_overdue_filled"] = tmp["AMT_CREDIT_MAX_OVERDUE"].fillna(0)
    tmp["days_credit_enddate_pos"] = np.where(tmp["DAYS_CREDIT_ENDDATE"] > 0, tmp["DAYS_CREDIT_ENDDATE"], np.nan)

    agg = tmp.groupby("SK_ID_CURR").agg(
        bureau_records_count=("SK_ID_BUREAU", "count"),
        bureau_active_credit_count=("is_active_credit", "sum"),
        bureau_closed_credit_count=("is_closed_credit", "sum"),
        bureau_bad_debt_credit_count=("is_bad_debt_credit", "sum"),
        bureau_sold_credit_count=("is_sold_credit", "sum"),
        bureau_overdue_credit_count=("has_overdue", "sum"),
        bureau_credit_day_overdue_max=("CREDIT_DAY_OVERDUE", "max"),
        bureau_credit_day_overdue_mean=("CREDIT_DAY_OVERDUE", "mean"),
        bureau_total_credit_sum=("credit_sum_filled", "sum"),
        bureau_total_credit_debt_sum=("credit_sum_debt_filled", "sum"),
        bureau_total_credit_overdue_sum=("credit_sum_overdue_filled", "sum"),
        bureau_total_credit_limit_sum=("credit_limit_filled", "sum"),
        bureau_total_annuity_sum=("annuity_filled", "sum"),
        bureau_total_prolong_sum=("CNT_CREDIT_PROLONG", "sum"),
        bureau_total_max_overdue_sum=("max_overdue_filled", "sum"),
        bureau_days_credit_mean=("DAYS_CREDIT", "mean"),
        bureau_days_credit_min=("DAYS_CREDIT", "min"),
        bureau_days_credit_max=("DAYS_CREDIT", "max"),
        bureau_days_credit_update_mean=("DAYS_CREDIT_UPDATE", "mean"),
        bureau_future_enddate_mean=("days_credit_enddate_pos", "mean"),
        bureau_unique_credit_types=("CREDIT_TYPE", "nunique"),
        bureau_unique_currencies=("CREDIT_CURRENCY", "nunique")
    ).reset_index()

    agg["bureau_debt_to_credit_ratio"] = np.where(
        agg["bureau_total_credit_sum"] != 0,
        agg["bureau_total_credit_debt_sum"] / agg["bureau_total_credit_sum"],
        np.nan
    )

    return agg


def build_previous_application_agg(data_dir: str) -> pd.DataFrame | None:
    path = os.path.join(data_dir, "previous_application.csv")
    if not os.path.exists(path):
        return None

    cols = [
        "SK_ID_CURR", "SK_ID_PREV", "NAME_CONTRACT_STATUS", "AMT_APPLICATION",
        "AMT_CREDIT", "AMT_ANNUITY", "HOUR_APPR_PROCESS_START",
        "RATE_DOWN_PAYMENT", "DAYS_DECISION"
    ]
    prev = pd.read_csv(path, usecols=cols, low_memory=False)
    prev["is_prev_approved"] = (prev["NAME_CONTRACT_STATUS"] == "Approved").astype(int)
    prev["is_prev_refused"] = (prev["NAME_CONTRACT_STATUS"] == "Refused").astype(int)

    agg = prev.groupby("SK_ID_CURR").agg(
        prev_app_count=("SK_ID_PREV", "count"),
        prev_approved_count=("is_prev_approved", "sum"),
        prev_refused_count=("is_prev_refused", "sum"),
        prev_amt_application_sum=("AMT_APPLICATION", "sum"),
        prev_amt_credit_sum=("AMT_CREDIT", "sum"),
        prev_amt_annuity_sum=("AMT_ANNUITY", "sum"),
        prev_hour_appr_mean=("HOUR_APPR_PROCESS_START", "mean"),
        prev_rate_down_payment_mean=("RATE_DOWN_PAYMENT", "mean"),
        prev_days_decision_mean=("DAYS_DECISION", "mean")
    ).reset_index()

    agg["prev_approval_rate"] = np.where(agg["prev_app_count"] != 0, agg["prev_approved_count"] / agg["prev_app_count"], np.nan)
    return agg


def build_installments_agg(data_dir: str) -> pd.DataFrame | None:
    path = os.path.join(data_dir, "installments_payments.csv")
    if not os.path.exists(path):
        return None

    cols = [
        "SK_ID_CURR", "SK_ID_PREV", "NUM_INSTALMENT_VERSION", "NUM_INSTALMENT_NUMBER",
        "DAYS_INSTALMENT", "DAYS_ENTRY_PAYMENT", "AMT_INSTALMENT", "AMT_PAYMENT"
    ]
    inst = pd.read_csv(path, usecols=cols, low_memory=False)

    inst["days_payment_delay"] = inst["DAYS_ENTRY_PAYMENT"] - inst["DAYS_INSTALMENT"]
    inst["is_late_payment"] = (inst["days_payment_delay"] > 0).astype(int)
    inst["payment_gap"] = inst["AMT_PAYMENT"] - inst["AMT_INSTALMENT"]
    inst["underpayment_flag"] = (inst["payment_gap"] < 0).astype(int)

    agg = inst.groupby("SK_ID_CURR").agg(
        installments_rows_count=("SK_ID_PREV", "count"),
        installments_loan_count=("SK_ID_PREV", "nunique"),
        installments_late_payment_count=("is_late_payment", "sum"),
        installments_underpayment_count=("underpayment_flag", "sum"),
        installments_payment_delay_mean=("days_payment_delay", "mean"),
        installments_payment_delay_max=("days_payment_delay", "max"),
        installments_amt_payment_sum=("AMT_PAYMENT", "sum"),
        installments_amt_instalment_sum=("AMT_INSTALMENT", "sum")
    ).reset_index()

    agg["installments_late_payment_rate"] = np.where(
        agg["installments_rows_count"] != 0,
        agg["installments_late_payment_count"] / agg["installments_rows_count"],
        np.nan
    )
    return agg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--save-csv", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    app = load_application(args.data_dir)
    bureau_agg = build_bureau_agg(args.data_dir)
    result = app.merge(bureau_agg, on="SK_ID_CURR", how="left")

    prev_agg = build_previous_application_agg(args.data_dir)
    if prev_agg is not None:
        result = result.merge(prev_agg, on="SK_ID_CURR", how="left")

    inst_agg = build_installments_agg(args.data_dir)
    if inst_agg is not None:
        result = result.merge(inst_agg, on="SK_ID_CURR", how="left")

    parquet_path = os.path.join(args.output_dir, "credit_application_datamart.parquet")
    saved_path = parquet_path
    try:
        result.to_parquet(parquet_path, index=False)
    except Exception:
        saved_path = os.path.join(args.output_dir, "credit_application_datamart.csv")
        result.to_csv(saved_path, index=False)

    if args.save_csv and saved_path != os.path.join(args.output_dir, "credit_application_datamart.csv"):
        csv_path = os.path.join(args.output_dir, "credit_application_datamart.csv")
        result.to_csv(csv_path, index=False)

    print(f"Saved datamart: {saved_path}")
    print(f"Rows: {len(result)}, Columns: {len(result.columns)}")


if __name__ == "__main__":
    main()
