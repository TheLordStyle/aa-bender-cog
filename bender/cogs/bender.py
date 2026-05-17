"""Discord cog providing the ``/bender`` slash command.

The cog is auto-discovered by ``aadiscordbot`` because the package is listed
in ``INSTALLED_APPS`` and exposes a top-level ``setup`` coroutine.
"""

import logging
import random

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from bender import app_settings

logger = logging.getLogger(__name__)


FALLBACK_GIFS = [
    "https://media.tenor.com/jJalKqB6oOoAAAAC/bender-futurama.gif",
    "https://media.tenor.com/uMnK6JTAGicAAAAC/bender-futurama.gif",
    "https://media.tenor.com/lzZ5R5G2RNkAAAAC/bender-bender-futurama.gif",
    "https://media.tenor.com/3oqfHQ3oCk0AAAAC/bender-futurama.gif",
    "https://media.tenor.com/Q2ETeaUI4soAAAAC/bender-rodriguez-futurama.gif",
    "https://media.tenor.com/4nGz1xX9yLEAAAAC/bender-futurama.gif",
    "https://media.tenor.com/zFqVjLp8aGwAAAAC/bender-bite-my-shiny-metal.gif",
    "https://media.tenor.com/H8Z2VV0c7iIAAAAC/bender-futurama.gif",
    "https://media.tenor.com/H6E3uM7t3HQAAAAC/futurama-bender.gif",
    "https://media.tenor.com/g2YfPnpsmXMAAAAC/bender-futurama.gif",
]

TENOR_ENDPOINT = "https://tenor.googleapis.com/v2/search"


class Bender(commands.Cog):
    """A cog with a single ``/bender`` slash command."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _fetch_tenor_gif(self) -> str | None:
        """Query Tenor for a random Bender gif. Returns ``None`` on failure."""
        if not app_settings.BENDER_TENOR_API_KEY:
            return None

        params = {
            "q": app_settings.BENDER_SEARCH_QUERY,
            "key": app_settings.BENDER_TENOR_API_KEY,
            "client_key": app_settings.BENDER_TENOR_CLIENT_KEY,
            "limit": app_settings.BENDER_SEARCH_LIMIT,
            "media_filter": "gif",
            "random": "true",
        }

        timeout = aiohttp.ClientTimeout(total=app_settings.BENDER_HTTP_TIMEOUT)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(TENOR_ENDPOINT, params=params) as resp:
                    if resp.status != 200:
                        logger.warning(
                            "Tenor returned HTTP %s for /bender", resp.status
                        )
                        return None
                    payload = await resp.json()
        except (aiohttp.ClientError, TimeoutError) as exc:
            logger.warning("Tenor request failed: %s", exc)
            return None

        results = payload.get("results") or []
        if not results:
            return None

        chosen = random.choice(results)
        for fmt in ("gif", "mediumgif", "tinygif"):
            media = chosen.get("media_formats", {}).get(fmt)
            if media and media.get("url"):
                return media["url"]
        return None

    @app_commands.command(
        name="bender",
        description="Display a random Futurama Bender gif.",
    )
    async def bender(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)

        gif_url = await self._fetch_tenor_gif()
        if gif_url is None:
            gif_url = random.choice(FALLBACK_GIFS)

        embed = discord.Embed(
            title="Bite my shiny metal ass!",
            color=discord.Color.from_rgb(150, 150, 170),
        )
        embed.set_image(url=gif_url)
        embed.set_footer(text="Futurama / Bender")

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Bender(bot))
