"""Settings for the bender cog.

These values are read from Django settings (``local.py``) with sensible
defaults. Override any of them by adding the matching ``BENDER_*`` setting
to your Alliance Auth ``local.py``.
"""

from django.conf import settings


BENDER_TENOR_API_KEY: str = getattr(settings, "BENDER_TENOR_API_KEY", "")
"""Tenor v2 API key. If empty the cog falls back to a built-in gif list."""

BENDER_TENOR_CLIENT_KEY: str = getattr(
    settings, "BENDER_TENOR_CLIENT_KEY", "aa-bender-cog"
)
"""Client key passed to Tenor (any non-empty string is fine)."""

BENDER_SEARCH_QUERY: str = getattr(
    settings, "BENDER_SEARCH_QUERY", "futurama bender"
)
"""Search term used when querying Tenor."""

BENDER_SEARCH_LIMIT: int = getattr(settings, "BENDER_SEARCH_LIMIT", 50)
"""How many gifs to ask Tenor for before picking one at random."""

BENDER_HTTP_TIMEOUT: float = getattr(settings, "BENDER_HTTP_TIMEOUT", 5.0)
"""HTTP timeout (seconds) when calling Tenor."""
