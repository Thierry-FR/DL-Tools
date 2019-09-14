# dl_tools : Easy forensic tools downloader for Windows

Usage :
         dl_tools.py/dl_tools.exe [-h] -t TOOL [-p PROXY]

         Forensic tools easy downloader

         optional arguments:
                            -h, --help            
                            Show this help message and exit

                            -t TOOL, --tool TOOL
                             Tools matching the pattern (regex) in 'tools_list.csv' will be downloaded

                            -p PROXY, --proxy PROXY
                             Proxy informations : PROXY:PORT


         tools_list.csv :   List of downloadable programs
                            Names finishing with "_" indicates that a specific version will be downloaded. Link has to be updated when a newer version comes.         
                            Names finishing with "_release" indicates that the latest release of the Github repository will be downloaded
