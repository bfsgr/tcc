import matplotlib as mpl
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def main():
    df = pd.read_parquet('data.parquet.brotli')

    df = df.rename(columns={'vpn': 'VPN'})

    df.insert(0, 'uso', df['%user'] + df['%system'] + df['%nice'])

    fig = plt.figure(figsize=(8, 7))

    data = df[['interval', 'VPN', 'uso']]

    print(data.describe())

    pv = data.pivot(index='interval', columns='VPN', values='uso')


    g = sns.violinplot(x='uso',
                       data=data,
                       hue='VPN',
                       ax=plt.gca(),
                       )

    plt.xlabel('Uso médio de CPU por núcleo (%)')

    hatches = ['//', '..', 'xx', '--']

    ax = plt.gca()

    patches = [patch for patch in ax.get_children() if isinstance(
        patch, mpl.collections.PolyCollection)]

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
    plt.savefig('usage.png', dpi=300)
    plt.show()


if __name__ == '__main__':
    main()
