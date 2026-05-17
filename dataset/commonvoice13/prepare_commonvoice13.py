#!/usr/bin/env python3
"""Prepare the Mandarin Common Voice 13 dataset for this repository.

This script is extracted and cleaned up from `ipa_phoneme.ipynb`.
It downloads the `zh-CN` subset from Hugging Face, applies the notebook's
preprocessing steps, and saves a Hugging Face dataset to disk.
"""

from __future__ import annotations

import argparse
import os
import re
import unicodedata
from pathlib import Path


IPA_EXCEPTIONS = [
    "pʰ",
    "ts",
    "tsʰ",
    "tʰ",
    "ʈʂ",
    "ʈʂʰ",
    "tɕ",
    "tɕʰ",
    "kʰ",
    "ɑɻ",
    "ai",
    "ei",
    "ɑʊ",
    "oʊ",
    "ia",
    "iɛ",
    "wa",
    "wɔ",
    "ɥœ",
    "iɑʊ",
    "ioʊ",
    "wai",
    "wei",
]

_HANZI_MODULE = None
_PINYIN_MODULE = None


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parents[1]
    parser = argparse.ArgumentParser(
        description="Download and preprocess Common Voice 13 Mandarin for model use.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--repo-id",
        default="mozilla-foundation/common_voice_13_0",
        help="Hugging Face dataset repository id.",
    )
    parser.add_argument(
        "--config",
        default="zh-CN",
        help="Dataset configuration name.",
    )
    parser.add_argument(
        "--hf-token",
        default=os.environ.get("HF_TOKEN"),
        help="Optional Hugging Face token. If omitted, the script uses the local login state.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Optional Hugging Face cache directory.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        required=True,
        help="Directory where the processed Hugging Face dataset will be saved.",
    )
    parser.add_argument(
        "--mapping-csv",
        type=Path,
        default=repo_root / "mandarin_p2a_model" / "data" / "IPAwithTone_p2attr_V2.csv",
        help="CSV file used to identify vowels for IPA+tone merging.",
    )
    parser.add_argument(
        "--resample-rate",
        type=int,
        default=16000,
        help="Target sampling rate for the audio column.",
    )
    parser.add_argument(
        "--merge-splits-and-resplit",
        action="store_true",
        help="Merge train, validation, and test, then recreate splits.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Combined size of the held-out portion when recreating splits.",
    )
    parser.add_argument(
        "--shuffle",
        action="store_true",
        help="Shuffle examples before recreating splits.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used when `--shuffle` is enabled.",
    )
    return parser.parse_args()


def contains_non_chinese(sentence: str) -> bool:
    for char in sentence:
        if char.isascii():
            return True
        if "\u3040" <= char <= "\u309F" or "\u30A0" <= char <= "\u30FF":
            return True
        if "\u0370" <= char <= "\u03FF":
            return True
        if unicodedata.category(char).startswith("S"):
            return True
    return False


def remove_punctuation(text: str) -> str:
    pattern = r"[!\"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~·•《》「」『』【】…（）、；：！？——‘’“”，‧。“”·：、/ㄟＰ|・／－〉〈─□Λ]+"
    return re.sub(pattern, "", text)


def remove_tones(ipa_text: str) -> str:
    return re.sub(r"[˥˧˩˦˨×]+", "", ipa_text)


def tokenize_ipa_symbols(ipa_text: str) -> str:
    symbols = list(ipa_text)
    result: list[str] = []
    i = 0

    while i < len(symbols):
        if symbols[i] == "ɻ":
            result.append("ɑɻ")
            i += 1
        elif i < len(symbols) - 2 and "".join(symbols[i : i + 3]) in IPA_EXCEPTIONS:
            result.append("".join(symbols[i : i + 3]))
            i += 3
        elif i < len(symbols) - 1 and "".join(symbols[i : i + 2]) in IPA_EXCEPTIONS:
            result.append("".join(symbols[i : i + 2]))
            i += 2
        else:
            result.append(symbols[i])
            i += 1

    return " ".join(result)


def convert_phoneme(text: str) -> str:
    global _HANZI_MODULE
    if _HANZI_MODULE is None:
        from dragonmapper import hanzi

        _HANZI_MODULE = hanzi

    normalized = remove_punctuation(text)
    ipa_result = _HANZI_MODULE.to_ipa(normalized, delimiter=" ", all_readings=False, container="[]")
    ipa_result = ipa_result.replace("j", "i").replace("ɪ", "i").replace("ń", "ən")
    ipa_result = remove_tones(ipa_result)
    ipa_result = " ".join(ipa_result.split())
    return tokenize_ipa_symbols(ipa_result)


