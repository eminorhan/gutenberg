## Download and preprocess a current snapshot of the English subset of the Project Gutenberg corpus
This repository is based on the [Gutenberg](https://github.com/pgcorpus/gutenberg) repository by Francesc Font-Clos and Martin Gerlach and can be used to download and preprocess an up-to-date snapshot of the English subset of the Project Gutenberg corpus.

1. Download the most recent snapshot of the Project Gutenberg corpus: 
```python
python -u get_data.py
```
This will download a copy of all UTF-8 books in PG and will create a csv file with metadata (e.g. author, title, year, ...). If you already have some of the data, it will only download those you are missing (we use `rsync` for this), so you can update the dataset periodically by just running `get_data.py`.

2. Preprocess all the data in the `raw/` directory:
```python
python -u process_data.py
```
This will select the English language subset of the corpus, clean up the files (removing headers and footers) and populate the `text/`, `tokens/` and `counts/` folders.

3. Divide the data into a few paragraph-long chunks and add the corresponding metadata info, save all the data in one big `jsonl` file, which we can then upload to Hugging Face:
```python
python -u create_dataset.py
```

