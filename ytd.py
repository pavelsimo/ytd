#!/usr/bin/env -S uv run --upgrade
# /// script
# requires-python = ">=3.11"
# dependencies = ["yt-dlp"]
# ///

import argparse
import glob
import os
import re
import sys
import tempfile

import yt_dlp

BRACKET_RE = re.compile(r"\[[A-Z][a-zA-Z ]+\]")
INLINE_TS_RE = re.compile(r"<\d{2}:\d{2}:\d{2}\.\d{3}>")
HTML_TAG_RE = re.compile(r"</?[a-z][^>]*>")
TIMESTAMP_RE = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+[\d:.]+")

PARAGRAPH_GAP_SECONDS = 4.0


def _ts_to_seconds(ts: str) -> float:
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def _format_timestamp(ts: str) -> str:
    h, m, s = ts.split(":")
    return f"[{int(h):02d}:{int(m):02d}:{int(float(s)):02d}]"


def _parse_vtt(content: str) -> list[tuple[str, str]]:
    content = INLINE_TS_RE.sub("", content)
    content = HTML_TAG_RE.sub("", content)

    cues: list[tuple[str, str]] = []
    for block in re.split(r"\n{2,}", content.strip()):
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        if lines[0].startswith(("WEBVTT", "Kind:", "Language:")):
            continue
        ts_start = None
        text_parts: list[str] = []
        for i, line in enumerate(lines):
            if "-->" in line:
                m = TIMESTAMP_RE.match(line)
                if m:
                    ts_start = m.group(1)
                    text_parts = lines[i + 1 :]
                break
        if ts_start is None or not text_parts:
            continue
        text = " ".join(text_parts)
        if text.strip():
            cues.append((ts_start, text))
    return cues


