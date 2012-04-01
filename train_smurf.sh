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
    echo "Usage: $0 <output-dir> <superfamily-sunid> <beta-threshold> <simev-freq> <simev-count> <simev-threshold> <query-file> [skip-matt]"
    exit $STATUS_ARGS
fi

OUTPUT_DIR=$1
SUPERFAMILY=$2
THRESHOLD=$3
SIMEV_FREQ=$4
SIMEV_COUNT=$5
SIMEV_THRESHOLD=$6
QUERY_FILE=$7
SF_NUM=$8
SKIPMATT=$9

CALIBRATION_FILE=/r/bcb/protein_structure/smurf_calibration/calibration.fasta

### vary: beta threshold, simev freq (10, 50), simev threshold (0, same as beta)

# generate the consensus multiple alignment template
if [ -z $SKIPMATT ]; then
    ./generate-all-matt-alignments.py -v -r blast7 $OUTPUT_DIR $SUPERFAMILY
    if [ $? -ne 0 ]; then
        echo "generate-all-matt-alignments.py exited with status $?"
        exit $?
    fi
fi

# these args go to generate-hmm (freq, simev threshold, simev count)

SMURF_LITE=smurf-lite

# run smurf-lite queries
./generate-complete-hmm.py -v $OUTPUT_DIR $SMURF_LITE -s $THRESHOLD -f $SIMEV_FREQ -c $SIMEV_COUNT -t $SIMEV_THRESHOLD

if [ $? -ne 0 ]; then
    echo "generate-complete-hmm.py exited with status $?"
    exit $?
fi

# now calibrate
./add_pvalue_to_hmm.rb $OUTPUT_DIR/${SF_NUM}_smurf-lite.hmm+ $CALIBRATION_FILE $THRESHOLD $SIMEV_FREQ $SIMEV_COUNT

./run-complete-hmm.py -v $OUTPUT_DIR $SMURF_LITE $QUERY_FILE
if [ $? -ne 0 ]; then
    echo "run-complete-hmm.py exited with status $?"
    exit $?
fi


exit 0
