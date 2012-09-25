#!/bin/bash

cd DATA

OUT=/mnt/minerva1/nlp/projects/meco/mg4j/server/root/xrylko00/sources/

HTML=${OUT}"index.html"

echo "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
<html>
  <head>
  <meta http-equiv=\"content-type\" content=\"text/html; charset=windows-1250\">
  </head>
  <body>" > $HTML



for file in source*.txt; do

    outfile=${OUT}${file}".png"
    echo $outfile

    DATA="
    set term png size 600, 400;
    set out \"$outfile\";
    set xdata time;
    set timefmt \"%Y-%m-%d\";

    set format y \"%2.f\";
    set format x \"%d/%m\";
    #set grid;
    set nokey;

    plot \"< tail -15 ${file}\" using 1:2 with boxes fill solid 0.4 border -1;
    "

    /usr/bin/gnuplot <<< "$DATA"
    echo $?
    echo "<br/><br/><h3>$file</h3><img src=\"$file.png\"/>" >> $HTML

done


echo "</body></html>" >> $HTML
