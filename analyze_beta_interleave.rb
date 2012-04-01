#!/usr/bin/env ruby

require './beta_pair'
require './stockholm'

infile = ARGV[0]

alignment = Stockholm.new(infile)

alignment.display_betas