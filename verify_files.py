import os
import numpy as np
import rasterio
import matplotlib.image

from pathlib import Path


files = {}

for f in os.listdir("data"):
    if ".jp2" in f:
        parts = f.split("_")
        if parts[0] not in files:
            files[parts[0]] = {}
        if parts[1] not in files[parts[0]]:
            files[parts[0]][parts[1]] = {}
        files[parts[0]][parts[1]][parts[2]] = f"data/{f}"


dates = []
for f in files.values():
    dates += list(f.keys())
dates = sorted(list(set(dates)))

bands = {
    'B02', 'B03', 'B04', 'B08', 'SCL'
}

ct = 0
for d in dates:
    print(d, ct, len(dates))
    ct += 1
    for ki, vi in files.items():
        if d in vi:
            fj = vi[d]
            for b in bands:
                if b in fj:
                    try:
                        rasterio.open(fj[b], driver="JP2OpenJPEG").read(1)
                        os.rename(fj[b], f"data_verified/{fj[b].split("/")[-1]}")
                    except BaseException as e:
                        if os.path.isfile(fj[b]):
                            print(e, "REMOVED", fj[b])
                            os.remove(fj[b])
