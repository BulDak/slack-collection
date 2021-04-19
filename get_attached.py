import os
import sys
import argparse
import zipfile


parser=argparse.ArgumentParser()
parser.add_argument("-a", "--archive", action="store", dest="archive", help="Archived file of Slack workspace export")
parser.add_argument("-d", "--directory", action="store", dest="directory", help="Directory of unarchived Slack workspace export")
parser.add_argument("-o", "--output", action="store", dest="output", help="Output directory to store the attached in the workspace")
parser.set_defaults(output=".")
args = parser.parse_args()

def get_attached_url(path, input_type="archive"):
    attached_url=list()
    if input_type=="archive":
        with zipfile.ZipFile(path) as zfd:
            namelist=zfd.namelist()
            for name in namelist:
                if '/' in name and '.json' in name:
                    with zfd.open(name, 'r') as json_fd:
                        for line in json_fd.readlines():
                            line=line.decode()
                            line=line.strip()
                            if line.startswith('\"url_private\"'):
                                url=line.split(': ')[1][1:-3]
                                channel, date=name.split('/')
                                download_url=(url, channel, date)
                                attached_url.append(download_url)

    if input_type=="directory":
        for parent_directory, dir_names, file_names in os.walk(path):
            if len(parent_directory) > len(path):
                for name in file_names:
                    if '.json' in name:
                        with open(os.path.join(parent_directory, name), 'r', encoding="UTF8") as fd:
                            for line in fd.readlines():
                                line=line.strip()
                                if line.startswith('\"url_private\"'):
                                    download_url=line.split(': ')[1][1:-3]
                                    channel=os.path.split(parent_directory)[1]
                                    date=name.split(".")[0]
                                    attached_url.append((download_url,channel, date))

    return attached_url

def get_download_url(url):
    return url.split("?")[0].replace("\\", "").replace("https://files", "https://files-origin")

def main():
    path=None
    input_type=None
    if args.directory is not None:
        path=args.directory
        input_type='directory'
    if args.archive is not None:
        path=args.archive
        input_type='archive'

    for url, channel, chat_filename in get_attached_url(path, input_type):
        print (get_download_url(url), channel, chat_filename)
    
if __name__=="__main__":
    main()