# 📁 Mispronunciation Detection & Model Evaluation

This directory contains evaluation scripts and notebooks designed for:

- Testing the **Mandarin speech attribute recognition model**
- Performing **mispronunciation detection and analysis**

> ⚠️ **Work in progress:**  
> This evaluation section was not fully finished for open-source release yet. The notebooks are being kept as research notes and partial examples rather than a finalized evaluation toolkit.

> ✅ **Important:**  
> Please ensure you have a **working Mandarin Attribute Recognition model** trained and saved before proceeding with the evaluations below.

---

## 📊 Evaluation Notebooks

### `model_evaluation.ipynb`
- General evaluation of model performance.
- Measures accuracy of speech attribute predictions on test data.

### `model_evaluation_IpaAndTone.ipynb`
- Focuses on detecting mispronunciations using **IPA** and **tone** information.
- Suitable for systems that integrate tonal errors into analysis.

### `model_evaluation_phoneme.ipynb`
- Evaluates mispronunciations based solely on **phoneme-level** predictions.
- Useful when tone is not considered in feedback.

### `model_evaluation_tone.ipynb`
- Detects tone-related pronunciation errors.
- Ideal for isolating tonal mispronunciation patterns in Mandarin.

---

## 🔧 Customization
Each notebook is pre-configured for mispronunciation detection tasks but can be modified to suit different experimental needs (e.g., using different datasets or thresholds).

---

## 💡 Tip
Use consistent phoneme and tone notations that match your training configuration (e.g., `phoneme_column`, `IPA_column`, `tone_scheme`), especially when adapting the scripts to new datasets.
