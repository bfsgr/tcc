import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt


def main():
    stat = 'bitrate'

    df = pd.read_parquet('data.parquet.brotli')

    df = df.rename(columns={'vpn': 'VPN'})

    print(f"Informações gerais")
    print(df.describe())
    print()

    fig = plt.figure(figsize=(10, 7))

    sns.scatterplot(x='interval',
                    y=stat,
                    data=df,
                    hue='VPN',
                    style='VPN',
                    markers=['^', 'o', 's', 'D'],
                    )

    plt.title('Taxa de transferência por intervalo de tempo')
    plt.xlabel('Intervalo de tempo (s)')
    plt.ylabel('Taxa de transferência (MBit/s)')

    for i, vpn in enumerate(df['VPN'].unique()):
        ut = df[df['VPN'] == vpn]

        print(f'VPN {vpn}')
        print(ut.describe())
        print()


    plt.tight_layout()
    plt.savefig('speed.png', dpi=300)
    plt.show()


if __name__ == '__main__':
    main()