def convert_tone(text: str) -> str:
    global _PINYIN_MODULE
    if _PINYIN_MODULE is None:
        import pinyin

        _PINYIN_MODULE = pinyin

    normalized = remove_punctuation(text)
    numerical = _PINYIN_MODULE.get(normalized, format="numerical")
    digits_only = re.sub(r"\D", "", numerical).replace("5", "0")
    return " ".join(digits_only)


def load_vowel_set(mapping_csv: Path) -> set[str]:
    import pandas as pd

    frame = pd.read_csv(mapping_csv)
    return {
        str(row["Phoneme_ipaDragon"])
        for _, row in frame.iterrows()
        if int(row["vowel"]) == 1
    }


def add_ipa_with_tone(ipa_text: str, tone_text: str, vowel_set: set[str]) -> str:
    tones = tone_text.split()
    ipa_symbols = ipa_text.split()
    tone_index = 0

    for idx, symbol in enumerate(ipa_symbols):
        if symbol not in vowel_set:
            continue
        if tone_index >= len(tones):
            break

        tone_value = tones[tone_index]
        if tone_value != "0":
            ipa_symbols[idx] = f"{symbol}{tone_value}"
        tone_index += 1

    return " ".join(ipa_symbols)


def main() -> None:
    from datasets import Audio, DatasetDict, concatenate_datasets, load_dataset

    args = parse_args()

    load_kwargs: dict[str, object] = {}
    if args.hf_token:
        load_kwargs["token"] = args.hf_token
    if args.cache_dir is not None:
        load_kwargs["cache_dir"] = str(args.cache_dir)

    print(f"[INFO] Downloading {args.repo_id} ({args.config})")
    data = load_dataset(args.repo_id, args.config, **load_kwargs)

    for split_name in ("invalidated", "other"):
        if split_name in data:
            del data[split_name]

    removable_columns = [
        "client_id",
        "up_votes",
        "down_votes",
        "age",
        "gender",
        "accent",
        "locale",
        "segment",
        "variant",
    ]
    present_columns = [name for name in removable_columns if name in data["train"].column_names]
    if present_columns:
        data = data.remove_columns(present_columns)

    if "audio" in data["train"].column_names:
        data = data.cast_column("audio", Audio(sampling_rate=args.resample_rate))

    for split_name in ("train", "validation", "test"):
        if split_name not in data:
            continue
        print(f"[INFO] Filtering non-Chinese content from {split_name}")
        data[split_name] = data[split_name].filter(
            lambda example: bool(example["sentence"]) and not contains_non_chinese(example["sentence"])
        )

    print("[INFO] Adding IPA transcripts")
    for split_name in ("train", "validation", "test"):
        if split_name not in data:
            continue
        data[split_name] = data[split_name].map(
            lambda example: {"transcript_IPA": convert_phoneme(example["sentence"])},
            desc=f"IPA for {split_name}",
        )

    print("[INFO] Adding tone sequences")
    for split_name in ("train", "validation", "test"):
        if split_name not in data:
            continue
        data[split_name] = data[split_name].map(
            lambda example: {"tone_pinyin": convert_tone(example["sentence"])},
            desc=f"Tone for {split_name}",
        )

    vowel_set = load_vowel_set(args.mapping_csv)
    print(f"[INFO] Loaded {len(vowel_set)} vowel symbols from {args.mapping_csv}")

    print("[INFO] Adding IPA+tone transcripts")
    for split_name in ("train", "validation", "test"):
        if split_name not in data:
            continue
        data[split_name] = data[split_name].map(
            lambda example: {
                "transcript_IPAwithTone": add_ipa_with_tone(
                    example["transcript_IPA"],
                    example["tone_pinyin"],
                    vowel_set,
                )
            },
            desc=f"IPA+tone for {split_name}",
        )

    if args.merge_splits_and_resplit:
        print("[INFO] Merging splits and recreating train/test/validation")
        merged = concatenate_datasets([data["train"], data["validation"], data["test"]])
        train_test = merged.train_test_split(
            test_size=args.test_size,
            shuffle=args.shuffle,
            seed=args.seed,
        )
        test_validation = train_test["test"].train_test_split(
            test_size=0.5,
            shuffle=args.shuffle,
            seed=args.seed,
        )
        data = DatasetDict(
            {
                "train": train_test["train"],
                "test": test_validation["train"],
                "validation": test_validation["test"],
            }
        )

    args.output_path.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Saving processed dataset to {args.output_path}")
    data.save_to_disk(str(args.output_path))
    print("[INFO] Done")


if __name__ == "__main__":
    main()
