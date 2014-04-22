"""Import Module"""

import csv
import io
import logging
import os
import zipfile

logger = logging.getLogger(__package__)


def import_zip(filepath):
    matrices = SUPPORTED_SUFFIXES

    with zipfile.ZipFile(filepath, "r", zipfile.ZIP_DEFLATED) as file:
        for filename in file.namelist():
            filename_split = os.path.splitext(filename)
            filename_suffix = ''.join(filename_split[:-1]).rsplit("_", 1)[-1]
            filename_extension = filename_split[-1]

            print filename_suffix

            if filename_extension not in SUPPORTED_FILETYPES.keys():
                logger.error("filetype not supported")
                raise Exception("filetype not supported")

            if filename_suffix not in SUPPORTED_SUFFIXES.keys():
                logger.error("unknown suffix")
                raise Exception("unknown suffix")

            data = io.StringIO(unicode(file.read(filename)))
            func = SUPPORTED_FILETYPES[filename_extension]

            matrices[filename_suffix].append(func(data))

    return matrices


def csv_read(data):
    reader = csv.reader(
        data,
        delimiter=";",
        quoting=csv.QUOTE_NONNUMERIC
    )
    return [row for row in reader]


SUPPORTED_FILETYPES = {
    ".csv": csv_read
}

SUPPORTED_SUFFIXES = {
    "d": [],
    "c": []
}


if __name__ == "__main__":
    print("Hello World")
    #print import_zip("./test.zip")
