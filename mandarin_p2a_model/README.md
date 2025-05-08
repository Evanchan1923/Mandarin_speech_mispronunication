
# 🗣️ Speech Attribute Transcription

This project focuses on training and evaluating models that transcribe speech into articulatory or phonological attributes based on IPA phonemes.

---

## 📦 Training

To train the Speech Attribute model, use one of the provided configuration files:

```bash
# Using general Mandarin setting
python train.py --config_file=mandarin_setting.yaml train_SA_model
```

---

## 🧪 Evaluation

You can evaluate a pre-trained model on different datasets by specifying the evaluation data path, part of the dataset, and other parameters.

### ▶️ Evaluate on AiShell (small subset)

```bash
python train.py \
  --config_file="mandarin_setting.yaml" \
  evaluate_SA_model \
  --eval_data="YOUR/PATH/TO/AiShell_small" \
  --eval_parts="test" \
  --suffix="test_AISHELL_Diph_withDecouple" \
  --phoneme_column="transcript_IPA"
```

### ▶️ Evaluate on CommonVoice 13

```bash
python train.py \
  --config_file="mandarin_setting.yaml" \
  evaluate_SA_model \
  --eval_data="YOUR/PATH/TO/CommonVoice13_CN" \
  --eval_parts="test" \
  --suffix="test_CV13_withDiph_withDecouple" \
  --phoneme_column="transcript_IPA"
```

---

## ✅ Notes

- `config_file`: YAML file containing model architecture, training hyperparameters, and preprocessing steps.
- `--phoneme_column`: Make sure the phoneme transcription in the dataset matches the expected IPA format.
- `--suffix`: Used to label evaluation output results.

---

For custom datasets, ensure your dataset folder follows the HuggingFace `datasets` format and includes the `transcript_IPA` column or your custom column name.
