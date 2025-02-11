https://github.com/eu-cdse/notebook-samples/tree/main

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
python -m jupyterlab
```

note - this appears to consume processing units veeeery quickly, I should probably process the images locally

https://sentinelhub-py.readthedocs.io/en/latest/examples/process_request.html

https://shapps.dataspace.copernicus.eu/dashboard/#/

https://land.copernicus.eu/en

https://sentinels.copernicus.eu/web/sentinel/view-data-product

Note: if I get a second node dedicated to this, I'd have 2 tb of traffic allowance - I'd imagine it should be enough

It would be cool to get per month (per 13 day (?)) forestation measurements, and to compare a given date to another date

Should probably suggest comparing to 12 months ago (or ahead), checking monthly changes may make sense as well

Sentinel 2 overview https://sentiwiki.copernicus.eu/web/s2-products

L2A docs https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html

L2A spec https://sentinel.esa.int/documents/247904/685211/Sentinel-2-MSI-L2A-Product-Format-Specifications.pdf

tile ids (e.g. T34VFJ) follow https://en.wikipedia.org/wiki/Military_Grid_Reference_System

info on which band is which https://docs.sentinel-hub.com/api/latest/data/sentinel-2-l2a/

TODO: check KML file ([here](https://sentiwiki.copernicus.eu/__attachments/1692737/S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.zip?inst-v=c9602fd8-862c-4637-a9c5-f5e318bba7ca)

scala book https://docs.scala-lang.org/scala3/book/introduction.html

## nice maps

https://glad.earthengine.app/view/global-forest-change#bl=off;old=off;dl=1;lon=23.2497053844484;lat=56.753584887795995;zoom=9;

https://www.globalforestwatch.org/map/?map=eyJjZW50ZXIiOnsibGF0Ijo1Ni45MzUwNDQ2ODk3OTk2MywibG5nIjoyMy45OTE5ODE4MDE2NTM1OTh9LCJ6b29tIjo5Ljc4NDY1NjA1OTA4MjQ0NywiZGF0YXNldHMiOlt7ImRhdGFzZXQiOiJwb2xpdGljYWwtYm91bmRhcmllcyIsImxheWVycyI6WyJkaXNwdXRlZC1wb2xpdGljYWwtYm91bmRhcmllcyIsInBvbGl0aWNhbC1ib3VuZGFyaWVzIl0sIm9wYWNpdHkiOjEsInZpc2liaWxpdHkiOnRydWV9LHsiZGF0YXNldCI6InRyZWUtY292ZXItZ2Fpbi01eSIsImxheWVycyI6WyJ0cmVlLWNvdmVyLWdhaW4tNXkiXSwib3BhY2l0eSI6MSwidmlzaWJpbGl0eSI6dHJ1ZSwidGltZWxpbmVQYXJhbXMiOnsic3RhcnREYXRlIjoiMjAxMC0wMS0wMSIsImVuZERhdGUiOiIyMDIwLTEyLTMxIiwidHJpbUVuZERhdGUiOiIyMDIwLTEyLTMxIn19LHsiZGF0YXNldCI6InRyZWUtY292ZXItbG9zcyIsImxheWVycyI6WyJ0cmVlLWNvdmVyLWxvc3MiXSwib3BhY2l0eSI6MSwidmlzaWJpbGl0eSI6dHJ1ZSwidGltZWxpbmVQYXJhbXMiOnsic3RhcnREYXRlIjoiMjAxMC0wMS0wMSIsImVuZERhdGUiOiIyMDIzLTEyLTMxIiwidHJpbUVuZERhdGUiOiIyMDIzLTEyLTMxIn19LHsiZGF0YXNldCI6InRyZWUtY292ZXIiLCJsYXllcnMiOlsidHJlZS1jb3Zlci0yMDEwIl0sIm9wYWNpdHkiOjEsInZpc2liaWxpdHkiOnRydWV9XX0%3D&mapPrompts=eyJvcGVuIjp0cnVlLCJzdGVwc0tleSI6InJlY2VudEltYWdlcnkifQ%3D%3D
