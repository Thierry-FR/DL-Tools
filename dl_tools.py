#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#########  DESCRIPTION  #########


# dl_tools : Easy forensic tools downloader for Windows

# Usage :
#         dl_tools.py [-h] -t TOOL [-p PROXY]
#
#         Forensic tools easy downloader
#
#         optional arguments:
#                            -h, --help            show this help message and exit
#
#                            -t TOOL, --tool TOOL
#                             Tools matching the pattern (regex) in 'tools_list.csv' will be downloaded. Patterns can be seperated by ",".
#
#                            -dr, --dryrun
#                            Print matching lines in 'tools_list.csv'
#
#                            -p PROXY, --proxy PROXY
#                             Proxy informations : PROXY:PORT
#                                
#                            -n, --newonly
#                            Download tool only if tool folder doesn't exist in "tools" folder

#         tools_list.csv :   List containing informations concerning downloadable programs.
#                            Names finishing with "_" indicates that a specific version will be downloaded. Link has to be updated when a newer version comes.         
#                            Names finishing with "_release" indicates that the latest release of the Github repository will be downloaded.
#                            Lines beginning with "# or #" will not be taken into account.  



#########  IMPORTS  #########


import argparse
import os
import urllib.request
import re
import shutil
import zipfile
import ssl
import pathlib
import time
import sys


#########  INIT  #########


## Variables

script_folder = pathlib.Path.cwd()
tools_folder = script_folder / "tools"
tools_list = script_folder / "tools_list.csv"


## Checking files


def redo_with_write(redo_func, path, err):
    """ Change file rights (readonly) so rmtree can work"""
    # Arguments: the function that failed, the path 
    # it failed on, and the error that occurred.
       
    path.chmod(S_IWRITE)
    redo_func(path)
      
if not (tools_folder).exists():    
    (tools_folder).mkdir()

if not (tools_list).is_file():    
    print("\nError - File 'tools_list.csv' not found !\n")
    sys.exit()
   
    
#########  ARGUMENTS #########


parser=argparse.ArgumentParser(description="Forensic tools easy downloader",epilog="Thierry-FR - Version : 0.1.1\n\n\n")
parser.add_argument("-t", "--tool", help="Tools matching the pattern (regex) in 'tools_list.csv' will be downloaded", required=True)
parser.add_argument("-dr", "--dryrun", help="Print matching lines in 'tools_list.csv'", action="store_true")
parser.add_argument("-p", "--proxy", help="Proxy informations : PROXY:PORT")
#parser.add_argument("-n", "--newonly", help="Download tool only if tool folder doesn't exist", action="store_true")
args=parser.parse_args()

    
#########  CLASSES  #########


