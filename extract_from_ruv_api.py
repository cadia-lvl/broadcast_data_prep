#Author: Judy Fong
#Description: Extract subtitles and videos of approved shows from the RUV api
#License: Apache 2
#TODO: follow pep8
# consider using BeautifulSoup to parse links
#TODO: create a usage

import csv
import json
import os
import requests
import sys
import urllib.request
from RUV_show import Season, Programme

#download the subtitles and videos
def get_file(file_path, subtitle_url):
    print("Downloading episode to ", file_path)
    r = requests.get(subtitle_url, stream = True)

    with open(file_path, 'wb') as f:
        f.write(r.content)
    return

def create_directory(show_path):
    try:
        os.mkdir(show_path)
    except FileExistsError:
        print("Directory exists; using existing directory,  ", show_path)
        pass
    except:
        print("Failed to create directory, ", show_path)
        sys.exit()
    else:
        print("Created directory, ", show_path)
    return

def only_contains_header(subtitle_path):
    HEADER_ONLY = 10
    return os.stat(subtitle_path).st_size == HEADER_ONLY

def add_episode_to_missing_subtitles_list(missing_subtitles_file, show_title, episode_filename):
    with open(missing_subtitles_file, "a") as missing_text:
        writer = csv.writer(missing_text)
        #TODO: check if filename exists
        writer.writerow([show_title, episode_filename])

def load_json_files(url_roots, shows_json):
    import json

    #read urls
    with open(url_roots, 'r') as url_file:
        url_data = url_file.read()

    url_obj = json.loads(url_data)

    #with open(seasons_json, 'r') as seasons_file:
    #   season_data = seasons_file.read()

    #seasons_obj = json.loads(season_data)

    with open(shows_json, 'r') as shows_file:
        shows_data = shows_file.read()

    shows_obj = json.loads(shows_data)

    return url_obj, shows_obj;

def main(root_urls, shows):
    programs = []
    for show in shows["shows"]:
        # create python objects of the shows
        programs.append(Programme(show["name"], show["broadcast_method"], show["player_url"], show["approved"], show["seasons"]))
    exit(0)

    #TODO: make the working dir an argument
    working_dir = "/media/judyfong/externalDrive/RUV"
    if os.getcwd() == working_dir:
        print("Extracting data from the RUV API ...")
        #loop through the shows
        for program in programs:
            if program.approved:
                print("written program name", program.name)
                data = urllib.request.urlopen(program.player_url).read().decode()
                show = json.loads(data)
                print("Creating directories for ", show['title'])
                create_directory(os.getcwd() + "/transcripts/")
                transcript_path = os.getcwd() + "/transcripts/" + ''.join(e for e in show['title'] if e.isalnum())
                create_directory(transcript_path)
                create_directory(os.getcwd() + "/videos/")
                videos_path = os.getcwd() + "/videos/" + ''.join(e for e in show['title'] if e.isalnum())
                create_directory(videos_path)

                print("Downloading... ")
                #extract older content
                #within firewall only use the seasons url:
                for season in program.seasons:
                    season_url = root_urls["seasons_root_url"] + season
                    print(season_url)
                    season_data = urllib.request.urlopen(season_url).read().decode()
                    season_dict = json.loads(season_data)
                    for episode in season_dict['files']:
                        # download videos
                        #videos only available as mp4 within the RUV firewall
                        #Parse firstrun for date, always use 800kbps
                        #TODO: check if filename contains R
                        #All files with the R*.mp4 are located in the root folder 
                        #just filtering by checking if it has a folder for now
                        video_url = root_urls["video_root_url"] + (episode['folder'] + "/800kbps/" if episode['folder'] else '') + episode['filename']
                        print(video_url)
                        video_path = videos_path + "/" + episode['filename'] 
                        get_file(video_path, video_url)

                        subtitle_url = root_urls["subtitle_root_url"] + episode['filename'] + '/is'
                        print(subtitle_url)
                        subtitle_filename = os.path.splitext(episode['filename'])[0] + ".vtt"
                        subtitle_path = transcript_path + "/" + subtitle_filename
                        get_file(subtitle_path, subtitle_url)
                        if only_contains_header(subtitle_path):
                            os.remove(subtitle_path)
                            add_episode_to_missing_subtitles_list("missing_subtitles.csv", show['title'], episode['filename'])

                if not program.seasons:
                #not necessary to use player_urls if there are seasons,
                # so only loop through the player_url if the show does
                # not have seasons
                #these are the only publicly available episodes for the show
                    print("No seasons so downloading episodes from the online player url")
                    for episode in show['episodes']:
                        if not episode['subtitles_url']:
                            add_episode_to_missing_subtitles_list("missing_subtitles.csv", ''.join(e for e in show['title'] if e.isalnum()), episode['temp']['filename'])
                        else:
                            print(episode['subtitles_url'], "empty")
                            subtitle_filename = os.path.splitext(episode['temp']['filename'])[0] + ".vtt"
                            subtitle_path = transcript_path + "/" + subtitle_filename
                            #download the subtitle file
                            get_file(subtitle_path, episode['subtitles']['is'])
                            #a subtitle file with only has the header: WEBVTT (10 bytes)
                            # gets the title and filename added to the missing subtitles csv
                            if only_contains_header(subtitle_path):
                                os.remove(subtitle_path)
                                add_episode_to_missing_subtitles_list("missing_subtitles.csv", ''.join(e for e in show['title'] if e.isalnum()), episode['temp']['filename'])
                        #download videos
                        #videos only available as mp4 within the RUV firewall
                        #Parse firstrun for date, always use 800kbps
                        #don't need highest quality video since we're only using the audio
                        video_url = root_urls["video_root_url"] + episode['temp']['folder'] + "/800kbps/" + episode['temp']['filename']
                        video_path = videos_path + "/" + episode['temp']['filename']
                        #this works TODO rename get_file to something more appropriate
                        get_file(video_path, video_url)
                        #only use one of the streams
                        print(episode['file'])

    else:
        print("Called script from the wrong directory. Must call it from ", working_dir)
        print("Called from ", os.getcwd())
        sys.exit()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extract subtitles and videos from RUV api')
    parser.add_argument('--url-file', required=True, help='the path to the api urls file')
    parser.add_argument('--shows-file', required=True, help='the path to the shows file')
    args = parser.parse_args()
    #TODO: check if the shows file argument was given
    if args.url_file:
        root_urls, shows = load_json_files(args.url_file, args.shows_file)
        main(root_urls, shows)
    else:
        print('Two files must be given, an api urls file and a shows file.')
        exit(0)
