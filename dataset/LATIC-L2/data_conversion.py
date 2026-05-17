#!/usr/bin/env python3
import os
import argparse
import re

def extract_transcripts(audio_filenames, transcript_file, filename_output, text_output):
    """
    Extract transcript lines where filename exists in audio_filenames.
    Write matched filenames and their cleaned transcripts to separate files.
    """
    audio_to_text = {}

    try:
        with open(transcript_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"[ERROR] Transcript file not found: {transcript_file}")
        return {}

    for line in lines:
        parts = line.strip().split('\t', 1)
        if len(parts) != 2:
            continue
        filename, text = parts
        text_no_spaces = text.replace(' ', '')
        if filename in audio_filenames:
            audio_to_text[filename] = text_no_spaces

    with open(filename_output, 'w', encoding='utf-8') as f_out:
        for filename in audio_to_text:
            f_out.write(f"{filename}.WAV\n")

    with open(text_output, 'w', encoding='utf-8') as t_out:
        for txt in audio_to_text.values():
            t_out.write(f"{txt}\n")

    print(f"[INFO] Extracted {len(audio_to_text)} entries from {os.path.basename(transcript_file)}")
    return audio_to_text

def filter_data_based_on_transcripts(data, transcript_file):
    """
    Filter the dataset to keep only those audio files listed in transcript_file.
    """
    from tqdm import tqdm

    with open(transcript_file, 'r', encoding='utf-8') as file:
        lines = {line.strip() for line in file}

    indices_to_keep = []
    for idx, item in enumerate(tqdm(data['train'], desc="Filtering dataset")):
        audio_path = item['audio']['path']
        audio_filename = os.path.basename(audio_path)
        if audio_filename in lines:
            indices_to_keep.append(idx)

    return data['train'].select(indices_to_keep)

def remove_tones(ipa_string):
    pattern = r'[˥˧˩˦˨×]+'
    return re.sub(pattern, '', ipa_string)

def remove_punctuation(input_string):
    pattern = r"[!\"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~·•《》「」『』【】…（）、；：！？——‘’“”，‧。“”·：、/ㄟＰ|・／－〉〈─□ΛSPK]+"
    return re.sub(pattern, '', input_string)

exceptions = [
    'pʰ', 'ts', 'tsʰ', 'tʰ', 'ʈʂ', 'ʈʂʰ', 'tɕ', 'tɕʰ', 'kʰ',
    'ɑɻ', 'ai', 'ei', 'ɑʊ', 'oʊ', 'ia', 'iɛ', 'wa', 'wɔ',
    'ɥœ', 'iɑʊ', 'ioʊ', 'wai', 'weɪ'
]

def convert_phoneme(input_string):
    from dragonmapper import hanzi

    try:
        s = remove_punctuation(input_string)
        ipa_result = hanzi.to_ipa(s, delimiter=' ', all_readings=False, container='[]')
        ipa_result = ipa_result.replace('j', 'i').replace('ɪ', 'i').replace('ń', 'ən')
        ipa_result = remove_tones(ipa_result)
        ipa_result = ipa_result.replace(' ', '')
        symbols = list(ipa_result)
        result = []
        i = 0
        while i < len(symbols):
            if symbols[i] == 'ɻ':
                result.append('ɑɻ')
                i += 1
            elif i < len(symbols) - 2 and ''.join(symbols[i:i+3]) in exceptions:
                result.append(''.join(symbols[i:i+3]))
                i += 3
            elif i < len(symbols) - 1 and ''.join(symbols[i:i+2]) in exceptions:
                result.append(''.join(symbols[i:i+2]))
                i += 2
            else:
                result.append(symbols[i])
                i += 1
        return ' '.join(result)
    except ValueError as e:
        print(f"Error processing syllable: {input_string} -> {e}")
        raise

def add_transcript_column(example):
    example['transcript_IPA_actual'] = convert_phoneme(example['sentence_speaker_said'])
    example['transcript_IPA_suppose'] = convert_phoneme(example['sentence_supposed_said'])
    return example

def replace_five_with_zero(example):
    example['tone_pinyin_actual'] = example['tone_pinyin_actual'].replace('5', '0')
    example['tone_pinyin_suppose'] = example['tone_pinyin_suppose'].replace('5', '0')
    return example

