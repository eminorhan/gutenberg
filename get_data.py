"""
Project Gutenberg parsing

Written by M. Gerlach & F. Font-Clos

Modified by Emin Orhan
"""
from src.utils import populate_raw_from_mirror, list_duplicates_in_mirror
from src.metadataparser import make_df_metadata
from src.bookshelves import parse_bookshelves

import argparse
import os
import subprocess
import pickle

if __name__ == '__main__':

    parser = argparse.ArgumentParser("Update local PG repository. This script will download all books currently not in your local copy of PG and get the latest version of the metadata.")
    parser.add_argument("--mirror", help="Path to the mirror folder that will be updated via rsync", default='data/.mirror/', type=str)
    parser.add_argument("--raw", help="Path to the raw folder", default='data/raw/', type=str)
    parser.add_argument("--metadata", help="Path to the metadata folder", default='metadata/', type=str)
    parser.add_argument("--pattern", help="Patterns to get only a subset of books", default='*', type=str)
    parser.add_argument("--keep_rdf", action="store_false", help="If there is an RDF file in metadata dir, do not overwrite it")
    parser.add_argument("--overwrite_raw", action="store_true", help="Overwrite files in raw")
    parser.add_argument("--quiet", action="store_true", help="Quiet mode, do not print info, warnings, etc")

    args = parser.parse_args()
    print("Args:", args)

    # check that all dirs exist
    if not os.path.isdir(args.mirror):
        raise ValueError("The specified mirror directory does not exist.")
    if not os.path.isdir(args.raw):
        raise ValueError("The specified raw directory does not exist.")
    if not os.path.isdir(args.metadata):
        raise ValueError("The specified metadata directory does not exist.")

    # Update the .mirror directory via rsync
    # --------------------------------------
    # We sync the 'mirror_dir' with PG's site via rsync
    # The matching pattern, explained below, should match
    # only UTF-8 files.

    # pass the -v flag to rsync if not in quiet mode
    if args.quiet:
        vstring = ""
    else:
        vstring = "v"

    # Pattern to match the +  but not the - :
    #
    # + 12345 .   t   x  t .            utf  8
    # - 12345 .   t   x  t .      utf8 .gzi  p
    # + 12345 -   0   .  t x                 t 
    #---------------------------------------------
    #        [.-][t0][x.]t[x.]    *         [t8]
    sp_args = ["rsync", f"-am{vstring}",
               "--include", "*/",
               "--include", f"[p123456789][g0123456789]{args.pattern}[.-][t0][x.]t[x.]*[t8]",
               "--exclude", "*",
               "aleph.gutenberg.org::gutenberg", args.mirror
               ]
    subprocess.call(sp_args)

    # Get rid of duplicates
    # ---------------------
    # A very small portion of books are stored more than
    # once in PG's site. We keep the newest one, see
    # erase_duplicates_in_mirror docstring.
    dups_list = list_duplicates_in_mirror(mirror_dir=args.mirror)

    # Populate raw from mirror
    # ------------------------
    # We populate 'raw_dir' hardlinking to
    # the hidden 'mirror_dir'. Names are standarized
    # into PG12345_raw.txt format.
    populate_raw_from_mirror(
        mirror_dir=args.mirror,
        raw_dir=args.raw,
        overwrite=args.overwrite_raw,
        dups_list=dups_list,
        quiet=args.quiet
        )

    # Update metadata
    # ---------------
    # By default, update the whole metadata csv
    # file each time new data is downloaded.
    make_df_metadata(
        path_xml=os.path.join(args.metadata, 'rdf-files.tar.bz2'),
        path_out=os.path.join(args.metadata, 'metadata.csv'),
        update=args.keep_rdf
        )

    # Bookshelves
    # -----------
    # Get bookshelves and their respective books and titles as dicts
    BS_dict, BS_num_to_category_str_dict = parse_bookshelves()
    with open("metadata/bookshelves_ebooks_dict.pkl", 'wb') as fp:
        pickle.dump(BS_dict, fp)
    with open("metadata/bookshelves_categories_dict.pkl", 'wb') as fp:
        pickle.dump(BS_num_to_category_str_dict, fp)