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

if [ $# -lt 4 ]; then
    echo "Usage: $0 <output-dir> <superfamily-sunid> <simev> [skip-matt]"
    exit $STATUS_ARGS
fi

OUTPUT_DIR=$1
SUPERFAMILY=$2
SIMEV=$3
SKIPMATT=$4

### vary: beta threshold, simev freq (10, 50), simev threshold (0, same as beta)

# these args go to generate-hmm (freq, simev threshold, simev count)

MRFY=mrfy

# generate the consensus multiple alignment template
if [ -z $SKIPMATT ]; then
    ./generate-matt-alignments.py -v -r blast7 $OUTPUT_DIR $SUPERFAMILY
    if [ $? -ne 0 ]; then
        echo "generate-matt-alignments.py exited with status $?"
        exit $?
    fi
fi

if [ $SIMEV -eq 1 ]; then
  ./generate-mrf.py -v $OUTPUT_DIR $MRFY -f 0.5 -c 150 -t 0
else
  ./generate-mrf.py -v $OUTPUT_DIR $MRFY -f 0.0 -c 0 -t 0
fi


if [ $? -ne 0 ]; then
    echo "generate-mrf.py exited with status $?"
    exit $?
fi

./generate-positive-controls.py -v -r nonident $OUTPUT_DIR $MRFY $SUPERFAMILY
if [ $? -ne 0 ]; then
    echo "generate-positive-controls.py exited with status $?"
    exit $?
fi

./generate-negative-controls.py -v -r blast7 $OUTPUT_DIR $MRFY $SUPERFAMILY
if [ $? -ne 0 ]; then
    echo "generate-negative-controls.py exited with status $?"
    exit $?
fi

./generate-csv.py -v $OUTPUT_DIR $MRFY
if [ $? -ne 0 ]; then
    echo "generate-csv.py exited with status $?"
    exit $?
fi

exit 0
