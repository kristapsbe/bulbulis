import sys
import json
import numpy as np
import pandas as pd
import requests
import rasterio
import itertools
import matplotlib.image
import xml.etree.ElementTree as ET

from pathlib import Path
from settings import username, password


runner = 0
total_runners = 1
if len(sys.argv) > 2:
    runner = int(sys.argv[1])
    total_runners = int(sys.argv[2])

print("runner", runner)
print("total_runners", total_runners)

catalogue_odata_url = "https://catalogue.dataspace.copernicus.eu/odata/v1"

collection_name = "SENTINEL-2"
product_type = "S2MSI2A"
max_cloud_cover = 1
corners = list(itertools.product(["20.95", "28.25"], ["55.7", "58.05"])) # Latvia
poly = [" ".join(corners[i]) for i in [0, 2, 3, 1, 0]]
aoi = f"POLYGON(({",".join(poly)}))"
search_period_start = "2015-06-23T00:00:00.000Z" # 2A mission launch https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-2
search_period_end = "2025-02-25T00:00:00.000Z"

search_query = f"{catalogue_odata_url}/Products?$filter=Collection/Name eq '{collection_name}' and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq '{product_type}') and OData.CSC.Intersects(area=geography'SRID=4326;{aoi}') and ContentDate/Start gt {search_period_start} and ContentDate/Start lt {search_period_end}"

print(f"""\n{search_query.replace(' ', "%20")}\n""")

# filter by cloud coverage
search_query = f"{search_query} and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le {max_cloud_cover})&$skip={runner*20}"
print(f"""\n{search_query.replace(' ', "%20")}\n""")

auth_server_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
data = {
    "client_id": "cdse-public",
    "grant_type": "password",
    "username": username,
    "password": password,
}

search_response = requests.get(search_query).json()
ct = 1
while True:
    result = pd.DataFrame.from_dict(search_response["value"])

    for i,r in result.iterrows():
        response = requests.post(auth_server_url, data=data, verify=True, allow_redirects=False)
        access_token = json.loads(response.text)["access_token"]

        session = requests.Session()
        session.headers["Authorization"] = f"Bearer {access_token}"

        product_identifier = r["Id"]
        product_name = r["Name"]

        url = f"{catalogue_odata_url}/Products({product_identifier})/Nodes({product_name})/Nodes(MTD_MSIL2A.xml)/$value"
        print(url)

        response = session.get(url, allow_redirects=False)
        while response.status_code in (301, 302, 303, 307):
            url = response.headers["Location"]
            response = session.get(url, allow_redirects=False)
            if response.status_code != 200:
                print(response)
                print(url)
        file = session.get(url, verify=False, allow_redirects=True)
        outfile = Path.home() / f"Projs/bulbulis/notebooks/data/MTD_{product_name}_MSIL2A_{ct*total_runners*20+runner*20}_{runner}_{total_runners}_{ct}.xml"
        ct += 1 # making sure separate outfiles (?)
        outfile.write_bytes(file.content)
        print("OUTFILE", str(outfile))
        tree = ET.parse(str(outfile))
        root = tree.getroot()
        band_location = [f"{product_name}/{e.text}.jp2".split("/") for e in root[0][0][12][0][0] if "B02_10m" in e.text or "B03_10m" in e.text or "B04_10m" in e.text or "B08_10m" in e.text or "SCL_20m" in e.text]

        bands = []
        for band_file in band_location:
            url = f"{catalogue_odata_url}/Products({product_identifier})/{"/".join([f"Nodes({b})" for b in band_file])}/$value"
            response = session.get(url, allow_redirects=False)
            while response.status_code in (301, 302, 303, 307):
                url = response.headers["Location"]
                response = session.get(url, allow_redirects=False)
                if response.status_code != 200:
                    print(url)
            file = session.get(url, verify=False, allow_redirects=True)

            outfile = Path.home() / f"Projs/bulbulis/notebooks/data/{band_file[-1]}"
            outfile.write_bytes(file.content)
            bands.append(str(outfile))
            print("Saved:", band_file[-1])

        # TODO: should probs get rid of this (?)
        try:
            red = rasterio.open([b for b in bands if "B04_10m" in b][0], driver="JP2OpenJPEG").read(1)
            green = rasterio.open([b for b in bands if "B03_10m" in b][0], driver="JP2OpenJPEG").read(1)
            blue = rasterio.open([b for b in bands if "B02_10m" in b][0], driver="JP2OpenJPEG").read(1)

            gain = 2
            red_n = np.clip(red * gain / 10000, 0, 1)
            green_n = np.clip(green * gain / 10000, 0, 1)
            blue_n = np.clip(blue * gain / 10000, 0, 1)
            rgb_composite_n = np.dstack((red_n, green_n, blue_n))
            #plt.imshow(rgb_composite_n)
            outfile = f"{Path.home()}/Projs/bulbulis/notebooks/images/Sentinel2_{product_name}_true_color_base.jpeg"
            matplotlib.image.imsave(outfile, rgb_composite_n)
            print("Saved as:", outfile)

            b04 = rasterio.open([b for b in bands if "B04_10m" in b][0], driver="JP2OpenJPEG").read(1)/10000
            b08 = rasterio.open([b for b in bands if "B08_10m" in b][0], driver="JP2OpenJPEG").read(1)/10000
            ndvi = ((b08-b04)/(b08+b04))
            # Create composite image
            clipped = np.clip(ndvi, 0.0, 1.0)
            clipped[clipped < 0.6] = 0.0
            rgb_composite_n = np.dstack((np.zeros(ndvi.shape), clipped, np.zeros(ndvi.shape)))
            outfile = f"{Path.home()}/Projs/bulbulis/notebooks/forests/Sentinel2_{product_name}_true_color_base.jpeg"
            matplotlib.image.imsave(outfile, rgb_composite_n)
            print("Saved as:", outfile)
        except BaseException as e:
            print(f"ERROR: {product_name} failed with {e}")

    if '@odata.nextLink' in search_response:
        print("NEXT_LINK", search_response['@odata.nextLink'])
        print("NEXT_LINK", search_response['@odata.nextLink'].split("skip=")[0]+f"skip={ct*total_runners*20+runner*20}")
        search_response = requests.get(search_response['@odata.nextLink'].split("skip=")[0]+f"skip={ct*total_runners*20+runner*20}").json()
    else:
        break
