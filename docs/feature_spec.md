# Спецификация витрины

## Ключ
- `SK_ID_CURR` — идентификатор текущей заявки / клиента в выборке.

## Базовые признаки из application_train
- `TARGET` — целевая метка: были ли у клиента трудности с выплатой.
- `NAME_CONTRACT_TYPE` — тип продукта.
- `CODE_GENDER` — пол клиента.
- `FLAG_OWN_CAR`, `FLAG_OWN_REALTY` — владение автомобилем / жильём.
- `CNT_CHILDREN`, `CNT_FAM_MEMBERS` — состав домохозяйства.
- `AMT_INCOME_TOTAL`, `AMT_CREDIT`, `AMT_ANNUITY`, `AMT_GOODS_PRICE` — финансовые показатели текущей заявки.
- `NAME_INCOME_TYPE`, `NAME_EDUCATION_TYPE`, `NAME_FAMILY_STATUS`, `NAME_HOUSING_TYPE` — социально-демографический профиль.
- `REGION_POPULATION_RELATIVE`, `REGION_RATING_CLIENT`, `REGION_RATING_CLIENT_W_CITY` — региональные признаки.
- `EXT_SOURCE_1`, `EXT_SOURCE_2`, `EXT_SOURCE_3` — внешние скоринговые признаки.
- `DAYS_LAST_PHONE_CHANGE`, `AMT_REQ_CREDIT_BUREAU_YEAR` — поведенческие и кредитные признаки.

## Производные признаки из application_train
- `age_years` — возраст клиента в годах.
- `employment_years` — стаж клиента в годах без технической аномалии `365243`.
- `days_employed_anom_flag` — флаг технической аномалии стажа.
- `credit_income_ratio` — отношение суммы кредита к доходу.
- `annuity_income_ratio` — отношение аннуитета к доходу.
- `credit_goods_ratio` — отношение кредита к стоимости товара.
- `employment_age_ratio` — отношение стажа к возрасту.

## Агрегаты из bureau
- `bureau_records_count` — число внешних кредитов.
- `bureau_active_credit_count` — число активных внешних кредитов.
- `bureau_closed_credit_count` — число закрытых внешних кредитов.
- `bureau_bad_debt_credit_count` — число кредитов со статусом bad debt.
- `bureau_sold_credit_count` — число проданных долгов.
- `bureau_overdue_credit_count` — число кредитов с просрочкой.
- `bureau_credit_day_overdue_max`, `bureau_credit_day_overdue_mean` — просрочка в днях.
- `bureau_total_credit_sum` — суммарный объём внешних кредитов.
- `bureau_total_credit_debt_sum` — суммарный внешний долг.
- `bureau_total_credit_overdue_sum` — суммарная просроченная сумма.
- `bureau_total_credit_limit_sum` — суммарный доступный лимит.
- `bureau_total_annuity_sum` — суммарный аннуитет.
- `bureau_total_prolong_sum` — число пролонгаций.
- `bureau_days_credit_mean/min/max` — признаки давности внешних кредитов.
- `bureau_unique_credit_types` — число типов кредитов.
- `bureau_unique_currencies` — число валют.
- `bureau_debt_to_credit_ratio` — отношение долга к объёму кредитов.

## Дополнительные расширения
Если в проект добавить `previous_application.csv` и `installments_payments.csv`, можно достроить:
- историю предыдущих заявок;
- долю прошлых отказов / одобрений;
- признаки платёжной дисциплины и задержек.


## Агрегаты из previous_application
- `prev_app_count` — число прошлых заявок клиента.
- `prev_approved_count` — число прошлых одобренных заявок.
- `prev_refused_count` — число прошлых отказов.
- `prev_amt_application_sum` — суммарный объём прошлых заявок.
- `prev_amt_credit_sum` — суммарный объём прошлых одобренных/запрошенных кредитов.
- `prev_amt_annuity_sum` — суммарный аннуитет по прошлым заявкам.
- `prev_hour_appr_mean` — средний час оформления прошлых заявок.
- `prev_rate_down_payment_mean` — средняя ставка первоначального взноса.
- `prev_days_decision_mean` — средняя глубина истории прошлых решений.
- `prev_approval_rate` — доля прошлых заявок со статусом `Approved`.
