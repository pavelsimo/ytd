---
name: ytd
description: Downloads YouTube videos, extracts audio as MP3, and fetches clean deduplicated transcripts using yt-dlp. Use when the user wants to download a YouTube video, extract its audio, or get a transcript from a YouTube URL.
trigger: /ytd
---

# ytd skill

A Claude Code skill that downloads YouTube videos, extracts audio, fetches transcripts, and lists available formats — delegating all work to `ytd.py` via `uv run --upgrade`.

## features

- downloads best quality video by default; restricts height with `--quality`
- extracts audio and converts to mp3 with `--audio`
- prints a clean, deduplicated transcript to stdout with `--transcript`
- lists all available formats with `--formats`
- supports language selection for subtitles and transcripts via `--lang`
- saves subtitle files alongside video with `--subs`
- adds `[HH:MM:SS]` timestamps to transcript lines with `--timestamps`

## usage

```
/ytd <url>                                  # download best quality video
/ytd <url> --audio                          # download audio only (mp3)
/ytd <url> --transcript                     # extract and print transcript
/ytd <url> --formats                        # list available formats
/ytd <url> --quality 720                    # cap video to 720p
/ytd <url> --lang es                        # Spanish subtitles or transcript
/ytd <url> --output ./downloads             # save to a specific directory
/ytd <url> --transcript --timestamps        # transcript with [HH:MM:SS] prefixes
/ytd <url> --transcript --keep-brackets     # keep [Music] [Applause] in output
/ytd <url> --subs                           # save subtitle files with video
```

## workflow

1. parse the `/ytd` invocation to extract the URL and all flags
2. resolve the output directory: use `--output` if provided; default to `.`
3. construct the full command with all parsed flags:
   ```bash
   uv run --upgrade ytd.py <url> [flags]
   ```
4. run the command via Bash and stream output to the terminal
5. on success: confirm what was downloaded or print the transcript inline
6. on error: surface the exact yt-dlp error message and suggest a fix:
   - `Video unavailable` → video is private, removed, or region-locked
   - `No subtitles found for language 'X'` → the error output lists available codes; suggest re-running with one of them
   - `ffmpeg not found` → instruct the user to install ffmpeg (`brew install ffmpeg` / `sudo apt install ffmpeg`)
   - `Sign in to confirm your age` → yt-dlp cannot bypass age-gated content without cookies; inform the user

## best practices

- **always use `--upgrade`** — pass `uv run --upgrade` on every invocation; this ensures yt-dlp is the latest version, critical for YouTube compatibility
- **transcript to file** — when the user wants to save a transcript, append `> filename.txt` rather than writing a separate file: `ytd <url> --transcript > notes.txt`
- **language codes** — use IETF BCP 47 codes: `en`, `es`, `fr`, `de`, `zh-Hans`, `pt-BR`; the script accepts prefix matches (`en` matches `en-US`)
- **quality vs format** — `--quality` selects by height; for codec or container control, run `--formats` first, then pass the raw format ID directly to yt-dlp
- **playlists** — `ytd.py` operates on single videos; for playlist downloads, use the yt-dlp CLI directly: `yt-dlp <playlist-url>`
