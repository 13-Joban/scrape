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
        '_gcl_au': '1.1.2064905489.1775391298',
        'AB': 'B',
        'dtm_token': 'AQANMyaYFX_XhQE70WYmAQBFtwABAQCaRaKcugEBAJxckFU4',
        'dtm_consent': 'UNSPECIFIED',
        '_fbp': 'fb.1.1775391299886.510030006200279687',
        'ajs_anonymous_id': 'cf1cd2fa-3de3-4822-9cce-078f990350dd',
        '_fpuuid': 'Y6BIa6_O2i4fZfcG8jVEl',
        'deviceId': 'Y6BIa6_O2i4fZfcG8jVEl',
        '_pin_unauth': 'dWlkPU1qVTJZbVZrTW1FdFlqSTJNUzAwTUdKaUxXSTJaR1V0TTJVMllXSXpZekZoTkdKbA',
        '_scid': 'tyOjbeTg_Ffy-nUECyxfn6Q4b-JOv6Bu',
        'g_state': '{"i_l":0,"i_ll":1775392459322,"i_b":"iBopxAc9h/eI/oBjRXX8VL1eiTTXlIHhGMPayCqc0Fw","i_e":{"enable_itp_optimization":0}}',
        'cdigiMrkt': 'utm_source%3A%7Cutm_medium%3A%7Cdevice%3Adesktop%7Cexpires%3ATue%2C%2005%20May%202026%2012%3A34%3A54%20GMT%7C',
        'ak_bmsc': 'DE2EABE4711B585095CF7C90385FE7C8~000000000000000000000000000000~YAAQj7MsMSqvYnKdAQAAUxtqgh9lfyTYYAVAO26AgbOq+/u0mzV+tEMw4xwiLesldx41N0lPqh+8md705s9tof+Vu+MTgEGd+0by7KxD9H514eFMOpbwc2+2ZTEd6h4bOrhZTPmjU1Dtf2gVQmApEYUDEkEULQ56fJ0fhj6ezXEyU815R+cKyUFWsSNUuXs/jP5NDwcQ8taQJE+McQOFPO8sgItVs6F4HiD/vVwFkuBygLjG7S/X1gJQkzDx9YLL8piIVvlKQUdU/4z6tuikwvNUidoLsq4XCyIavPVoZTueV9CAJNeBoNIAm4Sj6tyyCS2XMtq+c7kej8QU3aWrFzFQ+jD7hbU97De4PbpK6o6ddzFiVdWk9vP3zWyPrIYh6CIPsVmgM+24c4U1TjJ/zXHyM5Wmfw+fA7AiCxphnaf8CCsR',
        'bm_sz': '3F800A21B27CE32BC3302967051E22A4~YAAQj7MsMSuvYnKdAQAAUxtqgh+TMDkPndvoPi0AeNhd8iHBr+TpXR/OrG8muK40xkwZ/EQFsH4tebq3F65M80Q8gm4zb8cihWu/CBurGPO4e9AeE/tkQnB7s6UJs5T8OnPNH/iQyzXz+LATzk2MadXyOwpAKmZgg79tNtgyV77JiMnRGOXElCAs2b7k5R9wykOy/1e/4CQX9HckTSqNiUra0UNeWVXbFQ9fGWMOiMHwysvysSfqa8blQVeA0Q4xfEBqD5Ub20UybGFo6rK89xPaxYA1X+KcAP6LqqAdQ0EFZ9ewlBqRDItJ/cW9I7+XepYU/sx4s/Dc7j9a4GSPO/K9YtC74yww4uyK1mp434m1zWEQlPpQuooUvfnsoKrySDnypwkQwUEpgAyA6L/FAw==~3683632~3749442',
        '_gid': 'GA1.2.1102530401.1776009490',
        'analytics_session_id': '1776009494247',
        'segment_user_id': 'null',
        'segment_device_id': 'cf1cd2fa-3de3-4822-9cce-078f990350dd',
        '_sctr': '1%7C1775932200000',
        'ajiosessionid': 'F7CD4A486B73EDE5B5958193A07C65D0.a3693',
        'bm_ss': 'ab8e18ef4e',
        'recentlyViewed': '[{"id":"466681007_blue","store":0},{"id":"443380565_khaki","store":0},{"id":"465654503_black","store":0}]',
        'ImpressionCookie': '0',
        '_abck': 'E91817EF8A0CAB68C89AA98DF82A3631~0~YAAQDcksMdN5unSdAQAAkfC6gg+t2SU+NRLIx1rPCM0lqOWVuAKt5fnLfHklSSXqCsYXPBXOd6Qc+zR8tIuseDGszKGJd5n74g9ItOhuh98fQ8c/eLyPDzuch0VVHlTvIhSLfTsDxn1FSIR8UWOVKS6X3LOuNU3yaX10pjuy/nW5og7X4ha1A9unFOYaeeTBLhR8E4X2jISZlcaF73pvnfLPFgXtj9r/D2+HtdtbtCSSqjOcEg8UYs5ArwexUZLIktfeK6sQMmceni/2J9nP29luuwm2wDmLYuTgiZCsUelyhROKTuXwPmnO7JiVtpuWjeathVYYuquEQkz4K7O7WOseJ/mH7HadqBx4PGf2Lp5+yw07orKiXfQTPR8hE2EtkZgjvKekt6llYqkkVLSicJTkptwR2Ai78fmVaeDsEcA69jfltbhPN/mj5W4hIvoP2Ds5TNkAw/qK/GLJKWYF//JMgdBOoMi8DwamjX1ZQdPA+2RpLx9K+PoTb2OWpvZ0HBx9nD3MNIZCrxqIUoYbKaLLOLqyehG4JqEIaeFnAZzwQBXNSTqFhF5RoSJWyfS9aqSmCMkLoDENxJ5R4Z6BITpdRgFEtr4edqaexkCaMOSsiGrV/zPF+bbvkNG+BghNgnN3f0j1jZA6YnNzDuuvo4AHejODUU/xkxxK7W1I7P+VATXb1WlmCewmg/Xvb+Tfh/eLH7ScCsBERV0AINAc726tV8VkkQ65nTGw4Q==~-1~-1~1776018360~AAQAAAAF%2f%2f%2f%2f%2f+xcejyCi1BxHgcXvloEFqwGq+xeS10NcVhLCEqVWIOwhBBsDhHgwVL7XbikPOA3Bm7BUY9HU4%2fvQ1BioNmoLBRfDTkfUDT3dwo0p0%2fQ7pTz3B64dXlB2ViwWY+9IG4Uw%2fdXgQ5hi1f4ymMKK8TyE8SJf3ylx8fYDGZbHKUj5g%3d%3d~-1',
        'TS01d405db': '015d0fa2265980454c7b4bda64588d25f5e06bc35cbd6642fd2e2b1f08b5151d5e2afb1b1930ea0fb1366c1e3d12e327651c8f6e35',
        'bm_so': 'BF7035D9D7D55E7E4E9EA3A3B296B7E0E0D329117FF8AD17FC0D86FF23D3D392~YAAQhLMsMYQXaU6dAQAAEcXBggf9cx2yuLLnLGDJgo/j5jZGz4YR40JOofIFQkH9AwRPPv3wZpDrUTaCCkwviD1B9ScLVktonMW90p5FKOJazxD8+TbkRxFDva6VHSfaI1frxXOYH3TlJLvgk2ze4uw7QuA9dkymNBIBKYZ9GiZAJPn1pFLVQ+UjranHoMeLylvHRDe1IYUBHjG9HGOcW+OZlbJmvYifArm2D0VeKxo5hn160g1sckV3yzP39QDKdP5qfv0ktCUa59MLaZL+edpGupNEfUyPwmKzxOxFDIWVrk7MAupHmfJ4Xbg0KFbACX9US/iJwyv4HWEwN/d9pWmH5vrTCfQF006psMwqkBPjbnKxh1i0V3zjMNIjgbD5HbX8ChrdmrvHdudGlV/TdswbgIqG8I49E3lNq/ef01ha0JDkivm5oUebM2z0Od5hl4g6v3t+xSm/7y7B/kaRmnJ8zu89J33BbN5FO3C2xfnoJZNv4nAL+SFX',
        'sessionStatus': 'true|undefined',
        'FirstPage': 'Sun Apr 12 2026 23:03:53 GMT+0530 (India Standard Time)',
        '_scid_r': 'zKOjbeTg_Ffy-nUECyxfn6Q4b-JOv6BuxhRs-A',
        '_ga': 'GA1.1.1744058988.1775391297',
        'bm_lso': 'BF7035D9D7D55E7E4E9EA3A3B296B7E0E0D329117FF8AD17FC0D86FF23D3D392~YAAQhLMsMYQXaU6dAQAAEcXBggf9cx2yuLLnLGDJgo/j5jZGz4YR40JOofIFQkH9AwRPPv3wZpDrUTaCCkwviD1B9ScLVktonMW90p5FKOJazxD8+TbkRxFDva6VHSfaI1frxXOYH3TlJLvgk2ze4uw7QuA9dkymNBIBKYZ9GiZAJPn1pFLVQ+UjranHoMeLylvHRDe1IYUBHjG9HGOcW+OZlbJmvYifArm2D0VeKxo5hn160g1sckV3yzP39QDKdP5qfv0ktCUa59MLaZL+edpGupNEfUyPwmKzxOxFDIWVrk7MAupHmfJ4Xbg0KFbACX9US/iJwyv4HWEwN/d9pWmH5vrTCfQF006psMwqkBPjbnKxh1i0V3zjMNIjgbD5HbX8ChrdmrvHdudGlV/TdswbgIqG8I49E3lNq/ef01ha0JDkivm5oUebM2z0Od5hl4g6v3t+xSm/7y7B/kaRmnJ8zu89J33BbN5FO3C2xfnoJZNv4nAL+SFX~1776015235737',
        'cto_bundle': 'F5qoCF9NZiUyRmhKZDBEOE5TcDd3UE1MVFElMkJVVWE0RCUyRmNpdGFmdGVMcUZMZGlkSlFBZHh0V0d1R25aa0dETiUyQkk5ZkdOZnRsOGlSZzA3dmZ4em4lMkJTJTJGaVQ1VUJXdnZIZ2FNZE5ielZyaktYSzBud3FPaE95dm1HSmRENlFnJTJCdiUyQnhCU1dHb3ZEQWh1WmhuSjJYSHpEd09HV3BRWXZnJTNEJTNE',
        'ADRUM_BT': 'R:33|i:6333|g:433e6573-7848-4746-bc70-4a7acea70def1566554|e:284|n:customer1_be12de70-87be-45ee-86d9-ba878ff9a400',
        'bm_s': 'YAAQhLMsMZonaU6dAQAA0THCggUlmTOzDe9KoY3uTkwMi9gHDUfJI2hHv0/acWYa2diqOJXfUTPccvfX3N1x3l104dL1xgMxK2FtPUOoQoSd/sZQGeGLRtCqXByYNS4imDFmixAKAi+8+3Otfw+hPUX5WRciZiLcLmItbZ9TMjB/p87CWA6eqaI4zyIcPQs/W0fL7aSSyV4jamx++ChOSBtHD8WcShqhhv5i+zTGFcaMdVmJeVJDZfXBycIWX8nKzTZ5UodehshBS2XethCQZ7YWlqCLyjKzB0SKTjaCbdZOn1ZRb4GvA6r0HHufTu0uwRfwOsjepk7Est0tCNKiVAGyPxa1ueLBwDLfjXK7f8BOpc25yG+aA2ZgLwHdVdJOISoO/orjELKFD9wEOJ/hXOeYDS7FVIN/M7FMyVLS3I4zr+zPC/koI+Fov1MJYST16bYasnHac36JBVKwICsf5AgByA1lG+uRRxIis4cGI8AbinHQfShbqXXiTaqNLvCAys021+iH+43wZl+kT1U0sugwEzeAuH/a8QDNSAnrRlaroh8FV6Qfs1n/kap4znbb3Y6zKG0q4YJ8QEpVdLAbV2OSa7VpZGAA1y0QYl1ygHtMA9ryIJkH/ofohaLn7QFpIeD+uJkeoCrvhf17PSOcZ18kNygY6DYmFpPO28EEMnaHZshdw9krLpUjPieX4LB5a4YDrN74Zx2RN2dmx3pOmSAClYXhviLfxbFFVqwq+IqmYJAO/QSCRo0WNLJ1zsGQ43zgQDnAovampn2MND2TlB1j48JA4F4K5RQE0DvUwEhwUhkyBddj4oOdzzMaE0P51Ebd+u2JMcnLNMWmtlrSiI8DRcWyeDWBQIukrxkfBkbFSV3T3nwG9R8zPzJ8yTdSnSVk9zy12fGkotJ6QAL+N3LJtoqqlgZo6UQjDqXFHgYjmOXIOP4NadL1VsRn/pPkZKUQbYYa',
        'bm_sv': '88ACC446291AF7948AA2DD30BD36C144~YAAQhLMsMZsnaU6dAQAA0THCgh/o9UkbagEi/kjlrJiOKpErhPGAmDcgeK0EuF5qMbziacxNiV1SRFRxhZ/mr5OWH041Zo0na/MC8b2whhlSIwJxNB6c+CyZtExOAPlhG9Hoi5X3ujCN+TziTeuZFmRYhdc/7eUTXNj9pEWuu/lQAQefIYHKbbZkgMJ5HFZfiqJSL0q+YiQ8QRrdSEfyaCGmvF4sYzUeAtJXf2uafXFDUpI+WgPyGBCA4FDCzEeF~1',
        '_ga_X3MNHK0RVR': 'GS2.1.s1776009493$o4$g1$t1776015264$j48$l0$h0',
        'analytics_session_id.last_access': '1776015264805',
    }

    headers = {
        'authority': 'www.ajio.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,kk;q=0.8',
        'ai': 'www.ajio.com',
        # 'clientip': '2409:4090:d05a:800a:2f7b:3d61:1d94:8504, 49.44.179.132, 23.210.74.82, 23.197.28.134, 23.64.59.213, 23.45.91.216',
        'os': '4',
        'referer': 'https://www.ajio.com/c/830216',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        # 'ua': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        # 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        # 'vr': 'WEB-1.15.0',
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
