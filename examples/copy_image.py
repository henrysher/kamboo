import logging

logging.basicConfig(level=logging.INFO)
dist_config = {
    "type": "image",
    "source_account_id": "37401034ABCD",
    "source_credentials": {
        "access_key": "AKIA0XYZNKMBBZ5ABCD",
        "secret_key": "XYZ0Nrs0ubbL76H393TTTTaSbB4l6Bzm9/jNABCD"
        },
    "source_region": "ap-northeast-1",
    "source_id": "ami-3f50393f",
    "dest_account_id": "49830208CDEF",
    "dest_credentials": {
        "access_key": "AKIAJEVXYZ0FTIBABCD",
        "secret_key": "XYZ0TdV0rxPvJdMr9vTTTT9FWbXO584VAj5mABCD",
        },
    "dest_region": "eu-central-1"
}

from kamboo.dist import Distee
dd = Distee(**dist_config)
image = dd.distribute(wait=True)
