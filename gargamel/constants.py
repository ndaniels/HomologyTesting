# constants.py - constants for this package and modules which import it
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

"""Provides constants for modules in this package and modules which import it.

"""

import os
import os.path

# the version number of this collection of programs
VERSION_NUMBER = 0.1

# identifying strings for the two aligners
HMMER = 'hmmer'
SMURF = 'smurf'
PROFILE_SMURF = 'profile-smurf'
SMURF_LITE = 'smurf-lite'
MRFY = 'mrfy'

# the names of the executables for querying structural aligners
HMMER_EXECUTABLE = 'hmmsearch-a2'
SMURF_EXECUTABLE = 'smurf'
PROFILE_SMURF_EXECUTABLE = './run_profile_smurf.sh'
SMURF_LITE_EXECUTABLE = 'smurf-lite'
MRFY_EXECUTABLE = MRFY

DEFAULT_SIMEV_FREQUENCY = 0
DEFAULT_SIMEV_COUNT = 0
DEFAULT_SIMEV_THRESHOLD = 0

# default values for evalue, max hits for profile smurf
DEFAULT_MAX_NUM_HITS = 20
DEFAULT_EVALUE = 0.001

# the HMM filenames to be created by smurf training
HMM_PREFIX = 'training_result'
HMM_SUFFIX = 'hmm'
HMMER_HMM_FILENAME = '.'.join((HMM_PREFIX, HMMER, HMM_SUFFIX))
SMURF_HMM_FILENAME = '.'.join((HMM_PREFIX, SMURF, HMM_SUFFIX + '+'))
PROFILE_SMURF_HMM_FILENAME = '.'.join((HMM_PREFIX, SMURF, HMM_SUFFIX + '+'))
SMURF_LITE_HMM_FILENAME = '.'.join((HMM_PREFIX, SMURF_LITE, HMM_SUFFIX + '+'))
MRF_FILENAME = '.'.join((HMM_PREFIX, MRFY, HMM_SUFFIX + '+'))
MRFY_ARGS = ''
# executable name for smurf preparse
SMURF_PREPARSE_EXECUTABLE = 'smurf-preparse'
SMURF_LITE_PREPARSE_EXECUTABLE = './smurf_lite_preparse.rb'
PROFILE_SMURF_PREPARSE_EXECUTABLE = 'smurf-preparse'
SSANNOTATE_EXECUTABLE = 'SSAnnotate'
SSANNOTATE_OPTIONS = '-o beta '
SIMEV_MRFY_SSANOTATE_EXECUTABLE = "./mrfy_simev_preparse.rb"



# executable names for hmmer and smurf hmmbuild executables
SMURF_HMMBUILD_EXECUTABLE = 'smurfbuild'
PROFILE_SMURF_HMMBUILD_EXECUTABLE = 'smurfbuild'
HMMER_HMMBUILD_EXECUTABLE = 'hmmbuild-a2'
SMURF_LITE_HMMBUILD_EXECUTABLE = 'smurfbuild'
MRFBUILD_EXECUTABLE = 'mrfbuild'

HMMER_HMMBUILD_OPTIONS = '--symfrac 0.2 --eent --ere 0.7'
SMURF_HMMBUILD_OPTIONS = '--symfrac 0.2 --eent --ere 0.7 --fragthresh 0.0' 
# --fragthresh 0.0
SMURF_LITE_HMMBUILD_OPTIONS = '--symfrac 0.2 --eent --ere 0.7 --fragthresh 0.0'
MRFBUILD_OPTIONS = '--symfrac 0.2 --eent --ere 0.7 --fragthresh 0.0'
PROFILE_SMURF_HMMBUILD_OPTIONS = ''


DEFAULT_SMURF_LITE_THRESHOLD = 1000

# the prefix for files generated by matt
MATT_PREFIX = 'mattAlignment'

# the name of the directory which contains the positive/negative controls
POSITIVE_DIRNAME = 'positive'
NEGATIVE_DIRNAME = 'negative'

# the temporary directory for use with smurf
TMP_DIR = '/tmp/smurf'
if not os.path.isdir(TMP_DIR):
    os.mkdir(TMP_DIR)
