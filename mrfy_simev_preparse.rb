#!/usr/bin/env ruby
require 'fileutils'
# this takes the same arguments that smurf-preparse would plus an 'interleave'

# usage: smurf-preparse <structure pdb> <alignment fasta> <output ssi>

usage = "usage: #{$0} <fasta/pdb/ssi base> <mutation_rate> <num_seq> <blast_augment?>"

filebase = ARGV[0]

mutation_rate = ARGV[1]

num_seq = ARGV[2]

blast_augmentation = ( ARGV[3] && ARGV[3].downcase == 'true' )

output = filebase + '.ssi' # TODO fix this so we don't blow away 'mrfy' earlier in path

backup_output = output.gsub('mattAlignment', 'mattAlignment_bak')
FileUtils.copy(output, backup_output)

cmd = "SSAnnotate -o beta #{filebase}"
puts "running #{cmd}"

system(cmd)

FileUtils.copy(output, backup_output)

temp_output = output.gsub('mattAlignment', 'mattAlignment_temp')

if num_seq && mutation_rate
  mutation_output = temp_output.gsub('_temp', '_temp_m')
  puts "mutating, output: #{mutation_output}"
  cmd = "./sim_ev.rb #{temp_output} #{mutation_output} #{mutation_rate} #{num_seq} 0"
  temp_output = mutation_output
  puts "running #{cmd}"
  system(cmd)
end

# insert here optional blast-augmentation
if blast_augmentation
  # this is now orthogonal to mutation
  augmentation_output = temp_output.gsub('.ssi', '_blast.ssi')
  puts "blast augment: output: #{augmentation_output}"
  cmd = "./blast_augment_training.rb #{temp_output} #{augmentation_output}"
  temp_output = augmentation_output
  puts "running #{cmd}"
  system(cmd)
end
#
# now write real output

FileUtils.copy(temp_output, output)