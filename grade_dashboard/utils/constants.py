from decimal import Context, ROUND_HALF_UP

DECIMAL_CONTEXT = Context(
    prec=100,
    rounding=ROUND_HALF_UP,
)
