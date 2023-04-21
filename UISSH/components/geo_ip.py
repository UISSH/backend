import pathlib
import sys
import time

import requests

GEOIP_PATH = pathlib.Path("./data/GEO_IP")
GEOIP_CITY = GEOIP_PATH.joinpath("GeoLite2-City.mmdb")
GEOIP_COUNTRY = GEOIP_PATH.joinpath("GeoLite2-Country.mmdb")

print(GEOIP_PATH.absolute())


def init():
    url = "https://ghproxy.com/https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb"

    if not GEOIP_CITY.exists():
        print("init GEOIP_CITY data..")
        download(url, GEOIP_CITY)

    url = "https://ghproxy.com/https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb"
    if not GEOIP_COUNTRY.exists():
        print("init GEOIP_COUNTRY data..")
        download(url, GEOIP_COUNTRY)


def chunk_report(bytes_so_far, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent * 100, 2)
    progress = "Downloaded %d of %d bytes (%0.2f%%)\r" % (
        bytes_so_far,
        total_size,
        percent,
    )

    sys.stdout.write(progress)

    if bytes_so_far >= total_size:
        sys.stdout.write("\n")


def download(url, save_path):
    try:
        r = requests.get(url, stream=True)
        content_size = int(r.headers["content-length"])

        chunk_size = 65536
        bytes_so_far = 0

        f = open(save_path, "wb")
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                bytes_so_far += len(chunk)
                chunk_report(bytes_so_far, content_size)

    except Exception as e:
        print(e)
        time.sleep(5)

    finally:
        f.close()
