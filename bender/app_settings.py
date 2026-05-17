"""Settings for the bender cog.

Values are read from Django settings (``local.py``) with sensible defaults.
Override any of them by adding the matching ``BENDER_*`` setting to your
Alliance Auth ``local.py``.
"""

from django.conf import settings


BENDER_KLIPY_API_KEY: str = getattr(settings, "BENDER_KLIPY_API_KEY", "")
"""KLIPY API key. Required — without it /bender will return an error.

KLIPY (https://klipy.com) is the Tenor-compatible replacement we use after
Google deprecated the Tenor API on 2026-01-13 (full shutdown 2026-06-30).
Request a key at https://klipy.com/developers.
"""

BENDER_SEARCH_QUERY: str = getattr(
    settings, "BENDER_SEARCH_QUERY", "futurama bender"
)
"""Search term sent to KLIPY."""

BENDER_SEARCH_LIMIT: int = getattr(settings, "BENDER_SEARCH_LIMIT", 50)
"""How many gifs to ask KLIPY for before picking one at random (max 50)."""

BENDER_HTTP_TIMEOUT: float = getattr(settings, "BENDER_HTTP_TIMEOUT", 5.0)
"""HTTP timeout (seconds) when calling KLIPY."""