class Tool_To_Be_Downloaded(): 
    """File to download class"""
    
    def __init__(self, name, editor_name,category,dl_url):
        """Initialize object."""
        self.name = name
        self.editor_name = editor_name
        self.category = category
        self.dl_url = dl_url
        
        self.filename = (pathlib.Path(dl_url)).name
        self.tool_folder = tools_folder / self.name
        self.destination_file = self.tool_folder / self.filename
        

    ## Download


    def download_tool(self):
        """ Downloading the tool in destination folder"""
        
        # "Not verified SSL error" workaround :
        
        if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
            ssl._create_default_https_context = ssl._create_unverified_context        
        
        # Deleting/creating tool folder :
        
        if (self.tool_folder).exists():
            shutil.rmtree(self.tool_folder,onerror=redo_with_write)
            time.sleep(1)
        
        (self.tool_folder).mkdir()

        print("\tDownloading...")

        try:
            
            # Using Proxy : 
            
            if args.proxy:
                my_proxy = str(args.proxy)
                proxy = urllib.request.ProxyHandler({'https': my_proxy, 'http': my_proxy})
                opener = urllib.request.build_opener(proxy)
                urllib.request.install_opener(opener)
            
            
            # Download github latest release (with latest tag) :
            
            
            if re.match("https://api.github.com/repos/.*/releases/latest",self.dl_url,re.IGNORECASE):
                
                try:
                    req = urllib.request.Request(self.dl_url)
                    resp = urllib.request.urlopen(req)
                    resp_data = resp.read()
                   
                   # "browser_download_url" exploitation
                   
                    release_files = re.findall('browser_download_url":"(https://github.com/[^"]+\.(?:exe|msi|zip))',str(resp_data))
                    
                    if release_files:
                    
                        for release_file in release_files:
                            release_file_name = (pathlib.Path(release_file)).name
                            release_destination_file = self.tool_folder / release_file_name
                    
                            try:
                                urllib.request.urlretrieve(release_file,release_destination_file)
                            except Exception as error:
                                print("Error - Error downloading release file " + str(release_file) + " : ")
                                print(str(error))


                    # "zipball" exploitation
                    
                    else:
                        release_files = re.findall(r'zipball_url":"(https://api.github.com/repos/[^"]+/zipball/[^"]+)"',str(resp_data))
                                        
                        for release_file in release_files:
                            release_file_name = (pathlib.Path(release_file)).name
                        
                            # Releases without archive name :
                        
                            if not release_file_name.endswith(".zip"):
                                release_file_name = str(release_file_name) + ".zip"
                                release_destination_file = self.tool_folder / release_file_name
                            
                            try:
                                urllib.request.urlretrieve(release_file,release_destination_file)
                            except Exception as error:
                                print("Error - Error downloading release archive " + str(release_file) + " : ")
                                print(str(error))
                    
                except Exception as error:
                    print("Error - Error parsing  " + str(self.dl_url) + " : ")
                    print(str(error))


            # Download github latest release (without "latest" tag) :
                       
            elif re.match("https://github.com/.*/releases$",self.dl_url,re.IGNORECASE):
            
                try:
                    req = urllib.request.Request(self.dl_url)
                    resp = urllib.request.urlopen(req)
                    resp_data = resp.read()
                    
                    release_files = re.findall('href="(/[^"]+/archive/[^"]+\.zip)\"',str(resp_data))
                    release_file = "https://github.com" + str(release_files[0])
                    
                    release_destination_file = self.tool_folder / pathlib.Path(release_file).name
                    
                    try:
                        urllib.request.urlretrieve(release_file,release_destination_file)
                    except Exception as error:
                        print("Error - Error downloading release archive " + str(release_file) + " : ")
                        print(str(error))
                    
                except Exception as error:
                    print("Error - Error parsing  " + str(self.dl_url) + " : ")
                    print(str(error))           
                    
            
            # Download link without file name or Malzilla
                     
            elif re.match("^.*/.*\?.*=.*$|^.*package.Malzilla%20",self.dl_url,re.IGNORECASE):
                   
                self.destination_file = self.tool_folder / self.name
                
                try:                      
                    
                    # Link targets a file with extension :
                     
                    if re.match("^.*\.(pl|ps1|vbs|exe|py)$",self.dl_url,re.IGNORECASE):
                      
                        file_suffix = pathlib.Path(self.dl_url).suffix

                        self.destination_file = str(self.destination_file) + file_suffix
                        urllib.request.urlretrieve(self.dl_url,self.destination_file)
                             
                     
                    # Link targets a file without extension :
                    
                    else: 
                        urllib.request.urlretrieve(self.dl_url,self.destination_file)
                    
                        if (self.destination_file).exists():
                            with open(self.destination_file,'rb') as destination_file_hdl:
                                destination_file_header = destination_file_hdl.read(10)
                                destination_file_hdl.close()

                            if re.match(b"^MZ.*",destination_file_header):
                                (self.destination_file).rename(str(self.destination_file) + ".exe")
                        
                            elif re.match(b"^PK.*",destination_file_header):
                                (self.destination_file).rename(str(self.destination_file) + ".zip")

                except Exception as error:
                    print("Error - Error downloading " + str(self.dl_url) + " : ")
                    print(str(error))
                          
            
            # Download classic ".zip" files :
            
            else:
                
                try :                      
                    urllib.request.urlretrieve(self.dl_url,self.destination_file)
                except Exception as error:
                    print("Error - Error downloading " + str(self.dl_url) + " : ")
                    print(str(error))
                    print(str("Downloading issue may occures when contacted server is busy. Please try again."))

        except Exception as error:
            print("Error - Error downloading " + str(self.dl_url) + " : ")
            print(str(error))


    ## Unzip downloaded archives
            
    def unzip(self):
        """Uncompressing downloaded archives """
        
        zip_files = (self.tool_folder).glob('*.zip')
        
        if len(list(zip_files)) > 0:
            print("\tExtracting...")
            zip_files = (self.tool_folder).glob('*.zip') 
            
        for zip in zip_files:
            if (zip).is_file():
                extract_folder = self.tool_folder / zip.stem
                
                try:
                    with zipfile.ZipFile(zip, 'r') as zip_archive:
                        zip_archive.extractall(extract_folder)
                        
                except Exception as error:
                    print("Error - Error unzipping " + str(zip) + " :" )
                    print(str(error))
                    print(str("Unzipping issue might be consecutive to AV detection."))
            else:
                print("Error - Error unzipping : file " + str(zip) + " not found !" )



#########  FUNCTIONS  #########


def print_title():
    title="---  DOWNLOAD FORENSIC TOOLS  ---"

    print("\n\n")
    print("=".center(60,"="))
    print()
    print(title.center(60))
    print()
    print("=".center(60,"="))
 
def print_version():
    print()
    print("\t\t\t\t\t\tv0.1.1 - Thierry-FR")
    print("\n")

    

def generate_tools_list_dict(list_name,tools_pattern):
    """Parsing the 'tools_list.csv' file to return a list containing dictionary items generated from lines matching the pattern"""
    
    with open(tools_list) as hdl_tools_list:
        lines = hdl_tools_list.readlines()

    separated_patterns= list()
    separated_patterns = tools_pattern.split(',')

    list_name = []
    
    for line in lines:
        
        if not re.match("^(\")?Name.*URL(\")?$|^(\")?#", line):
             
            for pattern in separated_patterns:
             
                if re.findall(pattern,line,re.IGNORECASE):

                    new_file_to_download = {
                        'name' : (line.split(";")[0]).strip('"'),
                        'category' : (line.split(";")[1]).strip('"'),
                        'editor' : (line.split(";")[2]).strip('"'),
                        'dl_url' : ((line.split(";")[3]).strip("\n")).strip('"'),    ## remove "/n" and '"'
                    }
                    
                    list_name.append(new_file_to_download)
        
    hdl_tools_list.close()
        
    return list_name
    
    
#########  MAIN  #########


print_title()
print_version()


### ARGUMENT "TOOL"


if args.tool:

    if args.tool in ("All","all","ALL","*") :
        args.tool = ".*"
        
    tool_arg_list = list()
    final_list = generate_tools_list_dict(tool_arg_list,args.tool)
    
    if not final_list:
        print("\nSorry, no tool matches your regex !\n")
    else:    
        for f in final_list:
            
           # print(f)
        
            if args.dryrun:
                print("[+] " + str(f['name']) + " - " + str(f['category']))
            
            else:
                dl_this_file = Tool_To_Be_Downloaded(f['name'],f['editor'],f['category'],f['dl_url'])
                print("\n[+] " + str(f['name']))
                dl_this_file.download_tool()
                dl_this_file.unzip()
            

print("\n\nThe End !\n")
    