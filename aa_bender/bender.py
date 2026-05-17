"""Bender: post a random Futurama Bender gif via !bender / /bender."""
import json
import logging
import random
from dataclasses import dataclass

import aiohttp
from aadiscordbot.app_settings import get_all_servers
from discord.embeds import Embed
from discord.ext import commands

from django.conf import settings

logger = logging.getLogger(__name__)

# KLIPY is the Tenor-compatible replacement after Google deprecated the Tenor
# API on 2026-01-13 (full shutdown 2026-06-30). Request a key at
# https://klipy.com/developers. The key goes in the URL path, not a header.
KLIPY_SEARCH_URL = "https://api.klipy.com/api/v1/{api_key}/gifs/search"


@dataclass
class FetchResult:
    """Outcome of a KLIPY fetch attempt — either a usable gif URL or a
    human-readable reason it failed. The reason is surfaced both to the
    Discord invoker and to the bot log."""
    gif_url: str | None = None
    reason: str | None = None


def _build_embed(gif_url: str) -> Embed:
    embed = Embed(
        title="Bite my shiny metal ass!",
        colour=0x9696AA,
    )
    embed.set_image(url=gif_url)
    embed.set_footer(text="Futurama / Bender")
    return embed


def _extract_items(payload: dict) -> list[dict]:
    """Pull the result list out of KLIPY's paginated envelope.

    KLIPY wraps results as ``{"data": {"data": [...]}}``; older / alternate
    shapes flatten to ``{"data": [...]}``. Handle both.
    """
    data = payload.get("data")
    if isinstance(data, dict):
        inner = data.get("data")
        if isinstance(inner, list):
            return inner
    if isinstance(data, list):
        return data
    return []


def _extract_gif_url(item: dict) -> str | None:
    files = item.get("files") or {}
    for size in ("hd", "lg", "md", "sm"):
        url = (files.get(size) or {}).get("gif", {}).get("url")
        if url:
            return url
    return (files.get("gif") or {}).get("url")


def _summarise_payload(payload) -> str:
    """A short, single-line summary of the payload for an error message."""
    try:
        s = json.dumps(payload, separators=(",", ":"))
    except (TypeError, ValueError):
        s = repr(payload)
    return s[:300] + ("…" if len(s) > 300 else "")


async def _fetch_klipy_gif() -> FetchResult:
    api_key = getattr(settings, "BENDER_KLIPY_API_KEY", "")
    if not api_key:
        return FetchResult(reason="no API key configured")

    url = KLIPY_SEARCH_URL.format(api_key=api_key)
    per_page = max(8, min(50, getattr(settings, "BENDER_SEARCH_LIMIT", 50)))
    params = {
        "q": getattr(settings, "BENDER_SEARCH_QUERY", "futurama bender"),
        "per_page": per_page,
    }
    timeout = aiohttp.ClientTimeout(
        total=getattr(settings, "BENDER_HTTP_TIMEOUT", 5.0)
    )

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as resp:
                body_text = await resp.text()
                if resp.status != 200:
                    snippet = body_text[:200].replace("\n", " ")
                    reason = f"HTTP {resp.status} — {snippet}"
                    logger.error("KLIPY request: %s", reason)
                    return FetchResult(reason=reason)
                try:
                    payload = json.loads(body_text)
                except json.JSONDecodeError as exc:
                    reason = (
                        f"non-JSON response ({exc}): "
                        f"{body_text[:200].replace(chr(10), ' ')}"
                    )
                    logger.error("KLIPY request: %s", reason)
                    return FetchResult(reason=reason)
    except (aiohttp.ClientError, TimeoutError) as exc:
        reason = f"network error: {type(exc).__name__}: {exc}"
        logger.error("KLIPY request: %s", reason)
        return FetchResult(reason=reason)

    items = _extract_items(payload)
    if not items:
        reason = (
            "HTTP 200 but no items in response — payload was "
            f"{_summarise_payload(payload)}"
        )
        logger.error("KLIPY request: %s", reason)
        return FetchResult(reason=reason)

    random.shuffle(items)
    for item in items:
        gif_url = _extract_gif_url(item)
        if gif_url:
            return FetchResult(gif_url=gif_url)

    reason = (
        "HTTP 200, got items, but none had a files.{hd,lg,md,sm}.gif.url "
        f"field — first item was {_summarise_payload(items[0])}"
    )
    logger.error("KLIPY request: %s", reason)
    return FetchResult(reason=reason)


class Bender(commands.Cog):
    """A random Futurama Bender gif on demand."""

    def __init__(self, bot):
        self.bot = bot

    # ---- prefix --------------------------------------------------------

    @commands.command(pass_context=True)
    async def bender(self, ctx):
        result = await _fetch_klipy_gif()
        if result.gif_url:
            return await ctx.message.reply(embed=_build_embed(result.gif_url))
        await ctx.message.reply(
            f"Bender is taking a smoke break — {result.reason}"
        )

    # ---- slash ---------------------------------------------------------

    @commands.slash_command(name="bender", guild_ids=get_all_servers())
    async def slash_bender(self, ctx):
        await ctx.defer()
        result = await _fetch_klipy_gif()
        if result.gif_url:
            return await ctx.respond(embed=_build_embed(result.gif_url))
        await ctx.respond(
            f"Bender is taking a smoke break — {result.reason}"
        )


def setup(bot):
    bot.add_cog(Bender(bot))
