from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from multiprocessing import Event
import os
import random
import signal
import time
import traceback
from typing import TypedDict
from icmplib import ping
from tqdm import tqdm, trange

DIR = 'internet-100-120'

stop_event = Event()


class Result(TypedDict):
    timestamp: float
    seq: int
    vpn: str
    size: int
    rtt: float


def run_rtt(vpn: dict[str, str | int], sizes: list[int], packet_rate: int, runs: int, timeout: float):

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

                host = ping(vpn['ip'], count=1, privileged=True,
                            timeout=timeout, payload_size=size)

                time.sleep(0.01)

                rtt = host.rtts[0] if len(host.rtts) == 1 else -1

                total_sent += 1
                results.append(Result(timestamp=timestamp,
                                      seq=seq,
                                      vpn=vpn['name'],
                                      size=size,
                                      rtt=rtt))

                if rtt == -1:
                    loss += 1

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

    print(f"Finished {vpn['name']}")
    print(f"Loss: {loss}")


def main():
    vpns = [
        {
            'name': 'Controle',
            'ip': '<omitted>',
        },
        {
            'name': 'IPSec',
            'ip': 'fd65:1097:83f4:5b29::ff',
        },
        {
            'name': 'OpenVPN',
            'ip': 'fda9:6ed2:718c:b8d5::1',
        },
        {
            'name': 'Wireguard',
            'ip': 'fdab:913c:75d2:1d87::20',
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

    with ThreadPoolExecutor(max_workers=4) as executor:

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
