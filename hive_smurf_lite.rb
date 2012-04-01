#!/usr/bin/env ruby
require './hive'

RUN = true

alignments = ARGV[0]

results = Dir.glob(File.join(alignments, '*')).map{|f| File.basename(f)}

puts "#{results.length} total runs"

commands = []

thresh=2
simevfreq=0.5
simevthresh=thresh
results.each do |sf|
  mypath="/r/bcb/ndaniels/smurf_lite_thermotoga/#{sf}"
  cmd="cp -rp #{alignments}/#{sf} #{mypath} ; ./train_smurf.sh #{mypath} \"sf=#{sf}\" #{thresh} #{simevfreq} 150 #{simevthresh} /r/bcb/ndaniels/uniprot-thermotoga-maritima.fasta #{sf} true"
  commands << cmd
end

# now hive the results

assignments = Hive::assign_commands(commands, 'cd src/smurf-lite/scripts ; source ~/.bash_profile ; ')

if RUN
  Hive::run!(assignments)
else
  Hive::show_commands(assignments)
end
