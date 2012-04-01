# pisces.py - functions for reading from a PISCES culldb database file
# Copyright 2010 Noah Daniels
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

"""Provides functions for reading from a PISCES culldb database file.

"""

from util import require_python_version
require_python_version(2, 7)

from logger import logger

# the path to the NRPDB file
NRPDB_FILENAME = '/r/bcb/protein_structure/pisces_culldb/FOO'

###########################################

def nrpdbs_from_file(filename, rep_type=None):
    """Reads NRPDBs from the specified file, returning a mapping from PDB ID to
    a set of (chain-is_rep) tuples.

    If rep_type is provided, only representatives of the specified
    non-redundant set will be returned. Possible values for rep_type are
    the members of the class RepresentativeFields. Any other value is ignored.

    """
    nrpdbs = {}
    with open(filename, 'r') as nrpdb_file:

        # iterate over each record in the NRPDB file
        for line in nrpdb_file:

            # strip leading and trailing whitespace
            line = line.strip()

            try:
                # skip blank lines and comments
                if len(line) == 0 or line[0] == '#':
                    continue

                # get all of the fields from the current record
                fields = line.split()
                
                # I THINK we want to always go into this loop, but flag
                # those proteins that are reps

                # if this protein is a representative (or we don't care)
                # (relies on short-circuiting or operator)
                if (rep_type and rep_type in RepresentativeFields.REPFIELDS \
                    and \
                    int(fields[RepresentativeFields.REPFIELDS[rep_type]]) == 1):
                  is_rep = True
                else:
                  is_rep = False
                  
                    
                
                # if rep_type is None or \
                #        (rep_type in RepresentativeFields.REPFIELDS and
                #         int(fields[RepresentativeFields.REPFIELDS[rep_type]]) \
                #         == 1):

                # get the pdbid and chain letter of this protein
                pdbid, chain = fields[:2]

                # ensure pdbid is lowercase, chain is uppercase
                pdbid = pdbid.lower()
                chain = chain.upper()

                # add or update the set of chains
                if pdbid in nrpdbs:
                    nrpdbs[pdbid].add((chain, is_rep))
                else:
                    nrpdbs[pdbid] = set(((chain, is_rep), ))

            except ValueError:
                logger.warning('Incorrectly formatted NRPDB line ' + line)

    return nrpdbs
