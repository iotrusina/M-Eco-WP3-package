#!/bin/sh
cd DATA
for lang in languages-*.dat
do
gnuplot <<EOF
set term png size 600, 250;
set out "/homes/eva/xr/xrylko00/WWW/meco/$lang.png"
set xdata time
set timefmt "%Y-%m-%d"

set format y "%2.f"
set format x "%d/%m"
#set grid
set nokey

plot "< tail -15 $lang" using 1:2 with boxes fill solid 0.4 border -1
EOF
done
