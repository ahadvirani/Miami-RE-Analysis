import requests
from bs4 import BeautifulSoup
import json
import time
import csv

class zillowScraper():
    results = []
    headers = {
        'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding' : 'gzip, deflate, br',
        'accept-language' : 'en-US;q=0.6',
        'cache-control' : 'max-age=0',
        'cookie' : 'zguid=24|%247fcf96ba-b4d1-4f06-b687-467331cc4879; zgsession=1|28ab6cff-2774-4b24-8e4d-64aed051c286; pxcts=b3fcb84d-f340-11ec-9fe6-514f75537248; _pxvid=b3fcac4c-f340-11ec-9fe6-514f75537248; g_state={"i_p":1657852389896,"i_l":3}; JSESSIONID=A11CD71979EEF5908450DA44B206C156; _px3=732b56b99da4fb66f456ad1977c0c1ee42f3f24d61a12e05e0a838b52439df6c:7no6GgM1MnkJ4U87B/RECHeIrqAqlocnUDHEsrrCreumKliYA14WCHw1+wEphaL2fh15io7qUtqXyw/Z4iIsQg==:1000:UfF41nP8Mo+0TFpx4UUINuP+u5VsZuUSxWPlosHxqUFR5lmhqnYCTaMQgVHMYRRBaJSSrW1/OVn312XJhTo/5O03RBB5aS8jh8lP6KCwwpGGpCE8n+iRIFYVG8EPbuh9GZtjQUnUVPOwHxvvDJvccdh1fbK2dCXy+EBsfJPHds0QxCnaYCUe8ixfuMkKcPqnwlswGrpV1DjT2tqYQ6jwbg==; AWSALB=0dNrqGmdg+A4ZUSwL7UkeUGu/qSHpVFDmc/F2apbRZtvBMsCFSIxQGiVe+vkJYp4DHf4yGJwVgc0iyG+6zsHIVL0bUro+07UiK33J2QD9Lnec+u7zcrLQXXiuSNk; AWSALBCORS=0dNrqGmdg+A4ZUSwL7UkeUGu/qSHpVFDmc/F2apbRZtvBMsCFSIxQGiVe+vkJYp4DHf4yGJwVgc0iyG+6zsHIVL0bUro+07UiK33J2QD9Lnec+u7zcrLQXXiuSNk; search=6|1660068364991%7Crect%3D25.825849801930755%252C-80.03610456152344%252C25.626665913670767%252C-80.55932843847657%26rid%3D12700%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26z%3D1%26days%3D12m%26fs%3D0%26fr%3D0%26mmm%3D0%26rs%3D1%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%09%0912700%09%09%09%09%09%09',
        'referer' : 'https://www.zillow.com/',
        'sec-fetch-dest' : 'document',
        'sec-fetch-mode' : 'navigate',
        'sec-fetch-site' : 'same-origin',
        'sec-fetch-user' : '?1',
        'sec-gpc' : '1',
        'upgrade-insecure-requests' : '1',
        'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'
    }

    def fetch(self, url, params):
        response = requests.get(url, headers=self.headers, params=params)
        print(response.status_code)
        return response


    def parse(self, response):
        content = BeautifulSoup(response, 'lxml')
        deck = content.find('ul', {'class' : 'List-c11n-8-69-2__sc-1smrmqp-0 srp__sc-1psn8tk-0 ckwVds photo-cards_wow photo-cards_short photo-cards photo-cards_extra-attribution'})
        for card in deck.contents:
            script = card.find('script', {'type':'application/ld+json'})

            try:
                sqft = card.find('ul', {'class': 'list-card-details'}).findAll('li')[2].text.split(' ')[0]
            except:
                sqft = 'N/A'
            
            try:
                broker = card.find('p',{'class': 'list-card-extra-info'}).text
            except:
                broker = 'N/A'
            
            if script:
                script_json = json.loads(script.contents[0])
                self.results.append({
                    'type' : script_json['@type'],
                    'streetAddress' : script_json['address']['streetAddress'],
                    'city' : script_json['address']['addressLocality'],
                    'state' : script_json['address']['addressRegion'],
                    'postalCode' : script_json['address']['postalCode'],
                    'bedCount' : card.find('ul', {'class': 'list-card-details'}).findAll('li')[0].text.split(' ')[0],
                    'bathCount' : card.find('ul', {'class': 'list-card-details'}).findAll('li')[1].text.split(' ')[0],
                    'size' : sqft,
                    'realEstateBroker' : card.find('p',{'class': 'list-card-extra-info'}).text,
                    'price' : card.find('div', {'class': 'list-card-price'}).text,
                    'url' : script_json['url']
                })


    def to_csv(self):
        with open('zillowMiami.csv', 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.results[0].keys())
            writer.writeheader()

            for row in self.results:
                writer.writerow(row)

    def run(self):
        url = 'https://www.zillow.com/miami-fl/sold/'

        for page in range(1,20):
            params = {
                'searchQueryState' : '{"pagination":{"currentPage": %s},"usersSearchTerm":"Miami, FL","mapBounds":{"west":-80.55932843847657,"east":-80.03610456152344,"south":25.626665913670767,"north":25.825849801930755},"regionSelection":[{"regionId":12700,"regionType":6}],"isMapVisible":true,"filterState":{"doz":{"value":"12m"},"sort":{"value":"globalrelevanceex"},"fsba":{"value":false},"fsbo":{"value":false},"nc":{"value":false},"fore":{"value":false},"cmsn":{"value":false},"auc":{"value":false},"rs":{"value":true},"ah":{"value":true}},"isListVisible":true,"mapZoom":11}' %page
            }
            res = self.fetch(url, params)
            self.parse(res.text)
            time.sleep(2)
        self.to_csv()

if __name__ == '__main__':
    scraper = zillowScraper()
    scraper.run()