import os
import matplotlib.pyplot as plt
import pandas as pd


def save_fig(fig_name: str, tight_layout: bool = True, fig_extension: str = "png", resolution: int = 300,
             images_path: str = './images') -> None:
    """
    utility function to export graphs
    :param fig_name: figure file name
    :param tight_layout: whether export with tight layout, default True
    :param fig_extension: figure extension, default ".png"
    :param resolution: resolution of exported image, default 300 dpi
    :param images_path: exported path, default './images'
    :return:
    """
    if not os.path.exists(images_path):
        os.makedirs(images_path)
    path = os.path.join(images_path, fig_name + "." + fig_extension)
    print("Saving figure", fig_name)
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, format=fig_extension, dpi=resolution)


def save_result(df: pd.DataFrame, file_name: str, file_extension: str ='.csv', file_path: str = './out') -> None:
    """
    Save Pandas DF to csv file
    :param file_name: str
    :param file_extension: str
    :param file_path: str
    :return:
    """
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    df.to_csv(os.path.join(file_path,file_name + file_extension))
