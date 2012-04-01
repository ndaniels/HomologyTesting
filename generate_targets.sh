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

if [ $# -lt 2 ]; then
    echo "Usage: $0 <output-dir> <superfamily-sunid>"
    exit $STATUS_ARGS
fi

OUTPUT_DIR=$1
SUPERFAMILY=$2

# generate the consensus multiple alignment template
./generate-training-targets.py -v -r blast7 $OUTPUT_DIR $SUPERFAMILY
if [ $? -ne 0 ]; then
    echo "generate-training-targets.py exited with status $?"
    exit $?
fi

./generate-positive-targets.py -v -r nonident $OUTPUT_DIR $SUPERFAMILY
if [ $? -ne 0 ]; then
    echo "generate-positive-controls.py exited with status $?"
    exit $?
fi

./generate-negative-targets.py -v -r blast7 $OUTPUT_DIR $SUPERFAMILY
if [ $? -ne 0 ]; then
    echo "generate-negative-controls.py exited with status $?"
    exit $?
fi


exit 0
