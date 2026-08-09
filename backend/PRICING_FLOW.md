# Order pricing flow

Order creation now requires at least one menu item.

Example POST `/orders/`:

```json
{
  "restaurant_id": 1,
  "items": [
    {
      "menu_id": 1,
      "quantity": 2
    }
  ]
}
```

The API:
- verifies the menu item belongs to the selected restaurant;
- verifies the menu item is available;
- snapshots the current menu price into `OrderItem.unit_price`;
- calculates `subtotal`;
- calculates 5% tax;
- adds a 30 delivery charge;
- calculates `total_amount`.

Order-item updates use the same 5% tax rate.

Existing zero-value orders are not automatically changed; add valid order items to an existing order using `POST /order-items/` if you want to recalculate that order.
