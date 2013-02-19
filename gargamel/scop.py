# scop.py - utility functions and classes for reading SCOP classification files
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

"""Provides functions for reading from SCOP classification files, at a higher
level than the functionality provided by BioPython.

"""

from util import require_python_version
from logger import logger
require_python_version(2, 7)

from Bio.SCOP.Cla import parse as cla_parse

# SCOP classification file format is at
# http://scop.mrc-lmb.cam.ac.uk/scop/release-notes.html#scop-parseable-files
#
# first column - SCOP identifier, "sid"
# second column - PDB identifier
# third column - domain definition
# fourth column - SCCS
# fifth column - SUNID for that domain
# sixth column - list of SUNIDs for that domain: class (cl), fold (cf),
#                superfamily(sf), family (fa), protein domain (dm),
#                species (sp), and domain entry (px)
SCOP_CLASSIFICATION_FILE = '/r/bcb/protein_structure/SCOP/scop_cla'

class Keys:
    """The keys for SUNIDs in the SCOP Classification hierarchy."""
    CLASS = 'cl'
    FOLD = 'cf'
    SUPERFAMILY = 'sf'
    FAMILY = 'fa'
    DOMAIN = 'dm'
    SPECIES = 'sp'
    ENTRY = 'px'
    # TODO is this the right order?
    order = [CLASS, FOLD, SUPERFAMILY, FAMILY, DOMAIN, SPECIES, ENTRY]


def all_pdbids_from_file(filename):
    """Returns a set of all PDB ID:chains in the specified SCOP class file.

    """
    with open(filename, 'r') as f:
        res = set()
        for record in cla_parse(f):
          if record.residues.fragments and record.residues.fragments[0]:
            res.add(record.residues.pdbid + ':' + record.residues.fragments[0][0])
        return res
      
        # return set((record.residues.pdbid + ':' + record.residues.fragments[0][0] ) for record in cla_parse(f) if record.residues.fragments[0])

def all_pdbids_from_file_in(filename, target_key, target_value):
    """Returns a set of all PDB ID:chainss in the specified SCOP classification file
    in the hierarchy at the specified level (target_key) and with the specified
    SCOP unique identifying number (target_value).

    target_key should be one of the members of the Keys class.

    """
    pdbids = set(())
    with open(filename, 'r') as f:
        # iterate over each record in the SCOP Classification file
        for record in cla_parse(f):

            # iterate over each key/value pair in that record's hierarchy
            for key, value in record.hierarchy:

                # if this record is of the correct level of the hierarchy
                if key == target_key and value == target_value and record.residues.fragments and record.residues.fragments[0]:
                    pdbids.add(record.residues.pdbid + ':' + record.residues.fragments[0][0])
    return pdbids

# TODO I have submitted to BioPython a patch which changes each Record's
# hierarchy member from a list to a dictionary so that we don't have to iterate
# over the entire list just to find the hierarchy member we want
def hierarchy_sets_from_file(filename, target_key, target_value):
    """Reads PDB ids from the specified SCOP classification file and returns a
    map from elements of the hierarchy level beneath the specified target key
    to a set containing (PDB ID, chain) tupless of all proteins described by 
    that hierarchy classification.

    For example, if target_key is Keys.SUPERFAMILY and target_value is 50156
    (the PDZ domain superfamily), this function returns a map from family IDs
    to sets of all protein PDB IDs which are in that family.

    """
    
    # TODO change this to return the specific chain:range_start-range_end
    # instead of the 'to' in the map being PDB IDs, it should be to (maybe) pdbCHAIN:start-end
    # FOR NOW this returns a tuple of pdbid,chain (chain may be None)
    
    
    result = {}
    logger.debug("opening " + filename + " in hierarchy_sets_from_file. target: " + target_key + ':' + str(target_value))
    with open(filename, 'r') as hierarchy_file:

        try:
            if Keys.order.index(target_key) == len(Keys.order):
                raise Error('Cannot get sets for lowest level of hierarchy')
        except ValueError:
            raise ValueError('Key "' + str(target_key) + '" is not a ' + \
                             'known hierarchy key')

        # iterate over each record in the SCOP Classification file
        for record in cla_parse(hierarchy_file):

            # iterate over each key/value pair in that record's hierarchy
            for key, value in record.hierarchy:

                # if this record is of the correct level of the hierarchy
                if key == target_key and value == target_value:

                    # get the key for the next level down in the hierarchy
                    next_target_key = Keys.order[Keys.order.index(key) + 1]

                    # iterate over the record's hierarchy AGAIN
                    for key2, value2 in record.hierarchy:

                        # if we are looking at the next target key
                        if key2 == next_target_key:

                            # add this record's pdbid
                            # and chain to the result dictionary
                            # we get the fragments (residues.fragments)
                            # and add pdbid + fragments[0]
                            if record.residues.fragments:
                              # we have a fragment, use first chain
                              newfrag = str(record.residues.fragments[0][0])
                            else:
                              newfrag = None
                            newval = (str(record.residues.pdbid), newfrag)
                            if value2 in result:
                                result[value2].add(newval)
                                  
                            else:
                                result[value2] = set(())
                                result[value2].add(newval)

    return result
