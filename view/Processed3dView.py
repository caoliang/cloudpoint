from PIL import Image
import numpy as np
from time import time
import open3d as o3d
from tqdm import tqdm
import math
import multiprocessing as mp
from matplotlib import pyplot as plt
import json


xyz_data_results = []


def collect_result(result):
    global xyz_data_results
    xyz_data_results.append(result)


def fileter_map_pts(pts_data):
    xyz_data = np.empty((0, 3), int)

    slice_x = 1024
    slice_y = 1024

    size_x, size_y = pts_data.shape

    pieces_x = int(size_x / slice_x) + 1 if size_x % slice_x > 0 else int(size_x / slice_x)
    pieces_y = int(size_y / slice_y) + 1 if size_y % slice_y > 0 else int(size_y / slice_y)
    print(f"Total grids: {pieces_x} x {pieces_y}")

    grid_xyz_arr = []

    print("Number of processors: ", mp.cpu_count())
    pool = mp.Pool(mp.cpu_count())

    for grid_x in range(pieces_x):
        for grid_y in range(pieces_y):
            pool.apply_async(fileter_pts_grid, args=(grid_x, grid_y, slice_x, slice_y, pts_data),
                             callback=collect_result)

    pool.close()
    pool.join()

    for grid_data in xyz_data_results:
        xyz_data = np.vstack((xyz_data, grid_data))

    print("")

    return xyz_data

def fileter_pts_grid(grid_x, grid_y, slice_x, slice_y, pts_arr):
    xyz_arr = []
    size_x, size_y = pts_arr.shape
    downsample_size_x = 2
    downsample_size_y = 2

    x_start = grid_x * slice_x
    x_end = min((grid_x + 1) * slice_x, size_x)
    y_start = grid_y * slice_y
    y_end = min((grid_y + 1) * slice_y, size_y)

    #print(f"grid_x: {grid_x}, grid_y: {grid_y}")
    # print(f"x_start: {x_start}, x_end: {x_end}")
    # print(f"y_start: {y_start}, y_end: {y_end}")

    grid_min = np.min(pts_arr[x_start:x_end, y_start:y_end])
    grid_max = np.max(pts_arr[x_start:x_end, y_start:y_end])
    grid_avg = np.average(pts_arr[x_start:x_end, y_start:y_end])
    # print(f"grid_min: {grid_min}, grid_max: {grid_max}, grid_avg: {grid_avg}")

    if grid_min > 0 and grid_min == grid_max and grid_max == grid_avg:
        pass
        # print(f"Located empty grid at grid ({grid_x}, {grid_y})")
        # print(f"Reset empty grid points z value to 0")
        # filtered_pts[x_start:x_end, y_start:y_end] = 0
    else:
        # print(f"Prepare grid points at grid ({grid_x}, {grid_y})")

        for pts_x in range(x_start, x_end, downsample_size_x):
            for pts_y in range(y_start, y_end, downsample_size_y):
                rel_z = pts_arr[pts_x, pts_y]
                if rel_z != 0:
                    pts_z = 255 - rel_z

                    xyz_arr.append([pts_x, pts_y, pts_z])

    zyz_np_arr = np.array(xyz_arr).reshape(-1, 3)

    return zyz_np_arr


def read_2d_map_image(imag_file):
    image = Image.open(imag_file).transpose(Image.ROTATE_270)
    print(f"map_img: {imag_file}, format: {image.format}, size: {image.size}")

    return image

def read_pts_3d(map_img):
    pts_data = np.asarray(map_img)
    #pts_data = np.moveaxis(pts_data, 0, -1)
    print(f"pts_data: {pts_data.shape}, type: {type(pts_data)}")

    t_start = time()

    xyz_3d = fileter_map_pts(pts_data)

    t_spend = time() - t_start

    print(f"xyz_3d: {xyz_3d.shape}, type: {type(xyz_3d)}, time: {t_spend}")

    return xyz_3d


def locate_origin_point(min_x, min_y, map_factor_x=0.5, map_factor_y=0.5):
    pos_x = math.ceil(abs(0 - min_x) * map_factor_x)
    pos_y = math.ceil(abs(0 - min_y) * map_factor_y)

    origin_pt = (pos_x, pos_y, 0)

    print(f"Origin point: {origin_pt}")

    return origin_pt


