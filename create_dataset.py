import os
import csv
import jsonlines
import argparse
from datasets import load_dataset

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

def read_file(file_path, metadata, length_threshold):
    dataset = load_dataset("text", data_files=file_path, sample_by="paragraph")
    temp = ''
    all_data = []
    for d in dataset['train']:
        p = d['text']
        temp = temp + '\n' + p
        if len(temp) > length_threshold:
            temp_dict = {'text': temp}
            temp_dict.update(metadata)
            all_data.append(temp_dict)

            # reset
            temp = ''

    return all_data

def read_file_wholedoc(file_path, metadata):
    dataset = load_dataset("text", data_files=file_path, sample_by="document")
    for d in dataset['train']:
        data_dict = {'text': d['text']}
        data_dict.update(metadata)

    return data_dict

def read_directory(args):
    
    csv_data = read_metadata(args.metadata_file)

    all_data = []
    for filename in os.listdir(args.directory):
        if filename.endswith(".txt"):  # assuming you are processing text files
            file_id = filename.split('_')[0]  # assuming the file name is in the format "id_text.txt"
            if file_id in csv_data:
                metadata = csv_data[file_id]
                if args.wholedoc:
                    data = read_file_wholedoc(os.path.join(args.directory, filename), metadata)
                    all_data.append(data)
                else:
                    data = read_file(os.path.join(args.directory, filename), metadata, args.length_threshold)
                    all_data.extend(data)
                print(f"File: {filename}")
            else:
                print(f"No entry found for ID {file_id} in the CSV file.\n")

    return all_data

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Creating a dataset from processed Gutenberg texts.")
    parser.add_argument("--data_dir", help="Path to text data", default='data/text', type=str)
    parser.add_argument("--metadata_file", help="Path to metadata file", default='metadata/metadata.csv', type=str)
    parser.add_argument('--length_threshold', help="Length threshold to use when chunking texts (number of characters)", default=1024, type=int)
    parser.add_argument('--wholedoc', action='store_true', help="Whether to use whole documents instead of chunking texts into equal length units (default: false)")

    args = parser.parse_args()
    print(f"Args: {args}")
    
    all_data = read_directory(args)
    print(f"all_data length (number of records in dataset): {len(all_data)}")

    # write to jsonl file
    output_filename = f"gutenberg_en_wholedoc.jsonl" if args.wholedoc == True else f"gutenberg_en_paragraph_{args.length_threshold}.jsonl"
    with jsonlines.open(f"gutenberg_en_paragraph_{args.length_threshold}.jsonl", mode='w') as writer:
        writer.write_all(all_data)