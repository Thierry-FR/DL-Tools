#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#########  DESCRIPTION  #########


#########  RESSOURCES  #########


# https://pythonprogramming.net/parse-website-using-regular-expressions-urllib/
# https://tutorials.technology/tutorials/guess-mime-type-with-python.html
# https://realpython.com/read-write-files-python/#buffered-binary-file-types

# tools : zimmerman, mitec; harlan carvey, vss carver, wmi,  
# https://blog.didierstevens.com/my-software/

#########  IMPORTS  #########


import argparse
import os
import urllib.request
import re
import shutil
import zipfile
import stat
import ssl


#########  INIT  #########


## variables

script_folder = os.path.dirname(os.path.abspath(__file__))
tools_folder = script_folder + "\\tools"
tools_list = script_folder + "\\tools_list.csv" 

## checking files

# temp

def redo_with_write(redo_func, path, err):
    """ Change file rights (readonly) so rmtree can work"""
    # arguments: the function that failed, the path 
    # it failed on, and the error that occurred.
   
    os.chmod(path, stat.S_IWRITE)
    redo_func(path)
    
    
#if os.path.exists(tools_folder):  
#    shutil.rmtree(tools_folder,onerror=redo_with_write)
    
if not os.path.exists(tools_folder):
    os.makedirs(tools_folder)

if not os.path.isfile(tools_list):
    print("Error - File 'tools_list.csv' not found !")

## handle
    
    
#########  ARGUMENTS #########


parser=argparse.ArgumentParser(description="Forensic tools easy downloader",epilog="Done by Thierry G. - Version : 0.1\n\n")
parser.add_argument("-t", "--tool", help="Tools matching the pattern (regex) in 'tools_list.csv' will be downloaded", required=True)
parser.add_argument("-p", "--proxy", help="Proxy informations : PROXY:PORT")
args=parser.parse_args()


# add proxy compatibility


#########  VARIABLES  #########

    
#########  CLASSES  #########


