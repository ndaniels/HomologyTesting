#!/usr/bin/env python
#
# generate-negative-controls.py - run a structural aligner on chains not in a
# given superfamily
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
from gargamel.constants import NEGATIVE_DIRNAME
from gargamel.constants import TMP_DIR

from gargamel.fasta import FASTA_FILENAME
from gargamel.fasta import sequences_from_file
from gargamel.logger import logger
from gargamel.nrpdb import RepresentativeFields
from gargamel.nrpdb import NRPDB_FILENAME
from gargamel.nrpdb import nrpdbs_from_file
from gargamel.scop import Keys
from gargamel.scop import SCOP_CLASSIFICATION_FILE
from gargamel.scop import all_pdbids_from_file
from gargamel.scop import all_pdbids_from_file_in
#from gargamel.whitelist import WHITELIST_FILENAME
#from gargamel.whitelist import whitelist_from_file

# a brief description of the purpose of this program
PROGRAM_DESCRIPTION = ('Generates list of query proteins not in a given '
                       'SCOP hierarchy level')


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

output_filename = 'negative_controls'

# determine the amount of logging info to output
if parsed_args.verbose:
    from logging import DEBUG
    from gargamel.logger import console_handler
    console_handler.setLevel(DEBUG)

# configuration summary
config = {'target_level' : target_level,
          'target_sunid' : target_sunid,
          'output_dir' : output_dir,
          #'logging_level' : level,
          'representative_field' : representative_field}

logger.debug('Program configuration: ' + str(config))


# get the set of non-redundant PDB chains from the NRPDB file, and use only
# these chains for training
logger.debug('Getting non-redundant set of PDB chains...')
nrpdbs = nrpdbs_from_file(NRPDB_FILENAME, representative_field)
logger.debug('There are ' + str(len(nrpdbs)) + ' non-redundant chains.')

# then, filter the query_pdbids and the trained_pdbids to be only reps
# then subtract out the trained_pdbids

# get all the PDB IDs on which to test (don't test already trained superfamily)
logger.debug('Getting records to test from SCOP Classification file...')
original_query_pdbids = all_pdbids_from_file(SCOP_CLASSIFICATION_FILE)
query_pdbids = set([nrpdbs[x] for x in original_query_pdbids if x in nrpdbs])
logger.debug('  total number of chains: ' + str(len(query_pdbids)))
original_trained_pdbids = all_pdbids_from_file_in(SCOP_CLASSIFICATION_FILE,
                                         target_level, target_sunid)
trained_pdbids = set([nrpdbs[x] for x in original_trained_pdbids if x in nrpdbs])                   

used_base_pdbids = set([x.split(':')[0] for x in trained_pdbids])
                      
logger.debug('  number of trained chains: ' + str(len(trained_pdbids)))
query_pdbids -= trained_pdbids

logger.debug('  number of query chains: ' + str(len(query_pdbids)))



# create the whitelist of PDB chains on which to train explicitly
#logger.debug('Getting the whitelist of chains to test...')
#whitelist = whitelist_from_file(WHITELIST_FILENAME)

# end the program if the output dir doesn't exist
logger.debug('Checking whether output directory exists...')
if not os.path.isdir(output_dir):
    logger.critical('Output directory ' + output_dir + ' does not yet exist')
    logger.critical('Please run generate-matt-alignments.py, ' + \
                     'generate-hmm.py, and generate-positive-controls.py ' + \
                     'first')
    sys.exit(2)

# determine which hierarchy levels exist
logger.debug('Determining which hierarchy levels were left out during '
             'training...')
logger.debug('  output_dir contains: ' + str(os.listdir(output_dir)))
sunids = filter(lambda x: os.path.isdir(os.path.join(output_dir, x)),
                os.listdir(output_dir))
logger.debug('  sunids: ' + str(sunids))

# iterate over each family
# do NOT iterate over each family for now, just the first

pdb_names = {}

for sunid in [sunids[1]]:

    negative_dir = output_dir

    i = 1
    total_count = 0
    used_count = 0
    
    for pdbid in query_pdbids:
        bare_pdbid = pdbid.split(':')[0]
        
        # skip this whole pdb file if any of its chains were in used_base_pdbids
        if bare_pdbid in used_base_pdbids:
          continue

        # logger.debug('query PDB id: ' + str(pdbid))
        # logger.debug('query number ' + str(i) + ' out of ' + \
        #               str(len(query_pdbids)))
        i += 1
        total_count += 1

        if sunid in pdb_names:
           
            pdb_names[sunid].add(pdbid)
        else:
            logger.debug('    creating set for current hierarchy '
                         'level sunid')
            pdb_names[sunid] = set((pdbid, ))
        ##


            
        used_count += 1

    # now output to file
    output_file = os.path.join(negative_dir, output_filename)

    with open(output_file, 'w') as pdblist_file:
        for name in pdb_names[sunid]:
            pdblist_file.write(name + '\n')
    logger.debug('  written to file ' + output_filename)



