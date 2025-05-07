# Notation Extraction and Data Conversion Workflow

This project extracts musical or symbolic notations and converts them into a usable data format for further processing or model training. (huggingFace format)

## 📁 General Workflow

1. **Extract Notations**
   - Run `Extract_Notations_1.ipynb` to generate the notations file.
   - This notebook performs the initial extraction and processing.

2. **Convert Notations**
   - Choose one of the following options to convert the extracted data:
     - `Extract_Notations_2.ipynb` – An interactive Jupyter Notebook version.
     - `data_conversion.py` – A straightforward Python script version.

## ⚙️ Usage

### Option A: Use the Python script

```bash
python data_conversion.py --output-path /YOUR/OWN/PATH/ --split-ratio 0.3
