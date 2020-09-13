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

    scan_pts = None
    for sf_line in sf_lines:
        line = sf_line.replace("\n", "").replace(" ", ",")
        pos = np.transpose(np.array(eval("[" + line + "]")))
        res = np.round(np.matmul(scan_mat, pos) + pos).astype('int')

        if scan_pts is None:
            scan_pts = res
        else:
            scan_pts = np.vstack([scan_pts, res])

        scan_pts = scan_pts.reshape(-1, 3)

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
    scan_pts = None

    for i in scan_index_range:
        data_pts = read_scan_pts(i, data_folder)

        if scan_pts is None:
            scan_pts = data_pts
        else:
            scan_pts = np.vstack([scan_pts, data_pts])

        scan_pts = scan_pts.reshape(-1, 3)

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
    #show_scan_pts(data_pts)
    show_custom_view(data_pts, "renderoption.json")
