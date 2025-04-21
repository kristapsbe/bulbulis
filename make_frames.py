import os
import sys
import numpy as np
import rasterio
import matplotlib.image

from pathlib import Path
from scipy.ndimage import zoom, rotate


target_year = 2018
if len(sys.argv) > 1:
    target_year = int(sys.argv[1])
prev_year = start_year-1

files = {}

for f in os.listdir("/home/kristaps/Projs/bulbulis/data_verified"):
    if ".jp2" in f:
        parts = f.split("_")
        if parts[0] not in files:
            files[parts[0]] = {}
        if parts[1] not in files[parts[0]]:
            files[parts[0]][parts[1]] = {}
        files[parts[0]][parts[1]][parts[2]] = f"/home/kristaps/Projs/bulbulis/data_verified/{f}"

dates = []
for f in files.values():
    dates += list(f.keys())
dates = sorted(list(set(dates)))

dates = [d for d in dates if d[:4] == str(target_year) or d[:6] in set([f"{prev_year}{str(i).zfill(2)}" for i in range(8, 13)])]

gain = 2
deg = 5.1
lt_offset = 1230//2 # rotation takes an age with full sized images - going with SCL size instead
w = 10980//2
bc_offset = 4350//2
overlap = 980//2
bc_h = 4*(w-overlap)+overlap
bc_w = 3*(w-overlap)+overlap
t_h = bc_h+lt_offset
t_w = 2*bc_w-bc_offset
scale = 0.2

left_offsets = {
    'T34VDK': (0, 0), # top left
    'T34VEK': (0, 1),
    'T34VFK': (0, 2),
    'T34VDJ': (1, 0),
    'T34VEJ': (1, 1),
    'T34VFJ': (1, 2),
    'T34VDH': (2, 0),
    'T34VEH': (2, 1),
    'T34VFH': (2, 2),
    'T34UDG': (3, 0),
    'T34UEG': (3, 1),
    'T34UFG': (3, 2),
}

right_offsets = {
    'T35VLE': (0, 0),
    'T35VME': (0, 1),
    'T35VNE': (0, 2),
    'T35VLD': (1, 0),
    'T35VMD': (1, 1),
    'T35VND': (1, 2),
    'T35VLC': (2, 0),
    'T35VMC': (2, 1),
    'T35VNC': (2, 2),
    'T35ULB': (3, 0),
    'T35UMB': (3, 1),
    'T35UNB': (3, 2),
}

# TODO: this makes it easier to line up angles - get rid of it
right = np.dstack((np.zeros((bc_h, bc_w)), np.zeros((bc_h, bc_w)), np.zeros((bc_h, bc_w))))
composite = np.dstack((np.zeros((t_h, t_w)), np.zeros((t_h, t_w)), np.zeros((t_h, t_w))))

valid_files = set(list(left_offsets.keys())+list(right_offsets.keys()))
files = {k:v for k,v in files.items() if k in valid_files}

prev_day = ""

for d in dates:
    print(d)
    for k,v in left_offsets.items():
        if d in files[k]:
            fj = files[k][d]
            try:
                scl = rasterio.open(fj["SCL"], driver="JP2OpenJPEG").read(1)
                c_red = np.clip(rasterio.open(fj["B04"], driver="JP2OpenJPEG").read(1)*gain/10000, 0, 1)
                c_green = np.clip(rasterio.open(fj["B03"], driver="JP2OpenJPEG").read(1)*gain/10000, 0, 1) 
                c_blue = np.clip(rasterio.open(fj["B02"], driver="JP2OpenJPEG").read(1)*gain/10000, 0, 1)

                print(d, k)
                v_offset = v[0]*(w-overlap)+lt_offset
                h_offset = v[1]*(w-overlap)
                mask = (((scl == 0) | (scl == 1) | (scl == 3) | (scl == 7) | (scl == 8) | (scl == 9) | (scl == 10) | ((c_red == 0) & (c_green == 0) & (c_blue == 0))) != True)
                composite[v_offset:v_offset+w, h_offset:h_offset+w, 0][mask] = c_red[mask]
                composite[v_offset:v_offset+w, h_offset:h_offset+w, 1][mask] = c_green[mask]
                composite[v_offset:v_offset+w, h_offset:h_offset+w, 2][mask] = c_blue[mask]
            except BaseException as e:
                print(e)
    
    t_scl = np.zeros((bc_h, bc_w))
    did_right = False
    for k,v in right_offsets.items():
        if d in files[k]:
            fj = files[k][d]
            try:
                scl = rasterio.open(fj["SCL"], driver="JP2OpenJPEG").read(1)
                c_red = np.clip(rasterio.open(fj["B04"], driver="JP2OpenJPEG").read(1)*gain/10000, 0, 1)
                c_green = np.clip(rasterio.open(fj["B03"], driver="JP2OpenJPEG").read(1)*gain/10000, 0, 1) 
                c_blue = np.clip(rasterio.open(fj["B02"], driver="JP2OpenJPEG").read(1)*gain/10000, 0, 1)

                print(d, k)
                v_offset = v[0]*(w-overlap)
                h_offset = v[1]*(w-overlap)
                mask = (((scl == 0) | (scl == 1) | (scl == 3) | (scl == 7) | (scl == 8) | (scl == 9) | (scl == 10) | ((c_red == 0) & (c_green == 0) & (c_blue == 0))) != True)
                right[v_offset:v_offset+w, h_offset:h_offset+w, 0][mask] = c_red[mask]
                right[v_offset:v_offset+w, h_offset:h_offset+w, 1][mask] = c_green[mask]
                right[v_offset:v_offset+w, h_offset:h_offset+w, 2][mask] = c_blue[mask]

                t_scl[v_offset:v_offset+w, h_offset:h_offset+w] = scl
                did_right = True
            except BaseException as e:
                print(e)
    if did_right:
        mask = ((t_scl == 0) | (t_scl == 1) | (t_scl == 3) | (t_scl == 7) | (t_scl == 8) | (t_scl == 9) | (t_scl == 10) | ((right[:,:,0] == 0) & (right[:,:,1] == 0) & (right[:,:,2] == 0)))
        t_scl[mask] = -999 # rotation ends up interpolating values - need something exteme so that I can still tell where the clouds are
        
        temp_right = rotate(right, deg, reshape=False)
        t_scl = rotate(t_scl, deg, reshape=False)
        mask = ((t_scl > 0))
        composite[:bc_h, bc_w-bc_offset:, :][mask] = temp_right[mask] # no point in clipping here since I'll need to clip after zooming anyhow
    
    if prev_day != d[:8]:
        prev_day = d[:8]
        print("scaling down")
        scaled_down = np.clip(np.dstack((zoom(composite[:,:,0], scale), zoom(composite[:,:,1], scale), zoom(composite[:,:,2], scale))), 0, 1)
        print("saving composite")
        matplotlib.image.imsave(f"{Path.home()}/Projs/bulbulis/true_color_frames/{d[:8]}.jpeg", scaled_down)
    else:
        print(f"skipping save {prev_day} = {d}")
