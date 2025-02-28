## Download and preprocess a current snapshot of the English subset of the Project Gutenberg corpus
This repository is based on the [Gutenberg](https://github.com/pgcorpus/gutenberg) repository by Francesc Font-Clos and Martin Gerlach and can be used to download and preprocess an up-to-date snapshot of the English subset of the Project Gutenberg corpus.

1. Download the most recent snapshot of the Project Gutenberg corpus: 
```python
python -u get_data.py
```
This will download a copy of all UTF-8 books in the Project Gutenberg corpus and will create a csv file with metadata (e.g. author, title, year, ...). If you already have some of the data, it will only download those that are missing (we use `rsync` for this), so you can update the dataset periodically by just running `get_data.py`.

2. Preprocess all the data in the `raw/` directory:
```python
python -u process_data.py
```
This will clean up the files (removing headers and footers) and populate the `text/`, `tokens/` and `counts/` folders. You can pass the ``--language` argument to select books in a given language only (*e.g.* `--language 'en'` to select books in English only).

3. Divide the data into a few paragraph-long chunks of text (ideal for generating fine-grained embeddings) and add the corresponding metadata info, save all the data in one big `jsonl` file, which we can then upload to Hugging Face:
```python
python -u create_dataset.py
```
or alternatively save the whole document as a single record without chunking it into smaller units:
```python
python -u create_dataset.py --wholedoc
```

February 28, 2025 snapshot of the complete preprocessed PG corpus, containing a total of 73802 documents, can be accessed from [this Hugging Face repository](https://huggingface.co/datasets/eminorhan/gutenberg_feb25). The subset of the corpus containing only English language texts, containing a total of 58875 documents, can be accessed from [this Hugging Face repository](https://huggingface.co/datasets/eminorhan/gutenberg_en_feb25).
