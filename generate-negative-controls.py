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

from gargamel.argumentparsers import StructuralAlignmentArgumentParser
from gargamel.argumentparsers import DEFAULT_REP_ARG
from gargamel.constants import MRFBUILD_EXECUTABLE
from gargamel.constants import SSANNOTATE_EXECUTABLE
from gargamel.constants import MRF_FILENAME
from gargamel.constants import MRFBUILD_OPTIONS
from gargamel.constants import MRFY_ARGS
from gargamel.constants import MRFY
from gargamel.constants import MRFY_EXECUTABLE
from gargamel.constants import HMM_PREFIX
from gargamel.constants import HMM_SUFFIX
from gargamel.constants import HMMER
from gargamel.constants import HMMER_EXECUTABLE
from gargamel.constants import HMMER_HMM_FILENAME
from gargamel.constants import NEGATIVE_DIRNAME
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
PROGRAM_DESCRIPTION = ('Structurally aligns query proteins not in a given '
                       'SCOP hierarchy level')

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
argparser = StructuralAlignmentArgumentParser(PROGRAM_DESCRIPTION)

# parse the command-line arguments
parsed_args = argparser.parse_args()

# get the values from the command-line arguments
aligner = parsed_args.aligner
output_dir = parsed_args.outputdir.rstrip('/')  # remove trailing slash
target_level = parsed_args.target_level
target_sunid = parsed_args.target_sunid
representative_field = parsed_args.repfield

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
          'aligner' : aligner,
          'representative_field' : representative_field}

logger.debug('Program configuration: ' + str(config))

# create a dictionary from PDB IDs to residue sequences
logger.debug('Building a mapping from PDBID to residue sequence...')
sequences = sequences_from_file(FASTA_FILENAME)

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

for sunid in [sunids[1]]:

    aligner_output_dir = os.path.join(output_dir, sunid, aligner)
    if not os.path.isdir(aligner_output_dir):
        logger.critical('No directory found at ' + aligner_output_dir)
        logger.critical('Please run generate-positive-controls.py first')
        sys.exit(4)

    negative_dir = os.path.join(aligner_output_dir, NEGATIVE_DIRNAME)
    if not os.path.isdir(negative_dir):
        logger.debug('Creating directory ' + negative_dir)
        os.mkdir(negative_dir)
    else:
        logger.debug('Directory already exists at ' + negative_dir)

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
        # skip... only run every 10th one
        if total_count % 10 != 0:
          continue

        # only query this chain if it is in the whitelist and is a
        # representative of a set of chains
        # TODO relies on short-circuiting 'or' operator
        # if pdbid not in nrpdbs or len(nrpdbs[pdbid]) == 0:
        #     # logger.warning('  PDBID ' + pdbid + ' is in neither the ' + \
        #     #                 'whitelist nor the NRPDB file with a total ' + \
        #     #                 'of more than 0 chains')
        #     # logger.warning('  skipping this chain')
        #     continue

        # only query this chain if there was a FASTA sequence for it
        if bare_pdbid not in sequences:
            logger.error('  No FASTA sequence was read for PDB ID ' + bare_pdbid)
            logger.error('  Not writing FASTA file for this protein.')
            continue
            
        used_count += 1

        # open a FASTA file to which to write the sequence
        fasta_filename = os.path.join(TMP_DIR, 'pdb' + bare_pdbid + '.fasta')
        logger.debug('  Checking whether FASTA file for ' + str(pdbid)
                     + ' exists...')
        if not os.path.isfile(fasta_filename):
            logger.debug('  ...it doesn\'t, so we create it...')
            with open(fasta_filename, 'w') as fasta_file:
                fasta_file.writelines(sequences[bare_pdbid])
            logger.debug('  ...wrote to ' + fasta_filename)



        # TODO need to put the :CHAIN on the cmd line (or do we? change from bare?)
        # determine which executable and multiple alignment file to use for the
        # hmmbuild step, and determine the name of the HMM file
        output_filename = os.path.join(negative_dir, 'pdb' + bare_pdbid + '.out')
        if aligner == SMURF:
            query_cmd = [SMURF_EXECUTABLE,
                         os.path.join(aligner_output_dir, SMURF_HMM_FILENAME),
                         fasta_filename,
                         output_filename]
        elif aligner == MRFY:
            query_cmd = [MRFY_EXECUTABLE,
                         # MRFY_ARGS,
                         os.path.join(aligner_output_dir, MRF_FILENAME),
                         fasta_filename,
                         output_filename]
                           
        elif aligner == HMMER:
            query_cmd = [HMMER_EXECUTABLE,
                         '-Z 1.0',
                         '-E 10000',
                         '-o', output_filename,
                         os.path.join(aligner_output_dir, HMMER_HMM_FILENAME),
                         fasta_filename]
        elif aligner == PROFILE_SMURF:
            query_cmd = [PROFILE_SMURF_EXECUTABLE,
                        '-e ' + str(DEFAULT_EVALUE),
                        '-x ' + str(DEFAULT_MAX_NUM_HITS),
                        os.path.join(aligner_output_dir, SMURF_HMM_FILENAME),
                        fasta_filename,
                        output_filename]
        elif aligner == SMURF_LITE:
            query_cmd = [SMURF_LITE_EXECUTABLE,
                         os.path.join(aligner_output_dir, SMURF_LITE_HMM_FILENAME),
                         fasta_filename,
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

    logger.debug('Used ' + str(used_count) + ' out of ' + str(total_count) 
                 + ' pdbids')