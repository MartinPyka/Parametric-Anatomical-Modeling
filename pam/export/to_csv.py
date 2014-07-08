"""Export Module"""

import csv
import io
import logging
import zipfile

import bpy

from .. import model

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
    for c in model.CONNECTION_RESULTS:
        cmatrices.append(c['c'])
        dmatrices.append(c['d'])

    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as file:
        csv_write_matrices(file, "c", cmatrices)
        csv_write_matrices(file, "d", dmatrices)
        csv_write_matrix(file, "connections", model.CONNECTION_INDICES)
        csv_write_matrix(file, "neurongroups", model.NG_LIST)


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


# TODO(SK): missing docstring
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


# TODO(SK): missing docstring
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
