#!/usr/bin/env ruby

hosts = %w(a b c d e f g h i j k l m n o p)

%w(50249 50447 50494 50685 50814 50891 50182 50156 82057 63748 50090 50104 50475).each_with_index do |sf,index|
  host = "lab118#{hosts[index]}"
  cmd = <<-EOF
  ssh -f #{host} cd src/smurf-lite/scripts ; source ~/.bash_profile ;  ./generate-all-matt-alignments.py -v -r blast80 /r/bcb/ndaniels/smurf_alignments_complete/#{sf} \"sf=#{sf}\" &
  EOF
  puts cmd
end

hosts = %w(a b c d)

%w(50933 50938 50964 50997).each_with_index do |cf, index|
  host = "lab116#{hosts[index]}"
  cmd = <<-EOF
  ssh -f #{host} cd src/smurf-lite/scripts ; source ~/.bash_profile ;  ./generate-all-matt-alignments.py -v -r blast80 /r/bcb/ndaniels/smurf_alignments_complete/#{cf} \"cf=#{cf}\" &
  EOF
  puts cmd
end