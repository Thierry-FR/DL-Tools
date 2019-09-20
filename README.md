# dl_tools : Easy forensic tools downloader for Windows

Usage :
         dl_tools.py / dl_tools.exe [-h] -t TOOL [-dr] [-p PROXY]

         Forensic tools easy downloader

         optional arguments:
                            -h, --help            
                            Show this help message and exit

                            -t TOOL, --tool TOOL
                             Tools matching the pattern (regex) in 'tools_list.csv' will be downloaded

                            -dr, --dryrun
                            Print matching lines in 'tools_list.csv'

                            -p PROXY, --proxy PROXY
                             Proxy informations : PROXY:PORT


         tools_list.csv :   List of downloadable programs
                            Names finishing with "_" indicates that a specific version will be downloaded. Link has to be updated when a newer version comes.         
                            Names finishing with "_release" indicates that the latest release of the Github repository will be downloaded



AV Alert :
It seems that the compiled version of this script is sometimes detected as suspicious by AV.
The script was compiled using "auto-py-to-exe" tool (https://pypi.org/project/auto-py-to-exe/)
The script contains no virus as you can check by yourself.
Updating the Windows Defender signature definitions solved the problem in my case.


