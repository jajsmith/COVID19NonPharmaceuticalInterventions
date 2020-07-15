import requests
import urllib.request
import urllib3
import datetime
from bs4 import BeautifulSoup
import pandas as pd
import feedparser
from datetime import date
from datetime import datetime
import re

_country = 'Canada'
_src_cat = 'Government Website'
_columns = ['start_date', 'country', 'region', 'subregion', 'source_url', 'source_category', 'source_title', 'source_full_text']

def _load_ontario(since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of New Brunswick.
    """    
    today = date.today()
    today_str = str(today).replace('-', '%2F')

    base_url = 'https://news.ontario.ca/en/search?content_type=all&utf8=%E2%9C%93&date_range_end=' + today_str + '&date_range_start=2020%2F01%2F01&date_select=desc&page='
#     targets = [base_url + str(i) for i in range(1,4)]

    region = 'Ontario'
    subregion = ''

    if verbose: print("\nLoading {} Releases\n".format(region))

    # Specific structure for news.contario.ca/archive
    rows = []
    page = 1
    while True:
        if verbose: print('Searching page ', page)
        target = base_url + str(page)

        response = requests.get(target)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.findAll('article')

        if len(articles) == 0:
            if verbose: print('No articles found.')
            return pd.DataFrame(rows, columns=_columns)

        for article in articles:
            smallersoup = BeautifulSoup(str(article), "html.parser")
            link = smallersoup.findAll('a')[0]['href']
            title = smallersoup.findAll('a')[0].string
            pub_date = datetime.strptime(smallersoup.time.string.replace('.', ''), "%B %d, %Y %I:%M %p")
            
            if pub_date < since:
                return pd.DataFrame(rows, columns=_columns)
            
            response = requests.get(link)
            linksoup = BeautifulSoup(response.text, "html.parser")
            full_text = linksoup.article.text

            row = [pub_date, _country, region, subregion, link, _src_cat, title, full_text]
            rows.append(row)

        page += 1

def _load_manitoba(since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates
    
    Returns: a DataFrame containing news releases from the government of New Brunswick.
    """
    
    url_base = 'https://news.gov.mb.ca'
    targets = [url_base + '/news/index.html?month=' + str(i) + '&year=2020&day=01&bgnG=GO&d=' for i in range(12,1,-1)] # prevents stopping early

    region = 'Manitoba'
    subregion = ''

    if verbose: print("\nLoading {} Releases\n".format(region))
    
    rows = []
    for target in targets:
        if verbose: print(target)
        if target.startswith(url_base): #manitoba
            response = requests.get(target)
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.findAll("div", {"class": "maincontent"})
            smallersoup = BeautifulSoup(str(items), "html.parser")
            for article in smallersoup.findAll('h2'):
                a = article.a
                relative_link = a['href']
                link = url_base + relative_link.split('..')[-1]
                title = a.string

                response = requests.get(link)
                linksoup = BeautifulSoup(response.text, "html.parser")

                date_text = linksoup.findAll("span", {"class": "article_date"})[0].string
                pub_date = datetime.strptime(date_text, '%B %d, %Y') # January 31, 2020
                
                if pub_date < since:
                    return pd.DataFrame(rows, columns=_columns)

                full_text = linksoup.findAll("div", {"class": ""})[0].text


                row = [pub_date, _country, region, subregion, link, _src_cat, title, full_text]
                rows.append(row)

                # Get this link and copy full text
    return pd.DataFrame(rows, columns=_columns)

def _load_british_columbia(since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of New Brunswick.
    """
        
    region = 'British Columbia'
    subregion = ''
    
    if verbose: print("\nLoading {} Releases\n".format(region))

    query_url = 'https://news.gov.bc.ca/Search?FromDate=01/01/2020&Page='
    rows = []
    page = 1
    
    while True:
        if verbose: print("Page ", page)
        target = query_url + str(page)
        response = requests.get(target)
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.findAll("div", {"class": "article"})

        if not items:
            return pd.DataFrame(rows, columns=_columns)

        for article in items:
            smallersoup = BeautifulSoup(str(article), "html.parser")

            #for article in smallersoup.findAll('div'):

            title = smallersoup.a.string

            date_text = smallersoup.findAll("div", {"class" : "item-date"})[0].string
            pub_date = datetime.strptime(date_text, '%A, %B %d, %Y %I:%M %p') # Friday, July 10, 2020 12:30 PM
            
            if pub_date < since:
                return pd.DataFrame(rows, columns=_columns)

            link = smallersoup.a['href']

            response = requests.get(link)
            linksoup = BeautifulSoup(response.text, "html.parser")
            get_article = linksoup.findAll("article")
            if get_article:
                full_text = get_article[0].text
            else:
                if verbose: print("Couldn't retrieve full text for link: ", link)
                full_text = ""

            row = [pub_date, _country, region, subregion, link, _src_cat, title, full_text]
            rows.append(row)

        page += 1

def _load_new_brunswick(since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates

    
    Returns: a DataFrame containing news releases from the government of New Brunswick.
    """
    
    region = 'New Brunswick'
    sub_region = ''
    
    if verbose: print("\nLoading {} Releases\n".format(region))
    
    url_base = "https://www2.gnb.ca/"
    url = url_base + "content/gnb/en/news/recent_news.html?mainContent_par_newslist_start="
    start = 0
    rows = []
    
    while True:
        if verbose: print("Page {}".format(str(start // 25 + 1)))
        response = requests.get(url + str(start))
        soup = BeautifulSoup(response.content, "html.parser")

        article_div = soup.find('div', class_="none padded")
        article_soup = BeautifulSoup(str(article_div), 'html.parser')
        articles = article_soup.find_all('li')

        for article in articles:
            small_soup = BeautifulSoup(str(article), 'html.parser')
            ar_date_str = small_soup.find('span', class_="post_date")
            
            if ar_date_str: # ensure list entry corresponds to dated article
                # Date
                ar_date = datetime.strptime(ar_date_str.text, "%d %B %Y")
                
                if ar_date < since: # only collect data after specified date
                    if verbose: print("Stopping search at date {}".format(ar_date))
                    return pd.DataFrame(rows, columns=_columns)
                
                a = article.a
                # Title
                title = a.text
                # Body
                relative_link = a['href']
                link = url_base + relative_link
                article_page = requests.get(link)
                body_soup = BeautifulSoup(article_page.content, 'html.parser')
                body = body_soup.find('div', class_="articleBody").text
                
                row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
                rows.append(row)
#                 print("{}: {}\n".format(ar_date, title))
                

        start += 25 # articles per page

def _load_nova_scotia(since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Nova Scotia. 
    """
    region = 'Nova Scotia'
    sub_region = ''
    
    if verbose: print("\nLoading {} Releases\n".format(region))
    
    url_base = "https://novascotia.ca/news"
    page = 1
    
    rows = []
    
    while True:
        url = url_base + "/search/?page=" + str(page)
        if verbose: print("Searching page {}".format(page))
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        titles = soup.find_all('dt', class_="RelTitle")
        summaries = soup.find_all('dd', class_="RelSummary")
        
        for title, summary in zip(titles, summaries):
            
            if title['lang'] == "fr": continue
                        
            ar_date = datetime.strptime(summary.time.text, "%B %d, %Y - %I:%M %p")
            
            if ar_date < since:
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)
            
            relative_link = title.a['href'].split('..', 1)[1]
            link = url_base + relative_link
            
            ar_response = requests.get(link)
            ar_soup = BeautifulSoup(ar_response.content, 'html.parser')
            body = ar_soup.find('div', {'id' : 'releaseBody'}).text
            
            row = [ar_date, _country, region, sub_region, link, _src_cat, title.text, body]
            rows.append(row)

            
        page += 1
        
def _load_northwest_territories(since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of the Northwest Territories.    
    """
    region = 'Northwest Territories'
    sub_region = ''
    
    if verbose: print("\nLoading {} Releases\n".format(region))
    
    url_base = "https://www.gov.nt.ca/"
    page = 0
    
    rows = []
    
    while True:
        url = url_base + "en/newsroom?page=" + str(page)
        if verbose: print("Searching page {}".format(page + 1))
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        ar_boxes = soup.find_all('div', class_ = re.compile('views-row')) # regex accounts for inconsistent `div` class names
        
        for box in ar_boxes:
            boxed_soup = BeautifulSoup(str(box), 'html.parser') # parse each div
            date_str = boxed_soup.find('span').text
            ar_date = datetime.strptime(date_str, "%B %d, %Y")
            
            if ar_date < since: 
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)
            
            title_a = boxed_soup.find('a')
            title = title_a.text
            relative_link = title_a['href']
            
            link = url_base + relative_link
            ar_res = requests.get(link)
            ar_soup = BeautifulSoup(ar_res.content, 'html.parser')
            body = ar_soup.find('div', class_ = "field-item even").text
            
            row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
            rows.append(row)
            
        page += 1
        
def _load_saskatchewan(since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Saskatchewan.
    """
    
    region = 'Saskatchewan'
    sub_region = ''
    
    if verbose: print("\nLoading {} Releases\n".format(region))
    
    url_base = "https://www.saskatchewan.ca/government/news-and-media?page="
    page = 1
    
    rows = []
    
    while True:
        url = url_base + str(page)
        if verbose: print("Searching page {}".format(page))
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        article_list = soup.find('ul', class_="results")
        article_soup = BeautifulSoup(str(article_list), 'html.parser')
        list_items = article_soup.find_all('li')
        
        for item in list_items:
            
            date_str = item.time['datetime']
            ar_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            if ar_date < since: 
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)
            
            title = item.a.text
            link = item.a['href']
            
            body_soup = BeautifulSoup(requests.get(link).content, 'html.parser')
            body = body_soup.find('section', class_="general-content").text
            
            row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
            rows.append(row)
            
        page += 1
        
def _load_nunavut(since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Nunavut.
    
    Parameters: datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
    """
    
    region = 'Nunavut'
    sub_region = ''
    
    if verbose: print("\nLoading {} Releases\n".format(region))
    
    url_base = "https://gov.nu.ca"
    page = 0
    
    rows = []
    
    while True:
        url = url_base + "/news?page=" + str(page)
        if verbose: print("Searching page {}".format(page + 1))
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        main_section = soup.find('section', {"id" : "block-system-main"})
        main_section_soup = BeautifulSoup(str(main_section), 'html.parser')
        
        divs = main_section_soup.find_all('div', re.compile('views-row(.*)'))
        
        for div in divs:
            
            div_soup = BeautifulSoup(str(div), 'html.parser')
            date_str = div_soup.find('span', class_="date-display-single").text
            ar_date = datetime.strptime(date_str, "%d %B %Y")
            
            if ar_date < since: 
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)
            
            a = div_soup.find('a')
            title = a.text
            link = url_base + a['href']
                        
            body_soup = BeautifulSoup(requests.get(link).content, 'html.parser')
            body = body_soup.find('div', class_="region region-content").text
            
            row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
            rows.append(row)
            
        page += 1
        
def _load_yukon(since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of the Yukon.
    """
    
    region = 'Yukon'
    sub_region = ''
    
    if verbose: print("\nLoading {} Releases\n".format(region))
    
    url_base = "https://yukon.ca"
    page = 0
    
    rows = []
    
    while True:
        url = url_base + "/news?page=" + str(page)
        if verbose: print("Searching page {}".format(page + 1))
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        main_div = soup.find('div', class_ = "view-content")
        main_div_soup = BeautifulSoup(str(main_div), 'html.parser')
        
        divs = main_div_soup.find_all('div', re.compile('views-row(.*)'))
        
        for div in divs:
            
            div_soup = BeautifulSoup(str(div), 'html.parser')
            date_str = div_soup.find('small').text
            ar_date = datetime.strptime(date_str, "%B %d, %Y")
            
            if ar_date < since: 
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)
            
            a = div_soup.find('a')
            title = a.text
            link = url_base + a['href']
                        
            body_soup = BeautifulSoup(requests.get(link).content, 'html.parser')
            body = body_soup.find('div', class_="region region-content").text
            row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
            rows.append(row)
            
        page += 1
        
def _load_pei(since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Prince Edward Island.
    """
    
    region = 'Prince Edward Island'
    sub_region = ''
    
    if verbose: print("\nLoading {} Releases\n".format(region))
    
    url_base = "https://www.princeedwardisland.ca"
    page = 0
    
    rows = []
    
    while True:
        url = url_base + "/news?page=" + str(page)
        if verbose: print("Searching page {}".format(page + 1))
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        divs = soup.find_all('div', class_="right content views-fieldset")
        
        for div in divs:
                        
            div_soup = BeautifulSoup(str(div), 'html.parser')
            date_str = div_soup.find('div', class_="date").text
            ar_date = datetime.strptime(date_str, "%A, %B %d, %Y")
            
            if ar_date < since: 
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)
            
            a = div_soup.find('a')
            title = a.text
            link = url_base + a['href']
            
            body_soup = BeautifulSoup(requests.get(link).content, 'html.parser')
            body = body_soup.find('div', class_="maincontentmain").text
                        
            row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
            rows.append(row)
            
        page += 1
        
def _load_alberta(since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Alberta.
    """
    
    region = 'Alberta'
    sub_region = ''
    
    if verbose: print("\nLoading {} Releases\n".format(region))
    
    days_back = (datetime.today() - since).days
    url = "https://www.alberta.ca/NewsRoom/newsroom.cfm?numDaysBack=" + str(days_back + 1)
    
    rows = []
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
        
    links = [link.text for link in soup.find_all('link')[2:]] # First two links are not articles
    titles = [title.text for title in soup.find_all('title')[2:]] # First two titles are not articles
    dates = [date.text for date in soup.find_all('pubDate')]
    
    for link, title, date in zip(links, titles, dates):
        
        ar_date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S -0600")
        
        ar_page_soup = BeautifulSoup(requests.get(link).content, 'html.parser')
        ar_main = ar_page_soup.find('main')
        body_soup = BeautifulSoup(str(ar_main), 'html.parser')
        body = body_soup.find('div', class_="goa-grid-100-100-100").text
        
        row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
        rows.append(row)
                
    return pd.DataFrame(rows, columns=_columns)

def _load_quebec(since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Quebec.
    """
    
    region = 'Quebec'
    sub_region = ''
    
    if verbose: print("\nLoading {} Releases\n".format(region))
    
    url_base = "http://www.fil-information.gouv.qc.ca/Pages/Articles.aspx?lang=en&Page="
    page = 1
    
    rows = []
    
    while True:
        url = url_base + str(page)
        
        if verbose: print("Searching page {}".format(page))
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
                
        sections = soup.find_all('section', {"id" : "articles"})
        
        for section in sections:
            date_str = section.time['datetime']
            ar_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            if ar_date < since:
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)
            
            for a in section.find_all('a'):
            
                link = a['href']
                title = a.text.replace('\r', '')
                title = title.replace('\n', '')

                body_soup = BeautifulSoup(requests.get(link).content, 'html.parser')
                body = body_soup.find('div', class_="article").text

                row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
                rows.append(row)
            
        page += 1

def _load_newfoundland(since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Newfoundland.
    """
    
    region = 'Newfoundland'
    sub_region = ''
    
    if verbose: print("\nLoading {} Releases\n".format(region))
    
    current_year = datetime.today().year
    
    rows = []
    
    for year in range(current_year, since.year - 1, -1): # Not likely to be relevant in the near future
        url = "https://www.gov.nl.ca/releases/r/?ny=" + str(year) + "&nm=&ntype=&ndept="

        http = urllib3.PoolManager()

        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, 'html.parser')
        news_results = soup.find('div', class_ = "news-results")
        dates = news_results.find_all('h2')
        ar_lists = news_results.find_all('ul')
        

        for date, ar_list in zip(dates, ar_lists):
            ar_date = datetime.strptime(date.text + " 2020", "%B %d %Y")
            if verbose: print("Searching date: " + ar_date.strftime("%B %d %Y"))

            if ar_date < since:
                return pd.DataFrame(rows, columns=_columns)
                        
            for article in ar_list:
                title = article.a.text
                link = article.a['href']
                
                body_response = http.request('GET', link)
                body_soup = BeautifulSoup(body_response.data, 'html.parser')
                body = body_soup.find('div', class_ = "entry-content").text
                                
                row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
                rows.append(row)
    
    return pd.DataFrame(rows, columns=_columns)

def _load_province(province, since=datetime(2020, 1, 1), verbose=True):
    """
    Parameters: 
        - `province`
            string, represents the name of the province or territory whose releases are to be retrieved
        - `since` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published since Jan 1 2020 are retrieved.
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of the specified province or territory.
    """

    switcher = {'alberta' : _load_alberta, 
            'british columbia' : _load_british_columbia, 
            'manitoba' : _load_manitoba, 
            'new brunswick' : _load_new_brunswick, 
            'newfoundland' : _load_newfoundland,
            'northwest territories' : _load_northwest_territories, 
            'nova scotia' : _load_nova_scotia, 
            'nunavut' : _load_nunavut, 
            'ontario' : _load_ontario, 
            'pei' : _load_pei, 
            'quebec' : _load_quebec, 
            'saskatchewan' : _load_saskatchewan, 
            'yukon' : _load_yukon,
           }
    return switcher[province.lower()](since, verbose)

def _csv_path(province):
    """
    Returns the relative CSV path for a given province string
    """
    return 'sources/' + province.replace(' ', '').lower() + '.csv'

def load_province(province, verbose=True):
    """
    Parameters: 
        - `province`
            string, the name of the province or territory to be loaded
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of the specified province or territory.
    """
    try:
        province_df = pd.read_csv(_csv_path(province))
        province_df = province_df.drop('Unnamed: 0', axis=1) 
        
        province_df["start_date"] = pd.to_datetime(province_df["start_date"])
        
        largest_date = province_df["start_date"].max()            
        new_additions = _load_province(province, since=largest_date, verbose=verbose)  
        
        df = new_additions.append(province_df).drop_duplicates(['source_full_text', 'source_url'])
    except:
        if verbose: print('Failed to find CSV path')
        df = _load_province(province, verbose=verbose)
        
    df.to_csv(_csv_path(province))
    return df

def load_alberta(verbose=True):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Alberta.
    """
    return load_province('alberta', verbose)

def load_british_columbia(verbose=True):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of British Columbia.
    """
    return load_province('british columbia', verbose)

def load_manitoba(verbose=True):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Manitoba.
    """
    return load_province('manitoba', verbose)

def load_new_brunswick(verbose=True):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of New Brunswick.
    """
    return load_province('new brunswick', verbose)

def load_newfoundland(verbose=True):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Newfoundland.
    """
    return load_province('newfoundland', verbose)

def load_northwest_territories(verbose=True):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of the Northwest Territories.
    """
    return load_province('northwest territories', verbose)

def load_nova_scotia(verbose=True):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Nova Scotia.
    """
    return load_province('nova scotia', verbose)

def load_nunavut(verbose=True):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Nunavut.
    """
    return load_province('nunavut', verbose)

def load_ontario(verbose=True):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Ontario.
    """
    return load_province('ontario', verbose)

def load_pei(verbose=True):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Prince Edward Island.
    """
    return load_province('pei', verbose)

def load_quebec(verbose=True):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Quebec.
    """
    return load_province('quebec', verbose)

def load_saskatchewan(verbose=True):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Saskatchewan.
    """
    return load_province('saskatchewan', verbose)

def load_yukon(verbose=True):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Yukon.
    """
    return load_province('yukon', verbose)

def load_provinces(verbose=False):
    """
    Parameters: 
        - `verbose`
            boolean, whether or not the function should print updates (False by default)

    Returns: a dictionary mapping the names of provinces and territories to DataFrames containing information about their new releases.
    """
    return {'alberta' : load_alberta(verbose), 
            'british columbia' : load_british_columbia(verbose), 
            'manitoba' : load_manitoba(verbose), 
            'new brunswick' : load_new_brunswick(verbose), 
            'newfoundland' : load_newfoundland(verbose),
            'northwest territories' : load_northwest_territories(verbose), 
            'nova scotia' : load_nova_scotia(verbose), 
            'nunavut' : load_nunavut(verbose), 
            'ontario' : load_ontario(verbose), 
            'pei' : load_pei(verbose), 
            'quebec' : load_quebec(verbose), 
            'saskatchewan' : load_saskatchewan(verbose), 
            'yukon' : load_yukon(verbose),
           }
