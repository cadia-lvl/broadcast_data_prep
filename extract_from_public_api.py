#Author: Judy Fong
#Description: Extract subtitles and videos from the RUV api to the working directory
#TODO: follow pep8
# consider using BeautifulSoup to parse links


import csv
import json
import os
import requests
import sys
import urllib.request

#download the subtitles
def get_subtitles(file_path, subtitle_url):
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

def main():

    # create dictionary of shows and their urls
    #NOTE: dictionaries might be better as command line inputs
    #NOTE: also consider turning them into something that can be converted to a python object
    recent_programs = {'Kiljan': 'https://api.ruv.is/api/programs/program/25779/all',
                'Krakkafréttir': 'https://api.ruv.is/api/programs/program/24081/all',
                'Stundin okkar': 'https://api.ruv.is/api/programs/program/27792/all'}

    # not exactlty available on the API
    older_programs = {  'Gettubetur': '', 
                        'Vikan': 'https://api.ruv.is/api/programs/program/27861/all', 
                        'Fréttir': '', 
                        'Tíufréttir': '',
                        'Áramotaskaupið': ''}

    subtitle_root_url = 'https://api.ruv.is/api/subtitles/'

    #json object: id, title, episodes {event, title/firstrun, subtitles_url}
    # save the subtitle url as temp{filename}.srt within the folder id/title
    #TODO: make the working_dir an argument
    print("Extracting data from the RUV API ...")
    #TODO: loop through the shows
    for program, player_url in  recent_programs.items():
        data = urllib.request.urlopen(player_url).read().decode()
        show = json.loads(data)
        print("Downloading ", show['title'])
        create_directory(os.getcwd() + "/transcripts/")
        transcript_path = os.getcwd() + "/transcripts/" + show['title'].replace(" ","_")
        create_directory(transcript_path)

        #loop through episodes until there are no more
        for episode in show['episodes']:
            subtitle_filename = os.path.splitext(episode['temp']['filename'])[0] + ".srt"
            subtitle_path = transcript_path + "/" + subtitle_filename
            #download the subtitle file
            get_subtitles(subtitle_path, episode['subtitles']['is'])
            #a subtitle file with only has the header (10 bytes) 
            # gets the title and filename added to the missing subtitles csv
            # file of all the episodes and show titles to give to RUV
            #header_only = 10
            #if os.stat(subtitle_path).st_size == header_only:
            #    os.remove(subtitle_path)
            #    with open("missing_subtitles.csv", "a") as missing_text:
            #        writer = csv.writer(missing_text)
            #        writer.writerow([show['title'] , episode['filename']])
            #TODO: create a metadata file with title, event/episodeid, air date, genre, duration, format
    sys.exit()

if __name__ == '__main__':
    main()
#TO extract only the text from the subtitles if for some reason we want that: sed '/^\s*$/d' filename | sed '/^[0-9]/d' > srt_filename.txt
#doesn't work if a subtitle starts with a number
