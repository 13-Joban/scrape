import scrapy
from urllib.parse import quote, urlparse

from scraper.settings import get_data_dirs


class MyntraBase(scrapy.Spider):
    """Shared config inherited by all 3 spiders."""

    allowed_domains = ["myntra.com"]

    retailer = "myntra"
    custom_settings = {
        **get_data_dirs("myntra")
    }

    COOKIES =  {
    'at': 'ZXlKaGJHY2lPaUpJVXpJMU5pSXNJbXRwWkNJNklqRWlMQ0owZVhBaU9pSktWMVFpZlEuZXlKdWFXUjRJam9pWkdKa05qUTNZamt0TW1aa09DMHhNV1l4TFRneE16TXRZVFpqT0RObU5XUTBaalF6SWl3aVkybGtlQ0k2SW0xNWJuUnlZUzB3TW1RM1pHVmpOUzA0WVRBd0xUUmpOelF0T1dObU55MDVaRFl5WkdKbFlUVmxOakVpTENKaGNIQk9ZVzFsSWpvaWJYbHVkSEpoSWl3aWMzUnZjbVZKWkNJNklqSXlPVGNpTENKbGVIQWlPakUzT1RBNE1qWXpPRGNzSW1semN5STZJa2xFUlVFaWZRLjlISGd5QkcyVHp5XzJMVk1kMERET3dGelk1bVhuT2lLbW5weDZRcVZCTDQ=',
    '_d_id': '7c7e41e1-59b2-4823-aa3e-0d447e50eb4a',
    'mynt-eupv': '1',
    'x-mynt-pca': '8JVcch_4wDT_3AVw6u89zu_xLEWsS3pE_7yqq8ACJRpF1f5qAM8Qgr2MQjGNshU2kA7UzxwTjotXqJijX6gq0oWqE78w-tG1XwiTKqTQbVdai7-rS8I1pTLffSrX2FzwstFzR8DzK5XQa_ZTmH9pMjeTPyFi8WUejpq0asWxvcBFDgrrEqhw-5gh',
    '_gcl_au': '1.1.1476693302.1775274390',
    'tvc_VID': '1',
    '_scid': '8Q1ndsoYQLrq6IwT21z03eQSI_st7weS',
    '_fbp': 'fb.1.1775274392109.40149830923136927',
    '_cs_ex': '1',
    '_cs_c': '1',
    '_sctr': '1%7C1775241000000',
    'vw': '400',
    'vh': '961',
    'mynt-ulc-api': 'pincode%3A160019',
    'ak_bmsc': 'ABA4E87F06BC64A46E9EC3EA6B7551DE~000000000000000000000000000000~YAAQodxVuD4E1lOdAQAAxqaTVx+xFze9P8R1s7V9pzUyhAFH/DFMvdxeyMKuHZz3rYBxi7PtbFQPTytL6aCePDq3KDbp3YXuu5v14opqlQNnnhBt32OGa7DKeZuq8t0hlT6HQ9+vGefCkKTEP1+rqcwV1Dq9lbfTOevCSpUe0s/+iYd1tTgIRVHeI2HCZDN0CTSVXoKbr8gDmD+yjh4pfFIJigd7PhMEITfvDaYMFhv2U+h7NTMGzF4YrSQgWOD/nXk2hVwXfS/dLk2zpZncnV9bxSo437cJA19y9uuPys/XiQtWoXUIK0iLzjWQQNXPtCpNXUXWco0Bhspn4gbRDFlBggwfVdkXw8+58xBqlweaLjJ47oiAr15i3ZCYXS/ueupzpJl65/YyEwzRaFiuZgzfxl9iRny0qxjgAdVhzf2jbIZbYhAEAgX2/VMvelLsR9MD5c6YCxyVNacBkJgmaJ3bURLaRmcQB2JWMf9tqB1JJMRBaRQgsQ==',
    '_ma_session': '%7B%22id%22%3A%22babfbc79-6a7c-47ca-9f4b-07be3568c92d-7c7e41e1-59b2-4823-aa3e-0d447e50eb4a%22%2C%22referrer_url%22%3A%22%22%2C%22utm_medium%22%3A%22%22%2C%22utm_source%22%3A%22%22%2C%22utm_channel%22%3A%22direct%22%7D',
    '_mxab_': 'config.bucket%3Dregular%3Bcoupon.cart.channelAware%3DchannelAware_Enabled',
    '_pv': 'default',
    'dp': 'd',
    'lt_timeout': '1',
    'lt_session': '1',
    'microsessid': '266',
    '_xsrf': 'RlmtzytFk36wH8lYwIny4dGFHDJaNlLE',
    'mynt-loc-src': 'expiry%3A1775297868976%7Csource%3AIP',
    'bm_sz': 'FD95E7485F47E4ACE4213382121CE538~YAAQitxVuIQS706dAQAAB33qVx/aK08fIZJxTbfP6zwT/l/otUPe3qB+kmx4+DyNiXXXaKK4w+a6monvtnMEVBywnqG6OsFIUw389AvWNbfaW0qjHrv4wRP4Kfodw+tN0KJ+Qf85HeLjJu+MP25T+2DrK3iXMIEhJ+BfZwbKg18uE+ZobZHVBrf5bjvKH+HD25RJgOaTf4+8dP9lsI84jPwKq2GWVY/v1FMDaZoZegueDhvkhKbovDeiZif4W64xZjCzfpp+B8gUhqVD8oTV0h6geCA+BjBAWl8H3Qj81K8RH9i/6/9QYFJQTrfL72WjQPA/v5hkDRT9e1KMB+sojjmt72UBqagQ89AFn2/ds3sGtp2FDv7G4wBkOgBLk04jVeFR+gA2iH5kaqnBAjk2jEen04VlXDPXM+mD1gyBOpwQ0mSxJQWwfxQpjZjBz4x2oogzbL3josBBXQQj2XqvWLtembknCDdWviAihDcgpmkfoHA2WFeoLxf3xf4dqubJNloKv5bIic7c9+OfuTAt7k/t6aPoWUdjtNQv38VSCQUBpAP+9SupnrKAwYg=~3753286~3355446',
    'ak_RT': '"z=1&dm=myntra.com&si=73ed75a4-52a1-4a7a-ab44-5f33a72a63d5&ss=mnjxzq2o&sl=o&tt=ba2g&obo=9&rl=1"',
    '_abck': '2811AE96701261889FE3936E4E86F609~0~YAAQitxVuNoS706dAQAA+n/qVw/hkQjwuy8mcqiGxBdcOKDY0SsDjslbZBPh8CgEQrbtCGSb2W/j1QNtGOM96GkiSmHMS6b08fRKg6zI8TwkSmez0Uitxe4P+KK5aO2NM/0GRJnUUIisjcFwYqybD2Cfgd1CgNmr2aAK3mslAyRUUYeJ4I6N67kRGN4JXdYICU6D8GpcM73YnD7a/GnhdjdgoriB4RKGlKyydXLVfPFTE21MmsO0mZLvsalgqM6O9IpIfFNFoU/PiuRseqYuI9kHoNCMlre1Q/t8y7z7mE4Z17fi9J5O5k6fkWy0zUm9VDYNiLvOB4cQAVOvn1gvJPHzlEWpjcnnqO9QUXL1dkEOIk9ifRWlz0xo3HE+o1g+4TEE7e7VKvSX3P6XwDNiX8YLEpHj9be+irABKEh8wb/fpz8IXv8gf5Yp/DvaTJQK5is0LyjuUiJPdpoYzJp4uxFHESmODiRLoYxZBE1ZWWJra3Qp24W2pOP5CVrippvZeu+xEr3Wgr51HxFwGrZ1pNBmbXv4PbuHvptkWVbzSo77ONrFkM/e3dsWnLBpsYe2lohKm9TCjPs2y0nwh8GVtrsVbKxEV5LudnUNsycDcGXdzsUjZkMo+d9fQRHXwnTOvYj5fVoX8sQheCpQadPZc6vcZyWddTz0zZqTpVc96KTqdDYKNG60gLeRxKF2mGHVTS0L8TJwHwaCL6pBvsbEcEDNShGzFgK/CV7KG4vdXWBwB0mZozPkAlj9u2BfOfig7zHq+GtwqcBK4ewz+r5Fdk2S5aT0HarTnKrxQRBA+q79lvNncwsLANV3giC/YlWNvOcuQqk84BYdnh0j3aQYsSTDpHjcLjLrcSkd/nbuRAHou99pwjpvFNxDS7joQTcV9TfklqOlpv/DiHaqAUfCpUrzEdhEYOgLBEvhl/SE3c6VBdKHw01Po3T5WK/SHLtISP6/pwpxD9VdolAlCpjDEiAOgYYDeJ1ku0eV4iGX5Mk=~-1~-1~-1~AAQAAAAF%2f%2f%2f%2f%2fxlvmiNNLiOlVkjYwWvSG+4Yt6aqXhv0nxcEANCVNV4dpyDH7Be3b+jfuq2+o3jJ9WwRlmi+sLRQrNlICsmqGBlR7%2fmLk8E7jmmUfbB0syXdCIJ7wP9KZiuKcN8cJJUaTe+10oAkCmacSO4sM9bpPdTjWt6oyyhImNsfUItuUqmY4ZsYT4U%2fJoqAe69U0P3BwQU7z0iq30AW5Ak+ibvZUi4%2fy8voQzpds%2fplEc%2fCmMWBvIE%3d~-1',
    'user_session': 'OltGUZ5DEMrDsKCy29XNdg.bBbShLQEkS-4MLkq-bW3WlqA-nqnqkEy1gfOAWw8C1FId9YNV5cQyVLkakJa95V5j1yv1zVjYz7wUBJhdam-v-aWTXxya3Yv59lNMgEMd3lOjvQrM-c9H32W6BPrJbN51-fULqnOrsFHzGX71r-OdA.1775296428701.86400000.Z7_6BGlbhqrkEvmrXlbeB0LwqQzprKnsMMqs5GYbWJw',
    'utm_track_v1': '%7B%22utm_source%22%3A%22direct%22%2C%22utm_medium%22%3A%22direct%22%2C%22trackstart%22%3A1775296479%2C%22trackend%22%3A1775296539%7D',
    'utrid': 'c2VABEdaWmIQDnELUAZAMCMxMDg5MTYzMTU4JDI%3D.e57feddb784531c3f6f6b8c5e65d8aa2',
    'bm_sv': '8B84476CEDDAFE47CBD1B5FE669E46E6~YAAQitxVuMQT706dAQAAz4XqVx+AcLdAVk9duOsSbP8YmGkae1e7ApzkjnTquOxqaJxeqsWgP82yrm0wPnz/puYlc14i3gbTeluYz/iChd4z05VOY/iZONuvOMUV1oGbQPGmlz/XL38gD7voK1roCxMG53zTYGUBetwbXW8SNHNyj8pzxF0ozwJKJdZ1MCMWvvNv6cp4n5ivK9fDb9BLrjgQtVPsROAXfD1+xO8j4jOqAiojhJZJFrzD6oPPszjfXA==~1',
    '_scid_r': 'CY1ndsoYQLrq6IwT21z03eQSI_st7weSlkQBVw',
}


    HEADERS = {
        'authority': 'www.myntra.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    API_HEADERS = {
        **HEADERS,
        'accept': 'application/json, text/plain, */*',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'referer': 'https://www.myntra.com/',
    }

    PDP_HEADERS = {
    'authority': 'www.myntra.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,kk;q=0.8',
    'cache-control': 'max-age=0',
    'if-none-match': 'W/"6befb-a6EQbCfnHOfearrE2tl3xCAKODU"',
    'referer': 'https://www.myntra.com/dresses?f=Gender%3Amen%20women%2Cwomen',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

    def _req(self, url, callback, meta, priority=0, api=False):
        return scrapy.Request(
            url,
            headers=self.API_HEADERS if api else self.HEADERS,
            # cookies=self.COOKIES,
            callback=callback,
            meta=meta,
            priority=priority,
        )

    def _to_api_url(self, cat_url, category_filter=None, offset=0, page=1):
        slug = urlparse(cat_url).path.lstrip("/")
        params = {"rows": 50, "o": offset, "plaEnabled": "true", "p": page}
        if category_filter:
            params["f"] = f"Categories%3A{quote(category_filter)}"
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"https://www.myntra.com/gateway/v4/search/{slug}?{query}"
