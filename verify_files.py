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


ct = 0
for d in dates:
    print(d, ct, len(dates))
    ct += 1
    for ki, vi in files.items():
        if d in vi:
            fj = vi[d]
            if "SCL" in fj:
                try:
                    rasterio.open(fj["SCL"], driver="JP2OpenJPEG").read(1)
                    os.rename(fj["SCL"], f"data_verified/{fj["SCL"].split("/")[-1]}")
                except BaseException as e:
                    if os.path.isfile(fj["SCL"]):
                        print(e, "REMOVED", fj["SCL"])
                        os.remove(fj["SCL"])
            if "B08" in fj:
                try:
                    rasterio.open(fj["B08"], driver="JP2OpenJPEG").read(1)
                    os.rename(fj["B08"], f"data_verified/{fj["B08"].split("/")[-1]}")
                except BaseException as e:
                    if os.path.isfile(fj["B08"]):
                        print(e, "REMOVED", fj["B08"])
                        os.remove(fj["B08"])
            if "B04" in fj:
                try:
                    rasterio.open(fj["B04"], driver="JP2OpenJPEG").read(1)
                    os.rename(fj["B04"], f"data_verified/{fj["B04"].split("/")[-1]}")
                except BaseException as e:
                    if os.path.isfile(fj["B04"]):
                        print(e, "REMOVED", fj["B04"])
                        os.remove(fj["B04"])
            if "B03" in fj:
                try:
                    rasterio.open(fj["B03"], driver="JP2OpenJPEG").read(1)
                    os.rename(fj["B03"], f"data_verified/{fj["B03"].split("/")[-1]}")        
                except BaseException as e:
                    if os.path.isfile(fj["B03"]):
                        print(e, "REMOVED", fj["B03"])
                        os.remove(fj["B03"])
            if "B02" in fj:
                try:
                    rasterio.open(fj["B02"], driver="JP2OpenJPEG").read(1)
                    os.rename(fj["B02"], f"data_verified/{fj["B02"].split("/")[-1]}")
                except BaseException as e:
                    if os.path.isfile(fj["B02"]):
                        print(e, "REMOVED", fj["B02"])
                        os.remove(fj["B02"])
