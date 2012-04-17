#!/usr/bin/env python2.7

import argparse
import gargamel.cmdlib as cmd
import gargamel.constants as C

parser = argparse.ArgumentParser(
    description='Analyze MRFy')
aa = parser.add_argument
aa(dest='output_dir', metavar='OUTPUT_DIR')
aa(dest='pdb_key', metavar='SUPERFAMILY_SUNID')
aa('-b', '--beta-threshold', type=int, default=0)
aa('--run-hmmer', action='store_true')
aa('--simev-freq', type=int, default=0)
aa('--simev-count', type=int, default=0)
aa('--simev-threshold', type=int, default=0)
aa('--skip-matt', action='store_true')
conf = parser.parse_args()

hmmCmds = {
    'generate': ('./generate-hmm.py',
                 '-v %s %s -s %s -f %s -c %s -t %s' \
                 % (conf.output_dir, '%s', conf.beta_threshold,
                    conf.simev_freq, conf.simev_count, conf.simev_threshold)),
    'positive': ('./generate-positive-controls.py',
                 '-v -r nonident %s %s %s' \
                 % (conf.output_dir, '%s', conf.pdb_key)),
    'negative': ('./generate-negative-controls.py',
                 '-v -r nonident %s %s %s' \
                 % (conf.output_dir, '%s', conf.pdb_key)),
    'csv':      ('./generate-csv.py',
                 '-v %s %s' % (conf.output_dir, '%s')),
}

def run_hmm(hmmName):
    def hmmCmd(name):
        return ' '.join([hmmCmds[name][0], hmmCmds[name][1] % hmmName])

    for cmdType in ('generate', 'positive', 'negative', 'csv'):
        if not cmd.vomit(hmmCmd(cmdType)):
            cmd.eprint('%s exited with error' % hmmCmds[cmdType][0])

if not conf.skip_matt:
    c = './generate-matt-alignments.py -v -r blast7 %s %s' \
        % (conf.output_dir, conf.pdb_key)
    if not cmd.vomit(c):
        cmd.eprint('generate-matt-alignments.py exited with error')
        cmd.exit(1)

if conf.run_hmmer:
    run_hmm(C.HMMER)
else:
    run_hmm(C.SMURF_LITE)

