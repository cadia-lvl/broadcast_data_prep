# Broadcast Data Prep
Extracting subtitle and video files from RÚV apis

Cleaning subtitle files and converting video to audio only

Currently this repository works with Python 3.

888 is the name for the RÚV teletext subtitles. It is what needs to be pressed to make the subtitles appear on a TV screen. Expanded 888 are subtitles which have been text normalized to remove capitalizations, numbers(digits), and punctuation.

Template versions of the json files have been uploaded to the json folder. All the values in root_urls.json need to be filled out to extract anything from the api.

After the subtitle files are cleaned, they can be compared to automatic speech recognition(ASR) output using compare_hypothesis_and_expanded_888.sh
To use, compare_hypothesis_and_expanded_888.sh, you need to set up [`kaldi`](http://kaldi-asr.org/). Then, within path.sh, change /data/kaldi to the path of your version of kaldi.
Both the ASR transcript and the expanded 888 need to have reference ids at the beginning of every line.

## Usage

python3 extract_from_ruv_api.py --url-file json/root_urls.json --shows-file json/all_shows.json

./compare_hypothesis_and_expanded_888.sh -h

./compare_hypothesis_and_expanded_888.sh data/ASR/transcript.txt data/ref/expanded_no_punct.txt

