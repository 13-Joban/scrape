# from curl_cffi import requests
# res = requests.get('https://www.ajio.com/api/category/8303?fields=SITE&currentPage=2&pageSize=45&format=json&query=%3Arelevance%3Al1l3nestedcategory%3AWomen+-+Sarees&gridColumns=3&facets=l1l3nestedcategory%3AWomen+-+Sarees&segmentIds=&advfilter=true&platform=Desktop&showAdsOnNextPage=false&is_ads_enable_plp=true&displayRatings=true&segmentIds=&enableRushDelivery=true&vertexEnabled=false&visitorId=1744058988.1775391297&userEncryptedId=b375ae6486ac66358e3d20b08fd626680117787dfd2fcc5d662cd09d9d8808ec&previousSource=Saas&plaAdsProvider=OSMOS&plaAdsEliminationDisabled=false&plpBannerAdsEnabled=false&state=&city=&zone=&userRestriction=&userState=LOGGED_IN', impersonate="firefox")
# print(res.text)
import json

with open('New document 1 (1).json', 'r') as f:
    d = json.loads(f.read())

with open('men_filters.json', 'w') as f:
    f.write(json.dumps(d['facets']['currentFacets']['allfacetsItems']))

