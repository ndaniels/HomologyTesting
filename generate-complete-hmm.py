#!/usr/bin/env python
#
# generate-hmm.py - generate HMM files from multiple alignment files
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

import os
import os.path
import subprocess
import sys

from gargamel.argumentparsers import AlignmentArgumentParser
from gargamel.constants import HMM_SUFFIX
from gargamel.constants import HMM_PREFIX
from gargamel.constants import HMMER
from gargamel.constants import HMMER_HMM_FILENAME
from gargamel.constants import HMMER_HMMBUILD_EXECUTABLE
from gargamel.constants import MATT_PREFIX
from gargamel.constants import SMURF
from gargamel.constants import SMURF_HMM_FILENAME
from gargamel.constants import SMURF_HMMBUILD_EXECUTABLE
from gargamel.constants import SMURF_PREPARSE_EXECUTABLE
from gargamel.constants import PROFILE_SMURF
from gargamel.constants import PROFILE_SMURF_HMM_FILENAME
from gargamel.constants import PROFILE_SMURF_HMMBUILD_EXECUTABLE
from gargamel.constants import PROFILE_SMURF_PREPARSE_EXECUTABLE
from gargamel.constants import SMURF_LITE
from gargamel.constants import SMURF_LITE_HMM_FILENAME
from gargamel.constants import SMURF_LITE_HMMBUILD_EXECUTABLE
from gargamel.constants import SMURF_LITE_PREPARSE_EXECUTABLE
from gargamel.constants import HMMER_HMMBUILD_OPTIONS
from gargamel.constants import SMURF_HMMBUILD_OPTIONS
from gargamel.constants import PROFILE_SMURF_HMMBUILD_OPTIONS
from gargamel.constants import SMURF_LITE_HMMBUILD_OPTIONS
from gargamel.logger import logger

# a brief description of the purpose of this program
PROGRAM_DESCRIPTION = 'Generates HMM files from multiple alignment files ' + \
                      '(generated by the generate-matt-alignments.py script)'

# create a parser for command-line arguments, with a description of the purpose
# of this program
argparser = AlignmentArgumentParser(PROGRAM_DESCRIPTION)

# parse the command-line arguments
parsed_args = argparser.parse_args()

# get the values from the command-line arguments
output_dir = parsed_args.outputdir.rstrip('/')  # remove trailing slash
aligner = parsed_args.aligner
smurf_lite_threshold = parsed_args.smurf_lite_threshold
simev_frequency = parsed_args.simev_frequency
simev_count = parsed_args.simev_count
simev_threshold = parsed_args.simev_threshold

# determine the amount of logging info to output
if parsed_args.verbose:
    from logging import DEBUG
    from gargamel.logger import console_handler
    console_handler.setLevel(DEBUG)

# summary of the program configuration
config = {'output_dir' : output_dir, 'aligner' : aligner}
logger.debug('Program configuration: ' + str(config))

# end the program if the output dir doesn't exist
logger.debug('Checking whether output directory exists...')
if not os.path.isdir(output_dir):
    logger.critical('Output directory ' + output_dir + ' does not yet exist')
    logger.critical('Please run generate-matt-alignments.py first')
    sys.exit(2)


# determine which executable and multiple alignment file to use for the
# hmmbuild step, and determine the name of the HMM file
if aligner == SMURF_LITE:
    executable = SMURF_LITE_HMMBUILD_EXECUTABLE
    preparse_executable = SMURF_LITE_PREPARSE_EXECUTABLE
    hmm_filename = os.path.basename(output_dir) + '_smurf-lite.hmm+'
    hmmbuild_options = SMURF_LITE_HMMBUILD_OPTIONS
else:
    logger.critical('Unknown aligner type: ' + aligner)
    sys.exit(1)

mult_alignment_file = os.path.join(output_dir,
                                   MATT_PREFIX + '.ssi')
                                   
if not os.path.isfile(mult_alignment_file):
  logger.debug('Group not aligned; could not find alignment file ' + mult_alignment_file + ' - skipping.')
  sys.exit(1)

# call smurf-preparse to set up beta strand goodness
if aligner != HMMER:
  logger.debug('Running smurf-preparse...')
  mult_alignment_file = os.path.join(output_dir,
                                     MATT_PREFIX + '_' + aligner + '.ssi')
  if float(simev_frequency) > 0.0:        
    preparse_cmd = [preparse_executable,
                    os.path.join(output_dir, MATT_PREFIX + '.pdb'),
                    os.path.join(output_dir, MATT_PREFIX + '.fasta'),
                    mult_alignment_file,
                    smurf_lite_threshold,
                    simev_frequency,
                    simev_count,
                    simev_threshold
                    ]
  else:
    preparse_cmd = [preparse_executable,
                    os.path.join(output_dir, MATT_PREFIX + '.pdb'),
                    os.path.join(output_dir, MATT_PREFIX + '.fasta'),
                    mult_alignment_file,
                    smurf_lite_threshold
                    ]
  logger.debug('  ' + ' '.join(preparse_cmd))
  return_code = subprocess.call(preparse_cmd)
  logger.debug('Return code: ' + str(return_code))
  
# generate a hidden Markov model from the multiple alignment generated by
# matt (specifically, the .ssi file)

logger.debug('Running hmmbuild...')
hmmbuild_cmd = filter(lambda x: len(x)>0, [executable,
                hmmbuild_options,
                os.path.join(output_dir, hmm_filename),
                mult_alignment_file])
logger.debug('  ' + ' '.join(hmmbuild_cmd))
  
return_code = subprocess.call(' '.join(hmmbuild_cmd), shell=True)
logger.debug('Return code: ' + str(return_code))
