## 📂 Dataset Location

By default, this repository stores the processed dataset here.

However, users are free to specify any other output directory.

### ✅ Requirements

Please ensure that:

- All datasets are preprocessed and converted into **Hugging Face format** using either the provided script or notebook.
- Each example includes appropriate **notation features** compatible with your `phoneme2attr.csv` specification. This ensures consistency for downstream models that rely on articulatory or phonological attributes.

If you're contributing a new dataset, follow the same structure and preprocessing standards to maintain compatibility with this project.
