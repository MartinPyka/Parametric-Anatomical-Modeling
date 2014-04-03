"""Export Module"""

import csv
import io
import logging
import zipfile
import bpy

logger = logging.getLogger(__package__)

def export_zip(filepath, cmatrices, dmatrices, ng_list, connection_list):
    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as file:
       csv_write_matrices(file, "c", cmatrices)
       csv_write_matrices(file, "d", dmatrices)
       csv_write_matrix(file, "connections", connection_list)
       csv_write_matrix(file, "neurongroups", ng_list)


def csv_write_matrix(file, name, matrix):
    output = io.StringIO()
    writer = csv.writer(
        output,
        delimiter=";",
        quoting=csv.QUOTE_NONNUMERIC
    )
    for row in matrix:
        writer.writerow(row)
    file.writestr("%s.csv" % (name), output.getvalue())

    

def csv_write_matrices(file, suffix, matrices):
    for i, matrix in enumerate(matrices):
        output = io.StringIO()
        writer = csv.writer(
            output,
            delimiter=";",
            quoting=csv.QUOTE_NONNUMERIC
        )
        for row in matrix:
            writer.writerow(row)
        file.writestr("%i_%s.csv" % (i, suffix), output.getvalue())


if __name__ == "__main__":
    c = []
    d = []

    matrix = [[1, 2, 3, 4]]

    c.append(matrix)
    d.append(matrix)

    matrix.append([3, 4, 5, 6])

    c.append(matrix)

    export_zip("test.zip", c, d)
