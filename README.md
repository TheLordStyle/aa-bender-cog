# aa-bender-cog

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Alliance Auth](https://img.shields.io/badge/Alliance%20Auth-5.x-green.svg)](https://gitlab.com/allianceauth/allianceauth)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An [Alliance Auth](https://gitlab.com/allianceauth/allianceauth) Discord cog
that adds a `/bender` command. When invoked it pulls a random Futurama
*Bender* gif from [KLIPY](https://klipy.com) and posts it in the channel
the command was run in.

Built on top of [aadiscordbot](https://github.com/pvyParts/allianceauth-discordbot).

> "Bite my shiny metal ass!" — Bender Bending Rodríguez

## What it does

Posts a random Bender gif as a Discord embed. That's it.

KLIPY was chosen over Tenor because Google deprecated the Tenor API on
2026-01-13 and shuts it down completely on 2026-06-30. KLIPY is built by
former Tenor engineers as a near-drop-in replacement, free for our usage
volume, and currently the easiest migration target.

### Example output

> **Bite my shiny metal ass!**
> *(random Bender gif embedded here)*
> Futurama / Bender

## Requirements

| Component | Version |
|---|---|
| Alliance Auth | ≥ 5.0 |
| [allianceauth-discordbot](https://github.com/pvyParts/allianceauth-discordbot) | recent |
| Python | ≥ 3.10 |
| KLIPY API key | free, from <https://klipy.com/developers> |

The cog does not touch the database, the EVE SDE, or corptools.

## Install

### Production (pinned)

Add to your AA `requirements.txt`:

```text
git+https://github.com/TheLordStyle/aa-bender-cog.git@v0.1.0
```

Then in `local.py`, add this as its own self-contained block (it does
not need to be merged with any other cog's settings — `DISCORD_BOT_COGS
+= [...]` can appear once per cog):

```python
# ============================================================
#  aa-bender-cog  -  random Bender gif on /bender
#  https://github.com/TheLordStyle/aa-bender-cog
# ============================================================
DISCORD_BOT_COGS += ["aa_bender.bender"]

BENDER_KLIPY_API_KEY = "your-klipy-api-key"

# Optional — defaults shown
# BENDER_SEARCH_QUERY = "futurama bender"
# BENDER_SEARCH_LIMIT = 50
# BENDER_HTTP_TIMEOUT = 5.0
```

Rebuild and restart auth.

### Development

For iteration without rebuilding the whole stack, bind-mount a checkout
into the discordbot container and install it editable:

```bash
docker compose exec allianceauth_discordbot \
    pip install -e /opt/cogs/aa-bender-cog

docker compose restart allianceauth_discordbot
```

Note that editable installs don't survive a `docker compose down` and
rebuild — production state always returns to whatever's pinned in
`requirements.txt`.

## Settings

| Setting | Default | Description |
|---|---|---|
| `BENDER_KLIPY_API_KEY` | `""` | KLIPY API key. Required — without it the command returns a friendly error. |
| `BENDER_SEARCH_QUERY` | `"futurama bender"` | Base search term sent to KLIPY. User-supplied keywords are appended to this. |
| `BENDER_SEARCH_LIMIT` | `50` | How many gifs to fetch per call before picking one at random (8–50). |
| `BENDER_HTTP_TIMEOUT` | `5.0` | HTTP timeout (seconds) when calling KLIPY. |

## Usage

```text
!bender
!bender dance
!bender angry walking

/bender
/bender keywords:dance
/bender keywords:angry walking
```

With no argument the search is just `futurama bender`. Supplying
keywords narrows it — they're **appended** to the base query, so
`/bender keywords:dance` searches `futurama bender dance` and the
result is still a Bender gif. If no gifs match your keywords KLIPY
returns an empty result and the command will tell you so.

Both forms work in any channel the bot can see. Restrict access via
Discord's channel permissions or *Server Settings → Integrations →
\[your bot\] → /bender* if you need to.

## How it works

The cog issues a single `GET` to KLIPY's search endpoint
(`api.klipy.com/api/v1/{KEY}/gifs/search`) with `q=futurama bender` and
`per_page=50`, then picks one result at random and embeds its `files.hd.gif.url`
(falling back to lower-resolution variants if `hd` is missing). No
caching, no background jobs — every `/bender` is one fresh request.

## Contributing

Bug reports and PRs welcome. Please open an issue first for anything beyond
trivial fixes so we can talk about it.

## License

MIT — see [LICENSE](LICENSE).
