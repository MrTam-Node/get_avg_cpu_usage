############################################################################################
# This script is tested and compatible with the python version 3.10                        #
# make sure all python dependencies are installed to be able to import the listed modules. #
# This script was written and executed on a windows machine.                               #
# it can be adapted to a linux machine, by modifying few things like the file paths etc.   #
############################################################################################ 

import requests
import json
import re
import os
import subprocess
import csv
import statistics

################################################
# path to a folder containing .txt files       #
# of all my instances hostnames on Centreon    #
################################################

file_path = r'C:\Users\Documents\projects\get_cpu_ram\servers'


#############################################
# list the files in the folder              #
#############################################

def process_files_in_directory(directory):
    try:
        # Get a list of all files in the specified directory
        files = os.listdir(directory)

        # Iterate over each file in the directory
        for file in files:
            file_path = os.path.join(directory, file)

            # Check if the item is a file with .txt extension
            if os.path.isfile(file_path) and file.endswith('.txt'):
                print(f"Processing file: {file_path}")
                with open(file_path, 'r') as f:
                    contents = f.read()
                    print(contents)
                print()  # Print an empty line for separation

    except FileNotFoundError:
        print(f"The directory '{directory}' does not exist.")

# Provide the path to the directory you want to process
#directory_path = r"C:\Users\Documents\servers"

# Call the function to process the .txt files in the directory
process_files_in_directory(file_path)



######################################################
# A function to get CPU usage using Centreon's API   #
# from hostnames in a file                           #
######################################################

def get_cpu_usage(file_path):
    # URL and options
    url = "https://centreon.domain.net/centreon/api/index.php"
    option_cpu = "object=centreon_realtime_services&action=list&searchHost={}&searchOutput=CPU(s)&fields=host_name,output"

  # données authentification
    payload = {'username': 'your username', 'password': 'your password'}

    # Authentication request
    auth_response = requests.post(f"{url}?action=authenticate", data=payload, verify=False) #verify=false so as to bypass ssl verification of the request. 
    auth_token = auth_response.json()['authToken']

    # Initialize header with the auth token
    headers = {'centreon-auth-token': auth_token}

    # Read server names from file
    with open(file_path, 'r') as f:
        servers = f.read().splitlines()

    # Get CPU usage for each server
    total_cpu_usage = 0
    #cpu_usages = {}
    for server in servers:
        cpu_response = requests.get(f"{url}?{option_cpu.format(server)}", headers=headers, verify=False) #verify=false so as to bypass ssl verification of the request. 
        
        cpu_output = cpu_response.text
        
        cpu_pattern = re.compile(r'\d+ CPU\(s\)')
        cpu_usage_pattern = re.compile(r'(\d+\.\d+) %')

        cpu_match = cpu_pattern.search(cpu_output)
        if cpu_match:
            cpu = cpu_match.group(0)

        cpu_usage_match = cpu_usage_pattern.search(cpu_output)
        if cpu_usage_match:
            #cpu_usage = cpu_usage_match.group(0)
            cpu_usage = float(cpu_usage_match.group(0).split()[0])
            print(cpu_usage)
            total_cpu_usage += cpu_usage
        #cpu[server] = { 'cpu': cpu}
        
    # Calculate the average memory usage
    avg_cpu_usage = round(total_cpu_usage / len(servers))

    #Option A: you can activate this option and disactivate option B if you want to know the average CPU usage and number of available CPUs.#
    #return avg_cpu_usage, cpu

    #Option B: you can activate this option if you want to know only the average CPU usage#
    return avg_cpu_usage


######################################################
# A function to get RAM usage using Centreon's API   #
# from hostnames in a file                           #
######################################################

def get_mem_usage(file_path):
    # URL and options
    url = "https://centreon.domain.net/centreon/api/index.php"
    option_mem = "object=centreon_realtime_services&action=list&searchHost={}&searchOutput=Ram&fields=host_name,output"

  # données authentification
    payload = {'username': 'your username', 'password': 'your password'}

    # Authentication request
    auth_response = requests.post(f"{url}?action=authenticate", data=payload, verify=False) #verify=false so as to bypass ssl verification of the request. 
    auth_token = auth_response.json()['authToken']

    # Initialize header with the auth token
    headers = {'centreon-auth-token': auth_token}

    # Read server names from file
    with open(file_path, 'r') as f:
        servers = f.read().splitlines()
    mem_usages = {}
    total_mem_usage = 0
    for server in servers:
        mem_response = requests.get(f"{url}?{option_mem.format(server)}", headers=headers, verify=False) #verify=false so as to bypass ssl verification of the request. 
        mem_output = mem_response.text

        mem_pattern = re.compile(r'(\d+\.\d+) GB')
        mem_usage_pattern = re.compile(r'(\d+\.\d+) GB \((\d+\.\d+)%')

        mem_match = mem_pattern.search(mem_output)
        if mem_match:
            mem = mem_match.group(0)
    
        mem_usage_match = mem_usage_pattern.search(mem_output)
        if mem_usage_match:
            #mem_usage = mem_usage_match.group(2)
            mem_usage = float(mem_usage_match.group(2))
            total_mem_usage += mem_usage
            #mem[server] = {'mem': mem}
    
      # Calculate the average memory usage
    avg_mem_usage = round(total_mem_usage / len(servers))
    
    #Option A: you can activate this option and disactivate option B if you want to know the average RAM usage and number of available RAM.#
    #return avg_mem_usage, mem

    #Option B: you can activate this option if you want to know only the average RAM usage#
    return avg_mem_usage


