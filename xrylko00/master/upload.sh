#!/bin/bash


sftp xrylko00@merlin.fit.vutbr.cz <<zarazka
cd ./spinn/spinn3r/master
put gActualize.py
put *py
put crontab
put *sql
put README.txt
put *sh
zarazka
