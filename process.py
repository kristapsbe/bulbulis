import os


print(len([f for f in os.listdir("notebooks/data/") if ".jp2" in f]))
