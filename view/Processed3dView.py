from PIL import Image
import numpy as np
from time import time
import open3d as o3d


def read_pts_3d(map_img):
    t_start = time()
    image = Image.open(map_img)
    print(f"map_img: {map_img}, format: {image.format}, size: {image.size}")

    pts_data = np.asarray(image)
    print(f"pts_data: {pts_data.shape}, type: {type(pts_data)}")

    xyz_3d = np.zeros((pts_data.shape[0] * pts_data.shape[1], 3))

    idx = 0
    for idx_x in range(pts_data.shape[0]):
        for idx_y in range(pts_data.shape[1]):
            rel_z = pts_data[idx_x, idx_y]
            # Ignore ground points (rel_z = 0)
            if rel_z != 0:
                idx_z = 255 - pts_data[idx_x, idx_y]

                xyz_3d[idx] = (idx_x, idx_y, idx_z)
                idx = idx + 1


    t_spend = time() - t_start

    print(f"xyz_3d: {xyz_3d.shape}, type: {type(xyz_3d)}, time: {t_spend}")

    return xyz_3d


def check_pts_3d(pts_3d):
    limit = 5
    for idx, xyz in enumerate(pts_3d):
        if idx < limit:
            print(xyz)


def show_pts_3d(pts_3d):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts_3d)

    o3d.visualization.draw_geometries([pcd], mesh_show_wireframe=True)


def save_pcd_data(pts_3d, pcd_file):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts_3d)
    o3d.io.write_point_cloud(pcd_file, pcd)


def show_pcd_file(pcd_file):
    pcd = o3d.io.read_point_cloud(pcd_file)
    o3d.visualization.draw_geometries([pcd], mesh_show_wireframe=True)


if __name__ == "__main__":
    pts = read_pts_3d("..\\data\\processed\\merged_gray_images.png")
    show_pts_3d(pts)

    # Do not use pcd file since its size was too big (300MB+)
    #pcd_file = "..\\data\\processed\\merged_gray_images.pcd"
    #save_pcd_data(pts, pcd_file)
    #show_pcd_file(pcd_file)