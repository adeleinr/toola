#!../../../bin python
import os
import glob
import settings

host_ip_tag = 'HOST_IP_TAG'
host_ip_replacement = str(settings.HOST_IP)+":"+ str(settings.PORT)
 
dir = "media_rsc/js/*.js.tpl"
files = glob.glob(dir)



for file in files:
  output_file_name = file.partition('.')[0]+".js"
  new_file_content = [] 
  f = open(file, 'rU')
  for line in f:   ## iterates over the lines of the file
                   ## since 'line' already includes the end-of line.
    new_file_content.append(line.replace(host_ip_tag, host_ip_replacement))
  outfile = open(output_file_name, 'w')
  outfile.writelines(new_file_content)
  f.close() 
