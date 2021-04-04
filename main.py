import requests
from bs4 import BeautifulSoup as bs
import wget

python_wiki_rss_url = "https://www.thenationaldailyshow.com/feed/podcast"

response = requests.get(python_wiki_rss_url)
soup = bs(response.content)

mp3_file_url = soup.select_one('enclosure').attrs['url']

filename = wget.download(mp3_file_url)