def locate_point(real_x, real_y, min_x, min_y, map_factor_x=0.5, map_factor_y=0.5):
    pos_x = math.ceil(abs(real_x - min_x) * map_factor_x)
    pos_y = math.ceil(abs(real_y - min_y) * map_factor_y)

    map_pt = (pos_x, pos_y, 0)

    print(f"Mapped point: {map_pt} for real point ({real_x}, {real_y})")

    return map_pt


def check_pts_3d(pts_3d):
    limit = 5
    for idx, xyz in enumerate(pts_3d):
        if idx < limit:
            print(xyz)


def convert_to_pcd_data(pts_3d):
    pcd_data = o3d.geometry.PointCloud()
    pcd_data.points = o3d.utility.Vector3dVector(pts_3d)

    return pcd_data


def show_pts_3d(pts_3d):
    pcd = convert_to_pcd_data(pts_3d)

    o3d.visualization.draw_geometries([pcd], mesh_show_wireframe=True)


def save_pcd_data(pts_3d, pcd_file):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts_3d)
    o3d.io.write_point_cloud(pcd_file, pcd)


def show_pcd_file(pcd_file):
    pcd = o3d.io.read_point_cloud(pcd_file)
    o3d.visualization.draw_geometries([pcd], mesh_show_wireframe=True)


def show_pcd_data(pcd_data):
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(pcd_data)
    #vis.get_render_option().load_from_json("renderoption.json")
    vis.run()
    vis.destroy_window()


def show_pcd_data_with_key_callback(pcd_data):

    def change_background_to_black(vis):
        opt = vis.get_render_option()
        opt.background_color = np.asarray([0, 0, 0])
        return False

    def save_render_option(vis):
        vis.get_render_option().save_to_json("renderoption.json")
        return False

    def load_render_option(vis):
        vis.get_render_option().load_from_json("renderoption.json")
        return False

    def save_image(vis):
        vis.capture_screen_image("image.png")
        return False

    def capture_image(vis):
        image = vis.capture_screen_float_buffer()
        plt.imshow(np.asarray(image))
        plt.show()
        return False

    def save_view_trajectory(vis):
        ctr = vis.get_view_control()
        camera_param = ctr.convert_to_pinhole_camera_parameters()
        o3d.io.write_pinhole_camera_parameters("pinhole_camera_parameters.json", camera_param)
        return False

    def load_view_trajectory(vis):
        ctr = vis.get_view_control()
        camera_params = o3d.io.read_pinhole_camera_parameters("pinhole_camera_parameters.json")
        ctr.convert_from_pinhole_camera_parameters(camera_params)
        return False


    key_to_callback = {}
    key_to_callback[ord("K")] = change_background_to_black
    key_to_callback[ord("S")] = save_render_option
    key_to_callback[ord("R")] = load_render_option
    key_to_callback[ord(",")] = save_image
    key_to_callback[ord(".")] = capture_image
    key_to_callback[ord("P")] = save_view_trajectory
    key_to_callback[ord("V")] = load_view_trajectory

    window_width = 640
    window_height = 480

    vis = o3d.visualization.VisualizerWithKeyCallback()
    vis.create_window(width=window_width, height=window_height)
    vis.add_geometry(pcd_data)
    for key, callback in key_to_callback.items():
        vis.register_key_callback(key, callback)

    vis.run()
    vis.destroy_window()


if __name__ == "__main__":
    map_img = read_2d_map_image("..\\data\\processed\\merged_gray_images.png")
    pts = read_pts_3d(map_img)

    # Compute from scan3dview
    min_x = -5120
    min_y = -6144

    size_x, size_y = map_img.size

    origin_point = locate_origin_point(min_x=min_x, min_y=min_y)

    check_x = 10
    check_y = 10

    check_point = locate_point(check_x, check_y, min_x=min_x, min_y=min_y)

    #show_pts_3d(pts)

    pcd_data = convert_to_pcd_data(pts)

    #show_pcd_data(pcd_data)
    show_pcd_data_with_key_callback(pcd_data)

