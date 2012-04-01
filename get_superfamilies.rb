#!/usr/bin/env ruby



"d1dlwa_ 1dlw    A:      a.1.1.1 14982   cl=46456,cf=46457,sf=46458,fa=46459,dm=46460,sp=46461,px=14982"

"usage: #{$0} scop_file parent_key parent_value child_key <generate_runs?>"
parent_key, parent_sunid = ARGV[1], ARGV[2]
level = ARGV[3]

results = []
File.foreach(ARGV[0]) do |line|
  next if line =~ /^#/
  astral_id, pdb_id, pdb_chain, sccs, sunid, scop_string = line.chomp.split(/\s+/)
  sunid_set = Hash[scop_string.split(',').map{|entry| entry.split('=')}]
  if sunid_set[parent_key] == parent_sunid
   results << sunid_set[level] 
  end
end

results.uniq!

puts "#{results.length} total runs"

if ARGV[4]
  require 'timeout'
  require "socket"
  def pingecho(host, timeout=5, service="echo")
    begin
      timeout(timeout) do
        s = TCPSocket.new(host, service)
        s.close
      end
    rescue Errno::ECONNREFUSED
      return true
    rescue Timeout::Error, StandardError
      return false
    end
    return true
  end
  
  blast_level = 'blast80'
  dest = "/r/bcb/ndaniels/smurf_alignments_complete/#{blast_level}"
  labs = ['lab116', 'lab118']  
  letters = %w(a b c d e f g h i j k l m n)
  hosts = labs.map{|lab| ([lab]*(letters.length)).zip(letters).map(&:join)  }.flatten
  
  
  pingable_hosts = hosts.find_all{|h| pingecho(h, 3) }
  commands = {}
  pingable_hosts.each do |h|
    commands[h] = 'cd src/smurf-lite/scripts ; source ~/.bash_profile ; '
  end
  `mkdir -p #{dest}`
  results.each_with_index do |sunid, index|
    host = pingable_hosts[index % pingable_hosts.length]
    cmd = <<-EOF
     ./generate-all-matt-alignments.py -v -r #{blast_level} #{dest}/#{sunid} \"#{level}=#{sunid}\" ; 
    EOF
    commands[host] += cmd
  end
  
  pingable_hosts.each do |h|
    cmd = "ssh -f #{h} '#{commands[h]}'&"
    # system(cmd)
    system(cmd)
  end
  
end