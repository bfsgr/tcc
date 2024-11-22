import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl


def main():
    stat = 'bitrate'

    df = pd.read_parquet('data.parquet.brotli')

    # rename columns
    df = df.rename(columns={'vpn': 'VPN'})

    print(f"Informações gerais")
    print(df.describe())
    print()

    fig = plt.figure(figsize=(10, 7))

    plt.ylabel('VPN')
    plt.xlabel('Taxa de transferência (MBit/s)')

    g = sns.boxplot(x='bitrate',
                    data=df,
                    hue='VPN',
                    )
    
    ax = plt.gca()

    hatches = ['//', '..', 'xx', '--']

    patches = [patch for patch in ax.patches if type(patch) == mpl.patches.PathPatch]

    h = hatches * (len(patches) // len(hatches))

    for patch, hatch in zip(patches, h):
        patch.set_hatch(hatch)
        fc = patch.get_facecolor()
        patch.set_edgecolor(fc)
        patch.set_facecolor('none')

        l = ax.legend()

    for lp, hatch in zip(l.get_patches(), hatches):
        lp.set_hatch(hatch)
        fc = lp.get_facecolor()
        lp.set_edgecolor(fc)
        lp.set_facecolor('none')

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
