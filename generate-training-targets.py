#!/usr/bin/env python
#
# generate-matt-alignments.py - generates matt alignments of members of a
# level of the SCOP hierarchy, leaving out one lower lever each time
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

from gargamel.util import require_python_version
require_python_version(2, 7)

import os
import os.path
import subprocess
import sys

from gargamel.argumentparsers import SuperfamilyArgumentParser
from gargamel.argumentparsers import DEFAULT_REP_ARG
from gargamel.constants import MATT_PREFIX
from gargamel.logger import logger
from gargamel.nrpdb import NRPDB_FILENAME
from gargamel.nrpdb import RepresentativeFields
from gargamel.nrpdb import nrpdbs_from_file
from gargamel.scop import Keys
from gargamel.scop import SCOP_CLASSIFICATION_FILE
from gargamel.scop import hierarchy_sets_from_file
#from gargamel.whitelist import WHITELIST_FILENAME
#from gargamel.whitelist import whitelist_from_file

# a brief description of the purpose of this program
PROGRAM_DESCRIPTION = ('Generates multiple alignment targets by leaving '
                       'one lower hierarchy level out of a target hierarchy '
                       'level in turn.')

# the filename to which to write the list of PDB files to align
PDBLIST_FILENAME = 'training_list'


def to_pdb_filename(pdb_dir, pdbid):
    """Generates a string containing a filename constructed from the specified
    PDB id.

    For example, if the pdbid is '11ba', then the returned string will be
    something like '<pdb_dir>/1b/pdb11ba.ent.gz'. We expect that all PDB files
    look like this example, and are all gzipped files.

    """
    pdbid = str(pdbid)
    if len(pdbid) != 4:
        raise ValueError('PDB ID must be a string of length 4, but was length '
                         + len(pdbid))
    return os.path.join(pdb_dir, pdbid[1:3], 'pdb' + pdbid + '.ent.gz')

# create a parser for command-line arguments, with a description of the purpose
# of this program
argparser = SuperfamilyArgumentParser(PROGRAM_DESCRIPTION)

# parsed_args = argparser.parse_args()
parsed_args = argparser.parse_args()

# get the values from the command-line arguments
output_dir = parsed_args.outputdir.rstrip('/')  # remove trailing slash
target_level = parsed_args.target_level
target_sunid = parsed_args.target_sunid
representative_field = parsed_args.repfield

# determine the amount of logging info to output
if parsed_args.verbose:
    from logging import DEBUG
    from gargamel.logger import console_handler
    console_handler.setLevel(DEBUG)

# summary of the program configuration
config = {'output_dir' : output_dir,
          'representative_field' : representative_field,
          'target_level' : target_level,
          'target_sunid' : target_sunid}
logger.debug('Program configuration: ' + str(config))

# get the set of non-redundant PDB chains from the NRPDB file, and use only
# these chains for training

nrpdbs = nrpdbs_from_file(NRPDB_FILENAME, representative_field)

# get all the records from the SCOP classification file
logger.debug('Getting PDB IDs from SCOP Classification file...')
hierarchy = hierarchy_sets_from_file(SCOP_CLASSIFICATION_FILE, target_level,
                                     target_sunid)
logger.debug('hierarchy: ' + str(hierarchy))
if len(hierarchy) == 0:
    logger.critical('Nothing in hierarchy for target level: ' + str(target_level) + ' and target_sunid: ' + str(target_sunid))
    sys.exit(1)

# create the whitelist of PDB chains on which to train explicitly
#logger.debug('Getting the whitelist of chains to test...')
#whitelist = whitelist_from_file(WHITELIST_FILENAME)

# create the output directory if it doesn't exist
logger.debug('Checking whether output directory exists...')
if not os.path.isdir(output_dir):
    logger.debug('...it doesn\'t so we create it')
    os.mkdir(output_dir)

# generate the names of each of the PDB files on which to train
logger.debug('Generating filenames...')
num_chains = 0
pdb_names = {}

