# ytd

Download YouTube videos, audio, or transcripts from the command line — no config, always the latest yt-dlp.

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

<details>
<summary>macOS / Linux</summary>

Install [uv](https://docs.astral.sh/uv/getting-started/installation/):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Download the script:

```bash
curl -fsSL https://raw.githubusercontent.com/pavelsimo/ytd/main/ytd.py -o ~/bin/ytd.py
chmod +x ~/bin/ytd.py
```

Add a shell alias to your `.bashrc` or `.zshrc`:

```bash
alias ytd="uv run --upgrade ~/bin/ytd.py"
```

Reload your shell and run:

```bash
ytd https://youtu.be/dQw4w9WgXcQ
```

</details>

<details>
<summary>Windows</summary>

Install [uv](https://docs.astral.sh/uv/getting-started/installation/):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Download `ytd.py`, then add a PowerShell alias to your profile:

```powershell
Set-Alias ytd "uv run --upgrade $HOME\bin\ytd.py"
```

Then run:

```powershell
ytd https://youtu.be/dQw4w9WgXcQ
```

</details>

<details>
<summary>Claude Code</summary>

Install the `/ytd` skill globally:

```bash
mkdir -p ~/.claude/commands
cp SKILL.md ~/.claude/commands/ytd.md
```

Then type `/ytd <url>` in any Claude Code session.

</details>

## Dependencies

Requires [uv](https://docs.astral.sh/uv/) and Python ≥ 3.11. The script declares its own dependency (`yt-dlp`) via [PEP 723](https://peps.python.org/pep-0723/) inline metadata — no virtual environment setup needed.

FFmpeg is required for video merging and audio conversion:

```bash
brew install ffmpeg          # macOS
sudo apt install ffmpeg      # Debian / Ubuntu
winget install ffmpeg        # Windows
```

## Contributing

Open an issue or pull request. Keep commits atomic and follow the [commit conventions](https://github.com/pavelsimo/commit).

## License

MIT
