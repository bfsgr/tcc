#!/bin/bash

#Usage:  iperf3 -c localhost -t 5 | bash iperf3_to_csv.sh output_200_20_random.csv

echo "timestamp,interval,transfer,bitrate,retr,cwnd" >> $1

lines=()
while read line
do
  lines+=("$line")
done

num_lines=${#lines[@]}
for ((i=0; i < num_lines - 4; i++))
do
  line=${lines[$i]}
  if [[ $line =~ \[.*5\] ]] 
  then
    timestamp=$(echo $line | awk '{print $1}')
    interval=$(echo $line | awk '{split($4, arr, "-"); print arr[2]}')
    transfer=$(echo $line | awk '{print $6}')
    bitrate=$(echo $line | awk '{print $8}')
    retr=$(echo $line | awk '{print $10}')
    cwnd=$(echo $line | awk '{print $11}')
    echo "$timestamp,$interval,$transfer,$bitrate,$retr,$cwnd" >> $1
  fi
done

