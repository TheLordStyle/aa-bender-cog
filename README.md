# aa-bender-cog

An [Alliance Auth](https://gitlab.com/allianceauth/allianceauth) Discord cog
that adds a `/bender` slash command. When invoked it pulls a random
Futurama *Bender* gif and posts it in the channel where the command was run.

> "Bite my shiny metal ass!" — Bender Bending Rodríguez

## Features

- Single slash command: `/bender`
- Works in any text channel the bot can see
- Uses the [Tenor v2 API](https://developers.google.com/tenor/guides/quickstart)
  for a fresh, randomised gif each time
- Falls back to a built-in curated list of Bender gifs if no Tenor key is
  configured or the Tenor request fails

## Requirements

- Alliance Auth `>= 4.0`
- [`aa-discordbot`](https://github.com/pvyParts/allianceauth-discordbot)
  installed and running (this is the AA bot that loads cogs)
- Python `>= 3.10`
- A working Discord bot already registered with Alliance Auth

## Installation

The cog is a standard Django app that ships as a pip-installable package.
Install it into the same virtualenv that Alliance Auth and `aa-discordbot`
run in.

### 1. Install the package

From PyPI once published, or directly from the git repository:

```bash
# from PyPI (when released)
pip install aa-bender-cog

# or from source
pip install git+https://github.com/TheLordStyle/aa-bender-cog.git
```

### 2. Add the app to `INSTALLED_APPS`

Edit your Alliance Auth `local.py` (usually
`myauth/myauth/settings/local.py`):

```python
INSTALLED_APPS += [
    "bender",
]
```

### 3. Register the cog with `aa-discordbot`

In the same `local.py`, add the cog's import path to
`DISCORD_BOT_COGS`. Create the list if it does not exist yet:

```python
DISCORD_BOT_COGS = globals().get("DISCORD_BOT_COGS", []) + [
    "bender.cogs.bender",
]
```

### 4. (Optional) Configure Tenor

Without a Tenor API key the cog will serve gifs from a small built-in list.
For a continuously varied pool, get a free key from the
[Google Cloud Console](https://console.cloud.google.com/) (enable the
*Tenor API*) and add to `local.py`:

```python
# Required for live Tenor lookups (free)
BENDER_TENOR_API_KEY = "your-tenor-api-key"

# Optional knobs — defaults shown
BENDER_TENOR_CLIENT_KEY = "aa-bender-cog"
BENDER_SEARCH_QUERY = "futurama bender"
BENDER_SEARCH_LIMIT = 50
BENDER_HTTP_TIMEOUT = 5.0
```

### 5. Migrate and restart

The cog has no models, but you should still run migrate so Alliance Auth
registers the app, then restart the AA stack and the Discord bot:

```bash
python manage.py migrate
python manage.py collectstatic --noinput

# Restart whichever supervisor manages your services:
supervisorctl restart myauth:
# or, on a systemd-managed install:
systemctl restart auth-discordbot.service
```

### 6. Sync slash commands in Discord

`aa-discordbot` syncs application (slash) commands on start-up. After the
bot restarts, the `/bender` command should appear in Discord within a
minute or two. If it does not show up, run the bot's command sync helper
(consult your `aa-discordbot` version's docs — usually a `!sync` text
command from an authorised user).

## Usage

In any channel where the bot is present, type:

```
/bender
```

Discord will autocomplete the command. Pressing enter posts a random
Bender gif as an embed. The command is available to everyone who can see
the channel — restrict access via channel permissions if you need to.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `/bender` does not show up in Discord | Slash commands not synced yet — restart the bot and wait a couple of minutes, or trigger a manual sync. |
| Bot replies with the same handful of gifs every time | No Tenor API key configured (see step 4). |
| Bot logs `Tenor returned HTTP 403` | API key is invalid or the Tenor API is not enabled for the project. |
| Bot logs `Tenor request failed` | Outbound network blocked or DNS unavailable from the bot host. |

Bot logs live wherever you configured `aa-discordbot` to log — by default
the `aadiscordbot` logger writes alongside the rest of Alliance Auth.

## Development

```bash
git clone https://github.com/TheLordStyle/aa-bender-cog.git
cd aa-bender-cog
pip install -e .
```

The cog is intentionally tiny: one slash command, no models, no
templates. Cog file lives at `bender/cogs/bender.py`.

## License

MIT — see [LICENSE](LICENSE).
