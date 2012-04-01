module Hive

  require 'timeout'
  require "socket"
  def self.pingecho(host, timeout=5, service="echo")
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

  def self.pingable_hosts
    labs = ['lab116', 'lab118']  
    letters = %w(a b c d e f g h i j k l m n o p q r s t u v w x y z)
    hosts = labs.map{|lab| ([lab]*(letters.length)).zip(letters).map(&:join)  }.flatten
    hosts += ['titan', 'meteor', 'pulsar']
    hosts.find_all{|h| self.pingecho(h, 3) }
  end
  
  def self.assign_commands(command_list, prefix='cd src/smurf-lite/scripts ; source ~/.bash_profile ; ')
    
    hosts = self.pingable_hosts
    
    commands = {}

    command_list.each_with_index do |command, index|
      host = hosts[index % hosts.length]
      if prefix
        commands[host] ||= prefix 
      else
        commands[host] ||= ''
      end
      commands[host] += (command + '; ')
    end
    
    commands
  end
  
  def self.show_commands(commands)
    commands.keys.each do |host|
      cmd = "ssh -f #{host} '#{commands[host]}'&"
      puts cmd
    end
  end
  
  def self.run!(commands)
    commands.keys.each do |host|
      puts host
      cmd = "ssh -f -o StrictHostKeyChecking=no #{host} '#{commands[host]}'&"
      system(cmd)
    end
  end
  
end