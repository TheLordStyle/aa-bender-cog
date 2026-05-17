# aa-bender-cog

An [Alliance Auth](https://gitlab.com/allianceauth/allianceauth) Discord cog
that adds a `/bender` slash command. When invoked it pulls a random
Futurama *Bender* gif and posts it in the channel where the command was run.

> "Bite my shiny metal ass!" — Bender Bending Rodríguez

## Features

- Single slash command: `/bender`
- Works in any text channel the bot can see
- Uses the [KLIPY API](https://klipy.com/developers) for a fresh,
  randomised gif each time

> **Why KLIPY and not Tenor?** Google deprecated the Tenor API on
> 2026-01-13 and shuts it down completely on 2026-06-30. KLIPY is built by
> former Tenor engineers as a near-drop-in replacement and is free for
> our use case.

## Requirements

- Alliance Auth `>= 4.0`
- [`aa-discordbot`](https://github.com/pvyParts/allianceauth-discordbot)
  installed and running (this is the AA bot that loads cogs)
- Python `>= 3.10`
- A working Discord bot already registered with Alliance Auth
- A free KLIPY API key

## Installation

The cog is a standard Django app that ships as a pip-installable package.
Install it into the same virtualenv that Alliance Auth and `aa-discordbot`
run in.

### 1. Get a KLIPY API key

1. Go to <https://klipy.com/developers> and sign up.
2. Create an app from the Partner Panel — the test key works fine and
   gives 100 requests/minute, which is plenty for any alliance Discord.
3. Copy the API key — you'll paste it into `local.py` in step 4.

### 2. Install the package

From PyPI once published, or directly from the git repository:

```bash
# from PyPI (when released)
pip install aa-bender-cog

# or from source
pip install git+https://github.com/TheLordStyle/aa-bender-cog.git
```

### 3. Add the app to `INSTALLED_APPS`

Edit your Alliance Auth `local.py` (usually
`myauth/myauth/settings/local.py`):

```python
INSTALLED_APPS += [
    "bender",
]
```

### 4. Register the cog and configure KLIPY

In the same `local.py`:

```python
DISCORD_BOT_COGS = globals().get("DISCORD_BOT_COGS", []) + [
    "bender.cogs.bender",
]

# Required
BENDER_KLIPY_API_KEY = "your-klipy-api-key"

# Optional — defaults shown
BENDER_SEARCH_QUERY = "futurama bender"
BENDER_SEARCH_LIMIT = 50    # how many results to ask for (8-50)
BENDER_HTTP_TIMEOUT = 5.0   # seconds
```

### 5. Migrate and restart

The cog has no models, but you should still run `migrate` so Alliance
Auth registers the app, then restart the AA stack and the Discord bot:

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
the channel — restrict access via channel permissions or via Discord's
Application Command Permissions if you need to.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `/bender` does not show up in Discord | Slash commands not synced yet — restart the bot and wait a couple of minutes, or trigger a manual sync. |
| Bot says "Bender is misconfigured — no KLIPY API key set" | `BENDER_KLIPY_API_KEY` is missing from `local.py`, or the bot wasn't restarted after adding it. |
| Bot says "Bender is taking a smoke break" | KLIPY request failed — check `aadiscordbot` logs for an HTTP status or network error. Common causes: bad API key, outbound network blocked, KLIPY temporarily down. |
| Bot logs `KLIPY returned HTTP 401` or `403` | API key is invalid or revoked. Re-issue from the KLIPY Partner Panel. |

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
