#!/usr/bin/env python3
import os
import argparse
import re
from datasets import load_dataset, DatasetDict
from tqdm import tqdm
from dragonmapper import hanzi


# Function to extract audio filenames without extensions
def extract_audio_filenames(dataset):
    audio_filenames = []
    for item in tqdm(dataset["train"], desc="Extracting file names"):
        audio_path = item["audio"]["path"]
        filename = os.path.splitext(os.path.basename(audio_path))[0]
        audio_filenames.append(filename)
    return audio_filenames


# Function to load transcripts mapping from filename to text
def load_transcripts(transcript_file, audio_filenames):
    audio_to_text = {}
    with open(transcript_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                fname, text = parts
                text_clean = text.replace(" ", "")
                if fname in audio_filenames:
                    audio_to_text[fname] = text_clean
    return audio_to_text


# Function to filter dataset based on available transcripts
def filter_dataset(dataset, audio_to_text):
    indices = []
    for idx, item in tqdm(enumerate(dataset["train"]), desc="Filtering dataset", total=len(dataset["train"])):
        fname = os.path.basename(item["audio"]["path"])
        if os.path.splitext(fname)[0] in audio_to_text:
            indices.append(idx)
    return dataset["train"].select(indices)


# Text processing utilities
def remove_tones(ipa_string):
    return re.sub(r"[˥˧˩˦˨×]+", "", ipa_string)


def remove_punctuation(s):
    pattern = r"[\!\"\#\$%&'()*+,\-\./:;<=>?@\\\[\\\]\\^_`{|}~·•《》「」『』【】…（）、；：！？——‘’“”，‧。”“·：、/ㄟＰ|・／－〉〈─□Λ]+"
    return re.sub(pattern, "", s)


exceptions = [
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
    "weɪ",
]


def convert_phoneme(text):
    clean = remove_punctuation(text)
    ipa = hanzi.to_ipa(clean, delimiter=" ", all_readings=False, container="[]")
    ipa = ipa.replace("j", "i").replace("ɪ", "i")
    ipa = remove_tones(ipa)
    ipa = " ".join(ipa.split())
    symbols = list(ipa)
    result = []
    i = 0
    while i < len(symbols):
        # handle special symbols and exceptions
        if symbols[i] == "ɻ":
            result.append("ɑɻ")
            i += 1
        elif i < len(symbols) - 2 and "".join(symbols[i : i + 3]) in exceptions:
            result.append("".join(symbols[i : i + 3]))
            i += 3
        elif i < len(symbols) - 1 and "".join(symbols[i : i + 2]) in exceptions:
            result.append("".join(symbols[i : i + 2]))
            i += 2
        else:
            result.append(symbols[i])
            i += 1
    return " ".join(result)


# Add sentence and transcript to dataset
def add_sentence_and_transcript(dataset, audio_to_text):
    sentences = [audio_to_text[os.path.splitext(os.path.basename(item["audio"]["path"]))[0]] for item in dataset]

    def mapper(example, idx):
        example["sentence"] = sentences[idx]
        example["transcript"] = convert_phoneme(example["sentence"])
        return example

    return dataset.map(mapper, with_indices=True)


# Split into train, test, validation based on ratio
def split_dataset(dataset, split_ratio):
    # split_ratio is proportion of data that goes to test+validation
    train_test = dataset.train_test_split(test_size=split_ratio, shuffle=False)
    test_valid = train_test["test"].train_test_split(test_size=0.5, shuffle=False)
    return DatasetDict({"train": train_test["train"], "test": test_valid["train"], "validation": test_valid["test"]})


# Main function
def main():
    parser = argparse.ArgumentParser(description="Convert audio dataset with transcripts and split.")
    parser.add_argument("--output-path", type=str, required=True, help="Directory to save processed dataset")
    parser.add_argument("--split-ratio", type=float, default=0.3, help="Test+validation split ratio (e.g., 0.3 means 70/15/15)")
    parser.add_argument("--audio-dir", type=str, default="wav", help="Directory containing audio files")
    parser.add_argument("--transcript-file", type=str, default=os.path.join("transcript", "transcript.txt"), help="Path to transcript file")
    args = parser.parse_args()

    base_dir = os.getcwd()
    data = load_dataset("audiofolder", data_dir=os.path.join(base_dir, args.audio_dir))

    audio_filenames = extract_audio_filenames(data)
    audio_to_text = load_transcripts(os.path.join(base_dir, args.transcript_file), audio_filenames)

    filtered = filter_dataset(data, audio_to_text)
    enriched = add_sentence_and_transcript(filtered, audio_to_text)

    split_ds = split_dataset(enriched, args.split_ratio)
    split_ds.save_to_disk(args.output_path)
    print(f"Saved processed dataset to {args.output_path}")


if __name__ == "__main__":
    main()

# API
# python Convert_huggingFace_Aishell.py --output-path /your/own/path/ --split-ratio 0.3 --audio-dir /path/to/wav --transcript-file /path/to/transcript.txt

# Requrements Libraries:
# pip install datasets tqdm dragonmapper
