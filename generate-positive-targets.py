#!/usr/bin/env python
#
# generate-positive-controls.py - run a structural aligner on chains not
# aligned by matt
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

from gargamel.argumentparsers import SuperfamilyArgumentParser
from gargamel.argumentparsers import DEFAULT_REP_ARG

from gargamel.constants import POSITIVE_DIRNAME

from gargamel.constants import TMP_DIR

from gargamel.fasta import FASTA_FILENAME
from gargamel.fasta import sequences_from_file
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
PROGRAM_DESCRIPTION = ('Produces list of query proteins in a given target '
                       'SCOP hierarchy level not already used to generate HMM '
                       'files')



# create a parser for command-line arguments, with a description of the purpose
# of this program
argparser = SuperfamilyArgumentParser(PROGRAM_DESCRIPTION)

# parse the command-line arguments
parsed_args = argparser.parse_args()

# get the values from the command-line arguments
output_dir = parsed_args.outputdir.rstrip('/')  # remove trailing slash
target_level = parsed_args.target_level
target_sunid = parsed_args.target_sunid
representative_field = parsed_args.repfield

output_filename = 'positive_controls'

# determine the amount of logging info to output
if parsed_args.verbose:
    from logging import DEBUG
    from gargamel.logger import console_handler
    console_handler.setLevel(DEBUG)

# configuration summary
config = {'target_level' : target_level,
          'target_sunid' : target_sunid,
          'output_dir' : output_dir,
          'representative_field' : representative_field}
logger.debug('Program configuration: ' + str(config))



# get the set of non-redundant PDB chains from the NRPDB file

logger.debug('Getting non-redundant set of PDB chains...')
nrpdbs = nrpdbs_from_file(NRPDB_FILENAME, representative_field)

# logger.debug('nrpdbs: ' + str(nrpdbs))

# get all the records from the SCOP classification file
# this now has (pdbid,chain) tuples
logger.debug('Getting records to test from SCOP Classification file...')
hierarchy = hierarchy_sets_from_file(SCOP_CLASSIFICATION_FILE, target_level,
                                     target_sunid)
logger.debug('hierarchy: ' + str(hierarchy))

# create the whitelist of PDB chains on which to train explicitly
#logger.debug('Getting the whitelist of chains to test...')
#whitelist = whitelist_from_file(WHITELIST_FILENAME)

# end the program if the output dir doesn't exist
logger.debug('Checking whether output directory exists...')
if not os.path.isdir(output_dir):
    logger.critical('Output directory ' + output_dir + ' does not yet exist')
    logger.critical('Please run generate-training-targets.py first')
    sys.exit(2)

# iterate over each hierarchy level to query
logger.debug('Iterating over query families ' + str(hierarchy))

used_pdbids = set()
pdb_names = {}

# FIXME pdbids must be replaced with a set of (pdbid,chain) tuples
for sunid, pdbid_tuples in hierarchy.iteritems():

    # create a directory for the positive control queries, if it doesn't exist
    logger.debug('Checking whether directory for positive controls exists...')
    level_output_dir = os.path.join(output_dir, str(sunid))
    positive_dir = level_output_dir
    if not os.path.isdir(positive_dir):
        os.makedirs(positive_dir)
        logger.debug('  it doesn\'t, so we created it at ' + positive_dir)

    i = 1
    
    # pdbids is the set of all pdbids in this subtree of the hierarchy
    for pdbid_tuple in pdbid_tuples:
        orig_pdbid, orig_pdbchain = pdbid_tuple

        logger.debug('query PDB id: ' + str(orig_pdbid))
        logger.debug('query number ' + str(i) + ' out of ' + \
                      str(len(pdbid_tuples)) + ' in hierarchy level with sunid ' + \
                      str(sunid))
        
        query_id = orig_pdbid + ':' + orig_pdbchain
        
        if query_id not in nrpdbs:
          continue
        
        full_pdbid = nrpdbs[query_id]
        
        temp_pdb_tuple = full_pdbid.split(':')
        
        pdbid = temp_pdb_tuple[0]
        pdbchain = temp_pdb_tuple[1]
        
        ##
        if sunid in pdb_names:
           
            pdb_names[sunid].add(full_pdbid)
        else:
            logger.debug('    creating set for current hierarchy '
                         'level sunid')
            pdb_names[sunid] = set((full_pdbid, ))
        ##
        
        logger.debug('representative PDB id: ' + str(full_pdbid))
                      
        i += 1
        
    # now output to file
    output_file = os.path.join(positive_dir, output_filename)
    
    with open(output_file, 'w') as pdblist_file:
        for name in pdb_names[sunid]:
            pdblist_file.write(name + '\n')
    logger.debug('  written to file ' + output_filename)
    
    
    ####