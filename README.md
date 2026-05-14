# ytd skill

A skill for downloading YouTube videos, audio, or transcripts from the command line.

## Usage

```
ytd <url>                    # best quality video (default)
ytd <url> --audio            # audio only, saved as mp3
ytd <url> --transcript       # transcript to stdout
ytd <url> --formats          # list available formats
ytd <url> --quality 1080     # cap video height to 1080p
ytd <url> --lang es          # Spanish subtitles or transcript
ytd <url> --output ./dir     # save to a specific directory
ytd <url> --timestamps       # prefix transcript with [HH:MM:SS]
ytd <url> --keep-brackets    # keep [Music] [Applause] in output
ytd <url> --subs             # save subtitle files with video
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--audio` | off | Extract audio only and convert to mp3 |
| `--transcript` | off | Print clean transcript to stdout |
| `--formats` | off | List all available formats and exit |
| `--quality HEIGHT` | best | Max video height in pixels (`1080`, `720`, `480`) |
| `--lang CODE` | `en` | Language code for transcript or subtitles |
| `--output DIR` | `.` | Directory to save downloaded files |
| `--timestamps` | off | Prefix each transcript line with `[HH:MM:SS]` |
| `--keep-brackets` | off | Keep `[Music]` / `[Applause]` annotations in transcript |
| `--subs` | off | Write subtitle files alongside the video |

## Transcript

`--transcript` extracts captions as clean readable text — no timecodes in the body, no duplicate lines from YouTube's rolling auto-caption window:

```
ytd <url> --transcript
ytd <url> --transcript --timestamps       # [HH:MM:SS] per line
ytd <url> --transcript --lang fr          # French transcript
ytd <url> --transcript | pbcopy           # copy to clipboard (macOS)
ytd <url> --transcript > notes.txt        # save to file
```

Prefers manual subtitles; falls back to auto-generated captions. If the requested language is unavailable, the script lists what languages are available and exits.

## Installation

Choose the installation target you need.

<details>
<summary>GitHub Copilot Skill</summary>

Install the skill by placing this folder under your Copilot skills directory. The required layout is:

```text
~/.copilot/skills/ytd/
├── SKILL.md
└── ytd.py
```

From this repository checkout:

```bash
mkdir -p ~/.copilot/skills/ytd
cp SKILL.md ytd.py ~/.copilot/skills/ytd/
chmod +x ~/.copilot/skills/ytd/ytd.py
```

Or clone the repository directly into the skills directory:

```bash
git clone https://github.com/pavelsimo/ytd.git ~/.copilot/skills/ytd
chmod +x ~/.copilot/skills/ytd/ytd.py
```

For a repository-local Copilot skill, use `.github/skills/ytd/` instead of `~/.copilot/skills/ytd/`.

</details>

<details>
<summary>Claude Code Slash Command</summary>

Install the `/ytd` command by copying `SKILL.md` into the Claude commands directory:

```bash
mkdir -p ~/.claude/commands
cp SKILL.md ~/.claude/commands/ytd.md
```

Then type `/ytd <url>` in any Claude Code session.

</details>

<details>
<summary>Codex Skill</summary>

Install the skill by placing this folder under your Codex skills directory. The required layout is:

```text
${CODEX_HOME:-~/.codex}/skills/ytd/
├── SKILL.md
└── ytd.py
```

From this repository checkout:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills/ytd"
cp SKILL.md ytd.py "${CODEX_HOME:-$HOME/.codex}/skills/ytd/"
chmod +x "${CODEX_HOME:-$HOME/.codex}/skills/ytd/ytd.py"
```

Or clone the repository directly into the skills directory:

```bash
git clone https://github.com/pavelsimo/ytd.git "${CODEX_HOME:-$HOME/.codex}/skills/ytd"
chmod +x "${CODEX_HOME:-$HOME/.codex}/skills/ytd/ytd.py"
```

On Windows, from this repository checkout:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$skillDir = Join-Path $codexHome "skills\ytd"
New-Item -ItemType Directory -Force $skillDir
Copy-Item .\SKILL.md, .\ytd.py $skillDir
```

Or clone the repository directly into the Windows skills directory:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
git clone https://github.com/pavelsimo/ytd.git (Join-Path $codexHome "skills\ytd")
```

Restart Codex after installing so it can discover `SKILL.md`.

</details>

## Dependencies

Requires [uv](https://docs.astral.sh/uv/) and Python ≥ 3.11. The script declares its own dependency (`yt-dlp`) via [PEP 723](https://peps.python.org/pep-0723/) inline metadata — no virtual environment setup needed.

FFmpeg is required for video merging and audio conversion:

```bash
brew install ffmpeg          # macOS
sudo apt install ffmpeg      # Debian / Ubuntu
winget install ffmpeg        # Windows
```

A JavaScript runtime is required by yt-dlp for full YouTube compatibility. Install [deno](https://deno.com):

```bash
brew install deno            # macOS
sudo snap install deno       # Linux
winget install DenoLand.Deno # Windows
```

## Contributing

Open an issue or pull request. Keep commits atomic and follow the [commit conventions](https://github.com/pavelsimo/commit).

## License

MIT
