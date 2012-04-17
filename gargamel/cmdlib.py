import os
import os.path
from subprocess import (call, check_output, PIPE, STDOUT, CalledProcessError,
                        Popen)
import sys

VERBOSE = False

rawcmd    = lambda x: check_output(x)
cmd       = lambda x: check_output(x.split())
cmdret    = lambda x: call(x.split(), stdout=PIPE) == 0
vomit     = lambda x: call(x.split(), stdout=sys.stdout) == 0
cmdexists = lambda x: cmdret('cmd-exists %s' % x)
args      = sys.argv
xdgconf   = os.getenv('XDG_CONFIG_HOME')
home      = os.getenv('HOME')
user      = os.getenv('USER')
filedir   = lambda f: os.path.abspath(os.path.dirname(f))

try:
    hostname  = cmd('hostname').strip()
except CalledProcessError:
    hostname = 'unknown'

if args and args[0]:
    try:
        basename  = cmd('basename %s' % args[0]).strip()
    except CalledProcessError:
        basename = 'unknown'
else:
    basename = 'unknown'

def cmdstdin(cmd, stdin):
    return Popen(cmd.split(), stdin=PIPE).communicate(input=stdin)

def shift(i=1):
    assert i >= 1
    for _ in range(0, i):
        args.pop(0)

def cmdv(c):
    verbose(c)
    return cmd(c)

def rawcmdv(c):
    verbose(''.join(c))
    return rawcmd(c)

def verbose(s):
    if VERBOSE:
        print >> sys.stdout, s

def path(p):
    pieces = p.split('/')
    if p[0] == '/':
        pieces.insert(0, '/')
    return os.path.join(*pieces)

def eprint(s):
    print >> sys.stderr, s

def eprinti(s):
    print >> sys.stderr, s,

def exit(status=0):
    sys.exit(status)

def mapfile(fun, fp):
    f = open(fp)
    lines = f.readlines()
    f.close()
    f = open(fp, 'w')
    f.writelines(map(fun, lines))
    f.close()

def addtoenv(envfile):
    if not os.access(envfile, os.R_OK):
        eprint('Cannot read %s' % envfile)
        exit(1)

    command = ['bash', '-c', 'source %s && env' % envfile]

    for line in rawcmd(command).splitlines():
        (var, val) = line.split('=', 1)
        os.environ[var] = val

