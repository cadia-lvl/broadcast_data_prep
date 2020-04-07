# Data Prep

This repository has scripts to extract data from various sources for ASR and speaker diarization.

It was created to normalize the text by RÚV but it should be easy to use it to normalize other text as well, given that each segment has a segmentID

## Rúv Data Preparation
Extract subtitle and video files from the RÚV api

Cleaning subtitle files and converting video to audio only

Given a subtitle file, segments and text files for ASR can be created. The script, create_segments_and_text.py assumes that the subtitle file is in a directory named after the show. The segments and text files will appear in in the existing local data directory.

Currently this repository works with Python 3.

888 is the name for the RÚV teletext subtitles. It is what needs to be pressed to make the subtitles appear on a TV screen. Expanded 888 are subtitles which have been text normalized to remove capitalizations, numbers(digits), and punctuation.

Template versions of the json files have been uploaded to the json folder. All the values in root_urls.json need to be filled out to extract anything from the api.

After the subtitle files are cleaned, they can be compared to automatic speech recognition(ASR) output using compare_hypothesis_and_expanded_888.sh
To use, compare_hypothesis_and_expanded_888.sh, you need to set up [`kaldi`](http://kaldi-asr.org/). Then, within path.sh, change /data/kaldi to the path of your version of kaldi.
Both the ASR transcript and the expanded 888 need to have reference ids at the beginning of every line.

### Usage

python3 extract_from_ruv_api.py --url-file json/root_urls.json --shows-file json/all_shows.json

python3 create_segments_and_text.py --subtitle-file /absolute/path/for/webvtt/file

./compare_hypothesis_and_expanded_888.sh -h

./compare_hypothesis_and_expanded_888.sh data/ASR/transcript.txt data/ref/expanded_no_punct.txt

## ELAN files extraction
[ELAN](https://tla.mpi.nl/tools/tla-tools/elan/) is a professional tool for creating annotations for audio or video.
Extract data from ELAN files.
ELAN is a very populator annotation tool for conversational annotators. It works on top of PRAAT.

### .psfx
files contains the speakerIDS
can use this to create reco2num_spk

### .eaf and .eaf001
contain the segments/time_slots, speakerIDs, and transcriptions along with annotations

### .wav
contains the audio of the corresponding conversation

## Credits
Developer

* Judy Fong - judyfong@ru.is

This is part of the Language Technology Program by The Icelandic Government through Almannaromur.
