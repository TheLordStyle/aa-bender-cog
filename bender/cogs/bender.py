"""Discord cog providing the ``/bender`` slash command.

The cog is auto-discovered by ``aadiscordbot`` because the package is listed
in ``INSTALLED_APPS`` and its dotted path is added to ``DISCORD_BOT_COGS``.
"""

import logging
import random
from typing import Any

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from bender import app_settings

logger = logging.getLogger(__name__)

KLIPY_SEARCH_URL = (
    "https://api.klipy.com/api/v1/{api_key}/gifs/search"
)


class Bender(commands.Cog):
    """A cog with a single ``/bender`` slash command."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _fetch_klipy_gif(self) -> str | None:
        """Query KLIPY for a random Bender gif. Returns ``None`` on failure."""
        api_key = app_settings.BENDER_KLIPY_API_KEY
        if not api_key:
            return None

        url = KLIPY_SEARCH_URL.format(api_key=api_key)
        params = {
            "q": app_settings.BENDER_SEARCH_QUERY,
            "per_page": max(8, min(50, app_settings.BENDER_SEARCH_LIMIT)),
        }

        timeout = aiohttp.ClientTimeout(total=app_settings.BENDER_HTTP_TIMEOUT)
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

        items = self._extract_items(payload)
        if not items:
            return None

        random.shuffle(items)
        for item in items:
            gif_url = self._extract_gif_url(item)
            if gif_url:
                return gif_url
        return None

    @staticmethod
    def _extract_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Pull the result list out of KLIPY's paginated envelope.

        KLIPY wraps results as ``{"data": {"data": [...]}}``; older or
        alternate shapes flatten to ``{"data": [...]}``. Handle both.
        """
        data = payload.get("data")
        if isinstance(data, dict):
            inner = data.get("data")
            if isinstance(inner, list):
                return inner
        if isinstance(data, list):
            return data
        return []

    @staticmethod
    def _extract_gif_url(item: dict[str, Any]) -> str | None:
        files = item.get("files") or {}
        for size in ("hd", "lg", "md", "sm"):
            url = files.get(size, {}).get("gif", {}).get("url")
            if url:
                return url
        url = files.get("gif", {}).get("url")
        if url:
            return url
        return None

    @app_commands.command(
        name="bender",
        description="Display a random Futurama Bender gif.",
    )
    async def bender(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        if not app_settings.BENDER_KLIPY_API_KEY:
            await interaction.followup.send(
                "Bender is misconfigured — no KLIPY API key set. "
                "Ask your Alliance Auth admin to set `BENDER_KLIPY_API_KEY` "
                "in `local.py`.",
                ephemeral=True,
            )
            return

        gif_url = await self._fetch_klipy_gif()
        if gif_url is None:
            await interaction.followup.send(
                "Bender is taking a smoke break — couldn't reach KLIPY. "
                "Try again in a minute.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="Bite my shiny metal ass!",
            color=discord.Color.from_rgb(150, 150, 170),
        )
        embed.set_image(url=gif_url)
        embed.set_footer(text="Futurama / Bender")

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Bender(bot))
