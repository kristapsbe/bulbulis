import os
import sys
import json
import pandas as pd
import requests
import itertools
import xml.etree.ElementTree as ET

from pathlib import Path
from settings import username, password


start_year = 2015
end_year = 2026
if len(sys.argv) > 2:
    start_year = int(sys.argv[1])
    end_year = int(sys.argv[2])

print("start_year", start_year)
print("end_year", end_year)

catalogue_odata_url = "https://catalogue.dataspace.copernicus.eu/odata/v1"

collection_name = "SENTINEL-2"
product_type = "S2MSI2A"
max_cloud_cover = 101
#corners = list(itertools.product(["20.95", "28.25"], ["55.7", "58.05"])) # Latvia
corners = list(itertools.product(["20.95", "28.25"], ["53.7", "59.85"])) # getting Estonia and Lithuania as well
poly = [" ".join(corners[i]) for i in [0, 2, 3, 1, 0]]
aoi = f"POLYGON(({",".join(poly)}))"
#search_period_start = "2015-06-23T00:00:00.000Z" # 2A mission launch https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-2
#search_period_end = "2025-02-26T00:00:00.000Z"
search_period_start = f"{start_year}-01-01T00:00:00.000Z"
search_period_end = f"{end_year}-01-01T00:00:00.000Z"

search_query = f"{catalogue_odata_url}/Products?$filter=Collection/Name eq '{collection_name}' and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq '{product_type}') and OData.CSC.Intersects(area=geography'SRID=4326;{aoi}') and ContentDate/Start gt {search_period_start} and ContentDate/Start lt {search_period_end}"

print(f"""\n{search_query.replace(' ', "%20")}\n""")

# filter by cloud coverage
search_query = f"{search_query} and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le {max_cloud_cover})"
print(f"""\n{search_query.replace(' ', "%20")}\n""")

auth_server_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
data = {
    "client_id": "cdse-public",
    "grant_type": "password",
    "username": username,
    "password": password,
}

auth_response = requests.post(auth_server_url, data=data, verify=True, allow_redirects=False)
access_token = json.loads(auth_response.text)["access_token"]

session = requests.Session()
session.headers["Authorization"] = f"Bearer {access_token}"

search_response = requests.get(search_query).json()
ct = 0
while True:
    result = pd.DataFrame.from_dict(search_response["value"])

    for i,r in result.iterrows():
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

        if response.status_code == 401:
            auth_response = requests.post(auth_server_url, data=data, verify=True, allow_redirects=False)
            access_token = json.loads(auth_response.text)["access_token"]
            session = requests.Session()
            session.headers["Authorization"] = f"Bearer {access_token}"

            response = session.get(url, allow_redirects=False)

            while response.status_code in (301, 302, 303, 307):
                url = response.headers["Location"]
                response = session.get(url, allow_redirects=False)
                if response.status_code != 200:
                    print(response)
                    print(url)

        file = session.get(url, verify=False, allow_redirects=True)
        fname = f"data/MTD_{product_name}_MSIL2A_{start_year}_{end_year}_{ct}.xml"
        if os.path.isfile(fname):
            os.remove(fname)
        outfile = Path.home() / f"Projs/bulbulis/data/MTD_{product_name}_MSIL2A_{start_year}_{end_year}_{ct}.xml"
        outfile.write_bytes(file.content)
        print("OUTFILE", str(outfile))
        try:
            tree = ET.parse(str(outfile))
            root = tree.getroot()
            band_location = [f"{product_name}/{e.text}.jp2".split("/") for e in root[0][0][12][0][0] if "B02_10m" in e.text or "B03_10m" in e.text or "B04_10m" in e.text or "B08_10m" in e.text or "SCL_20m" in e.text]

            bands = []
            for band_file in band_location:
                if os.path.isfile(f"data/{band_file[-1]}"):
                    print("FILE ALREADY THERE - skipping", f"data/{band_file[-1]}")
                    continue
                url = f"{catalogue_odata_url}/Products({product_identifier})/{"/".join([f"Nodes({b})" for b in band_file])}/$value"
                response = session.get(url, allow_redirects=False)
                while response.status_code in (301, 302, 303, 307):
                    url = response.headers["Location"]
                    response = session.get(url, allow_redirects=False)
                    if response.status_code != 200:
                        print(url)
                file = session.get(url, verify=False, allow_redirects=True)

                outfile = Path.home() / f"Projs/bulbulis/data/{band_file[-1]}"
                outfile.write_bytes(file.content)
                bands.append(str(outfile))
                print("Saved:", band_file[-1])
        except BaseException as e:
            print("ERROR", e)
    ct += 1
    if '@odata.nextLink' in search_response:
        print("NEXT_LINK", search_response['@odata.nextLink'])
        search_response = requests.get(search_response['@odata.nextLink']).json()
    else:
        break
