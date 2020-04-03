#Author: Judy Fong <lvl@judyyfong.xyz.> Reykjavik University
#Description: Parse elan files to create kaldi formatted files (and possible
#   subtitle files)
#conda activate extract-data
#deactivate

def milliseconds_to_seconds(micros):
    return(micros/1000)

#convert seconds.microseconds to 00:00:00:.0000 formatted string
def convert_secs_to_timestamp(given_time):
    import datetime
    formatted_date = datetime.datetime.fromtimestamp(given_time)
    return formatted_date.strftime('%H:%M:%S.%f')

#Convert annotation ids to the same length because there will be sorting
#   problems in kaldi if they're not all the same length.
#Separate "a" from the numbers then left pad the numbers to the same length.
#Prepend the filename/recording id to annotation ids so that the same
#   annotation ids can be used across multiple audio files and to become proper
#   utterance ids.
def create_utterance_id(a_id, filename):
    #numbers should all be length 4
    #assume annotation_id always starts with a followed by non padded numbers
    padded_a_id = "a" + a_id[1:].zfill(4)
    return filename + "_" + padded_a_id

def main(eaf_file, filename):
    import xml.etree.ElementTree as ET

    root = ET.parse(eaf_file).getroot()
    time_slot = {}
    for child in root.findall('TIME_ORDER/TIME_SLOT'):
        time_slot[child.attrib['TIME_SLOT_ID']] = child.attrib['TIME_VALUE']

    #make a dictionary of all the timeslots then they can be used for the
    #segments file by referencing the time slot_id like
    #time_slot[aa.attrib['TIME_SLOT_REF1']]

    with open('data/' + filename + '_utt2spk', 'w') as utt2spk, \
        open('data/' + filename + '_utt2reco', 'w') as utt2reco:
        participants = set()
        #create empty list of annotations/segments
        segment_tuples = []
        for child in root.findall('TIER'):
            for alignable_annotation in child.findall('.//ANNOTATION/ALIGNABLE_ANNOTATION'):
                annotations = alignable_annotation.find('.//ANNOTATION_VALUE')
                utterance_id = \
                    create_utterance_id(alignable_annotation.attrib['ANNOTATION_ID'],
                    filename)
                #change time to seconds and milliseconds
                #instead of printing the time slot ids, print the corresponding
                # time_value instead
                starting_time=milliseconds_to_seconds(int(time_slot[
                    alignable_annotation.attrib['TIME_SLOT_REF1']]))
                ending_time=milliseconds_to_seconds(int(time_slot[
                    alignable_annotation.attrib['TIME_SLOT_REF2']]))
                participants.add(child.attrib['PARTICIPANT'])
                #create tuple of each annotation: utterance, start_time,
                #end_time, participant, and text
                segment_tuples.append((utterance_id, starting_time, ending_time,
                    child.attrib['PARTICIPANT'], annotations.text))

                #create kaldi files
                #utt2reco file
                print(utterance_id, filename, file=utt2reco)
                #utt2spk
                print(utterance_id, child.attrib['PARTICIPANT'], file=utt2spk)

                #TODO: in separate file parse annotations.text further to get
                #rid of all the internal tags
        #sort by the start time
        sorted_segments = sorted(segment_tuples, key=lambda segment: segment[1])
        with open('data/' + filename + '_rttm', 'w') as rttm, open('data/' +
        filename + '_segments', \
            'w') as seg, \
            open('data/' + filename + '_time_ordered', 'w') as time_ordered, \
            open('data/' + filename + '_vtt', 'w') as vtt, \
            open('data/' + filename + '_text', 'w') as trans:
            #create initial content for webvtt file
            print('WeBVTT\n\n', file=vtt)
            count=1
            for segment in sorted_segments:
                #create remaining kaldi files
                #text file
                print("{} {}".format(segment[0], segment[4]), file=trans)
                #segments
                print("{} {} {:.3f} {:.3f}".format(segment[0], filename,
                    segment[1], segment[2]), file=seg)
                #TODO: account for overlapping utterances in rttm and vtt
                #since rttm files are for speaker diarization, remove
                #non-speaker segments
                if segment[3] not in ("Umhverfishljóð", "Tónlist"):
                    duration=segment[2] - segment[1]
                    #create time ordered oracle RTTM file
                    print("SPEAKER {} 0 {:.03f} {:.03f} <NA> <NA> {} <NA> <NA>".format(
                        filename, segment[1], duration,
                        segment[3]), file=rttm)
                #time ordered annotations
                print(segment[0] , segment[1], segment[2], segment[4],
                file=time_ordered)

                #create a webvtt subtitle file
                #NOTE! to create srt file from vtt file:
                # >ffmpeg -i input.vtt -codec srt output.srt
                converted_start_time = convert_secs_to_timestamp(segment[1])
                converted_end_time = convert_secs_to_timestamp(segment[2])
                print("\n{}-0\n{} --> {}\n{}".format(count,
                    converted_start_time, converted_end_time, segment[4]),
                    file=vtt)
                count=count+1
        #create set of participants then get len for num_speakers
        #create reco2num_spk file
        with open('data/' + filename + '_reco2num_spk', 'w') as reco2num_spk:
            print(filename, len(participants), file=reco2num_spk)
    print("Finished creating Kaldi format files")


if __name__ == '__main__':
    # have the transcript and title as input parameters so any Elan file
    #   can be used
    import argparse
    parser = argparse.ArgumentParser(description='Extract ASR, speaker \
        diarization, and subtitle files from ELAN file')
    parser.add_argument('--eaf-file', required=True, help='the path to the \
        ELAN eaf file')
    parser.add_argument('--title', required=True, help='the recording \
        specific name for all generated files')
    args = parser.parse_args()
    # check if the shows file argument was given otherwise nothing can be done
    if args.eaf_file and args.title:
        main(args.eaf_file, args.title)
    else:
        print('Two parameters must be given, an eaf file and a title for \
        output files.')
        exit(0)
