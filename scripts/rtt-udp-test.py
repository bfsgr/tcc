from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from multiprocessing import Event
import os
import random
import signal
import socket
import time
import traceback
from typing import TypedDict
from icmplib import ping

import numpy as np
from tqdm import tqdm, trange

DIR = 'internet-udp-100-120'

stop_event = Event()


class Result(TypedDict):
    timestamp: float
    vpn: str
    size: int
    rtt: float


def run_rtt(vpn: dict[str, str | int], sizes: list[int], packet_rate: int, runs: int, timeout: float):

    client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    client.settimeout(timeout)
    client.bind(('::', 0))

    loss = 0
    total_sent = 0

    with trange(runs, desc=f'{vpn["name"]}', mininterval=1, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}') as t:
        for i in t:
            random_sleep = random.uniform(0.1, 0.5)

            time.sleep(random_sleep)

            rand_sizes = sizes.copy() * packet_rate

            random.shuffle(rand_sizes)

            results = []

            for seq, size in enumerate(rand_sizes):

                timestamp = time.time()

                message = bytes([0] * size)

                try:
                    send_time = time.perf_counter()

                    client.sendto(message, (vpn['ip'], vpn['port']))

                    client.recv(1024)

                    receive_time = time.perf_counter()

                    rtt = (receive_time - send_time) * 1000
                except socket.timeout:
                    rtt = -1
                    loss += 1

                time.sleep(0.01)

                total_sent += 1

                results.append(Result(timestamp=timestamp,
                                      vpn=vpn['name'],
                                      size=size,
                                      rtt=rtt))

            t.set_postfix(
                {'loss': min((loss / max(total_sent, 1) * 100), 100)})

            # flush to csv
            with open(f"{DIR}/{vpn['name']}.csv", 'a') as file:
                writer = csv.DictWriter(
                    file, fieldnames=Result.__annotations__)
                writer.writerows(results)

            if stop_event.is_set():
                tqdm.write(f"Stopping {vpn['name']}...")
                return

    client.close()

    print(f"Finished {vpn['name']}")
    print(f"Loss: {loss}")


def main():
    vpns = [
        {
            'name': 'Controle',
            'ip': '<omitted>',
            'port': 1200,
            'color': 'blue'
        },
        {
            'name': 'IPSec',
            'ip': 'fd36:e940:f1ad:367::ff',
            'port': 1201,
            'color': 'green'
        },
        {
            'name': 'OpenVPN',
            'ip': 'fdeb:a1c2:63d4:bae7::1',
            'port': 1202,
            'color': 'red'
        },
        {
            'name': 'Wireguard',
            'ip': 'fdab:913c:75d2:1d87::1',
            'port': 1203,
            'color': 'yellow'
        }
    ]

    total_runs = 120  # 24 hours
    packet_sizes = [64, 512, 1024]
    packet_rate = 100  # packet per size per run
    timeout = 0.1

    if os.path.exists(f"{DIR}"):
        os.rename(f"{DIR}", f"{DIR}_{time.strftime('%Y%m%d%H%M%S')}")

    try:
        os.mkdir(DIR)
    except FileExistsError:
        pass

    for vpn in vpns:
        with open(f"{DIR}/{vpn['name']}.csv", 'w') as file:
            writer = csv.DictWriter(
                file, fieldnames=Result.__annotations__)
            writer.writeheader()

    with ThreadPoolExecutor(max_workers=1) as executor:

        future_to_vpn = {}

        for vpn in vpns:
            f = executor.submit(run_rtt, vpn, packet_sizes,
                                packet_rate, total_runs, timeout)

            future_to_vpn[f] = vpn

        def signal_handler(signum, frame):
            stop_event.set()

        signal.signal(signal.SIGINT, signal_handler)

        for future in as_completed(future_to_vpn):
            try:
                future.result()
            except Exception as e:
                print(
                    f"Exception in worker thread {future_to_vpn[future]['name']}: {e}")

                print(traceback.format_exc())

    print("Collecting results")
    # merge all csvs
    with open(f"{DIR}/merged.csv", 'w') as file:
        writer = csv.DictWriter(
            file, fieldnames=Result.__annotations__)
        writer.writeheader()

        for vpn in vpns:
            with open(f"{DIR}/{vpn['name']}.csv", 'r') as file:
                reader = csv.DictReader(file)

                writer.writerows(reader)

    print("Done")


if __name__ == '__main__':
    main()
