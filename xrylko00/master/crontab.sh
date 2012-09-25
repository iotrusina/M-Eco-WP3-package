# this is comment - starts with #
# this file is parsed "per-line" and each line is interpreted

. ~/newpythoninit
WWW=/mnt/minerva1/nlp/projects/meco/mg4j/server/root/xrylko00/jstats/
crontab.last_run.log
LOG=/mnt/minerva1/nlp/projects/meco/mg4j/server/root/xrylko00/data/daily_dump/logs/crontab.txt

echo "start `date`" >> $LOG

while true; do
    echo "loop `date`" >> $LOG

    cd /mnt/minerva1/nlp/projects/spinn3r/master

    #actualize with google docs
    python2.7 gActualize.py

    rm -f /mnt/minerva1/nlp/projects/meco/mg4j/server/root/xrylko00/jstats/*.html
    python2.7 jData.py
    date >> $WWW/last_update.txt

    # get data from db
    ./getData.py

    # plot graphs and move public data
    ./PlotCalais.sh
    ./PlotAffected.sh
    ./plotAlchemy.sh
    ./PlotTotal.sh
    ./plotSources.sh
    ./plotLanguages.sh
    ./PlotAnalyzed??.sh
    cp ./DATA/diseases.txt ~/WWW/meco/statdata
    # pocet analyzovanych
    tail -1 ./DATA/analyzed.dat | head -1 | cut -f2 > ~/WWW/meco/statdata/analyzed.dat

    # timestamp
    echo `date +%Y-%m-%dT%H:%M` > ~/WWW/meco/lastupdate.txt

    # cp data's
    cp ./DATA/diseases_list.dat ../solr_data/fromdb/
    cp ./DATA/symptoms_list.dat ../solr_data/fromdb/


    startTime=$(date +%s)
    endTime=$(date -d "next day" +%s)
    timeToWait=$(($endTime- $startTime))
    echo "going to sleep: $timeToWait seconds"
    sleep $timeToWait
done
