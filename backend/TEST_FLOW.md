# RevenueShield AI - Current Test Flow

## Reviews

1. CUSTOMER creates a review only for their own DELIVERED order.
2. ADMIN uses `GET /reviews` to view all reviews.
3. CUSTOMER can update their own review.
4. ADMIN can delete a review.
5. One review per order is enforced.

## Order status flow

`PLACED -> ACCEPTED -> PREPARING -> READY -> PICKED_UP -> ON_THE_WAY -> DELIVERED`

- Restaurant assignment endpoint changes `PLACED -> ACCEPTED`.
- Restaurant can then change `ACCEPTED -> PREPARING -> READY`.
- The assigned delivery partner can change `READY -> PICKED_UP -> ON_THE_WAY -> DELIVERED`.
- A CUSTOMER cannot change order status.
- A restaurant cannot update another restaurant's order.
- A delivery partner cannot update another partner's order.

## Important

Do not try `PLACED -> DELIVERED` directly. The transition validation is intentional.
Do not allow ADMIN to create customer reviews; ADMIN is a reviewer/management role, not the customer who placed the order.
