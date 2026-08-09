# Revenue leakage detection

Revenue leakage is now calculated from delivered orders and successful payments.

For each DELIVERED order:

- `expected_revenue = order.total_amount`
- `collected_revenue = SUM(successful payment amounts)`
- `leakage_amount = max(expected_revenue - collected_revenue, 0)`

Only orders with a positive leakage amount are reported.

Therefore, an old delivered order with `total_amount = 0` is not treated as monetary leakage.

Example:

`total_amount = 408`, successful payments = `0` -> leakage = `408`.

`total_amount = 408`, successful payment = `408` -> leakage = `0`.

`total_amount = 408`, successful payment = `300` -> leakage = `108`.

Use `POST /payments/` as CUSTOMER to record a successful payment for an order, then `GET /orders/revenue/leakage` as ADMIN to verify the calculation.
