#!/bin/bash
#
# Medidas de performance do sistema servidor foram retiradas usando o comando `sar -o mesures-ipv6.sar 1` durante toda duração desse teste
#
# 

IPS=("omitted" "fd65:1097:83f4:5b29::ff" "fda9:6ed2:718c:b8d5::1" "fdab:913c:75d2:1d87::20")

for ip in "${IPS[@]}"
do
  echo "Running iperf3 test to $ip"
  iperf3 -c $ip --timestamps='%s ' -t 3600 -V | tee $ip-raw.log | bash iperf3_to_csv.sh $ip.csv
done
