# fasta.py - functions for reading from and writing to files in FASTA format
# Copyright 2010 Jeffrey Finkelstein
#
# This file is part of smurf.
#
# smurf is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# smurf is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# smurf.  If not, see <http://www.gnu.org/licenses/>.

"""Provides functions for reading from and writing to files in FASTA format.

"""

from util import require_python_version
require_python_version(2, 7)

import gzip

# the FASTA file containing all protein sequences, along with their PDB IDs
FASTA_FILENAME = '/r/bcb/protein_structure/pdb_seqres.fasta.gz'

def sequences_from_file(filename):
    """Read the specified file containing multiple sequences in FASTA format
    and return a map from PDB ID to tuple containing the header line and the
    sequence line of that protein.

    """
    # determine the command which opens the FASTA file (gzip.open or open)
    open_cmd = (open, gzip.open)[filename[-3:] == '.gz']

    sequences = {}
    with open_cmd(filename, 'r') as f:

        # get the header line and the sequence
        header = f.readline()
        sequence = f.readline()

        while not header == '':
            # this can happen when there are FASTA entries for A, B, C,
            # etc. chains. However, the sequences seem to be identical.
            # TODO check that the sequences in the FASTA file are identical
            id = header[1:5]
            if id not in sequences:
                sequences[id] = (header, sequence)

            header = f.readline()
            sequence = f.readline()

    return sequences