used_pdbids = set()

# TODO should get more specific sequences (including chain and range) and pull those appropriately.


for hierarchy_level_sunid, pdbids in hierarchy.iteritems():
    for pdbid_tuple in pdbids:
        query_pdbid = ':'.join(pdbid_tuple)
        query_base_pdbid = pdbid_tuple[0]
        query_pdb_chain = pdbid_tuple[1]
        logger.debug('  PDB ID: ' + str(query_pdbid))
        # only add this pdb file if it is in the whitelist and is not already
        # represented by a redundant chain
        #if pdbid in whitelist and pdbid in nrpdbs:
        if query_pdbid in nrpdbs:
            pdbid = nrpdbs[query_pdbid]
            base_pdbid, pdb_chain = pdbid.split(':')
            
            if pdbid in used_pdbids:
              # logger.debug(pdbid + ' already used!')
              continue # if we've already added this chain, skip
            

            
            used_pdbids.add(pdbid)
                # generate the filename of this pdb file plus its chain
            pdbname = base_pdbid + ':' + pdb_chain
            # add that filename to the set of pdb filenames (plus chains)
            if hierarchy_level_sunid in pdb_names:
                logger.debug('    adding to set for current hierarchy '
                             'level sunid')
                logger.debug('   which is ' + str(hierarchy_level_sunid))
                pdb_names[hierarchy_level_sunid].add(pdbname)
            else:
                logger.debug('    creating set for current hierarchy '
                             'level sunid')
                pdb_names[hierarchy_level_sunid] = set((pdbname, ))

# determine which pdb filenames are to be used for consensus alignment for each
# hierarchy level sunid to be left out
logger.debug('Determining pdb filenames for each hierarchy level sunid to be'
             'left out...')
all_others = {}
for hierarchy_level_sunid in pdb_names:
    logger.debug('  current hierarchy level sunid: '
                 + str(hierarchy_level_sunid))
    for hierarchy_level_sunid2, filenames2 in pdb_names.iteritems():
        logger.debug('    hierarchy level sunid 2: '
                     + str(hierarchy_level_sunid2))
        if hierarchy_level_sunid != hierarchy_level_sunid2:
            logger.debug('      does not equal current hierarchy_level_sunid')
            if hierarchy_level_sunid in all_others:
                logger.debug('      adding to set for current'
                             ' hierarchy_level_sunid')
                all_others[hierarchy_level_sunid].update(filenames2)
            else:
                logger.debug('      creating set for current hierarchy level '
                             'sunid')
                all_others[hierarchy_level_sunid] = set(filenames2)

# iterate over each hierarchy level sunid to query
logger.debug('Iterating over query hierarchy level sunid '
             + str(all_others.keys()))
for hierarchy_level_sunid, filenames in all_others.iteritems():

    logger.debug('Current hierarchy level sunid: '
                 + str(hierarchy_level_sunid))
    logger.debug('  contains ' + str(len(filenames)) + ' filenames:')
    for filename in filenames:
        logger.debug('    ' + filename)

    # create an output directory if it doesn't exist yet
    logger.debug('Checking whether hierarchy level sunid output directory'
                 ' exists...')
    level_output_dir = os.path.join(output_dir, str(hierarchy_level_sunid))
    if not os.path.isdir(level_output_dir):
        logger.debug('  it doesn\'t so we create it: ' + level_output_dir)
        os.mkdir(level_output_dir)

    # write the list of PDB files on which to train
    logger.debug('Writing list of PDB files on which to train...')
    pdblist_filename = os.path.join(level_output_dir, PDBLIST_FILENAME)
    limit = 100
    count = 0
    with open(pdblist_filename, 'w') as pdblist_file:
        for name in filenames:
            count += 1
            logger.debug('considering name: ' + name)
            if count > limit:
              logger.debug('SKIPPING!')
              continue
            logger.debug('writing')
            pdblist_file.write(name + '\n')
    logger.debug('  written to file ' + pdblist_filename)
