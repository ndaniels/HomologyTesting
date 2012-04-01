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

from gargamel.argumentparsers import SmurfArgumentParser
from gargamel.argumentparsers import DEFAULT_REP_ARG
from gargamel.constants import HMM_PREFIX
from gargamel.constants import HMM_SUFFIX
from gargamel.constants import HMMER
from gargamel.constants import HMMER_EXECUTABLE
from gargamel.constants import HMMER_HMM_FILENAME
from gargamel.constants import POSITIVE_DIRNAME
from gargamel.constants import SMURF
from gargamel.constants import SMURF_EXECUTABLE
from gargamel.constants import SMURF_HMM_FILENAME
from gargamel.constants import PROFILE_SMURF
from gargamel.constants import PROFILE_SMURF_EXECUTABLE
from gargamel.constants import SMURF_LITE
from gargamel.constants import SMURF_LITE_EXECUTABLE
from gargamel.constants import SMURF_LITE_HMM_FILENAME
from gargamel.constants import TMP_DIR
from gargamel.constants import DEFAULT_EVALUE
from gargamel.constants import DEFAULT_MAX_NUM_HITS
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
PROGRAM_DESCRIPTION = ('Structurally aligns query proteins in a given target '
                       'SCOP hierarchy level not already used to generate HMM '
                       'files')

# the text to write to a readme file for each query output file
QUERY_README = \
"""This file contains the result of running a structural aligner on a single
query protein chain, using the HMM file in the parent directory."""

def write_query_readme(filename, query_cmd):
    with open(filename, 'w') as f:
        f.write(QUERY_README + '\n')
        f.write('\n')
        f.write('query command:\n')
        f.write('  ' + str(query_cmd) + '\n')

# create a parser for command-line arguments, with a description of the purpose
# of this program
argparser = SmurfArgumentParser(PROGRAM_DESCRIPTION)

# parse the command-line arguments
parsed_args = argparser.parse_args()

# get the values from the command-line arguments
aligner = parsed_args.aligner
output_dir = parsed_args.outputdir.rstrip('/')  # remove trailing slash
query_file = parsed_args.query_file


# determine the amount of logging info to output
if parsed_args.verbose:
    from logging import DEBUG
    from gargamel.logger import console_handler
    console_handler.setLevel(DEBUG)

# configuration summary
config = {'output_dir' : output_dir,
          #'logging_level' : level,
          'aligner' : aligner,
          'query_file': query_file}
logger.debug('Program configuration: ' + str(config))

# end the program if the output dir doesn't exist
logger.debug('Checking whether output directory exists...')
if not os.path.isdir(output_dir):
    logger.critical('Output directory ' + output_dir + ' does not yet exist')
    logger.critical('Please run generate-matt-alignments.py and ' + \
                     'generate-hmm.py first')
    sys.exit(2)



        
# TODO get base fasta filename, put this in a loop over all queries        

base_fasta_filename = os.path.basename(query_file)
        
output_filename = os.path.join(output_dir, 'pdb' + base_fasta_filename + '.out')
if aligner == SMURF_LITE:
   hmm_filename = os.path.basename(output_dir) + '_smurf-lite.hmm+'
   query_cmd = [SMURF_LITE_EXECUTABLE,
               os.path.join(output_dir, hmm_filename),
               query_file,
               output_filename]          
else:
    logger.critical('Unknown aligner type: ' + aligner)
    sys.exit(1)

# run the query script on the current protein
logger.debug('  Running query script...')
logger.debug('  ' + ' '.join(query_cmd))
return_code = subprocess.call(query_cmd)
logger.debug('  Return code: ' + str(return_code))

# add a README to the directory containing the alignment of the
# current query protein
logger.debug('  Writing README for smurf query result...')
query_readme = output_filename + '.README'
write_query_readme(query_readme, query_cmd)
logger.debug('    wrote to ' + query_readme)
