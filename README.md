# Description
**bedrock-server-dl** is a command-line program to download minecraft bedrock servers from Minecraft.net. It is also possible to use the python code to download bedrock servers in your own project.

``bedrock-server-dl [OPTIONS]``
### Options
```
  -h, --help  show this help message and exit
  -type TYPE  Downloads given build, with optional path
  -path PATH  Optional destination folder
  -info       Shows version info
```
Possible types are
- WINDOWS
- WIN-PREVIEW
- LINUX
- LINUX-PREVIEW

### Notes
- When run, it will generate a versions.json file, which contains all links and available versions.