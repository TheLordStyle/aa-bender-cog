"""Bender: post a random Futurama Bender gif via !bender / /bender."""
import logging
import random

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


async def _fetch_klipy_gif() -> str | None:
    api_key = getattr(settings, "BENDER_KLIPY_API_KEY", "")
    if not api_key:
        return None

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
                if resp.status != 200:
                    logger.warning(
                        "KLIPY returned HTTP %s for /bender", resp.status
                    )
                    return None
                payload = await resp.json()
    except (aiohttp.ClientError, TimeoutError) as exc:
        logger.warning("KLIPY request failed: %s", exc)
        return None

    items = _extract_items(payload)
    if not items:
        return None
    random.shuffle(items)
    for item in items:
        gif_url = _extract_gif_url(item)
        if gif_url:
            return gif_url
    return None


class Bender(commands.Cog):
    """A random Futurama Bender gif on demand."""

    def __init__(self, bot):
        self.bot = bot

    # ---- prefix --------------------------------------------------------

    @commands.command(pass_context=True)
    async def bender(self, ctx):
        if not getattr(settings, "BENDER_KLIPY_API_KEY", ""):
            return await ctx.message.reply(
                "Bender is misconfigured — no KLIPY API key set. "
                "Ask your AA admin to set `BENDER_KLIPY_API_KEY` in `local.py`."
            )

        gif_url = await _fetch_klipy_gif()
        if not gif_url:
            return await ctx.message.reply(
                "Bender is taking a smoke break — couldn't reach KLIPY. "
                "Try again in a minute."
            )
        await ctx.message.reply(embed=_build_embed(gif_url))

    # ---- slash ---------------------------------------------------------

    @commands.slash_command(name="bender", guild_ids=get_all_servers())
    async def slash_bender(self, ctx):
        if not getattr(settings, "BENDER_KLIPY_API_KEY", ""):
            return await ctx.respond(
                "Bender is misconfigured — no KLIPY API key set. "
                "Ask your AA admin to set `BENDER_KLIPY_API_KEY` in `local.py`.",
                ephemeral=True,
            )

        await ctx.defer()
        gif_url = await _fetch_klipy_gif()
        if not gif_url:
            return await ctx.respond(
                "Bender is taking a smoke break — couldn't reach KLIPY. "
                "Try again in a minute."
            )
        await ctx.respond(embed=_build_embed(gif_url))


def setup(bot):
    bot.add_cog(Bender(bot))
