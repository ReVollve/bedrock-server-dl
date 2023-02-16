# Description
**bedrock_server_dl** is a command-line program to download the **latest** minecraft bedrock servers from Minecraft.net. It is also possible to use the source code to download bedrock servers in your own project. The script also is capable of just giving out the exact latest version.

``python bedrock_server_dl.py [OPTIONS]``
### Options
```
  -h, --help  show this help message and exit
  -type TYPE  Downloads given build, with optional path
  -path PATH  Optional destination folder
  -info       Shows version info
  -vf         Generates versions.json file
```
Possible types are
- WINDOWS
- WIN-PREVIEW
- LINUX
- LINUX-PREVIEW

### Notes
- The versions.json file contains the latest links to the servers and the latest version itself

## Requirements
``pip install -r requirements.txt``