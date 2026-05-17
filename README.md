# Mandarin P2A Research Repository

This repository collects the main resources behind the thesis and conference-paper workflow for Mandarin pronunciation modeling.

It is organized so that other researchers can:

- understand how the datasets were prepared,
- inspect the model and training code,
- and review the evaluation direction and unfinished experiments.

## Repository Structure

### `dataset/`

The `dataset/` folder contains example dataset-conversion workflows used for the model.

- [`dataset/aishell-native/`](dataset/aishell-native/): example conversion assets for the AISHELL native Mandarin dataset.
- [`dataset/LATIC-L2/`](dataset/LATIC-L2/): example conversion assets for the LATIC L2 Mandarin learner dataset.
- [`dataset/commonvoice13/`](dataset/commonvoice13/): example conversion assets for the Mandarin Common Voice 13 dataset downloaded from Hugging Face.

These folders include the source metadata, notebooks, and script-based preprocessing utilities used to turn the datasets into a format that can be consumed by the model pipeline.

### `mandarin_p2a_model/`

The [`mandarin_p2a_model/`](mandarin_p2a_model/) folder contains the main model and training code.

This is the core implementation area for:

- model configuration,
- training scripts,
- phoneme or attribute transcription logic,
- related utilities used in the thesis experiments,
- and the evaluation notebooks under [`mandarin_p2a_model/evaluation/`](mandarin_p2a_model/evaluation/).

The evaluation section inside `mandarin_p2a_model/` is not fully finished yet. It is included mainly as research reference material showing the intended evaluation direction, rather than a final polished evaluation package.

## Notes for Researchers

- Start with `dataset/` if you want to understand how the AISHELL, LATIC, and Common Voice 13 datasets were converted for the model.
- Start with `mandarin_p2a_model/` if you want to inspect or reuse the training pipeline.
- Treat [`mandarin_p2a_model/evaluation/`](mandarin_p2a_model/evaluation/) as work-in-progress documentation and exploratory evaluation material.

## Current Status

This repository is being cleaned up for open-source release. Some parts are already script-based and reusable, while others still reflect the original research workflow and may require adaptation for new environments.
