import matplotlib as mpl
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def main():
    stat = 'rtt'

    df = pd.read_parquet('data.parquet.brotli')

    df['size'] = pd.Categorical(df['size'], 
                      categories=['64', '512', '1024'],
                      ordered=True)

    # Remove rows with -1 rtt
    df = df[df[stat] != -1]

    # rename columns
    df = df.rename(columns={'vpn': 'VPN', 'size': 'Tamanho'})

    print(f"Informações gerais")
    print(df.describe())
    print()

    fig = plt.figure(figsize=(9, 5))

    ax = fig.gca()

    ax.set_xlim(13, 15)
    ax.set_xlabel('Latência (ms) - escala logarítmica')

    ax = sns.boxplot(
        data=df,
        hue='Tamanho',
        log_scale=True,
        x=stat
    )

    hatches = ['//', '..', 'xx']

    patches = [patch for patch in ax.patches if type(
        patch) == mpl.patches.PathPatch]

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

    plt.tight_layout()
    plt.savefig('rtt-hist-udp-size.png', dpi=300)
    plt.show()

    for i, vpn in enumerate(df['VPN'].unique()):
        for j, size in enumerate(sorted(df['Tamanho'].unique(), reverse=True)):
            ut = df[df['VPN'] == vpn]
            ut = ut[ut['Tamanho'] == size]

            print(f'VPN {vpn} - Size {size}')
            print(ut.describe())
            print()


if __name__ == '__main__':
    main()
