#!/usr/bin/env ruby

# this takes the same arguments that smurf-preparse would plus an 'interleave'

# usage: smurf-preparse <structure pdb> <alignment fasta> <output ssi>

usage = "usage: #{$0} <structure pdb> <alignment fasta> <output ssi> <mutation_rate> <num_seq> <blast_augment?>"

structure = ARGV[0]

alignment = ARGV[1]

output = ARGV[2]

mutation_rate = ARGV[3]

num_seq = ARGV[5]

blast_augmentation = ( ARGV[6] && ARGV[6].downcase == 'true' )

backup_output = output.gsub('mrfy', 'mrfy_bak')
temp_output = output.gsub('mrfy', 'mrfy_temp')

cmd = "SSAnnotate -o beta #{structure} #{alignment} #{temp_output}"
puts "running #{cmd}"

system(cmd)

File.copy(temp_output, backup_output)

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

File.copy(temp_output, output)