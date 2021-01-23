import json
import re

import browser_cookie3
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver


cookie_text = []


def interceptor(request):
    if request.headers.get('Cookie', None):
        del request.headers['Cookie']
        request.headers['Cookie'] = cookie_text
        if not driver.last_refresh:
            driver.refresh()
            driver.last_refresh = True
    if request.url == 'https://guc-spclient.spotify.com/track-playback/v1/devices' and request.method != 'OPTIONS':
        body = request.body.decode('utf-8')
        data = json.loads(body)
        driver.device_id = data['device']['device_id']
        data['device']['name'] = 'Spotify Ad-Free Player'
        body = json.dumps(data)
        request.body = bytes(body, 'utf-8')
    if re.search(r'spotify[.]com/melody/v1/logging/', request.url, re.IGNORECASE):
        request.abort()
    if re.search(r'doubleclick[.]net/', request.url, re.IGNORECASE):
        request.abort()
    if fetch := request.headers.get('Sec-Fetch-Dest'):
        if fetch == 'video':
            request.abort()


chrome_options = Options()
chrome_options.add_experimental_option('detach', True)
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                            '(KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

cj = browser_cookie3.chrome()
# noinspection PyProtectedMember
cookies = [cj._cookies['.spotify.com'].get('/', None)] + [cj._cookies['.open.spotify.com'].get('/', None)]

for cd in cookies:
    if cd:
        for cookie in cd:
            cookie_text.append(f'{cd[cookie].name}={cd[cookie].value}; ')
cookie_text = ''.join(cookie_text)[:-2]


driver = webdriver.Chrome('chromedriver.exe', options=chrome_options,
                          seleniumwire_options={'exclude_hosts': ['guc-dealer.spotify.com'],
                                                'ignore_http_methods': []})
driver.request_interceptor = interceptor
driver.last_refresh = False

driver.get('https://open.spotify.com')

while True:
    if not driver.current_url:
        break
