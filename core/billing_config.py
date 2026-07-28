from __future__ import annotations

import os
from typing import Optional


PAYMENT_DESTINATION_ENV = "NOVA_PAYMENT_DESTINATION"

FREE_CONTEXT_CALL_LIMIT = 50
DEFAULT_PRICE_PER_DECISION_USD = 0.02


def load_payment_destination_from_env() -> Optional[str]:
    """Return the explicitly configured business payment destination.

    Payment collection is inactive when the variable is absent or blank.
    No wallet address is embedded in source code.
    """

    value = os.getenv(PAYMENT_DESTINATION_ENV, "").strip()
    return value or None


# Retain the existing public symbol temporarily to minimize unrelated change.
# Its value is now optional and never falls back to a repository address.
USDC_PAYMENT_WALLET = load_payment_destination_from_env()
