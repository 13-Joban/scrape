import curl_cffi.requests
import scrapy
from urllib.parse import quote, urlparse

from scraper.settings import get_data_dirs


class AjioBase(scrapy.Spider):
    """Shared config inherited by all 3 spiders."""

    allowed_domains = ["ajio.com"]

    retailer = "ajio"
    custom_settings = {
        **get_data_dirs("ajio")
    }
    cookies = {
        'V': '201',
        'TS01a68201': '015d0fa2262c0c0fb797ecddf53418ec23d43a75acda992f20aab81dee8192fe42488e7f72801158735fc20274b3fb468404a28223',
        'bm_sz': '52BDC95A4365716A74332CD6E4616971~YAAQj7MsMWd77EadAQAA9kaRXR/YJiaKFXS4fLI1gq+RdOD0VKkXwff9Dupq9Bhdz5x476NSVEyC3qvLYB/BW8xtpUpzmrUJp6Inx7WnwtlCnuTmMR5wyRuA0D8sJyzCqKZLvoNxzX2UiWGoPqMgrpJy2353NZjW0R6yc6hNQd1+bKA8mrwkRWQ01cAKRDJgBDeaAz3yUh32M8O650IhrxFlB9QsaZoIxES3CqqNM1kVZmK9TYpJ6TYWxbv+bhmhJT5cx+F8y0F2aTMcTx3FeIZcynZCoGt+qe42BrRyC/CGB9vScZOLS564Era44z9qwX4S6I61szOWA7J5WXzfnFzUK7gFZ+3bFGmpnQFD0HQhYeGpky1TylbwjXZzKBB1k8Myg1uT/xe0AqwcMofwtVURMvFQVgRtJRhmfMg3SjrZ877QnDUF~4473411~3290929',
        '_gid': 'GA1.2.2118034999.1775391297',
        '_gcl_au': '1.1.2064905489.1775391298',
        'AB': 'B',
        'dtm_token': 'AQANMyaYFX_XhQE70WYmAQBFtwABAQCaRaKcugEBAJxckFU4',
        'dtm_consent': 'UNSPECIFIED',
        '_fbp': 'fb.1.1775391299886.510030006200279687',
        'segment_user_id': 'null',
        'ajs_anonymous_id': 'cf1cd2fa-3de3-4822-9cce-078f990350dd',
        'segment_device_id': 'cf1cd2fa-3de3-4822-9cce-078f990350dd',
        '_fpuuid': 'Y6BIa6_O2i4fZfcG8jVEl',
        'deviceId': 'Y6BIa6_O2i4fZfcG8jVEl',
        'ifa': 'fb90b365-83f0-4b89-b3af-b6322207fd10',
        'os': '4',
        'vr': 'WEB-2.0.11',
        '_pin_unauth': 'dWlkPU1qVTJZbVZrTW1FdFlqSTJNUzAwTUdKaUxXSTJaR1V0TTJVMllXSXpZekZoTkdKbA',
        '_scid': 'tyOjbeTg_Ffy-nUECyxfn6Q4b-JOv6Bu',
        '_sctr': '1%7C1775327400000',
        'g_state': '{"i_l":0,"i_ll":1775392459322,"i_b":"iBopxAc9h/eI/oBjRXX8VL1eiTTXlIHhGMPayCqc0Fw","i_e":{"enable_itp_optimization":0}}',
        'ajiosessionid': 'E73E9B6901943C79A39D23E0DD73FBF3.a3693',
        'bm_so': 'E60F1C835905DCD895E020CAA2E552661FC4F5FED8E3A414EA873FAFEC1A31F0~YAAQj7MsMRsQ8UadAQAAi4+jXQcDBAFal97ox/6U9NANBfk9lrvjl93VqTiolWEayHHqUGo6ln9WipnmGVJUlnQBs+3T3ZcwbDbP2sM6584d7CN/w+WniGZrinq2TYo+Dd/G2aTvzbkPGmKgRh55nxBCzkcGhWQWgdnzhuPtl5oi78bOT3n+MG7xWwWDMrZ2HgtvwFbH35GEncDGrPvq6LD2sToZMGeGpx2f1kx3kSM5OGjuwjS389lEppFc1A6iiGUyYwCHk3oZyH2oNcFE475bi/ty6ACJocfnaUMTjlm0gv6dEiBiyY3yX7Ey5QD+6zJJ1qwgNHBONa6DZpRHRT+FRfwl+Y8f5+CLgsDWj+Xstp2T9qK+cf2W9g9l/SinlOCKx3tJDGZyzvSo6MVy9yTnC7qEqJGby6BXQ63pTawBHBuAyCEI7QLmXky0rrwGGglvj+tQKRbVuXOrUrQnUX1TPoUjPZjCx1VehXA51O9Z/gNG7qVNgwj7',
        'cdigiMrkt': 'utm_source%3A%7Cutm_medium%3A%7Cdevice%3Adesktop%7Cexpires%3ATue%2C%2005%20May%202026%2012%3A34%3A54%20GMT%7C',
        'bm_lso': 'E60F1C835905DCD895E020CAA2E552661FC4F5FED8E3A414EA873FAFEC1A31F0~YAAQj7MsMRsQ8UadAQAAi4+jXQcDBAFal97ox/6U9NANBfk9lrvjl93VqTiolWEayHHqUGo6ln9WipnmGVJUlnQBs+3T3ZcwbDbP2sM6584d7CN/w+WniGZrinq2TYo+Dd/G2aTvzbkPGmKgRh55nxBCzkcGhWQWgdnzhuPtl5oi78bOT3n+MG7xWwWDMrZ2HgtvwFbH35GEncDGrPvq6LD2sToZMGeGpx2f1kx3kSM5OGjuwjS389lEppFc1A6iiGUyYwCHk3oZyH2oNcFE475bi/ty6ACJocfnaUMTjlm0gv6dEiBiyY3yX7Ey5QD+6zJJ1qwgNHBONa6DZpRHRT+FRfwl+Y8f5+CLgsDWj+Xstp2T9qK+cf2W9g9l/SinlOCKx3tJDGZyzvSo6MVy9yTnC7qEqJGby6BXQ63pTawBHBuAyCEI7QLmXky0rrwGGglvj+tQKRbVuXOrUrQnUX1TPoUjPZjCx1VehXA51O9Z/gNG7qVNgwj7~1775392495233',
        'bm_ss': 'ab8e18ef4e',
        'ak_bmsc': 'B360DD9B88139D20D87F4DF5C1C2BA98~000000000000000000000000000000~YAAQ12w/F0ADrUmdAQAATpQ4Xh/l+QfhCkaccJkDyebh/OgBQCN/tSKXV4bS2ayARSHFbaaBOStuPqKL9Pmpt6JV5CUTaOZB/2BKYCwOrniF3uBOI0I4TvOpOsVFIzQYiwk41KRhY+id1DDOpo8rKHM1ESbtAzV7NgFcjp+Et9ok9y8M5cgZx8nJeNvhde6JKBZfXi4/ZKAnYfqG1deXGNgFVsJwvm4g07zFkTRqopX5dNO4mcb2QW/k4OtfS9J07YeaA4xw3A9NVnx0Nt98AkLPhu5AlSnVFejWtPob69oONT5mc9YD9V7Wtnpp5suSkah70aK9Qz8pWsTy1ljqyuzOwo27OlIx8qic1Wu9wWftEozwbH9lR+pZl99/sAXSnWnttqqjwyjmDoyVDu7f7s9vPJCCe6AiUJCe',
        'analytics_session_id': '1775402311945',
        'ImpressionCookie': '0',
        'sessionStatus': 'true|undefined',
        'FirstPage': 'Sun Apr 05 2026 20:53:30 GMT+0530 (India Standard Time)',
        '_scid_r': 'x6OjbeTg_Ffy-nUECyxfn6Q4b-JOv6BuxhRs5A',
        'cto_bundle': 'a_OBAV9lWlFyNXo5ZFFLQkd4YmZHbGhJZmU0OVNDNXZieDB4TTBTY0U4U09EdWI0SXN4QTN1ZkU4VWRhdTJ6WE9JbTl5ZDNBTHp4UGRsZk55MGQwdG9yb0wxdlV5OVg4b2NZU256Qno5UEsxT2RETzBKVlNCMHBXeDlWQUUlMkZEWUNKWWplV1NmNG9IdXZzZnpmcndtanZGMzFqUSUzRCUzRA',
        '_ga': 'GA1.2.1744058988.1775391297',
        '_abck': 'E91817EF8A0CAB68C89AA98DF82A3631~0~YAAQzGw/FzNR/k+dAQAAeFRLXg+z1Xn9E0EFwXhzXHXwxiGBznmCzwOvfAwNIQLSzdLAHyMIDTcIjbnLgyook9I9XHXoT1qpG62+QLXO4hIwxBce9qB18CgSEU+1PeILJH2AbGh0xKF+7egfwZPPf9dZPsyP1J6Hi/US0de6qgUaIuNvgqo8ddxBA1z84LzUUl5Rw/gD6b5VJj1X3l9Q978o9G5/+pgeTqgmQnCLOYhJej/4iAQrCuY+BlCQNIgDGW+aRi/fcmF+ZlYVR1/UjEl6L4nuZqxab8r76w1DVzD3xNFg2YtWFOLeXUTqteQ8J7UGWwfXv+ZkdX6y29FG6dfnTtXBfdbYt5tI/W6pMwkYUHd5YFCCQzbCkTRO7BFzKOWZ4011Ky779TufFEqM3IOLH8fj0DS3675OwR3NCDBx7QksRiNIXz1hpRKU45TRNq5rpS3WneldRJNO8dPS0DaHXdmbOR+iaZ/7Ki5+4dlTgrBCrkjg+ASwgoqDXPtd/fEnC+pp3USDJRnGFrVlYM4Jml7NcOTTZRKTuhga23RcQJPJOojML5pJQtw4D51yAQnw1if2UHDUzhs75jjLLyJs7qbQ9wSi+7bh5s2FeOlrGG6K1bHEwgQBt2Z9fQTS++caWQ1K3ouYVFNqWJJVyDw+sAZ/ii9qiItQhqVFFArmDACwnYFDV1tk994wMgB9vXSrsV6BTVx0DPe/0Y1SjsLXUdTqn78Lw35LLCsbY1D1fiNdlBbNfQHDQMBmxzCh/2eA73A0~-1~-1~1775407088~AAQAAAAF%2f%2f%2f%2f%2f8CJkdpOW8CrNJI0qUC35u65F8ZCBEj2+uVY1UvqBItKoGxLQkA2wJ4AfyPWWSZrdWvtN6yx6YnC8rIH4TV3v%2fRBETwwYLGwcwYNMDbLYDcGeWxKZ3MNBp4V6DqTBiS2h%2fTHohaQc4jBJy4lvDXFujvKLCG38y3Vhu64UeHOLC%2fSDyMPSYR%2fp9LfJiw1wo69jBsPa3fPximx~-1',
        'analytics_session_id.last_access': '1775403940047',
        'TS01d405db': '015d0fa22695545e0ad19d8180acfa6721b08045c9b6a37aa4bad73a594cbd8183d6b84c0f1176da6a1bb726b1c4e14f8c687b0d21267e09a56c01c0e3b3dd0003e7ce1f6029341babd2fad41341acf543ddf450137243e17ce5d49d8e1c4d345b17a8b9e6',
        '_ga_X3MNHK0RVR': 'GS2.1.s1775401377$o3$g1$t1775403942$j58$l0$h0',
        'ADRUM_BT': 'R:0|i:6333|g:c1728ec4-ecd3-4081-84ea-076550a7fd4e1225410|e:356|n:customer1_be12de70-87be-45ee-86d9-ba878ff9a400',
        'bm_s': 'YAAQzGw/FwUYAFCdAQAAGSdTXgVi1VVg4p4nUPYq9jUNWAympZYswmZ9+uHvF870hnW8OOLrhghazD8EyKta3CsvEaS7zrmfb9af6CgpIwJBEji9gEBMTYqEHZN+/NCpn7bxIRfdcSGtFuLCscUOyccnlW3bMJsWyESIgz8mP0iZjab31Msv3QyR6agYKh53YwszXLLg90C6uuV0oph+9GJExKzTQphhJY0IZl5q/IAWpyMBD2JNvJFELfxc6ErMQ85CFL0Zi52xpe6F7Wu4pMrQpTKyaiQAB/M2k5d6jtIcosbEdpNVTglSYga5K1E8Cml5kjcNY9DlRA3MCxj0iksLTQdnG5xqK8OjhzwEYuZUmmNcWs8mqjbiewF1QhpckbrbkA6YnDrm8SRYzUWl0DLQKFX8vLEy+HNpP7s8kP5Kj4x931jB3oKVO6FN0wW9D3rNTJgbHdPgaBpZfH80DryXUQzfHWXxV+bzr3ndnn3cLnD1a5w2ZQmB6hzPmgBUcCgnhdCnJfP+KNXaj/kQZOuGaeAb5w358XojodlFP5H6ydVB3KtQuFkP2+f3dAvgQJaBamW8rNI2PzJ/jLWh9RKB9ckL0bsx7r/od9HSPl/UsuEgoE3/n+vhaLt3ZjKHEiaM2zukQ+LKuKyzV/Mb2+sGImpTN07E1uCh5xUshCpgz8GGmlp5l+lUJRh6aGPetK64pKisP/bFMU59XfpiDbUmbrs0TZCbSrCD3Z5zwscVv6vFb+XrLRLy/EI1+dNF23IR5CHQ/tzv1F3sYbt8cIEW2XNG2yZXkG8wBv3hPYODQSuls1KBs4lioBaRFs+evCW7hUfyThQG24gwPwEccWuKqfzlWg4sXaGRTGXpBJNWMpXv7e/p/f0yqL/wwnKOzKmoxYJodNOh4NMVU5akBcfqw9rNCBlFnR5pwbtd5iAYaDYQAMo7M5QP1rT0K31Hjhrp54TAutJ4jLc=',
        'bm_sv': 'E582F85598E018ECF407B11E366C01F0~YAAQzGw/FwYYAFCdAQAAGSdTXh8qwnJJgJ8vj1ud224EieRJzKcGLSgm1HEfOapQE8FFfd7dzuZ1T+Knhfd8NF1fOiqVBCxKZNdu3VOuI5LUuePWyYtl2OOrpwbaJzpYZruWHzFkU/rH2xZb0R64CVhaSHUTEJQAnF0BwTYFRuP9HX2dy6UFH55Q6Y+W7xlQ8XGDOPdAWke9p9xDagcTz4PeCYh0iILIL5/DBfj3ChsAsWkpZZFXA6rtiiRsENo=~1',
    }

    headers = {
        'authority': 'www.ajio.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,kk;q=0.8',
        'ai': 'www.ajio.com',
        'clientip': '2409:4090:d05a:800a:2f7b:3d61:1d94:8504, 23.63.108.204, 23.210.74.70, 23.197.28.143, 23.35.149.14',
        # 'cookie': 'V=201; TS01a68201=015d0fa2262c0c0fb797ecddf53418ec23d43a75acda992f20aab81dee8192fe42488e7f72801158735fc20274b3fb468404a28223; bm_sz=52BDC95A4365716A74332CD6E4616971~YAAQj7MsMWd77EadAQAA9kaRXR/YJiaKFXS4fLI1gq+RdOD0VKkXwff9Dupq9Bhdz5x476NSVEyC3qvLYB/BW8xtpUpzmrUJp6Inx7WnwtlCnuTmMR5wyRuA0D8sJyzCqKZLvoNxzX2UiWGoPqMgrpJy2353NZjW0R6yc6hNQd1+bKA8mrwkRWQ01cAKRDJgBDeaAz3yUh32M8O650IhrxFlB9QsaZoIxES3CqqNM1kVZmK9TYpJ6TYWxbv+bhmhJT5cx+F8y0F2aTMcTx3FeIZcynZCoGt+qe42BrRyC/CGB9vScZOLS564Era44z9qwX4S6I61szOWA7J5WXzfnFzUK7gFZ+3bFGmpnQFD0HQhYeGpky1TylbwjXZzKBB1k8Myg1uT/xe0AqwcMofwtVURMvFQVgRtJRhmfMg3SjrZ877QnDUF~4473411~3290929; _gid=GA1.2.2118034999.1775391297; _gcl_au=1.1.2064905489.1775391298; AB=B; dtm_token=AQANMyaYFX_XhQE70WYmAQBFtwABAQCaRaKcugEBAJxckFU4; dtm_consent=UNSPECIFIED; _fbp=fb.1.1775391299886.510030006200279687; segment_user_id=null; ajs_anonymous_id=cf1cd2fa-3de3-4822-9cce-078f990350dd; segment_device_id=cf1cd2fa-3de3-4822-9cce-078f990350dd; _fpuuid=Y6BIa6_O2i4fZfcG8jVEl; deviceId=Y6BIa6_O2i4fZfcG8jVEl; ifa=fb90b365-83f0-4b89-b3af-b6322207fd10; os=4; vr=WEB-2.0.11; _pin_unauth=dWlkPU1qVTJZbVZrTW1FdFlqSTJNUzAwTUdKaUxXSTJaR1V0TTJVMllXSXpZekZoTkdKbA; _scid=tyOjbeTg_Ffy-nUECyxfn6Q4b-JOv6Bu; _sctr=1%7C1775327400000; g_state={"i_l":0,"i_ll":1775392459322,"i_b":"iBopxAc9h/eI/oBjRXX8VL1eiTTXlIHhGMPayCqc0Fw","i_e":{"enable_itp_optimization":0}}; ajiosessionid=E73E9B6901943C79A39D23E0DD73FBF3.a3693; bm_so=E60F1C835905DCD895E020CAA2E552661FC4F5FED8E3A414EA873FAFEC1A31F0~YAAQj7MsMRsQ8UadAQAAi4+jXQcDBAFal97ox/6U9NANBfk9lrvjl93VqTiolWEayHHqUGo6ln9WipnmGVJUlnQBs+3T3ZcwbDbP2sM6584d7CN/w+WniGZrinq2TYo+Dd/G2aTvzbkPGmKgRh55nxBCzkcGhWQWgdnzhuPtl5oi78bOT3n+MG7xWwWDMrZ2HgtvwFbH35GEncDGrPvq6LD2sToZMGeGpx2f1kx3kSM5OGjuwjS389lEppFc1A6iiGUyYwCHk3oZyH2oNcFE475bi/ty6ACJocfnaUMTjlm0gv6dEiBiyY3yX7Ey5QD+6zJJ1qwgNHBONa6DZpRHRT+FRfwl+Y8f5+CLgsDWj+Xstp2T9qK+cf2W9g9l/SinlOCKx3tJDGZyzvSo6MVy9yTnC7qEqJGby6BXQ63pTawBHBuAyCEI7QLmXky0rrwGGglvj+tQKRbVuXOrUrQnUX1TPoUjPZjCx1VehXA51O9Z/gNG7qVNgwj7; cdigiMrkt=utm_source%3A%7Cutm_medium%3A%7Cdevice%3Adesktop%7Cexpires%3ATue%2C%2005%20May%202026%2012%3A34%3A54%20GMT%7C; bm_lso=E60F1C835905DCD895E020CAA2E552661FC4F5FED8E3A414EA873FAFEC1A31F0~YAAQj7MsMRsQ8UadAQAAi4+jXQcDBAFal97ox/6U9NANBfk9lrvjl93VqTiolWEayHHqUGo6ln9WipnmGVJUlnQBs+3T3ZcwbDbP2sM6584d7CN/w+WniGZrinq2TYo+Dd/G2aTvzbkPGmKgRh55nxBCzkcGhWQWgdnzhuPtl5oi78bOT3n+MG7xWwWDMrZ2HgtvwFbH35GEncDGrPvq6LD2sToZMGeGpx2f1kx3kSM5OGjuwjS389lEppFc1A6iiGUyYwCHk3oZyH2oNcFE475bi/ty6ACJocfnaUMTjlm0gv6dEiBiyY3yX7Ey5QD+6zJJ1qwgNHBONa6DZpRHRT+FRfwl+Y8f5+CLgsDWj+Xstp2T9qK+cf2W9g9l/SinlOCKx3tJDGZyzvSo6MVy9yTnC7qEqJGby6BXQ63pTawBHBuAyCEI7QLmXky0rrwGGglvj+tQKRbVuXOrUrQnUX1TPoUjPZjCx1VehXA51O9Z/gNG7qVNgwj7~1775392495233; bm_ss=ab8e18ef4e; ak_bmsc=B360DD9B88139D20D87F4DF5C1C2BA98~000000000000000000000000000000~YAAQ12w/F0ADrUmdAQAATpQ4Xh/l+QfhCkaccJkDyebh/OgBQCN/tSKXV4bS2ayARSHFbaaBOStuPqKL9Pmpt6JV5CUTaOZB/2BKYCwOrniF3uBOI0I4TvOpOsVFIzQYiwk41KRhY+id1DDOpo8rKHM1ESbtAzV7NgFcjp+Et9ok9y8M5cgZx8nJeNvhde6JKBZfXi4/ZKAnYfqG1deXGNgFVsJwvm4g07zFkTRqopX5dNO4mcb2QW/k4OtfS9J07YeaA4xw3A9NVnx0Nt98AkLPhu5AlSnVFejWtPob69oONT5mc9YD9V7Wtnpp5suSkah70aK9Qz8pWsTy1ljqyuzOwo27OlIx8qic1Wu9wWftEozwbH9lR+pZl99/sAXSnWnttqqjwyjmDoyVDu7f7s9vPJCCe6AiUJCe; analytics_session_id=1775402311945; ImpressionCookie=0; sessionStatus=true|undefined; FirstPage=Sun Apr 05 2026 20:53:30 GMT+0530 (India Standard Time); _scid_r=x6OjbeTg_Ffy-nUECyxfn6Q4b-JOv6BuxhRs5A; cto_bundle=a_OBAV9lWlFyNXo5ZFFLQkd4YmZHbGhJZmU0OVNDNXZieDB4TTBTY0U4U09EdWI0SXN4QTN1ZkU4VWRhdTJ6WE9JbTl5ZDNBTHp4UGRsZk55MGQwdG9yb0wxdlV5OVg4b2NZU256Qno5UEsxT2RETzBKVlNCMHBXeDlWQUUlMkZEWUNKWWplV1NmNG9IdXZzZnpmcndtanZGMzFqUSUzRCUzRA; _ga=GA1.2.1744058988.1775391297; _abck=E91817EF8A0CAB68C89AA98DF82A3631~0~YAAQzGw/FzNR/k+dAQAAeFRLXg+z1Xn9E0EFwXhzXHXwxiGBznmCzwOvfAwNIQLSzdLAHyMIDTcIjbnLgyook9I9XHXoT1qpG62+QLXO4hIwxBce9qB18CgSEU+1PeILJH2AbGh0xKF+7egfwZPPf9dZPsyP1J6Hi/US0de6qgUaIuNvgqo8ddxBA1z84LzUUl5Rw/gD6b5VJj1X3l9Q978o9G5/+pgeTqgmQnCLOYhJej/4iAQrCuY+BlCQNIgDGW+aRi/fcmF+ZlYVR1/UjEl6L4nuZqxab8r76w1DVzD3xNFg2YtWFOLeXUTqteQ8J7UGWwfXv+ZkdX6y29FG6dfnTtXBfdbYt5tI/W6pMwkYUHd5YFCCQzbCkTRO7BFzKOWZ4011Ky779TufFEqM3IOLH8fj0DS3675OwR3NCDBx7QksRiNIXz1hpRKU45TRNq5rpS3WneldRJNO8dPS0DaHXdmbOR+iaZ/7Ki5+4dlTgrBCrkjg+ASwgoqDXPtd/fEnC+pp3USDJRnGFrVlYM4Jml7NcOTTZRKTuhga23RcQJPJOojML5pJQtw4D51yAQnw1if2UHDUzhs75jjLLyJs7qbQ9wSi+7bh5s2FeOlrGG6K1bHEwgQBt2Z9fQTS++caWQ1K3ouYVFNqWJJVyDw+sAZ/ii9qiItQhqVFFArmDACwnYFDV1tk994wMgB9vXSrsV6BTVx0DPe/0Y1SjsLXUdTqn78Lw35LLCsbY1D1fiNdlBbNfQHDQMBmxzCh/2eA73A0~-1~-1~1775407088~AAQAAAAF%2f%2f%2f%2f%2f8CJkdpOW8CrNJI0qUC35u65F8ZCBEj2+uVY1UvqBItKoGxLQkA2wJ4AfyPWWSZrdWvtN6yx6YnC8rIH4TV3v%2fRBETwwYLGwcwYNMDbLYDcGeWxKZ3MNBp4V6DqTBiS2h%2fTHohaQc4jBJy4lvDXFujvKLCG38y3Vhu64UeHOLC%2fSDyMPSYR%2fp9LfJiw1wo69jBsPa3fPximx~-1; analytics_session_id.last_access=1775403940047; TS01d405db=015d0fa22695545e0ad19d8180acfa6721b08045c9b6a37aa4bad73a594cbd8183d6b84c0f1176da6a1bb726b1c4e14f8c687b0d21267e09a56c01c0e3b3dd0003e7ce1f6029341babd2fad41341acf543ddf450137243e17ce5d49d8e1c4d345b17a8b9e6; _ga_X3MNHK0RVR=GS2.1.s1775401377$o3$g1$t1775403942$j58$l0$h0; ADRUM_BT=R:0|i:6333|g:c1728ec4-ecd3-4081-84ea-076550a7fd4e1225410|e:356|n:customer1_be12de70-87be-45ee-86d9-ba878ff9a400; bm_s=YAAQzGw/FwUYAFCdAQAAGSdTXgVi1VVg4p4nUPYq9jUNWAympZYswmZ9+uHvF870hnW8OOLrhghazD8EyKta3CsvEaS7zrmfb9af6CgpIwJBEji9gEBMTYqEHZN+/NCpn7bxIRfdcSGtFuLCscUOyccnlW3bMJsWyESIgz8mP0iZjab31Msv3QyR6agYKh53YwszXLLg90C6uuV0oph+9GJExKzTQphhJY0IZl5q/IAWpyMBD2JNvJFELfxc6ErMQ85CFL0Zi52xpe6F7Wu4pMrQpTKyaiQAB/M2k5d6jtIcosbEdpNVTglSYga5K1E8Cml5kjcNY9DlRA3MCxj0iksLTQdnG5xqK8OjhzwEYuZUmmNcWs8mqjbiewF1QhpckbrbkA6YnDrm8SRYzUWl0DLQKFX8vLEy+HNpP7s8kP5Kj4x931jB3oKVO6FN0wW9D3rNTJgbHdPgaBpZfH80DryXUQzfHWXxV+bzr3ndnn3cLnD1a5w2ZQmB6hzPmgBUcCgnhdCnJfP+KNXaj/kQZOuGaeAb5w358XojodlFP5H6ydVB3KtQuFkP2+f3dAvgQJaBamW8rNI2PzJ/jLWh9RKB9ckL0bsx7r/od9HSPl/UsuEgoE3/n+vhaLt3ZjKHEiaM2zukQ+LKuKyzV/Mb2+sGImpTN07E1uCh5xUshCpgz8GGmlp5l+lUJRh6aGPetK64pKisP/bFMU59XfpiDbUmbrs0TZCbSrCD3Z5zwscVv6vFb+XrLRLy/EI1+dNF23IR5CHQ/tzv1F3sYbt8cIEW2XNG2yZXkG8wBv3hPYODQSuls1KBs4lioBaRFs+evCW7hUfyThQG24gwPwEccWuKqfzlWg4sXaGRTGXpBJNWMpXv7e/p/f0yqL/wwnKOzKmoxYJodNOh4NMVU5akBcfqw9rNCBlFnR5pwbtd5iAYaDYQAMo7M5QP1rT0K31Hjhrp54TAutJ4jLc=; bm_sv=E582F85598E018ECF407B11E366C01F0~YAAQzGw/FwYYAFCdAQAAGSdTXh8qwnJJgJ8vj1ud224EieRJzKcGLSgm1HEfOapQE8FFfd7dzuZ1T+Knhfd8NF1fOiqVBCxKZNdu3VOuI5LUuePWyYtl2OOrpwbaJzpYZruWHzFkU/rH2xZb0R64CVhaSHUTEJQAnF0BwTYFRuP9HX2dy6UFH55Q6Y+W7xlQ8XGDOPdAWke9p9xDagcTz4PeCYh0iILIL5/DBfj3ChsAsWkpZZFXA6rtiiRsENo=~1',
        'os': '4',
        # 'referer': 'https://www.ajio.com/c/8302?query=%3Arelevance%3Al1l3nestedcategory%3ABoys%20-%20Bracelets%20%26%20Bangles%3Al1l3nestedcategory%3AMen%20-%20Tshirts%3Al1l3nestedcategory%3AWomen%20-%20Tshirts&gridColumns=3&segmentIds=',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'ua': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'vr': 'WEB-1.15.0',
    }

    PDP_HEADERS = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}



    def _to_api_url(self, cat_url, category_filter=None, offset=0, page=1):
        slug = urlparse(cat_url).path.lstrip("/")
        params = {"rows": 50, "o": offset, "plaEnabled": "true", "p": page}
        if category_filter:
            params["f"] = f"Categories%3A{quote(category_filter)}"
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"https://www.myntra.com/gateway/v4/search/{slug}?{query}"
