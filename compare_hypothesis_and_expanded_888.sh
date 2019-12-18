#! /bin/bash
#Reykjavik University (Author: Judy Fong)
#Description: This script assumes that the subtitle text has been expanded
#using the Althingi text normalization script and therefore all utterance ids
#contain rad. Thus rad is removed in this script.

. ./path.sh

if [ "$1" == "-h" ] || [ "$#" -eq 0 ]; then
    echo "This script compares the ASR transcript with a reference text"
    echo "then aligns them into aligned_texts.log."
    echo "It must be run from the same directory as a kaldi path file"
    echo "Usage: $0 <ASR transcript> <ref-text>"
    echo " e.g.: $0 data/ASR/transcript.txt data/ref/expanded_no_punct.txt"
    echo ""
    exit 1;
fi


hypothesis=$1
expanded_888=$2
log_file=$(dirname ${expanded_888})/aligned_texts.log
punctuation='s/[.!,?:"]//g'


cut -d'-' -f2- ${hypothesis} | sed -e 's/^/rad/' -e 's/_//' | sed $punctuation | sed 's/-/ /g' | compute-wer --text --mode=present ark:- ark:${expanded_888}

#align-text if want to see what the differences are
cut -d'-' -f2- ${hypothesis} | sed -e 's/^/rad/' -e 's/_//' | sed $punctuation | sed 's/-/ /g' | align-text --special-symbol="'***'" ark:- ark:${expanded_888} ark,t:- > $log_file
