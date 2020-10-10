import tkinter as tk


window = tk.Tk()

frm_left = tk.Frame(master=window, width=100, height=100,
                    relief=tk.SUNKEN, borderwidth=5)

frm_left_top = tk.Frame(master=frm_left, width=100,
                        relief=tk.SUNKEN, borderwidth=5)

lbl_front_view = tk.Label(master=frm_left_top, text="Front View")
lbl_front_view.pack()

frm_left_bottom = tk.Frame(master=frm_left, width=100,
                           relief=tk.SUNKEN, borderwidth=5)

lbl_rear_view = tk.Label(text="Rear View", master=frm_left_bottom)
lbl_rear_view.pack()


frm_right = tk.Frame(master=window, width=200,
                     relief=tk.SUNKEN, borderwidth=5)

frm_right_top = tk.Frame(master=frm_right, width=200,
                        relief=tk.SUNKEN, borderwidth=5)

lbl_map2d = tk.Label(master=frm_right_top, text="2D Map")
lbl_map2d.pack()

frm_right_bottom = tk.Frame(master=frm_right, width=200,
                        relief=tk.SUNKEN, borderwidth=5)

btn_map2d_show = tk.Button(master=frm_right_bottom, text="Show Map")
btn_map2d_show.pack()

frm_left.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
frm_left_top.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
frm_left_bottom.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True)
frm_right.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True)
frm_right_top.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
frm_right_bottom.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

window.mainloop()