class Tool_To_Be_Downloaded(): 
    """File to download class"""
    
    def __init__(self, name, editor_name,category,dl_url):
        """Initialize object."""
        self.name = name
        self.editor_name = editor_name
        self.category = category
        self.dl_url = dl_url
        
        self.filename = os.path.basename(dl_url)
        self.tool_folder = tools_folder + "\\" + self.name
        self.destination_file = self.tool_folder + "\\" + self.filename


    def download_tool(self):
        """ Downloading the tool in destination folder"""
        
        # Not verfied SSL error workaround :
        
        if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
            ssl._create_default_https_context = ssl._create_unverified_context        
        
        # deleting/creating tool folder :
        
        if os.path.exists(self.tool_folder):
            shutil.rmtree(self.tool_folder,onerror=redo_with_write)
        
        os.makedirs(self.tool_folder)

        print("\tDownloading...")

        try:
            
            # Using Proxy : 
            
            if args.proxy:
                my_proxy = str(args.proxy)
                proxy = urllib.request.ProxyHandler({'https': my_proxy, 'http': my_proxy})
                opener = urllib.request.build_opener(proxy)
                urllib.request.install_opener(opener)
            
            
            # Download release files :
            
            
            if re.match("https://api.github.com/repos/.*/releases/latest",self.dl_url,re.IGNORECASE):
                
                try:
                    req = urllib.request.Request(self.dl_url)
                    resp = urllib.request.urlopen(req)
                    resp_data = resp.read()
                    
                    release_files = re.findall(r'browser_download_url":"(https://github.com/[^"]+\.zip)',str(resp_data))
                    
                    if not release_files:
                        release_files = re.findall(r'zipball_url":"(https://api.github.com/repos/[^"]+/zipball/[^"]+)"',str(resp_data))
                    
                    for release_file in release_files:
                        release_file_name = os.path.basename(release_file)
                        
                        # cas des release ne contenant pas de nom d'archive :
                        
                        if not release_file_name.endswith(".zip"):
                            release_destination_file = self.tool_folder + "\\" + release_file_name + ".zip"
                        else:
                            release_destination_file = self.tool_folder + "\\" + release_file_name
                        
                        try:
                            urllib.request.urlretrieve(release_file,release_destination_file)
                        except Exception as error:
                            print("Error - Error downloading release archive " + str(release_file) + " : ")
                            print(str(error))
                    
                except Exception as error:
                    print("Error - Error parsing  " + str(self.dl_url) + " : ")
                    print(str(error))
            
            
            # download link without file name
            
            
            elif re.match("^.*/.*\?.*=.*$|^.*package.Malzilla%20",self.dl_url,re.IGNORECASE):
                               
                self.destination_file = self.tool_folder + "\\" + self.name
                
                try:                      
                    urllib.request.urlretrieve(self.dl_url,self.destination_file)
                    
                    if os.path.exists(self.destination_file):
                        with open(self.destination_file,'rb') as destination_file_hdl:
                            destination_file_header = destination_file_hdl.read(10)
                        
                        destination_file_hdl.close()

                        if re.match(b"^MZ.*",destination_file_header):
                            os.rename(self.destination_file, self.destination_file + ".exe")
                        
                        elif re.match(b"^PK.*",destination_file_header):
                            os.rename(self.destination_file, self.destination_file + ".zip")

                except Exception as error:
                    print("Error - Error downloading " + str(self.dl_url) + " : ")
                    print(str(error))
                          
            
            # Download classic .zip files :
            
            else:
                try :                      
                    urllib.request.urlretrieve(self.dl_url,self.destination_file)
                except Exception as error:
                    print("Error - Error downloading " + str(self.dl_url) + " : ")
                    print(str(error))

        except Exception as error:
            print("Error - Error downloading " + str(self.dl_url) + " : ")
            print(str(error))


    def unzip(self):
        """Uncompressing downloaded archives """
        
        zip_files = []
        for r, d, f in os.walk(self.tool_folder):
            for file in f:
                if '.zip' in file:
                    
                    zip_files.append(os.path.join(r, file))
        
                    print("\tExtracting...")
        
                    for z in zip_files:
                        if os.path.isfile(z):
                            extract_folder = self.tool_folder + "\\" + str(os.path.splitext(os.path.basename(z))[0])
                
                            try:
                                with zipfile.ZipFile(z, 'r') as zip_archive:
                                    zip_archive.extractall(extract_folder)
                            except Exception as error:
                                print("Error - Error unzipping " + str(z) + " :" )
                                print(str(error))
                        else:
                            print("Error - Error unzipping : file " + str(z) + " not found !" )

         

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
    print("\t\t\t\t\t\tv0.1 - T.G.")
    print("\n")

    

def generate_tools_list_dict(list_name,pattern):
    """Parsing the 'tools_list.csv' file to return a list containing dictionary items generated from lines matching the pattern"""
    
    with open(tools_list) as hdl_tools_list:
        lines = hdl_tools_list.readlines()
    
    list_name = []
    
    for line in lines:
        
        if not re.match("^Name.*URL$", line):

            if re.findall(pattern,line,re.IGNORECASE):

                new_file_to_download = {
                    'name' : line.split(";")[0],
                    'category' : line.split(";")[1],
                    'editor' : line.split(";")[2],
                    'dl_url' : (line.split(";")[3]).strip(),
                    }
                list_name.append(new_file_to_download)
        
    hdl_tools_list.close()
        
    return list_name
    

    
#########  MAIN  #########


print_title()
print_version()


### ARGUMENT "TOOL"


if args.tool:

    if args.tool in ("All","all","ALL") :
        args.tool = ".*"
        
    tool_arg_list = []
    final_list = generate_tools_list_dict(tool_arg_list,args.tool)
    
    for f in final_list:
        dl_this_file = Tool_To_Be_Downloaded(f['name'],f['editor'],f['category'],f['dl_url'])
        print("\n[+] " + str(f['name']))
        dl_this_file.download_tool()
        dl_this_file.unzip()
            

print("\n\nThe End !\n")
    