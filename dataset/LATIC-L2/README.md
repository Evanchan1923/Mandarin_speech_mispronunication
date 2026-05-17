# LATIC-L2

This folder contains the LATIC L2 Mandarin learner dataset, its annotations, and the preprocessing code used in the thesis workflow.

## Terminology

- `actual`: what the L2 speaker actually said in the recording.
- `suppose`: the official target script that the L2 speaker was instructed to say.

## Corpus Summary

- Sampling rate: 16 kHz
- Total samples: 2,579
- Total duration: about 4 hours
- Speakers: 4 L2 Mandarin learners

Two native-Mandarin annotators listened to each recording and documented both the closest transcript of what the learner actually produced and the target script they were expected to produce, along with phonetic annotations.

## Folder Contents

- `data/`: dataset metadata, annotations, and audio download information.
- `Extract_Notations_1.ipynb`: original notebook for extracting pinyin and tone helper files.
- `Extract_Notations_2.ipynb`: original notebook for downstream dataset conversion.
- `generate_latic_text_files.py`: reproducible script version of the notebook-based helper text generation.
- `data_conversion.py`: end-to-end dataset conversion script that consumes the generated helper files.

## Open-Source Workflow

The full audio is not committed to this repository. After downloading or unpacking the audio files, place them under:

```text
dataset/LATIC-L2/data/WAVA/
```

Then generate the aligned helper text files:

```bash
python3 dataset/LATIC-L2/generate_latic_text_files.py
```

This creates `generated/` with:

- `actual_wav.txt`
- `suppose_wav.txt`
- `actual_transcript.txt`
- `suppose_transcript.txt`
- `Pinyin_notations_actual.txt`
- `Pinyin_notations_suppose.txt`
- `tone_actual.txt`
- `tone_suppose.txt`

If you also want to run the legacy full conversion script, install its Python dependencies first:

```bash
pip install datasets tqdm dragonmapper
```

To continue with the legacy Hugging Face conversion workflow:

```bash
python3 dataset/LATIC-L2/data_conversion.py \
  --metadata-dir dataset/LATIC-L2/generated \
  --output-path /path/to/output
```

## Notes

- The notebooks are kept for transparency and research reference.
- The scripts are the recommended entry point for other researchers using this repository outside the original development environment.
