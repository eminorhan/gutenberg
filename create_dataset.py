import os
import csv
import argparse
import numpy as np
from datasets import load_dataset, Dataset

def read_metadata(csv_file):
    data = {}
    with open(csv_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data[row['id']] = {
                'title': row['title'],
                'author': row['author'],
                'author year of birth': row['authoryearofbirth'],
                'author year of death': row['authoryearofdeath'],
                'language': row['language'],
                'downloads': row['downloads'],
                'subjects': row['subjects'],
                'document id': row['id'],
                'type': row['type']
            }
    return data

def read_file(file_path, metadata, chunk_length):
    dataset = load_dataset("text", data_files=file_path, sample_by="paragraph")
    temp = ''
    all_data = []
    for d in dataset['train']:
        p = d['text']
        temp = temp + '\n' + p
        if len(temp) > chunk_length:
            temp_dict = {'text': temp}
            temp_dict.update(metadata)
            all_data.append(temp_dict)

            # reset
            temp = ''

    return all_data

def read_file_wholedoc(file_path, metadata):
    dataset = load_dataset("text", data_files=file_path, sample_by="document")
    assert len(dataset['train']) == 1, f"More than 1 document in file {file_path}!" 
    data_dict = {'text': dataset['train'][0]['text']}
    data_dict.update(metadata)

    return data_dict

def read_directory(args):
    
    csv_data = read_metadata(args.metadata_file)

    # all_data to hold the data, lens to hold the number of words in document when args.wholedoc is True
    all_data, lens = [], []

    for filename in os.listdir(args.data_dir):
        if filename.endswith(".txt"):  # assuming you are processing text files
            file_id = filename.split('_')[0]  # assuming the file name is in the format "id_text.txt"
            if file_id in csv_data:
                metadata = csv_data[file_id]
                if args.wholedoc:
                    data = read_file_wholedoc(os.path.join(args.data_dir, filename), metadata)
                    all_data.append(data)
                    lens.append(len(data['text'].split()))
                else:
                    data = read_file(os.path.join(args.data_dir, filename), metadata, args.chunk_length)
                    all_data.extend(data)
                print(f"File: {filename}")
            else:
                print(f"No entry found for ID {file_id} in the CSV file.\n")

    return all_data, np.array(lens)

def random_subset_gutenberg(ds, lens, target_length=1e7):
    
    # shuffle indices, pick the first n articles whose word count sum exceeds target length
    indices = np.random.permutation(len(ds))
    lens_shuffled_cumsum = np.cumsum(lens[indices])
    n = np.searchsorted(lens_shuffled_cumsum, target_length, side="left")
    selected_indices = indices[:n]
    val_indices = indices[n:(n+100)]

    # select subset with given indices
    ds_selected = list(np.array(ds)[selected_indices])
    ds_val = list(np.array(ds)[val_indices])

    print(f"========= Target length: {target_length} =========")
    print(f"Total number of documents selected: {n-1}")
    print(f"Total number of words: {lens_shuffled_cumsum[n-1]}")

    return ds_selected, ds_val

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Creating a dataset from processed Gutenberg texts.")
    parser.add_argument("--data_dir", help="Path to text data", default='data/text', type=str)
    parser.add_argument("--metadata_file", help="Path to metadata file", default='metadata/metadata.csv', type=str)
    parser.add_argument('--chunk_length', help="Chunk length to use when chunking texts (number of characters)", default=1024, type=int)
    parser.add_argument('--wholedoc', action='store_true', help="Whether to save whole documents instead of chunking texts into equal length units (default: false)")

    args = parser.parse_args()
    print(f"Args: {args}")
    
    ds, lens = read_directory(args)
    print(f"Total number of records in dataset: {len(ds)}")
    if args.wholedoc:
        ds_10M, ds_10M_val = random_subset_gutenberg(ds, lens, target_length=1e7)  # 10M word subset
        ds_100M, ds_100M_val = random_subset_gutenberg(ds, lens, target_length=1e8)  # 100M word subset

    ds = Dataset.from_list(ds)
    print("Generated dataset ds")
    ds_10M = Dataset.from_list(ds_10M)
    ds_10M_val = Dataset.from_list(ds_10M_val)
    print("Generated dataset ds_10M")
    ds_100M = Dataset.from_list(ds_100M)
    ds_100M_val = Dataset.from_list(ds_100M_val)
    print("Generated dataset ds_100M")

    # push subset to hub
    ds.push_to_hub("eminorhan/gutenberg_en_sep24", "all", split="train", token=True)
    ds_10M.push_to_hub("eminorhan/gutenberg_en_sep24", "10M", split="train", token=True)
    ds_10M_val.push_to_hub("eminorhan/gutenberg_en_sep24", "10M", split="validation", token=True)
    ds_100M.push_to_hub("eminorhan/gutenberg_en_sep24", "100M", split="train", token=True)
    ds_100M_val.push_to_hub("eminorhan/gutenberg_en_sep24", "100M", split="validation", token=True)