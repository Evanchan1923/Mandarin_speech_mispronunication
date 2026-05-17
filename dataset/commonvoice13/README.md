# CommonVoice13

This folder contains the Common Voice 13 Mandarin (`zh-CN`) dataset preparation workflow used in this repository.

## What Is Included

- `ipa_phoneme.ipynb`: the original notebook workflow, kept as reference.
- `prepare_commonvoice13.py`: a cleaned script version for reproducible preprocessing.

## What The Script Does

The preprocessing script downloads the Mandarin Common Voice 13 dataset from Hugging Face and prepares a model-ready Hugging Face dataset by:

- removing unused splits such as `invalidated` and `other`,
- removing unused metadata columns,
- resampling audio to 16 kHz,
- filtering out sentences containing non-Chinese text,
- adding `transcript_IPA`,
- adding `tone_pinyin`,
- adding `transcript_IPAwithTone`.

The `transcript_IPAwithTone` column uses the tone-aware IPA mapping file already stored in this repository:

```text
mandarin_p2a_model/data/IPAwithTone_p2attr_V2.csv
```

## Dependencies

Install the required Python packages before running the script:

```bash
pip install datasets dragonmapper pinyin pandas
```

If your Hugging Face environment requires authentication, either run:

```bash
huggingface-cli login
```

or provide a token with `--hf-token` or the `HF_TOKEN` environment variable.

## Usage

From the repository root:

```bash
python3 dataset/commonvoice13/prepare_commonvoice13.py \
  --output-path /path/to/CommonVoice13_prepared
```

To merge the original splits and recreate new train/test/validation splits:

```bash
python3 dataset/commonvoice13/prepare_commonvoice13.py \
  --output-path /path/to/CommonVoice13_prepared \
  --merge-splits-and-resplit
```

## Notes

- The notebook was originally developed in a local research environment and is kept mainly for transparency.
- The Python script is the recommended entry point for other researchers.
- The saved output is a Hugging Face dataset on disk and is intended to be used by the model code in [`mandarin_p2a_model/`](../../mandarin_p2a_model/).