def main():
    from datasets import load_dataset, DatasetDict
    from tqdm import tqdm

    args = parse_args()

    base_path = os.path.dirname(os.path.abspath(__file__))
    metadata_dir = os.path.abspath(args.metadata_dir)

    # 1) Load dataset
    data_path = os.path.join(base_path, 'data', 'WAVA')
    print(f"Loading audio dataset from: {data_path}")
    data = load_dataset("audiofolder", data_dir=data_path)

    # 2) Extract audio filenames
    audio_filenames = [
        os.path.splitext(os.path.basename(item["audio"]["path"]))[0]
        for item in tqdm(data["train"], desc="Extracting file names")
    ]

    # 3) Extract transcripts
    scripts = {
        os.path.join(base_path, "data", "SCRIPT", "Actual_text", "total_transcript.txt"):
            (os.path.join(metadata_dir, "actual_wav.txt"), os.path.join(metadata_dir, "actual_transcript.txt")),
        os.path.join(base_path, "data", "SCRIPT", "Suppose_text", "total_transcript.txt"):
            (os.path.join(metadata_dir, "suppose_wav.txt"), os.path.join(metadata_dir, "suppose_transcript.txt")),
    }
    os.makedirs(metadata_dir, exist_ok=True)
    for transcript_file, (fname_out, txt_out) in scripts.items():
        extract_transcripts(audio_filenames, transcript_file, fname_out, txt_out)

    # 4) Filter dataset by transcripts
    data["train"] = filter_data_based_on_transcripts(data, os.path.join(metadata_dir, "actual_wav.txt"))
    data["train"] = filter_data_based_on_transcripts(data, os.path.join(metadata_dir, "suppose_wav.txt"))

    # 5) Insert sentences
    with open(os.path.join(metadata_dir, "actual_transcript.txt"), encoding="utf-8") as f:
        actual = [l.strip() for l in f]
    with open(os.path.join(metadata_dir, "suppose_transcript.txt"), encoding="utf-8") as f:
        suppose = [l.strip() for l in f]

    def add_sentences(example, idx):
        example["sentence_speaker_said"] = actual[idx]
        example["sentence_supposed_said"] = suppose[idx]
        return example

    data["train"] = data["train"].map(add_sentences, with_indices=True)

    # 6) Insert tones
    with open(os.path.join(metadata_dir, "tone_actual.txt"), encoding="utf-8") as f:
        tone_actual = [l.strip() for l in f]
    with open(os.path.join(metadata_dir, "tone_suppose.txt"), encoding="utf-8") as f:
        tone_suppose = [l.strip() for l in f]

    def add_tones(example, idx):
        example["tone_pinyin_actual"] = tone_actual[idx]
        example["tone_pinyin_suppose"] = tone_suppose[idx]
        return example

    data["train"] = data["train"].map(add_tones, with_indices=True)

    # 7) Normalize tone '5'→'0'
    data["train"] = data["train"].map(replace_five_with_zero)

    # 8) Add IPA transcripts
    data["train"] = data["train"].map(add_transcript_column)

    # 9) Split into train / test / validation
    split_ratio = args.split_ratio
    train_test = data["train"].train_test_split(test_size=split_ratio, shuffle=False)
    test_val = train_test["test"].train_test_split(test_size=0.5, shuffle=False)
    dataset = DatasetDict({
        "train": train_test["train"],
        "test": test_val["train"],
        "validation": test_val["test"],
    })

    # 10) Save to disk
    os.makedirs(args.output_path, exist_ok=True)
    print(f"Saving dataset to {args.output_path}")
    dataset.save_to_disk(args.output_path)
    print("Done.")
    
def parse_args():
    parser = argparse.ArgumentParser(
        description="Prepare and split the LATIC-L2 Mandarin audio-transcript dataset"
    )
    parser.add_argument(
        "--metadata-dir",
        type=str,
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated"),
        help="Directory containing the helper text files used during conversion."
    )
    parser.add_argument(
        "--split-ratio",
        type=float,
        default=0.3,
        help="Proportion of the dataset to reserve for (test+validation)."
    )
    parser.add_argument(
        "--output-path",
        type=str,
        required=True,
        help="Directory where the final DatasetDict will be saved"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()

# API EXAMPLE
# python data_conversion.py --metadata-dir ./generated --output-path /YOUR_OWN_PATH/ --split-ratio 0.3
