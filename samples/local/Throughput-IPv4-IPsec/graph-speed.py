import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt


def main():
    stat = 'bitrate'

    df = pd.read_csv('IPsec.csv')
    df['VPN'] = 'IPSec'

    print(f"Informações gerais")
    print(df.describe())
    print()

    fig = plt.figure(figsize=(10, 7))

    sns.scatterplot(x='interval',
                    y=stat,
                    hue='VPN',
                    data=df,
                    palette=["tab:orange"],
                    )

    plt.ylim(0, 300)

    plt.title('Taxa de transferência por intervalo de tempo')
    plt.xlabel('Intervalo de tempo (s)')
    plt.ylabel('Taxa de transferência (MBit/s)')

    plt.tight_layout()
    plt.savefig('speed.png', dpi=300)
    plt.show()


if __name__ == '__main__':
    main()
