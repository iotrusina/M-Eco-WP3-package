#!/bin/sh

soft/./map -l $1 -m tmp_map

length=`tail -1 tmp_map | wc -m`

soft/./finalizemap -i tmp_map -o $2 -l $length

rm tmp_map

echo "Done"

