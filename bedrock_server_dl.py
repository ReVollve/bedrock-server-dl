import os
import sys
import time
import requests
import bs4
import json
import argparse
from enum import Enum

servers = {}


class Build(Enum):
    WINDOWS = 0
    LINUX = 1
    WIN_PREVIEW = 2
    LINUX_PREVIEW = 3


def latest_version(preview=False):
    """
    :param preview: Determines if the preview version shall be returned
    :return: string of the latest version
    """
    if not __first_request():
        return
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


def download(build: Build, folder=None):
    """
    Downloads given build with optional path.
    :param build: Build type. Example Build.LINUX will work
    :param folder: String to directory path
    :return: string to absolute file path
    """
    if not __first_request():
        return
    if build == Build.WINDOWS:
        url = servers['win']
    elif build == Build.LINUX:
        url = servers['linux']
    elif build == Build.WIN_PREVIEW:
        url = servers['win-preview']
    elif build == Build.LINUX_PREVIEW:
        url = servers['linux-preview']
    else:
        print("Download request malformed! ->", build)
        return
    if folder is None:
        folder = os.path.dirname(__file__)
    print("Starting downloading build type", build.name)
    print("Destination folder will be", folder)

    get_response = requests.get(url, stream=True)
    file_name = os.path.join(folder, url.split("/")[-1])
    try:
        with open(file_name, 'wb') as f:
            for chunk in get_response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    except:
        print("Download failed!")
        return
    print("Download complete!")
    return str(file_name)


def gen_versions():
    """
    Generates versions.json file.
    :return versions dict:
    """
    if not __first_request():
        return
    dictionary = servers.copy()
    dictionary["version"] = latest_version()
    dictionary["version-preview"] = latest_version(preview=True)

    json_obj = json.dumps(dictionary)

    with open("versions.json", "w") as out:
        out.write(json_obj)
    return dictionary


def print_info():
    """
    Prints information for links and versions
    """
    if not __first_request():
        return
    for key, value in servers.items():
        print("Gathered: {:>13} | {}".format(key, value))
    print("Latest version: {:>18}".format(latest_version()))
    print("Latest preview version: {:>10}".format(latest_version(preview=True)))


def request():
    """
    Retrieves the latest versions from minecraft.net.
    """
    url = 'https://minecraft.net/en-us/download/server/bedrock'
    azure = "https://minecraft.azureedge.net/"
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}
    r = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    servers_list = []
    for link in soup.find_all('a', {"class": "btn btn-disabled-outline mt-4 downloadlink"}):
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


def __first_request():
    if servers == {}:
        try:
            request()
        except:
            print("Couldn't request data from minecraft.net!")
            return False
    return True


def __main():
    if not __first_request():
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", help="Downloads given build with optional path")
    parser.add_argument("-p", "--path", help="Optional destination folder")
    parser.add_argument("-i", "--info", help="Prints version info", action='count', default=0)
    parser.add_argument("-v", "--vfile", help="Generates versions.json file", action='count', default=0)
    args = parser.parse_args()

    if args.v:
        gen_versions()
    if args.i:
        print_info()
    if not args.type:
        return
    if args.type == "WINDOWS":
        build = Build.WINDOWS
    elif args.type == "LINUX":
        build = Build.LINUX
    elif args.type == "WIN-PREVIEW":
        build = Build.WIN_PREVIEW
    elif args.type == "LINUX-PREVIEW":
        build = Build.LINUX_PREVIEW
    else:
        print("No or misspelled arguments were given")
        return
    download(build, args.path)


if __name__ == '__main__':
    __main()
