# whitelist.py - functions for reading from/writing to a whitelist
# Copyright 2010 Jeffrey Finkelstein
#
# This file is part of smurf.
#
# smurf is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# smurf is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# smurf.  If not, see <http://www.gnu.org/licenses/>.

"""Provides functions for reading from/writing to a whitelist of protein chains
to explicitly include when generating matt, hmmer, or smurf command lines.

"""

from util import require_python_version
require_python_version(2, 7)

from logger import logger

# the name of the file containing the whitelist of protein chains
WHITELIST_FILENAME = 'whitelist'

def whitelist_from_file(filename):
    """ Reads a whitelist from the specified file and returns a mapping from
    PDB ID to chains in the whitelist.

    """
    whitelist = {}
    with open(filename, 'r') as whitelist_file:

        # iterate over each entry in the whitelist, which is a PDB ID, followed
        # by a colon, followed by one or more chain IDs (like A, B, C, etc.)
        # separated by commas to include for training
        for line in whitelist_file:
            line = line.strip()
            try:
                # skip blank lines and comments
                if len(line) == 0 or line[0] == '#':
                    continue

                # get the pdbid and the chain ids from the line
                pdbid, chains = line.split(':')

                # ensure pdbid is lowercase, chains are uppercase
                pdbid = pdbid.lower()
                chains = chains.upper()

                # update or create a new set containing each chain id
                if pdbid in whitelist:
                    whitelist[pdbid].update((chain_id for chain_id in chains))
                else:
                    whitelist[pdbid] = set((chain_id for chain_id in chains))
            except ValueError:
                logger.warning('Incorrectly formatted whitelist line: ' + line)

    return whitelist
