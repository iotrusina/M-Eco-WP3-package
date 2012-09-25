source /mnt/data2/rrs_local/profile.sh
export PYTHONPATH=$PYTHONPATH:/mnt/minerva1/nlp/projects/spinn3r/modules/

if [ -z $2 ]
then
    echo "usage ./dailyDump NUMBER_OF_DAYS MAX_DAYS"
    exit -1
fi

count=0
for i in $(seq $1 -1 1)
do 
    if [ $count -eq $2 ]
    then
        break
    fi
    yesterday=`date --date="$i day ago" +"%Y-%m-%d"`
    for lang in de en
    do
        OUT=/mnt/minerva1/nlp/projects/meco/mg4j/server/root/xrylko00/data/daily_dump/$yesterday.$lang.xml
        echo "pubdate='$yesterday'"
        # de language -> must exists some symptom/disease
        echo "pubdate='$yesterday' 
            and documents.language='$lang'
            and doc_processed(documents.id)
            and (documents.guid not like 'euro2012:%')
            and (documents.guid not like 'london2012:%')" | python2.7 /mnt/minerva1/nlp/projects/spinn3r/db/db2xml.py -b > $OUT.tmp
        mv $OUT.tmp $OUT

        # EURO
        OUT_EURO=/mnt/minerva1/nlp/projects/meco/mg4j/server/root/xrylko00/data/daily_dump_london/$yesterday.$lang.xml
        echo "pubdate='$yesterday'
            and documents.language='$lang'
            and doc_processed(documents.id)
            and documents.guid like 'london2012:%'" | python2.7 /mnt/minerva1/nlp/projects/spinn3r/db/db2xml.py -b > $OUT_EURO.tmp
        mv $OUT_EURO.tmp $OUT_EURO
    done
    count=$[ $count + 1 ]
done
