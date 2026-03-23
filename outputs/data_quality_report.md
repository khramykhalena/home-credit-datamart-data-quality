# Отчёт по качеству данных

## Общая сводка

### application_train
- строк: 307511
- колонок: 122
- SK_ID_CURR_duplicate_rows: 0
- топ колонок по доле пропусков:
  - COMMONAREA_AVG: 69.87%
  - COMMONAREA_MODE: 69.87%
  - COMMONAREA_MEDI: 69.87%
  - NONLIVINGAPARTMENTS_MEDI: 69.43%
  - NONLIVINGAPARTMENTS_MODE: 69.43%
  - NONLIVINGAPARTMENTS_AVG: 69.43%
  - FONDKAPREMONT_MODE: 68.39%
  - LIVINGAPARTMENTS_AVG: 68.35%
  - LIVINGAPARTMENTS_MEDI: 68.35%
  - LIVINGAPARTMENTS_MODE: 68.35%
  - FLOORSMIN_MODE: 67.85%
  - FLOORSMIN_AVG: 67.85%
  - FLOORSMIN_MEDI: 67.85%
  - YEARS_BUILD_AVG: 66.5%
  - YEARS_BUILD_MODE: 66.5%

### bureau
- строк: 1716428
- колонок: 17
- SK_ID_BUREAU_duplicate_rows: 0
- SK_ID_CURR_duplicate_rows: 1410617
- топ колонок по доле пропусков:
  - AMT_ANNUITY: 71.47%
  - AMT_CREDIT_MAX_OVERDUE: 65.51%
  - DAYS_ENDDATE_FACT: 36.92%
  - AMT_CREDIT_SUM_LIMIT: 34.48%
  - AMT_CREDIT_SUM_DEBT: 15.01%
  - DAYS_CREDIT_ENDDATE: 6.15%
  - AMT_CREDIT_SUM: 0.0%
  - SK_ID_CURR: 0.0%
  - SK_ID_BUREAU: 0.0%
  - CREDIT_DAY_OVERDUE: 0.0%
  - CREDIT_ACTIVE: 0.0%
  - CREDIT_CURRENCY: 0.0%
  - DAYS_CREDIT: 0.0%
  - CNT_CREDIT_PROLONG: 0.0%
  - AMT_CREDIT_SUM_OVERDUE: 0.0%

### previous_application
- строк: 1670214
- колонок: 37
- SK_ID_PREV_duplicate_rows: 0
- SK_ID_CURR_duplicate_rows: 1331357
- топ колонок по доле пропусков:
  - RATE_INTEREST_PRIVILEGED: 99.64%
  - RATE_INTEREST_PRIMARY: 99.64%
  - AMT_DOWN_PAYMENT: 53.64%
  - RATE_DOWN_PAYMENT: 53.64%
  - NAME_TYPE_SUITE: 49.12%
  - DAYS_TERMINATION: 40.3%
  - DAYS_FIRST_DRAWING: 40.3%
  - DAYS_FIRST_DUE: 40.3%
  - DAYS_LAST_DUE_1ST_VERSION: 40.3%
  - DAYS_LAST_DUE: 40.3%
  - NFLAG_INSURED_ON_APPROVAL: 40.3%
  - AMT_GOODS_PRICE: 23.08%
  - AMT_ANNUITY: 22.29%
  - CNT_PAYMENT: 22.29%
  - PRODUCT_COMBINATION: 0.02%

## Проверки и наблюдения

### application_train.csv
- target_default_rate_pct: 8.07
- days_employed_365243_count: 55374
- days_birth_positive_count: 0
- negative_income_count: 0
- credit_less_than_annuity_count: 0

### bureau.csv
- rows_with_credit_day_overdue_gt_0: 4217
- rows_with_debt_gt_credit_sum: 29642
- active_credit_share_pct: 36.74
- closed_credit_share_pct: 62.88
- avg_bureau_records_per_client: 5.61

### previous_application.csv
- approved_share_pct: 62.07
- refused_share_pct: 17.4
- canceled_share_pct: 18.94
- unused_offer_share_pct: 1.58
- avg_previous_applications_per_client: 4.93
- rows_with_application_gt_credit: 357691
- rows_not_last_application_in_day: 5900

## Интерпретация

- `application_train.csv` является главной таблицей витрины: `1 строка = 1 заявка`, ключ — `SK_ID_CURR`.
- В `application_train.csv` нет дублей по `SK_ID_CURR`.
- Значение `DAYS_EMPLOYED = 365243` выглядит как технический код аномалии, а не реальный стаж; его стоит выносить в отдельный флаг и заменять на `NaN` для расчётов.
- В `bureau.csv` одна заявка / клиент может иметь несколько записей по внешним кредитам; это слой `1:N`, который нужно агрегировать перед объединением с базовой заявкой.
- В `previous_application.csv` один клиент может иметь несколько прошлых заявок; это второй важный слой `1:N`, который нужно агрегировать до уровня клиента/текущей заявки.
- Существенные пропуски наблюдаются в жилищных признаках `application_train.csv`, в финансовых колонках `bureau.csv` и части стоимостных полей `previous_application.csv`, поэтому витрина должна явно фиксировать стратегию обработки пропусков.