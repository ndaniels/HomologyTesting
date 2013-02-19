# nrpdb.py - functions for reading from a non-redundant PDB database file
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

"""Provides functions for reading from a non-redundant PDB database file.

"""

from util import require_python_version
require_python_version(2, 7)

from logger import logger

# the path to the NRPDB file
NRPDB_FILENAME = '/r/bcb/protein_structure/NRPDB/nrpdb'

class RepresentativeFields:
    """The columns in the NRPDB file at which the representative flag for each
    set of chains.

    """
    NONIDENT = 'nonident'
    BLAST80 = 'blast80'
    BLAST40 = 'blast40'
    BLAST7 = 'blast7'
    ALL_REPS = [NONIDENT, BLAST80, BLAST40, BLAST7]
    REPFIELDS = {NONIDENT : 14, BLAST80 : 11, BLAST40 : 8, BLAST7 : 5}
    GROUPFIELDS = {NONIDENT : 12, BLAST80 : 9, BLAST40 : 6, BLAST7 : 3}


def nrpdbs_from_file(filename, rep_type=None):
    # this is the wrong spec. It should simply return the representative
    # pdb-chain for a given pdb-chain and rep-type.
    
    # we actually want two functions: give ALL the reps for a level, or
    # give a mapping from pdb:chain to representative pdb:chain
  
  
    """Reads NRPDBs from the specified file, returning a mapping from PDB ID and
    chain to a representative pdb ID and chain.

    If rep_type is provided, only representatives of the specified
    non-redundant set will be returned. Possible values for rep_type are
    the members of the class RepresentativeFields. Any other value is ignored.

    """
    nrpdbs = {}
    groups = {}
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
                  
                if (rep_type and rep_type in RepresentativeFields.GROUPFIELDS):
                  group_id = fields[RepresentativeFields.GROUPFIELDS[rep_type]]
                else:
                  group_id = None
                
                # if rep_type is None or \
                #        (rep_type in RepresentativeFields.REPFIELDS and
                #         int(fields[RepresentativeFields.REPFIELDS[rep_type]]) \
                #         == 1):

                # get the pdbid and chain letter of this protein
                pdbid, chain = fields[:2]
                

                # ensure pdbid is lowercase, chain is uppercase
                pdbid = pdbid.lower()
                chain = chain.upper()
                full_pdbid = pdbid + ':' + chain
                
                if group_id and group_id in groups:
                  groups[group_id].add((full_pdbid, is_rep))
                else:
                  groups[group_id] = set(((full_pdbid, is_rep), ))
                  
                # 
                #   
                # # add or update the set of chains
                # if full_pdbid in nrpdbs:
                #     nrpdbs[full_pdbid].add((chain, is_rep))
                # else:
                #     nrpdbs[full_pdbid] = set(((chain, is_rep), ))

            except ValueError:
                logger.warning('Incorrectly formatted NRPDB line ' + line)
                
    # now for each group, we want to add a mapping for each pdb:chain to its rep
    
    for group_id in groups.keys():
      
      redundant_entries = set()
      for nrpdb_entry in groups[group_id]:
        if nrpdb_entry[1]:
          rep = nrpdb_entry[0]
          redundant_entries.add(rep)
        else:
          redundant_entries.add(nrpdb_entry[0])
      
      for redundant_entry in redundant_entries:
        nrpdbs[redundant_entry] = rep
    
    return nrpdbs
