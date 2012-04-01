#!/usr/bin/env bash
#
# analyze-smurf.sh - run all scripts necessary to generate positive and
# negative controls for analyzing the efficacy of smurf versus hmmer
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

# run this script from the current directory, because the scripts which it
# calls have hardcoded locations

STATUS_ARGS=4

if [ $# -lt 7 ]; then
    echo "Usage: $0 <output-dir> <superfamily-sunid> <beta-threshold> <run-hmmer> <simev-freq> <simev-count> <simev-threshold> [skip-matt]"
    exit $STATUS_ARGS
fi

OUTPUT_DIR=$1
SUPERFAMILY=$2
THRESHOLD=$3
RUN_HMMER=$4
SIMEV_FREQ=$5
SIMEV_COUNT=$6
SIMEV_THRESHOLD=$7
SKIPMATT=$8

### vary: beta threshold, simev freq (10, 50), simev threshold (0, same as beta)

# these args go to generate-hmm (freq, simev threshold, simev count)

HMMER=hmmer
SMURF=smurf
PROFILE_SMURF=profile-smurf
SMURF_LITE=smurf-lite

# generate the consensus multiple alignment template
if [ -z $SKIPMATT ]; then
    ./generate-matt-alignments.py -v -r blast7 $OUTPUT_DIR $SUPERFAMILY
    if [ $? -ne 0 ]; then
        echo "generate-matt-alignments.py exited with status $?"
        exit $?
    fi
fi

# run smurf-lite queries
./generate-hmm.py -v $OUTPUT_DIR $SMURF_LITE -s $THRESHOLD -f $SIMEV_FREQ -c $SIMEV_COUNT -t $SIMEV_THRESHOLD

if [ $? -ne 0 ]; then
    echo "generate-hmm.py exited with status $?"
    exit $?
fi

./generate-positive-controls.py -v -r nonident $OUTPUT_DIR $SMURF_LITE $SUPERFAMILY
if [ $? -ne 0 ]; then
    echo "generate-positive-controls.py exited with status $?"
    exit $?
fi

./generate-negative-controls.py -v -r blast7 $OUTPUT_DIR $SMURF_LITE $SUPERFAMILY
if [ $? -ne 0 ]; then
    echo "generate-negative-controls.py exited with status $?"
    exit $?
fi

# generate smurf-lite csv

./generate-csv.py -v $OUTPUT_DIR $SMURF_LITE
if [ $? -ne 0 ]; then
    echo "generate-csv.py exited with status $?"
    exit $?
fi

# only run HMMER if HMMER specified, to save time
if [ $RUN_HMMER -eq 1 ]; then

  # run hmmer queries
  ./generate-hmm.py -v $OUTPUT_DIR $HMMER
  if [ $? -ne 0 ]; then
      echo "generate-hmm.py exited with status $?"
      exit $?
  fi

  ./generate-positive-controls.py -v -r nonident $OUTPUT_DIR $HMMER $SUPERFAMILY
  if [ $? -ne 0 ]; then
      echo "generate-positive-controls.py exited with status $?"
      exit $?
  fi

  ./generate-negative-controls.py -v -r blast7 $OUTPUT_DIR $HMMER $SUPERFAMILY
  if [ $? -ne 0 ]; then
      echo "generate-negative-controls.py exited with status $?"
      exit $?
  fi

  # generate HMMER csv

  ./generate-csv.py -v $OUTPUT_DIR $HMMER
  if [ $? -ne 0 ]; then
      echo "generate-csv.py exited with status $?"
      exit $?
  fi
fi
# run smurf queries
# ./generate-hmm.py -v $OUTPUT_DIR $SMURF
# if ($? != 0) then
#     echo "generate-hmm.py exited with status $?"
#     exit $?
# endif
# 
# ./generate-positive-controls.py -v $OUTPUT_DIR $SMURF $SUPERFAMILY
# if ($? != 0) then
#     echo "generate-positive-controls.py exited with status $?"
#     exit $?
# endif
# 
# ./generate-negative-controls.py -v -r blast7 $OUTPUT_DIR $SMURF $SUPERFAMILY
# if ($? != 0) then
#     echo "generate-negative-controls.py exited with status $?"
#     exit $?
# endif

# run profile-smurf queries
# ./generate-hmm.py -v $OUTPUT_DIR $PROFILE_SMURF
# if ($? != 0) then
#     echo "generate-hmm.py exited with status $?"
#     exit $?
# endif
# 
# ./generate-positive-controls.py -v $OUTPUT_DIR $PROFILE_SMURF $SUPERFAMILY
# if ($? != 0) then
#     echo "generate-positive-controls.py exited with status $?"
#     exit $?
# endif
# 
# ./generate-negative-controls.py -v $OUTPUT_DIR $PROFILE_SMURF $SUPERFAMILY
# if ($? != 0) then
#     echo "generate-negative-controls.py exited with status $?"
#     exit $?
# endif

# ./generate-csv.py -v $OUTPUT_DIR $SMURF
# if ($? != 0) then
#     echo "generate-csv.py exited with status $?"
#     exit $?
# endif

# ./generate-csv.py -v $OUTPUT_DIR $PROFILE_SMURF
# if ($? != 0) then
#     echo "generate-csv.py exited with status $?"
#     exit $?
# endif

exit 0
