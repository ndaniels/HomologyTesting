#!/usr/bin/env ruby

# takes 2 arguments: results directory, threshold

results_dir = ARGV[0]
results = []
threshold = ARGV[1].to_f
SCOP = '/r/bcb/protein_structure/SCOP/dir.des.scop.txt_1.75.txt'

def parse_file(filename, superfamily, threshold)
  results = []
  name = ''
  alignment = ''
  rawscore = nil
  pval = nil
  File.foreach(filename) do |line|
    if line =~ /^>/
      # new entry
      # close out last one
      if name
        results << {:name => name, :alignment => alignment, :raw_score => rawscore, :p_value => pval} if pval && pval <= threshold
      end
      name = line.chomp.gsub(/^>/,'')
      pval = nil
      rawscore = nil
      alignment = ''
    elsif line =~ /Raw score: (-?\d+\.?\d+)/
      rawscore = Regexp.last_match[1].to_f
    elsif line =~ /P-value: ([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)/
      pval = Regexp.last_match[1].to_f
    else # part of alignment
      alignment += line
    end
  end
  results << {:name => name, :alignment => alignment, :raw_score => rawscore, :p_value => pval} if pval && pval <= threshold
  
  results.sort!{|a,b| a[:p_value] <=> b[:p_value]}
  
  {:superfamily => superfamily, :results => results}
      
end

Dir.glob(File.join(results_dir, '*')).each do |superfamily_dir|
  superfamily = File.basename(superfamily_dir)
  next unless File.directory?(superfamily_dir)
  Dir.glob(File.join(superfamily_dir, '*.out')).each do |smurf_file|
    results << parse_file(smurf_file, superfamily, threshold)
    
  end
end

scop = {}
File.foreach(SCOP) do |line|
  next if line =~ /^#/
  # 46461   sp      a.1.1.1 -       Ciliate (Paramecium caudatum) [TaxId: 5885]
  sunid, kind, sccs, chain, rest = line.chomp.split(/\s+/, 5)
  if kind == 'sf'
    scop[sunid] = rest
  end
end

counter = 0
results.each do |r|
  puts "Superfamily #{r[:superfamily]}: #{scop[r[:superfamily]]}" unless r[:results].empty?
  r[:results].each do |result|
    puts result[:name]
    puts result[:p_value]
    puts
    counter += 1
  end
end

puts "#{counter} good hits"

