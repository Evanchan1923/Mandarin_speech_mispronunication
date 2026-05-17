#!/usr/bin/env python3
"""Generate aligned helper text files for the LATIC Mandarin dataset.

This script is derived from the notebook workflow in:
  - Extract_Notations_1.ipynb
  - Extract_Notations_2.ipynb

It reproduces the text artifacts needed by downstream conversion steps
without requiring users to run the notebooks manually.

Terminology:
  - actual: what the L2 speaker actually said
  - suppose: the official target script the speaker was instructed to say
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Generate aligned transcript, notation, and tone text files for LATIC.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--audio-dir",
        type=Path,
        default=script_dir / "data" / "WAVA",
        help="Directory containing the LATIC audio files.",
    )
    parser.add_argument(
        "--actual-transcript",
        type=Path,
        default=script_dir / "data" / "SCRIPT" / "Actual_text" / "total_transcript.txt",
        help="Path to the source transcript for what the L2 speaker actually said.",
    )
    parser.add_argument(
        "--suppose-transcript",
        type=Path,
        default=script_dir / "data" / "SCRIPT" / "Suppose_text" / "total_transcript.txt",
        help="Path to the source transcript for the official target script.",
    )
    parser.add_argument(
        "--actual-notations",
        type=Path,
        default=script_dir / "data" / "SCRIPT" / "Actual_Notations" / "total_notations_actual.txt",
        help="Path to the pinyin notation source for what the L2 speaker actually said.",
    )
    parser.add_argument(
        "--suppose-notations",
        type=Path,
        default=script_dir / "data" / "SCRIPT" / "Suppose_Notations" / "total_notations_suppose.txt",
        help="Path to the pinyin notation source for the official target script.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=script_dir / "generated",
        help="Directory where the generated text files will be written.",
    )
    return parser.parse_args()


def collect_audio_lookup(audio_dir: Path) -> dict[str, str]:
    if not audio_dir.exists():
        raise FileNotFoundError(f"Audio directory does not exist: {audio_dir}")

    audio_files = sorted(
        path for path in audio_dir.rglob("*") if path.is_file() and path.suffix.lower() == ".wav"
    )
    if not audio_files:
        raise FileNotFoundError(
            f"No .wav files were found under {audio_dir}. Download or unpack the audio set first."
        )

    audio_lookup: dict[str, str] = {}
    for path in audio_files:
        stem = path.stem
        if stem in audio_lookup:
            raise ValueError(f"Duplicate audio stem found: {stem}")
        audio_lookup[stem] = path.name
    return audio_lookup


def load_tab_mapping(path: Path, *, remove_spaces: bool = False) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Source file does not exist: {path}")

    mapping: dict[str, str] = {}
    malformed_lines = 0
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) != 2:
                malformed_lines += 1
                continue
            key, value = parts
            mapping[key] = value.replace(" ", "") if remove_spaces else value

    if malformed_lines:
        print(f"[WARN] Skipped {malformed_lines} malformed line(s) in {path.name}")
    return mapping


def extract_tone_numbers(pinyin_line: str) -> str:
    digits_only = re.sub(r"\D", "", pinyin_line)
    return " ".join(digits_only)


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for line in lines:
            handle.write(f"{line}\n")


def main() -> None:
    args = parse_args()

    audio_lookup = collect_audio_lookup(args.audio_dir)
    audio_ids = list(audio_lookup.keys())

    actual_transcript = load_tab_mapping(args.actual_transcript, remove_spaces=True)
    suppose_transcript = load_tab_mapping(args.suppose_transcript, remove_spaces=True)
    actual_notations = load_tab_mapping(args.actual_notations)
    suppose_notations = load_tab_mapping(args.suppose_notations)

    sources = {
        "actual transcript": actual_transcript,
        "suppose transcript": suppose_transcript,
        "actual notation": actual_notations,
        "suppose notation": suppose_notations,
    }

    common_ids = [
        audio_id
        for audio_id in audio_ids
        if all(audio_id in mapping for mapping in sources.values())
    ]
    if not common_ids:
        raise ValueError("No shared utterance IDs were found across audio and annotation sources.")

    print(f"[INFO] Found {len(audio_ids)} audio files in {args.audio_dir}")
    print(f"[INFO] Keeping {len(common_ids)} aligned utterances with complete annotations")
    for label, mapping in sources.items():
        missing = len(audio_ids) - sum(1 for audio_id in audio_ids if audio_id in mapping)
        print(f"[INFO] Missing from {label}: {missing}")

    output_dir = args.output_dir
    actual_wav_lines = [audio_lookup[audio_id] for audio_id in common_ids]
    actual_transcript_lines = [actual_transcript[audio_id] for audio_id in common_ids]
    suppose_transcript_lines = [suppose_transcript[audio_id] for audio_id in common_ids]
    actual_notation_lines = [actual_notations[audio_id] for audio_id in common_ids]
    suppose_notation_lines = [suppose_notations[audio_id] for audio_id in common_ids]
    tone_actual_lines = [extract_tone_numbers(line) for line in actual_notation_lines]
    tone_suppose_lines = [extract_tone_numbers(line) for line in suppose_notation_lines]

    outputs = {
        "actual_wav.txt": actual_wav_lines,
        "suppose_wav.txt": actual_wav_lines,
        "actual_transcript.txt": actual_transcript_lines,
        "suppose_transcript.txt": suppose_transcript_lines,
        "Pinyin_notations_actual.txt": actual_notation_lines,
        "Pinyin_notations_suppose.txt": suppose_notation_lines,
        "tone_actual.txt": tone_actual_lines,
        "tone_suppose.txt": tone_suppose_lines,
    }

    for filename, lines in outputs.items():
        destination = output_dir / filename
        write_lines(destination, lines)
        print(f"[INFO] Wrote {len(lines)} lines to {destination}")


if __name__ == "__main__":
    main()
