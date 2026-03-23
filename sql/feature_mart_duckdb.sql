-- Эскиз SQL-витрины для DuckDB / PostgreSQL
-- База: 1 строка = 1 текущая заявка из application_train.csv

WITH application_base AS (
    SELECT
        SK_ID_CURR,
        TARGET,
        NAME_CONTRACT_TYPE,
        CODE_GENDER,
        FLAG_OWN_CAR,
        FLAG_OWN_REALTY,
        CNT_CHILDREN,
        AMT_INCOME_TOTAL,
        AMT_CREDIT,
        AMT_ANNUITY,
        AMT_GOODS_PRICE,
        NAME_INCOME_TYPE,
        NAME_EDUCATION_TYPE,
        NAME_FAMILY_STATUS,
        NAME_HOUSING_TYPE,
        REGION_POPULATION_RELATIVE,
        ABS(DAYS_BIRTH) / 365.25 AS age_years,
        CASE WHEN DAYS_EMPLOYED = 365243 THEN NULL ELSE ABS(DAYS_EMPLOYED) / 365.25 END AS employment_years,
        CASE WHEN DAYS_EMPLOYED = 365243 THEN 1 ELSE 0 END AS days_employed_anom_flag,
        AMT_CREDIT / NULLIF(AMT_INCOME_TOTAL, 0) AS credit_income_ratio,
        AMT_ANNUITY / NULLIF(AMT_INCOME_TOTAL, 0) AS annuity_income_ratio,
        AMT_CREDIT / NULLIF(AMT_GOODS_PRICE, 0) AS credit_goods_ratio,
        EXT_SOURCE_1,
        EXT_SOURCE_2,
        EXT_SOURCE_3
    FROM application_train
),
bureau_agg AS (
    SELECT
        SK_ID_CURR,
        COUNT(*) AS bureau_records_count,
        SUM(CASE WHEN CREDIT_ACTIVE = 'Active' THEN 1 ELSE 0 END) AS bureau_active_credit_count,
        SUM(CASE WHEN CREDIT_ACTIVE = 'Closed' THEN 1 ELSE 0 END) AS bureau_closed_credit_count,
        SUM(CASE WHEN CREDIT_ACTIVE = 'Bad debt' THEN 1 ELSE 0 END) AS bureau_bad_debt_credit_count,
        SUM(CASE WHEN CREDIT_ACTIVE = 'Sold' THEN 1 ELSE 0 END) AS bureau_sold_credit_count,
        SUM(CASE WHEN CREDIT_DAY_OVERDUE > 0 THEN 1 ELSE 0 END) AS bureau_overdue_credit_count,
        MAX(CREDIT_DAY_OVERDUE) AS bureau_credit_day_overdue_max,
        AVG(CREDIT_DAY_OVERDUE) AS bureau_credit_day_overdue_mean,
        SUM(COALESCE(AMT_CREDIT_SUM, 0)) AS bureau_total_credit_sum,
        SUM(COALESCE(AMT_CREDIT_SUM_DEBT, 0)) AS bureau_total_credit_debt_sum,
        SUM(COALESCE(AMT_CREDIT_SUM_OVERDUE, 0)) AS bureau_total_credit_overdue_sum,
        SUM(COALESCE(AMT_CREDIT_SUM_LIMIT, 0)) AS bureau_total_credit_limit_sum,
        SUM(COALESCE(AMT_ANNUITY, 0)) AS bureau_total_annuity_sum,
        SUM(COALESCE(CNT_CREDIT_PROLONG, 0)) AS bureau_total_prolong_sum,
        AVG(DAYS_CREDIT) AS bureau_days_credit_mean,
        COUNT(DISTINCT CREDIT_TYPE) AS bureau_unique_credit_types,
        COUNT(DISTINCT CREDIT_CURRENCY) AS bureau_unique_currencies
    FROM bureau
    GROUP BY SK_ID_CURR
)
SELECT
    a.*,
    b.* EXCLUDE (SK_ID_CURR),
    b.bureau_total_credit_debt_sum / NULLIF(b.bureau_total_credit_sum, 0) AS bureau_debt_to_credit_ratio
FROM application_base a
LEFT JOIN bureau_agg b USING (SK_ID_CURR);
