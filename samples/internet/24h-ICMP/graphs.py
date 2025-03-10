from datetime import date, datetime, tzinfo
import time
import matplotlib as mpl
import pandas as pd
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from termcolor import colored


def main():
    stat = 'rtt'

    df = pd.read_parquet('data.parquet.brotli')

    # Remove rows with -1 rtt
    df = df[df[stat] != -1]

    # rename columns
    df = df.rename(columns={'vpn': 'VPN', 'size': 'Tamanho'})
    df = df[['hour', stat, 'Tamanho', 'VPN']]

    print(f"Informações gerais")
    print(df.describe())
    print()

    g = sns.relplot(
        data=df,
        x="hour",
        y="rtt",
        col="Tamanho",
        hue="VPN",
        style="VPN",
        markers=['o', '^', 's', 'P'],
        kind="line",
        dashes=False,
        errorbar=None,
        height=3,
        col_order=sorted(df['Tamanho'].unique(), reverse=True),
    )

    g.set_axis_labels("Hora", "Latência (ms)")
    g.set_titles("Tamanho do pacote: {col_name} bytes")

    g.tight_layout()
    g.savefig('rtt-hora-internet.png', dpi=300)
    plt.show()

    fig = plt.figure(figsize=(7, 4))

    ax = fig.gca()

    ax.set_xlim(11.5, 18)
    ax.set_xlabel('Latência (ms) - escala logarítmica')
    ax.set_ylabel('Densidade')

    sns.histplot(
        x=stat,
        stat='density',
        data=df,
        log_scale=True,
        hue='Tamanho',
        ax=ax
    )

    hatches = ['//', '..', 'xx', '||']

    for container, hatch, handle in zip(ax.containers, hatches, ax.get_legend().legend_handles[::-1]):
        handle.set_hatch(hatch)

        for rectangle in container:
            rectangle.set_hatch(hatch)

    plt.tight_layout()
    plt.savefig('rtt-tamanho-internet.png', dpi=300)
    plt.show()

    for i, vpn in enumerate(df['VPN'].unique()):
        for j, size in enumerate(sorted(df['Tamanho'].unique())):
            ut = df[df['VPN'] == vpn]
            ut = ut[ut['Tamanho'] == size]

            print(f'VPN {vpn} - Size {size}')
            print(ut.describe())
            print()


if __name__ == '__main__':
    main()
