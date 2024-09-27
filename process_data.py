"""
Process counts for all PG data.

Written by
M. Gerlach and F. Font-Clos

Modified by Emin Orhan
"""
import os
from os.path import join
import argparse
import glob
import ast
import pandas as pd

from src.pipeline import process_book
from src.utils import get_langs_dict


if __name__ == '__main__':

    parser = argparse.ArgumentParser("Processing raw texts from Project Gutenberg: i) removing headers, ii) tokenizing, and iii) counting words.")
    parser.add_argument("--raw", help="Path to the raw-folder", default='data/raw/', type=str)
    parser.add_argument("--output_text", help="Path to text-output (text_dir)", default='data/text/', type=str)
    parser.add_argument("--output_tokens", help="Path to tokens-output (tokens_dir)", default='data/tokens/', type=str)
    parser.add_argument("--output_counts", help="Path to counts-output (counts_dir)", default='data/counts/', type=str)
    parser.add_argument("--pattern", help="Patttern to specify a subset of books", default='*', type=str)
    parser.add_argument("--quiet", action="store_true", help="Quiet mode, do not print info, warnings, etc")
    parser.add_argument("--overwrite", action="store_true", help="Whether to overwrite any existing processed files")
    parser.add_argument("--log_file", help="Path to log file", default=".log", type=str)

    args = parser.parse_args()
    print("Args:", args)

    # check whether the output directories exist
    if os.path.isdir(args.output_text) is False:
        raise ValueError(f"The directory for output of texts {args.output_text} does not exist")
    if os.path.isdir(args.output_tokens) is False:
        raise ValueError(f"The directory for output of tokens {args.output_tokens} does not exist")
    if os.path.isdir(args.output_counts) is False:
        raise ValueError(f"The directory for output of counts {args.output_counts} does not exist")

    # load metadata
    metadata = pd.read_csv("metadata/metadata.csv").set_index("id")

    # load languages dict
    langs_dict = get_langs_dict()

    # loop over all books in the raw-folder
    cbooks = 0  # completed books counter
    pbooks = 0  # processed books counter
    for filename in glob.glob(join(args.raw, f"PG{args.pattern}_raw.txt")):
        # The process_books function will fail very rarely, when
        # a file tagged as UTf-8 is not really UTF-8. We skip those books.
        try:
            # get PG_id
            PG_id = filename.split("/")[-1].split("_")[0]

            # language is a string representing a list of languages codes
            lang_id = ast.literal_eval(metadata.loc[PG_id, "language"])[0]

            # only process English books
            if lang_id == 'en':
                # process the book: strip headers, tokenize, count
                process_book(
                    path_to_raw_file=filename,
                    text_dir=args.output_text,
                    tokens_dir=args.output_tokens,
                    counts_dir=args.output_counts,
                    overwrite_all=args.overwrite,
                    language="english",
                    log_file=args.log_file
                )
                print(f"Processed book {PG_id}")
                pbooks += 1
            else:
                print(f"Skipping book {PG_id} because it is not in English")

            cbooks += 1
            if not args.quiet:
                print(f"Gone over {cbooks} books, processed {pbooks} of them")
        except UnicodeDecodeError:
            if not args.quiet:
                print(f"# WARNING: cannot process {filename} (encoding not UTF-8)")
        except KeyError:
            if not args.quiet:
                print(f"# WARNING: metadata for {filename} not found")
        except Exception as e:
            if not args.quiet:
                print(f"# WARNING: cannot process {filename} (unkown error)")