from time import time
from PIL import Image
from tqdm import tqdm
import vedo
import numpy as np


def read_pts_3d(map_img):
    t_start = time()
    image = Image.open(map_img)
    print(f"map_img: {map_img}, format: {image.format}, size: {image.size}")

    pts_data = np.asarray(image)
    print(f"pts_data: {pts_data.shape}, type: {type(pts_data)}")

    x_limit = int(pts_data.shape[0])
    y_limit = int(pts_data.shape[1])

    xyz_3d = np.zeros((x_limit * y_limit, 3))

    idx = 0
    for idx_x in tqdm(range(x_limit), ncols=68, desc="Load 3D points"):
        for idx_y in range(y_limit):
            rel_z = pts_data[idx_x, idx_y]
            # Ignore ground points (rel_z = 0)
            if rel_z != 0:
                idx_z = 255 - pts_data[idx_x, idx_y]

                xyz_3d[idx] = (idx_x, idx_y, idx_z)
                idx = idx + 1

    t_spend = time() - t_start
    print(f"xyz_3d: {xyz_3d.shape}, type: {type(xyz_3d)}, time: {t_spend:.0f}")

    return xyz_3d


def show_3d_viewer(coords_3d):
    print(f"coords_3d shape: {coords_3d.shape}")

    #apts = vedo.Points(coords_3d)

    # Show 1st data to check
    data_1st = coords_3d[0]
    print(f"coords_3d[0]: {coords_3d[0]}")

    # Show 3D world
    vedo.show(coords_3d, __doc__, axes=2)
    #vedo.show(coords_3d, np.copy(coords_3d), __doc__, at=[0, 1, 2], shape="2/1", axes=2)
    #plt = vedo.Plotter(shape="2|1")
    #plt.show(coords_3d, at=0)
    #plt.show(np.copy(coords_3d), at=1)
    #plt.show(np.copy(coords_3d), at=2, interactive=True)


if __name__ == "__main__":
    pts_3d_file = "..\\data\\processed\\merged_gray_images.png"

    npy_data = read_pts_3d(pts_3d_file)

    show_3d_viewer(npy_data)
