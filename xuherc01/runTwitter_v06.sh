#!/bin/bash


napoveda="Spustenie aplikacie:

./download_twitter --input [súbor s hľadanými výrazmi, lokaciami, uživateľmi]

Oba parametre sú povinné !


Vypis napovedy:
./download_twitter --help


Pre podrobnejší popis nahliadnite do README"

# potrebne premenne
xml_classification="_filtered.xml"
file_name1=$(date +%Y-%m-%dT%TZ)
nekonecno=1
allKeywords="allKeywords"

# export python path
source exportPath.sh
unset http_proxy

# volanie skciptu na vytvorenie jedneho trackFile
python ./modules/createOneTrackFile.py

# spustenie stahovania
./download_v06.sh $allKeywords $file_name1.json >&tmp&

while [ "$nekonecno" -ne 0 ]
do
    sleep 5000
    for PID in `pgrep "curl"`
    do
        kill -9 $PID
    done
    file_name2=$(date +%Y-%m-%dT%TZ)
    unset http_proxy
    ./download_v06.sh $allKeywords $file_name2.json >&tmp&
    cp ./track_all_DE_EN_outputs/$file_copy /mnt/minerva1/nlp/projects/spinn3r/solr_data/xuherc01/data_pre_indexovanie/
    source exportPath.sh
    python parsovanie_json_v07.py $file_name1.json $file_name1.xml "${file_name1}${xml_classification}" &
    cp $file_name1.json ./backups/
    file_copy="${file_name1}${xml_classification}"
    file_name1=$file_name2
done


exit 0
