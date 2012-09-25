export pythonpath=/mnt/minerva1/nlp/local/lib/python2.5/site-packages
. ~/pythoninit
ulimit -v 3000000


cd /mnt/minerva1/nlp/projects/spinn3r/db
TOROOT=/mnt/data2/meco/xrylko00
LOG=/mnt/minerva1/nlp/projects/meco/mg4j/server/root/xrylko00/data/daily_dump/logs/db_indexer.txt

while true; do

    echo "xml indexing start `date`" >> $LOG
    # xjerab:
    files=`ls -1 /homes/eva/xr/xrylko00/spinn/spinn3r/solr_data/xjerab13/*.xml`
    while [ "$files" ]
    do
        files=`ls -1 /homes/eva/xr/xrylko00/spinn/spinn3r/solr_data/xjerab13/*.xml | head -80`
        to=$TOROOT/xjerab13_data/indexed

        echo "$files" | ./nunixml2db-dom.py -
        if [[ $? -eq 0 ]]
        then
            for file in $files
            do
                echo $file OK
                mv $file $to/
            done
        fi
    done


    # uhercik
    from=/homes/eva/xr/xrylko00/spinn/spinn3r/solr_data/xuherc01/data_pre_indexovanie
    to=$TOROOT/xuherc01_data/indexed/
     
    files=$from/*xml
    for file in $files
    do
        ./nunixml2db-dom.py $file
        if [[ $? -eq 0 ]] 
        then
            echo $file OK
            mv $file $to/
        fi
    done



    # xkolla:
    files=/homes/eva/xr/xrylko00/spinn/spinn3r/solr_data/xkolla04/*.xml
    to=$TOROOT/xkolla04_data/indexed

    for file in $files
    do
        ./nunixml2db-dom.py $file
        if [[ $? -eq 0 ]]
        then
            echo $file OK
            mv $file $to/
        fi
    done

    # xseitl01
    files=/homes/eva/xr/xrylko00/spinn/spinn3r/solr_data/xseitl01/*.xml
    to=$TOROOT/xseitl01_data/indexed

    for file in $files
    do
        ./nunixml2db-dom.py $file
        if [[ $? -eq 0 ]]
        then
            echo $file OK
            mv $file $to/
        fi
    done

    # xsumba
    files=/homes/eva/xr/xrylko00/spinn/spinn3r/solr_data/xsumba00/*.xml
    to=$TOROOT/xsumba00_data/indexed

    for file in $files
    do
        ./nunixml2db-dom.py $file
        if [[ $? -eq 0 ]]
        then
            echo $file OK
            mv $file $to/
        fi
    done

    # srnec
    #from=/homes/eva/xr/xrylko00/spinn/spinn3r/solr_data/xsrnec01/todo
    #to=$TOROOT/xsrnec01_data/indexed/
    #
    # 
    #files=$from/*xml
    #for file in $files
    #do
    #    ./nunixml2db-dom.py $file
    #    if [[ $? -eq 0 ]] 
    #    then
    #        echo $file OK
    #        mv $file $to/
    #    fi
    #done


    ## kalma:
    #files=/homes/eva/xr/xrylko00/spinn/spinn3r/solr_data/xkalma01/todo/*/*/*/*.xml
    #to=$TOROOT/xkalma01_data/indexed/
    # 
    #for file in $files
    #do
    #    ./nunixml2db-dom.py $file
    #    if [[ $? -eq 0 ]] 
    #    then
    #        echo $file OK
    #        x=${file:61}
    #        y=${x//\//.}
    #        echo $to/$y
    #        mv $file $to/$y
    #    fi
    #done

    echo -n "deleting blacklist words `date`: " >> $LOG
    psql --host meco.l3s.uni-hannover.de meco meco -f /mnt/minerva1/nlp/projects/spinn3r/master/euro_delete_blacklist.sql >> $LOG 2>>$LOG
    echo "" >>$LOG
    echo "daily dump start `date`" >> $LOG
    /mnt/minerva1/nlp/projects/spinn3r/master/dailyDump.sh 5 5

    echo "going to sleep"
    echo "going to sleep `date`" >> $LOG
    sleep 7200
done