##############################################################################
# A variable to store the interated CPU and RAM                              #
# results of all the instances.                                              #
#                                                                            #
# Note: You will need to specify the full path                               #
# of each file containing hostnames if using                                 #
# python 3.7                                                                 #
#                                                                            #
# Example: r'C:\Users\Documents\projects\get_cpu_ram\servers\selfcare.txt'   #
# or create a variable like this:                                            #
# selfcare = r'C:\Users\Documents\projects\get_cpu_ram\servers\selfcare.txt' #
# and use the varaible as: get_cpu_usage(selfcare)                           #
##############################################################################


data = {
        'CPU_selfcare': get_cpu_usage('selfcare.txt'),
        'RAM_selfcare': get_mem_usage('selfcare.txt'),
        'CPU_nav': get_cpu_usage('nav.txt'),
        'RAM_nav': get_mem_usage('nav.txt'),
        'CPU_indexeur': get_cpu_usage('indexeur.txt'),
        'RAM_indexeur': get_mem_usage('indexeur.txt'),
        'CPU_pricing': get_cpu_usage('pricing.txt'),
        'RAM_pricing': get_mem_usage('pricing.txt'),
        'CPU_scoring': get_cpu_usage('scoring.txt'),
        'RAM_scoring': get_mem_usage('scoring.txt'),
        'CPU_dispo': get_cpu_usage('dispo.txt'),
        'RAM_dispo': get_mem_usage('dispo.txt'),
        'CPU_order': get_cpu_usage('order.txt'),
        'RAM_order': get_mem_usage('order.txt'),
        'CPU_innovente': get_cpu_usage('innovente.txt'),
        'RAM_innovente': get_mem_usage('innovente.txt'),
        'CPU_notifg': get_cpu_usage('notifg.txt'),
        'RAM_notifg': get_mem_usage('notifg.txt'),
        'CPU_mpi': get_cpu_usage('mpi.txt'),
        'RAM_mpi': get_mem_usage('mpi.txt'),
        'CPU_comparateur': get_cpu_usage('comparateur.txt'),
        'RAM_comparateur': get_mem_usage('comparateur.txt'),
    }

######################################################
# Check the variable $data to see the results        #
# of the functions.                                  #
# You can delete this or leave it                    #
######################################################
print(data)


######################################################
# Output the results in the variable $data           #
# to a JSON file                                     #
######################################################

json_file = r'C:\Users\Documents\projects\get_cpu_ram\csv_json\data_json.json'
with open(json_file, 'w') as outfile:
    json.dump(data, outfile, indent=4)
    


######################################################
# Output the results in the variable $data           #
# to a CSV file                                      #
######################################################

csv_file = r'C:\Users\Documents\projects\get_cpu_ram\csv_json\Avg_Cpu_Ram.csv'
# Check if the file exists and has a non-zero size
if os.path.isfile(csv_file) and os.path.getsize(csv_file) > 0:
    
# Open the CSV file in append mode and write the header if the file is empty
   with open(csv_file, 'a', newline='') as f:
       writer = csv.writer(f)
       writer.writerow([data['CPU_selfcare'], data['RAM_selfcare'], data['CPU_nav'], data['RAM_nav'], data['CPU_indexeur'], data['RAM_indexeur'], data['CPU_pricing'], data['RAM_pricing'],data['CPU_scoring'], data['RAM_scoring'], data['CPU_order'], data['RAM_order'], data['CPU_dispo'], data['RAM_dispo'], data['CPU_innovente'], data['RAM_innovente'], data['CPU_notifg'], data['RAM_notifg'], data['CPU_mpi'], data['RAM_mpi'], data['CPU_comparateur'],data['RAM_comparateur']])
else: 
    # Open the CSV file in write mode and write the header
   with open(csv_file, 'w', newline='') as f:
      writer = csv.writer(f, lineterminator='')
      writer.writerow(['CPU_selfcare', 'RAM_selfcare', 'CPU_nav', 'RAM_nav', 'CPU_indexeur', 'RAM_indexeur', 'CPU_pricing', 'RAM_pricing', 'CPU_scoring', 'RAM_scoring', 'CPU_order', 'RAM_order', 'CPU_dispo', 'RAM_dispo', 'CPU_innovente', 'RAM_innovente', 'CPU_notifg', 'RAM_notifg', 'CPU_mpi', 'RAM_mpi', 'CPU_comparateur', 'RAM_comparateur'])
      f.flush()
      f.write('\n')
      writer.writerow([data['CPU_selfcare'], data['RAM_selfcare'], data['CPU_nav'], data['RAM_nav'], data['CPU_indexeur'], data['RAM_indexeur'], data['CPU_pricing'], data['RAM_pricing'],data['CPU_scoring'], data['RAM_scoring'], data['CPU_order'], data['RAM_order'], data['CPU_dispo'], data['RAM_dispo'], data['CPU_innovente'], data['RAM_innovente'], data['CPU_notifg'], data['RAM_notifg'], data['CPU_mpi'], data['RAM_mpi'], data['CPU_comparateur'],data['RAM_comparateur']])
    
    

                    
  