def _deduplicate_rolling(cues: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Strip prefix overlap from YouTube's sliding-window auto-captions."""
    if not cues:
        return []
    result: list[tuple[str, str]] = []
    seen_words: list[str] = []
    for ts, text in cues:
        words = text.split()
        max_overlap = 0
        for n in range(min(len(words), len(seen_words)), 0, -1):
            if seen_words[-n:] == words[:n]:
                max_overlap = n
                break
        new_words = words[max_overlap:]
        if new_words:
            result.append((ts, " ".join(new_words)))
        seen_words = words
    return result


def _format_transcript(
    cues: list[tuple[str, str]],
    keep_brackets: bool = False,
    timestamps: bool = False,
    gap: float = PARAGRAPH_GAP_SECONDS,
) -> str:
    paragraphs: list[list[str]] = []
    current: list[str] = []
    prev_sec: float | None = None

    for ts, text in cues:
        if not keep_brackets:
            text = BRACKET_RE.sub("", text).strip()
        if not text:
            continue
        sec = _ts_to_seconds(ts)
        if prev_sec is not None and (sec - prev_sec) > gap:
            if current:
                paragraphs.append(current)
                current = []
        if timestamps:
            current.append(f"{_format_timestamp(ts)} {text}")
        else:
            current.append(text)
        prev_sec = sec

    if current:
        paragraphs.append(current)

    sep = "\n" if timestamps else " "
    return "\n\n".join(sep.join(para) for para in paragraphs)


def _resolve_lang(lang: str, sources: dict) -> str | None:
    if lang in sources:
        return lang
    for code in sources:
        if code.startswith(lang):
            return code
    return None


def get_transcript(
    url: str,
    lang: str = "en",
    keep_brackets: bool = False,
    timestamps: bool = False,
) -> None:
    probe_params = {"quiet": True, "skip_download": True, "simulate": True}
    with yt_dlp.YoutubeDL(probe_params) as ydl:
        info = ydl.extract_info(url, download=False)

    manual = info.get("subtitles") or {}
    auto = info.get("automatic_captions") or {}

    resolved = _resolve_lang(lang, manual) or _resolve_lang(lang, auto)
    if resolved is None:
        avail = sorted(set(manual) | set(auto))
        sys.exit(
            f"No subtitles found for language '{lang}'.\n"
            f"Available: {', '.join(avail) if avail else 'none'}"
        )

    with tempfile.TemporaryDirectory(prefix="ytd_") as tmpdir:
        dl_params = {
            "quiet": True,
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": [resolved],
            "subtitlesformat": "vtt/best",
            "paths": {"home": tmpdir},
            "outtmpl": {"default": "%(id)s.%(ext)s"},
        }
        with yt_dlp.YoutubeDL(dl_params) as ydl:
            ydl.download([url])

        vtt_files = glob.glob(os.path.join(tmpdir, "*.vtt"))
        if not vtt_files:
            sys.exit("Subtitle download succeeded but no .vtt file was produced.")

        content = open(vtt_files[0], encoding="utf-8").read()

    cues = _parse_vtt(content)
    cues = _deduplicate_rolling(cues)
    print(_format_transcript(cues, keep_brackets=keep_brackets, timestamps=timestamps))


def download_video(
    url: str,
    quality: int | None = None,
    output_dir: str = ".",
    with_subs: bool = False,
) -> None:
    fmt = (
        f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
        if quality
        else "bestvideo+bestaudio/best"
    )
    params: dict = {
        "format": fmt,
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
    }
    if with_subs:
        params["writesubtitles"] = True
        params["writeautomaticsub"] = True
    with yt_dlp.YoutubeDL(params) as ydl:
        ydl.download([url])


def download_audio(url: str, output_dir: str = ".") -> None:
    params = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with yt_dlp.YoutubeDL(params) as ydl:
        ydl.download([url])


def list_formats(url: str) -> None:
    with yt_dlp.YoutubeDL({"listformats": True}) as ydl:
        ydl.extract_info(url, download=False)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ytd",
        description="Download YouTube videos, audio, or transcripts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  uv run --upgrade ytd.py https://youtu.be/dQw4w9WgXcQ\n"
            "  uv run --upgrade ytd.py https://youtu.be/dQw4w9WgXcQ --audio\n"
            "  uv run --upgrade ytd.py https://youtu.be/dQw4w9WgXcQ --transcript\n"
            "  uv run --upgrade ytd.py https://youtu.be/dQw4w9WgXcQ --quality 720\n"
            "  uv run --upgrade ytd.py https://youtu.be/dQw4w9WgXcQ --transcript --lang es\n"
        ),
    )
    p.add_argument("url", help="YouTube video URL")
    p.add_argument("--audio", action="store_true", help="download audio only (mp3)")
    p.add_argument("--transcript", action="store_true", help="extract transcript to stdout")
    p.add_argument("--formats", action="store_true", help="list available formats and exit")
    p.add_argument(
        "--quality",
        type=int,
        metavar="HEIGHT",
        help="maximum video height in pixels (e.g. 1080, 720, 480)",
    )
    p.add_argument(
        "--lang",
        default="en",
        metavar="CODE",
        help="language code for transcript/subtitles (default: en)",
    )
    p.add_argument(
        "--output",
        default=".",
        metavar="DIR",
        help="output directory (default: current directory)",
    )
    p.add_argument(
        "--timestamps",
        action="store_true",
        help="prefix each transcript line with [HH:MM:SS]",
    )
    p.add_argument(
        "--keep-brackets",
        dest="keep_brackets",
        action="store_true",
        help="keep [Music] [Applause] etc. in transcript (stripped by default)",
    )
    p.add_argument(
        "--subs",
        action="store_true",
        help="save subtitle files alongside the downloaded video",
    )
    return p


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.formats:
            list_formats(args.url)
        elif args.transcript:
            get_transcript(
                args.url,
                lang=args.lang,
                keep_brackets=args.keep_brackets,
                timestamps=args.timestamps,
            )
        elif args.audio:
            download_audio(args.url, output_dir=args.output)
        else:
            download_video(
                args.url,
                quality=args.quality,
                output_dir=args.output,
                with_subs=args.subs,
            )
    except yt_dlp.utils.DownloadError as e:
        sys.exit(f"Download failed: {e}")
    except yt_dlp.utils.ExtractorError as e:
        sys.exit(f"Could not extract video info: {e}")
    except KeyboardInterrupt:
        sys.exit("\nCancelled.")


if __name__ == "__main__":
    main()
