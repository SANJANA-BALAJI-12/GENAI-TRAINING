import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}
resp = requests.get(
    'https://www.bing.com/search',
    params={'q': 'Groq AI web search agents', 'setlang': 'en-US'},
    headers=headers,
    timeout=15,
)
print('status', resp.status_code)
text = resp.text
print('has_b_algo', 'b_algo' in text)
print('has_li', '<li class="b_algo"' in text)
if 'b_algo' in text:
    idx = text.find('b_algo')
    print('snippet', text[max(0, idx-100):idx+200])

soup = BeautifulSoup(text, 'html.parser')
results = soup.select('li.b_algo')
print('results count', len(results))
for item in results[:5]:
    title = item.select_one('h2 > a')
    snippet = item.select_one('.b_caption p')
    print('title', title.get_text(strip=True) if title else None)
    print('href', title['href'] if title else None)
    print('snippet', snippet.get_text(strip=True) if snippet else None)
