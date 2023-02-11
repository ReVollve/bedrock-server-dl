import requests
import bs4
import pathlib
import argparse
import json
from enum import Enum
from rich import print
from rich.progress import Progress

servers = {}


class Build(Enum):
    WINDOWS = 0
    LINUX = 1
    WIN_PREVIEW = 2
    LINUX_PREVIEW = 3


def latest_version(preview=False):
    result: str = None
    if not preview:
        result = servers['linux']
    if preview:
        result = servers['linux-preview']
    pos1 = result.rfind('.zip')
    result = result[:pos1]
    pos2 = result.find('1')
    result = result[pos2:]
    return result


def download(request: Build, folder=None):
    if request.value == 0:
        url = servers['win']
    elif request.value == 1:
        url = servers['linux']
    elif request.value == 2:
        url = servers['win-preview']
    elif request.value == 3:
        url = servers['linux-preview']
    else:
        print("Download request malformed! Please use numbers 0-3 for selection!")
        return
    if folder is None:
        folder = pathlib.Path().resolve()
    print("Starting downloading build type", request.name)
    print("Destination folder will be", folder)

    with Progress() as p:

        get_response = requests.get(url, stream=True)
        file_name = str(folder) + "/" + url.split("/")[-1]
        with open(file_name, 'wb') as f:
            size = len(get_response.content)
            task = p.add_task("[green]Downloading...", total=size)
            for chunk in get_response.iter_content(chunk_size=1024):
                p.update(task, advance=1024)
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return file_name


def print_info():
    for elem in servers.keys():
        print("Gathered: {:>13} | {}".format(elem, servers[elem]))
    print("Latest version: {:>18}".format(latest_version()))
    print("Latest preview version: {:>10}".format(latest_version(preview=True)))


def __request():
    url = 'https://minecraft.net/en-us/download/server/bedrock'
    azure = "https://minecraft.azureedge.net/"
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}
    r = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    links = soup.find_all('a')
    servers_list = []
    for link in links:
        ref: str = link.get('href')
        if ref.count(azure):
            servers_list.append(ref)
    for var in servers_list:
        if var.count("bin-win") and not var.count("preview"):
            servers["win"] = var
        if var.count("bin-linux") and not var.count("preview"):
            servers["linux"] = var
        if var.count("bin-win") and var.count("preview"):
            servers["win-preview"] = var
        if var.count("bin-linux") and var.count("preview"):
            servers["linux-preview"] = var


try:
    __request()
except Exception as e:
    print("An error appeared during the request! Shutting down ...")
    print(e)
    exit(-1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-type", help="Downloads given build with optional path")
    parser.add_argument("-path", help="Optional destination folder")
    parser.add_argument("-info", help="Shows version info", action='count', default=0)
    args = parser.parse_args()

    dictionary = servers.copy()
    dictionary["version"] = latest_version()
    dictionary["version-preview"] = latest_version(preview=True)

    json_obj = json.dumps(dictionary)

    with open("versions.json", "w") as out:
        out.write(json_obj)

    if args.info:
        print_info()
    if args.type is None:
        exit(0)
    build = None
    if args.type == "WINDOWS":
        build = Build.WINDOWS
    elif args.type == "LINUX":
        build = Build.LINUX
    elif args.type == "WIN-PREVIEW":
        build = Build.WIN_PREVIEW
    elif args.type == "LINUX-PREVIEW":
        build = Build.LINUX_PREVIEW
    else:
        print("No or misspelled arguments were given. Shutting down")
        exit(0)
    download(build, args.path)
    print("[green]Download complete!")
