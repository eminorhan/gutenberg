import os
import csv
import jsonlines
from datasets import load_dataset

LENGTH_THRESHOLD = 1024

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
                'type': row['type']
            }
    return data

def read_file(file_path, metadata):
    dataset = load_dataset("text", data_files=file_path, sample_by="paragraph")
    temp = ''
    all_data = []
    for d in dataset['train']:
        p = d['text']
        temp = temp + '\n' + p
        if len(temp) > LENGTH_THRESHOLD:
            temp_dict = {'text': temp}
            temp_dict.update(metadata)
            all_data.append(temp_dict)

            # reset
            temp = ''

    return all_data

def read_directory(directory, csv_data):
    all_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):  # assuming you are processing text files
            file_id = filename.split('_')[0]  # assuming the file name is in the format "id_text.txt"
            if file_id in csv_data:
                metadata = csv_data[file_id]
                data = read_file(os.path.join(directory, filename), metadata)
                all_data.extend(data)
                print(f"File: {filename}")
            else:
                print(f"No entry found for ID {file_id} in the CSV file.\n")

    return all_data

if __name__ == "__main__":

    data_directory = 'data/text'
    csv_data = read_metadata("metadata/metadata.csv")
    all_data = read_directory(data_directory, csv_data)
    print(f"all_data length: {len(all_data)}")

    # write to jsonl file
    with jsonlines.open(f"gutenberg_en_paragraph_{LENGTH_THRESHOLD}.jsonl", mode='w') as writer:
        writer.write_all(all_data)