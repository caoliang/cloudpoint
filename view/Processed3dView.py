from PIL import Image
import numpy as np
from time import time
import open3d as o3d
from tqdm import tqdm


def fileter_map_pts(pts_data, xyz_data):
    slice_x = 1024
    slice_y = 1024

    size_x, size_y = pts_data.shape

    pieces_x = int(size_x / slice_x) + 1 if size_x % slice_x > 0 else int(size_x / slice_x)
    pieces_y = int(size_y / slice_y) + 1 if size_y % slice_y > 0 else int(size_y / slice_y)
    print(f"Total grids: {pieces_x} x {pieces_y}")

    xyz_data_index = 0

    for grid_x in tqdm(range(pieces_x)):
        for grid_y in range(pieces_y):
            x_start = grid_x * slice_x
            x_end = min((grid_x + 1) * slice_x, size_x)
            y_start = grid_y * slice_y
            y_end = min((grid_y + 1) * slice_y, size_y)

            #print(f"grid_x: {grid_x}, grid_y: {grid_y}")
            #print(f"x_start: {x_start}, x_end: {x_end}")
            #print(f"y_start: {y_start}, y_end: {y_end}")

            grid_min = np.min(pts_data[x_start:x_end, y_start:y_end])
            grid_max = np.max(pts_data[x_start:x_end, y_start:y_end])
            grid_avg = np.average(pts_data[x_start:x_end, y_start:y_end])
            #print(f"grid_min: {grid_min}, grid_max: {grid_max}, grid_avg: {grid_avg}")

            if grid_min > 0 and grid_min == grid_max and grid_max == grid_avg:
                pass
                #print(f"Located empty grid at grid ({grid_x}, {grid_y})")
                #print(f"Reset empty grid points z value to 0")
                #filtered_pts[x_start:x_end, y_start:y_end] = 0
            else:
                #print(f"Prepare grid points at grid ({grid_x}, {grid_y})")

                for pts_x in range(x_start, x_end):
                    for pts_y in range(y_start, y_end):
                        rel_z = pts_data[pts_x, pts_y]
                        if rel_z != 0:
                            pts_z = 255 - rel_z

                            xyz_data[xyz_data_index] = (pts_x, pts_y, pts_z)
                            xyz_data_index = xyz_data_index + 1

    return xyz_data


def read_pts_3d(map_img):
    image = Image.open(map_img)
    print(f"map_img: {map_img}, format: {image.format}, size: {image.size}")

    pts_data = np.asarray(image)
    print(f"pts_data: {pts_data.shape}, type: {type(pts_data)}")

    t_start = time()

    xyz_3d = np.zeros((pts_data.shape[0] * pts_data.shape[1], 3))

    fileter_map_pts(pts_data, xyz_3d)

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