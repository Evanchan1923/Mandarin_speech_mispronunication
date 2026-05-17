# Aishell-to-HuggingFace Conversion Toolkit

This repository provides two methods to convert the Aishell dataset into a HuggingFace-compatible format and an example project structure strictly following the Aishell directory layout.

## 1. Automated Conversion Script

**File:** `Aishell_Conversion.py`

A standalone Python script for one-shot conversion of your audio and transcript files into a HuggingFace `DatasetDict` and saving it to disk.

### Usage (CLI)

```bash
python Aishell_Conversion.py \
  --output-path /your/own/path/ \
  --split-ratio 0.3 \
  --audio-dir /path/to/wav \
  --transcript-file /path/to/transcript.txt
```

| Argument            | Description                                                     |
| ------------------- | --------------------------------------------------------------- |
| `--output-path`     | Directory where the processed dataset will be saved.            |
| `--split-ratio`     | Fraction of the data reserved for test+validation (e.g. `0.3`). |
| `--audio-dir`       | Path to the folder containing `.wav` audio files.               |
| `--transcript-file` | Path to the text file mapping filenames to transcriptions.      |

## 2. Interactive Conversion Notebook

**File:** `data_change_to_Huggingface.ipynb`

A Jupyter Notebook that guides you step-by-step through:

1. Loading the Aishell audio folder with `datasets.load_dataset("audiofolder")`.
2. Extracting filenames and matching transcripts.
3. Filtering out unmatched or invalid samples.
4. Adding `sentence` and `transcript` columns via phoneme conversion.
5. Splitting into `train` / `test` / `validation` sets interactively.

Open it in Jupyter and follow the prompts to customize each step.

## 3. Repository Structure

This example repo assumes the following Aishell directory layout:

```
├── wav/                               # Root audio folder
│   ├── zip file                       # Training audio files
├── transcript/                        # Transcription files
│   └── transcript.txt                 # filename <space> sentence mapping
├── Aishell_Conversion.py              # Automated conversion script
├── data_change_to_Huggingface.ipynb   # Interactive Jupyter pipeline
└── README.md                          # This documentation
```

Make sure your local copy matches this structure so the scripts and notebook run out-of-the-box.

---

For questions or issues, feel free to open an issue on GitHub or contact the maintainer.
