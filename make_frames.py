# zoom both T34 and T35 (0.2 ?)
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.zoom.html#scipy.ndimage.zoom
# then rotate T35
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.rotate.html

import os
import numpy as np
import rasterio
import matplotlib.image

from pathlib import Path
from scipy.ndimage import zoom, rotate


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

# TODO: this makes it easier to line up angles - may want to get rid of it since it makes rotation a lot more expensive
right = np.dstack((np.zeros((bc_h, bc_w)), np.zeros((bc_h, bc_w)), np.zeros((bc_h, bc_w))))
composite = np.dstack((np.zeros((t_h, t_w)), np.zeros((t_h, t_w)), np.zeros((t_h, t_w))))

valid_files = set(list(left_offsets.keys())+list(right_offsets.keys()))

temp_files = {}
for f in os.listdir("data_verified"):
    if ".jp2" in f:
        p = f.split("_")
        if p[0] in valid_files:
            if p[0] not in temp_files:
                temp_files[p[0]] = {}
            if p[1] not in temp_files[p[0]]:
                temp_files[p[0]][p[1]] = {}
            temp_files[p[0]][p[1]][p[2]] = f"data_verified/{f}"

bands = {'B02', 'B03', 'B04', 'SCL'}
files = {}
for ki,vi in temp_files.items():
    for kj,vj in vi.items():
        if len(bands-set(vj.keys())) == 0:
            if ki not in files:
                files[ki] = {}
            if kj not in files[ki]:
                files[ki][kj] = {}
            files[ki][kj] = vj

dates = []
for f in files.values():
    dates += list(f.keys())

prev_day = ""
for d in sorted(list(set(dates))):
    print(d)
    for k,v in left_offsets.items():
        if d in files[k] and len(bands-set(files[k][d].keys())) == 0:
            fj = files[k][d]
            try:
                scl = rasterio.open(fj["SCL"], driver="JP2OpenJPEG").read(1)
                c_red = np.clip(rasterio.open(fj["B04"], driver="JP2OpenJPEG").read(1)*gain/10000, 0, 1)
                c_green = np.clip(rasterio.open(fj["B03"], driver="JP2OpenJPEG").read(1)*gain/10000, 0, 1)
                c_blue = np.clip(rasterio.open(fj["B02"], driver="JP2OpenJPEG").read(1)*gain/10000, 0, 1)

                print(d, k)
                v_offset = v[0]*(w-overlap)+lt_offset
                h_offset = v[1]*(w-overlap)
                mask = ((scl != 0) & (scl != 1) & (scl != 3) & (scl != 7) & (scl != 8) & (scl != 9) & (scl != 10))

                composite[v_offset:v_offset+w, h_offset:h_offset+w, 0][mask] = c_red[mask]
                composite[v_offset:v_offset+w, h_offset:h_offset+w, 1][mask] = c_green[mask]
                composite[v_offset:v_offset+w, h_offset:h_offset+w, 2][mask] = c_blue[mask]
            except BaseException as e:
                print(e)

    #if prev_day != d[:8]: # save twice to see if there's jitter
    #    print("scaling down")
    #    scaled_down = np.clip(np.dstack((zoom(composite[:,:,0], scale), zoom(composite[:,:,1], scale), zoom(composite[:,:,2], scale))), 0, 1)
    #    print("saving composite")
    #    matplotlib.image.imsave(f"{Path.home()}/Projs/bulbulis/true_color_frames/{d[:8]}_left_only.jpeg", scaled_down)
    #else:
    #    print(f"skipping save {prev_day} = {d}")

    t_scl = np.zeros((bc_h, bc_w))
    did_right = False
    for k,v in right_offsets.items():
        if d in files[k] and len(bands-set(files[k][d].keys())) == 0:
            fj = files[k][d]
            try:
                scl = rasterio.open(fj["SCL"], driver="JP2OpenJPEG").read(1)
                c_red = np.clip(rasterio.open(fj["B04"], driver="JP2OpenJPEG").read(1)*gain/10000, 0, 1)
                c_green = np.clip(rasterio.open(fj["B03"], driver="JP2OpenJPEG").read(1)*gain/10000, 0, 1)
                c_blue = np.clip(rasterio.open(fj["B02"], driver="JP2OpenJPEG").read(1)*gain/10000, 0, 1)

                print(d, k)
                v_offset = v[0]*(w-overlap)
                h_offset = v[1]*(w-overlap)
                mask = ((scl != 0) & (scl != 1) & (scl != 3) & (scl != 7) & (scl != 8) & (scl != 9) & (scl != 10))
                right[v_offset:v_offset+w, h_offset:h_offset+w, 0][mask] = c_red[mask]
                right[v_offset:v_offset+w, h_offset:h_offset+w, 1][mask] = c_green[mask]
                right[v_offset:v_offset+w, h_offset:h_offset+w, 2][mask] = c_blue[mask]

                t_scl[v_offset:v_offset+w, h_offset:h_offset+w] = scl
                did_right = True
            except BaseException as e:
                print(e)
    if did_right:
        mask = ((t_scl == 0) | (t_scl == 1) | (t_scl == 3) | (t_scl == 7) | (t_scl == 8) | (t_scl == 9) | (t_scl == 10))
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
