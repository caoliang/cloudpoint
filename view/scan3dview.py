import numpy as np
import sys
import math
import open3d as o3d


def read_pose_file(pose_file):
    with open(pose_file,"r") as pf:
        pf_line = pf.readline().replace("\n", "").replace(" ", ",")
        pos = np.array(eval("[" + pf_line + "]"))
        pf_line = pf.readline().replace("\n", "").replace(" ", ",")
        eu = np.array(eval("[" + pf_line + "]")) * math.pi / 180

    return [pos, eu]


def construct_mat(eu):
    #rotation matrix (processing .pose file)
    matz=[[ math.cos(eu[2]) , -1*math.sin(eu[2]) , 0 ],[ math.sin(eu[2]) ,  1*math.cos(eu[2]) , 0 ],[ 0 , 0, 1] ]
    maty=[[ math.cos(eu[1]) , 0, 1*math.sin(eu[1]) ],[ 0 , 1, 0],[ -1*math.sin(eu[1]) , 0, 1*math.cos(eu[1])] ]
    matx=[ [1,0,0],[ 0, math.cos(eu[0]) , -1*math.sin(eu[0]) ],[ 0, math.sin(eu[0]) ,  1*math.cos(eu[0]) ] ]
    matz=np.array(matz)
    maty=np.array(maty)
    matx=np.array(matx)

    mat=np.matmul(matz,maty)
    mat=np.matmul(mat,matx)

    return mat


def read_scan_file(scan_file, scan_mat, scan_pos):
    with open(scan_file, "r") as sf:
        sf_lines = sf.readlines()

    scan_pts = np.empty((0, 3), int)
    for sf_line in sf_lines:
        line = sf_line.replace("\n", "").replace(" ", ",")
        pos = np.transpose(np.array(eval("[" + line + "]")))
        res = np.round(np.matmul(scan_mat, pos) + pos).astype('int')

        scan_pts = np.vstack((scan_pts, res))

    return scan_pts


def read_scan_pts(scan_index, data_folder):
    index_value = str.format("{:03d}", scan_index)

    pose_file = f"{data_folder}\\scan{index_value}.pose"
    scan_data_file = f"{data_folder}\\scan{index_value}.3d"

    data_pos, data_eu = read_pose_file(pose_file)
    data_mat = construct_mat(data_eu)

    data_pts = read_scan_file(scan_data_file, data_mat, data_pos)

    print(data_pts.shape)
    print(data_pts[0])

    return data_pts


def read_scan_pts_in_range(scan_index_range, data_folder):
    scan_pts = np.empty((0, 3), int)

    for i in scan_index_range:
        data_pts = read_scan_pts(i, data_folder)
        scan_pts = np.vstack([scan_pts, data_pts])

    return scan_pts


def show_scan_pts(scan_pts):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(scan_pts)

    o3d.visualization.draw_geometries([pcd], mesh_show_wireframe=True)

def show_custom_view(scan_pts, view_config):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(scan_pts)

    vis = o3d.visualization.Visualizer()
    vis.create_window(width=1024, height=768)
    vis.add_geometry(pcd)
    vis.get_render_option().load_from_json(view_config)

    ctr = vis.get_view_control()
    ctr.set_zoom(0.3)

    vis.run()
    vis.destroy_window()


if __name__ == "__main__":
    data_pts = read_scan_pts_in_range(range(0, 10), "..\\data\\scandata")

    slicesize = 1024
    # xmin=np.min(data_pts[:,0])
    # xmax=np.max(data_pts[:,0])
    # ymin=np.min(data_pts[:,2])
    # ymax=np.max(data_pts[:,2])
    # zmin=np.min(data_pts[:,1])
    # zmax=np.max(data_pts[:,1])
    #
    # print(f"data_pts range: ({xmin}, {xmax}), ({ymin}, {ymax}), ({zmin, zmax})")

    min_pts = np.amin(data_pts, axis=0)
    max_pts = np.amax(data_pts, axis=0)

    print(f"data_pts min: {min_pts}")
    print(f"data_pts max: {max_pts}")

    xmin, xmax, ymin, ymax = min_pts[0], max_pts[0], min_pts[2], max_pts[2]

    startx = math.floor(xmin / slicesize) * slicesize
    starty = math.floor(ymin / slicesize) * slicesize
    endx = math.floor(xmax / slicesize) * slicesize
    endy = math.floor(ymax / slicesize) * slicesize

    print(f"data_pts x range: ({startx}, {endx}), ")
    print(f"data_pts y range: ({starty}, {endy}), ")

    map_size = (endx + slicesize - startx, endy + slicesize - starty)

    print(f"Processed3dView point min_x: {startx}, min_y: {starty}")

    print(f"map size: {map_size}")

    #show_scan_pts(data_pts)
    show_custom_view(data_pts, "renderoption.json")
