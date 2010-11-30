#!../../../bin python
import os
import glob
import settings

host_ip_tag = 'HOST_IP_TAG'
host_ip = settings.HOST_IP
 
dir = "media_rsc/js/*.js"
files = glob.glob(dir)



for file in files:
  new_file_content = [] 
  f = open(file, 'rU')
  for line in f:   ## iterates over the lines of the file
                   ## since 'line' already includes the end-of line.
    new_file_content.append(line.replace(host_ip_tag, host_ip))
  outfile = open(file, 'w')
  outfile.writelines(new_file_content)
  f.close() 
