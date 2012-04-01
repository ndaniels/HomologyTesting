#!/usr/bin/env tcsh

if ($# != 3) then
    echo "Usage: $0 <PDBlistfile> <FASTAfiletotest> <outputfile>"
    exit 1
endif

# temporary file names
set PREFIX=/tmp/mattAlignment
set HMMFILE=/tmp/result.hmm+

# train the alignment on the specified comma-separated list of PDB(?) files
matt -o $PREFIX -L $1

# add some beta strand information
smurf-preparse $PREFIX

# build the hidden Markov model
hmmbuild $HMMFILE $PREFIX.ssi

# run smurf
smurf $HMMFILE $2 $3

exit 0
