"""Export Module"""

import csv
import io
import logging
import zipfile
import bpy
import pam

logger = logging.getLogger(__package__)


def export_connections(filepath):
    """ export connection and distance-informations
    cmatrices           : list of connection matrices
    dmatrices           : list of distance matrices
    nglist              : list of neural groups
    connection_list     : list of layer-based connections
    """
    
    cmatrices = []
    dmatrices = []
    for c in pam.pam_connection_results:
        cmatrices.append(c['c'])
        dmatrices.append(c['d'])
    
    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as file:
        csv_write_matrices(file, "c", cmatrices)
        csv_write_matrices(file, "d", dmatrices)
        csv_write_matrix(file, "connections", pam.pam_connection_indices)
        csv_write_matrix(file, "neurongroups", pam.pam_ng_list)


def export_UVfactors(filepath, uv_matrices, layer_names):
    """ list of UV-matrices, including the length of a real edge an its
    UV-distance

    uv_matrices         : list of uv-matrices
    layer_names         : list of layer-names, the order corresponds to the
                          list-order in uv_matrices
    """
    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as file:
        for i, matrix in enumerate(uv_matrices):
            csv_write_matrix(file, layer_names[i], [matrix])


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
