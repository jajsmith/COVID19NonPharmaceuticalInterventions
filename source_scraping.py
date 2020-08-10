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
from warnings import warn

_country = 'Canada'
_src_cat = 'Government Website'
_columns = ['start_date', 'country', 'region', 'subregion', 'source_url', 'source_category', 'source_title', 'source_full_text']

def _load_ontario(start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Ontario.
    """    

    # Start searching at `end_date` date
    end_str = end_date.strftime('%Y/%m/%d')
    start_str = start_date.strftime('%Y/%m/%d')

    base_url = 'https://news.ontario.ca/en/search?content_type=all&utf8=%E2%9C%93&date_range_end=' + end_str + '&date_range_start=' + start_str + '&date_select=desc&page='

    region = 'Ontario'
    subregion = ''

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
            
            if pub_date < start_date:
                return pd.DataFrame(rows, columns=_columns)

            if pub_date > end_date: # Articles that follow the `end_date` parameter are ignored
                continue
            
            response = requests.get(link)
            linksoup = BeautifulSoup(response.text, "html.parser")
            full_text = linksoup.article.text

            row = [pub_date, _country, region, subregion, link, _src_cat, title, full_text]
            rows.append(row)

        page += 1

def _load_manitoba(start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved.
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `verbose`
            boolean, whether or not the function should print updates

    
    Returns: a DataFrame containing news releases from the government of Manitoba.
    """
    
    month_start = datetime(start_date.year, start_date.month, 1) # If the date range does not begin on the start of the month it skips the month in its entirety.
    dates_between = pd.date_range(start=month_start, end=end_date, freq="MS")

    url_base = 'https://news.gov.mb.ca'
    # reversed to account for the most recent to least recent convention adopted when loading articles
    targets = reversed([url_base + '/news/index.html?month=' + str(date.month) + '&year=' + str(date.year) + '&day=01&bgnG=GO&d=' for date in dates_between])

    region = 'Manitoba'
    subregion = ''
    
    rows = []
    for target in targets:
        if verbose: 
            print('Searching link', target)
        if target.startswith(url_base):
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
                pub_date = datetime.strptime(date_text, '%B %d, %Y')
                
                if pub_date < start_date:
                    return pd.DataFrame(rows, columns=_columns)

                if pub_date > end_date: # Articles that follow the `end_date` parameter are ignored
                    continue

                full_text = linksoup.findAll("div", {"class": ""})[0].text


                row = [pub_date, _country, region, subregion, link, _src_cat, title, full_text]
                rows.append(row)

    return pd.DataFrame(rows, columns=_columns)

def _load_british_columbia(start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of British Columbia.
    """

    region = 'British Columbia'
    subregion = ''

    query_url = 'https://news.gov.bc.ca/Search?FromDate=' + start_date.strftime('%Y/%m/%d') + '&toDate=' + end_date.strftime('%Y/%m/%d') + '&Page='
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

            title = smallersoup.a.string

            date_text = smallersoup.findAll("div", {"class" : "item-date"})[0].string
            pub_date = datetime.strptime(date_text, '%A, %B %d, %Y %I:%M %p')
            
            if pub_date < start_date:
                return pd.DataFrame(rows, columns=_columns)

            if pub_date > end_date: # Articles that follow the `end_date` parameter are ignored
                continue

            link = smallersoup.a['href']

            response = requests.get(link)
            linksoup = BeautifulSoup(response.text, "html.parser")
            get_article = linksoup.findAll("article")
            if get_article:
                full_text = get_article[0].text
            else:
                if verbose: print("Couldn't retrieve full text for link: ", link)
                continue

            row = [pub_date, _country, region, subregion, link, _src_cat, title, full_text]
            rows.append(row)

        page += 1

def _load_new_brunswick(start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `verbose`
            boolean, whether or not the function should print updates

    
    Returns: a DataFrame containing news releases from the government of New Brunswick.
    """
    
    region = 'New Brunswick'
    sub_region = ''
    
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

        if len(articles) == 1: # Only button that says "previous page"
            return pd.DataFrame(rows, columns=_columns)

        for article in articles:
            small_soup = BeautifulSoup(str(article), 'html.parser')
            ar_date_str = small_soup.find('span', class_="post_date")
            
            if ar_date_str:
                ar_date = datetime.strptime(ar_date_str.text, "%d %B %Y")
                
                if ar_date < start_date:
                    if verbose: print("Stopping search at date {}".format(ar_date))
                    return pd.DataFrame(rows, columns=_columns)

                if ar_date > end_date:
                    continue

                a = article.a
                title = a.text

                relative_link = a['href']
                link = url_base + relative_link
                article_page = requests.get(link)

                body_soup = BeautifulSoup(article_page.content, 'html.parser')
                body = body_soup.find('div', class_="articleBody").text
                
                row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
                rows.append(row)
        start += 25 # articles per page

def _load_nova_scotia(start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Nova Scotia. 
    """

    region = 'Nova Scotia'
    sub_region = ''
    
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

        if not (titles or summaries):
            return pd.DataFrame(rows, columns=_columns)

        for title, summary in zip(titles, summaries):
            
            if title['lang'] == "fr": continue
                        
            ar_date = datetime.strptime(summary.time.text, "%B %d, %Y - %I:%M %p")
            
            if ar_date < start_date:
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)
            
            if ar_date > end_date: # Articles that follow the `end_date` parameter are ignored
                continue
            
            relative_link = title.a['href'].split('..', 1)[1]
            link = url_base + relative_link
            
            ar_response = requests.get(link)
            ar_soup = BeautifulSoup(ar_response.content, 'html.parser')
            body = ar_soup.find('div', {'id' : 'releaseBody'}).text
            
            row = [ar_date, _country, region, sub_region, link, _src_cat, title.text, body]
            rows.append(row)

            
        page += 1
        
def _load_northwest_territories(start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of the Northwest Territories.    
    """

    region = 'Northwest Territories'
    sub_region = '' 
    
    url_base = "https://www.gov.nt.ca/"
    page = 0
    
    rows = []
    
    while True:
        url = url_base + "en/newsroom?page=" + str(page)
        if verbose: print("Searching page {}".format(page + 1))
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        ar_boxes = soup.find_all('div', class_ = re.compile('views-row')) # regex accounts for inconsistent `div` class names
        
        if not ar_boxes:
            return pd.Dataframe(rows, columns=_columns)

        for box in ar_boxes:
            boxed_soup = BeautifulSoup(str(box), 'html.parser') # parse each div
            date_str = boxed_soup.find('span').text
            ar_date = datetime.strptime(date_str, "%B %d, %Y")
            
            if ar_date < start_date: 
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)

            if ar_date > end_date: # Articles that follow the `end_date` parameter are ignored
                continue
            
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
        
def _load_saskatchewan(start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Saskatchewan.
    """
    
    region = 'Saskatchewan'
    sub_region = ''
    
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

        if not list_items:
            return pd.DataFrame(rows, columns=_columns)        
        
        for item in list_items:
            
            date_str = item.time['datetime']
            ar_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            if ar_date < start_date: 
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)

            if ar_date > end_date: # Articles that follow the `end_date` parameter are ignored
                continue
            
            title = item.a.text
            link = item.a['href']
            
            body_soup = BeautifulSoup(requests.get(link).content, 'html.parser')
            body = body_soup.find('section', class_="general-content").text
            
            row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
            rows.append(row)
            
        page += 1
        
def _load_nunavut(start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Nunavut.
    
    Parameters: datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved.
    """

    region = 'Nunavut'
    sub_region = ''
    
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

        if not divs:
            return pd.DataFrame(rows, columns=_columns)        
        
        for div in divs:
            
            div_soup = BeautifulSoup(str(div), 'html.parser')
            date_str = div_soup.find('span', class_="date-display-single").text
            ar_date = datetime.strptime(date_str, "%d %B %Y")
            
            if ar_date < start_date: 
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)

            if ar_date > end_date: # Articles that follow the `end_date` parameter are ignored
                continue
            
            a = div_soup.find('a')
            title = a.text
            link = url_base + a['href']
                        
            body_soup = BeautifulSoup(requests.get(link).content, 'html.parser')
            body = body_soup.find('div', class_="region region-content").text
            
            row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
            rows.append(row)
            
        page += 1
        
def _load_yukon(start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of the Yukon.
    """

    region = 'Yukon'
    sub_region = ''
    
    url_base = "https://yukon.ca"
    page = 0
    
    rows = []
    
    while True:
        url = url_base + "/news?page=" + str(page)
        if verbose: print("Searching page {}".format(page + 1))
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        main_div = soup.find('div', class_ = "view-content")

        if not main_div:
            return pd.DataFrame(rows, columns=_columns)

        main_div_soup = BeautifulSoup(str(main_div), 'html.parser')
        
        divs = main_div_soup.find_all('div', re.compile('views-row(.*)'))
        
        for div in divs:
            
            div_soup = BeautifulSoup(str(div), 'html.parser')
            date_str = div_soup.find('small').text
            ar_date = datetime.strptime(date_str, "%B %d, %Y")
            
            if ar_date < start_date: 
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)
            
            if ar_date > end_date: # Articles that follow the `end_date` parameter are ignored
                continue

            a = div_soup.find('a')
            title = a.text
            link = url_base + a['href']
                        
            body_soup = BeautifulSoup(requests.get(link).content, 'html.parser')
            body = body_soup.find('div', class_="region region-content").text
            row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
            rows.append(row)
            
        page += 1
        
def _load_pei(start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Prince Edward Island.
    """

    region = 'Prince Edward Island'
    sub_region = ''
    
    url_base = "https://www.princeedwardisland.ca"
    page = 0
    
    rows = []
    
    while True:
        url = url_base + "/news?page=" + str(page)
        if verbose: print("Searching page {}".format(page + 1))
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        divs = soup.find_all('div', class_="right content views-fieldset")

        if not divs:
            return pd.DataFrame(rows, columns=_columns)        

        for div in divs:
                        
            div_soup = BeautifulSoup(str(div), 'html.parser')
            date_str = div_soup.find('div', class_="date").text
            ar_date = datetime.strptime(date_str, "%A, %B %d, %Y")
            
            if ar_date < start_date: 
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)
            
            if ar_date > end_date: # Articles that follow the `end_date` parameter are ignored
                continue

            a = div_soup.find('a')
            title = a.text
            link = url_base + a['href']
            
            body_soup = BeautifulSoup(requests.get(link).content, 'html.parser')
            body = body_soup.find('div', class_="maincontentmain").text
                        
            row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
            rows.append(row)
            
        page += 1
        
def _load_alberta(start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Alberta.
    """

    region = 'Alberta'
    sub_region = ''
    
    days_back = (datetime.today() - start_date).days
    url = "https://www.alberta.ca/NewsRoom/newsroom.cfm?numDaysBack=" + str(days_back + 1)
    
    rows = []
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
        
    links = [link.text for link in soup.find_all('link')[2:]] # First two links are not articles
    titles = [title.text for title in soup.find_all('title')[2:]] # First two titles are not articles
    dates = [date.text for date in soup.find_all('pubDate')]
    
    for link, title, date in zip(links, titles, dates):
        
        ar_date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S -0600")

        if ar_date > end_date: # Articles that follow the `end_date` parameter are ignored
             continue
        
        if verbose: print('Searching date ' + ar_date.strftime('%B %d, %Y'))

        ar_page_soup = BeautifulSoup(requests.get(link).content, 'html.parser')
        ar_main = ar_page_soup.find('main')
        body_soup = BeautifulSoup(str(ar_main), 'html.parser')
        body = body_soup.find('div', class_="goa-grid-100-100-100").text
        
        row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
        rows.append(row)
                
    return pd.DataFrame(rows, columns=_columns)

def _load_quebec(start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Quebec.
    """
    
    region = 'Quebec'
    sub_region = ''
    
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
                    
            if ar_date < start_date:
                if verbose: print("Stopping search at date {}".format(ar_date))
                return pd.DataFrame(rows, columns=_columns)
            
            if ar_date > end_date: # Articles that follow the `end_date` parameter are ignored
                continue

            
            for a in section.find_all('a'):
            
                link = a['href']
                title = a.text.replace('\r', '')
                title = title.replace('\n', '')

                body_soup = BeautifulSoup(requests.get(link).content, 'html.parser')
                body = body_soup.find('div', class_="article").text

                row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
                rows.append(row)
        
        if not soup.find('li', class_='last'): # No 'go to last page' indicates that this is the last page
            if verbose: print("Stopping search at date {}".format(ar_date))
            return pd.DataFrame(rows, columns=_columns)

        page += 1

def _load_newfoundland(start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of Newfoundland.
    """

    region = 'Newfoundland and Labrador'
    sub_region = ''
    
    current_year = datetime.today().year
    
    rows = []
    
    for year in range(current_year, start_date.year - 1, -1): # Searches range backwards
        url = "https://www.gov.nl.ca/releases/r/?ny=" + str(year) + "&nm=&ntype=&ndept="

        http = urllib3.PoolManager()

        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, 'html.parser')
        news_results = soup.find('div', class_ = "news-results")
        dates = news_results.find_all('h2')
        ar_lists = news_results.find_all('ul')
        

        for date, ar_list in zip(dates, ar_lists):
            ar_date = datetime.strptime(date.text + " " + str(year), "%B %d %Y")

            if ar_date < start_date:
                return pd.DataFrame(rows, columns=_columns)

            if ar_date > end_date: # Articles that follow the `end_date` parameter are ignored
                continue

            if verbose: print("Searching date: " + ar_date.strftime("%B %d %Y"))
                        
            for article in ar_list:
                title = article.a.text
                link = article.a['href']
                
                body_response = http.request('GET', link)
                body_soup = BeautifulSoup(body_response.data, 'html.parser')
                body = body_soup.find('div', class_ = "entry-content").text
                                
                row = [ar_date, _country, region, sub_region, link, _src_cat, title, body]
                rows.append(row)
    
    return pd.DataFrame(rows, columns=_columns)

def _load_province(province, start_date=datetime(2020, 1, 1), end_date=datetime.today(), verbose=True):
    """
    Parameters: 
        - `province`
            string, represents the name of the province or territory whose releases are to be retrieved
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, only the releases published before Jan 1 2020 are retrieved
         - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
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

    if province.lower() not in switcher:
        warn("Province \'{}\' not recognized".format(province))
        return None

    if verbose: print("\nLoading {} Releases between {} and {}\n".format(province.upper(), start_date.strftime('%B %d, %Y'), end_date.strftime('%B %d, %Y')))

    if start_date > end_date:
        if verbose: print("Cannot search between {} and {}".format(start_date, end_date))
        return pd.DataFrame([], columns=_columns)

    try:
        df = switcher[province.lower()](start_date=start_date, end_date=end_date, verbose=verbose)
    except:
        df = pd.DataFrame([], columns=_columns)
        print("Could not load new articles for province", province)
    return df

def _csv_path(province):
    """
    Returns the relative CSV path for a given province string
    """
    return 'sources/' + province.replace(' ', '').lower() + '.csv'

def load_province(province, start_date=None, end_date=datetime.today(), update_csv=False, verbose=True):
    """
    Parameters: 
        - `province`
            string, the name of the province or territory to be loaded
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, this is set to None, which indicates that the program should begin searching from the last possible date in the CSV
         - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `update_csv`
            boolean, whether or not the results from the search should be saved to a CSV. By default, this is set to False.
        - `verbose`
            boolean, whether or not the function should print updates

    Returns: a DataFrame containing news releases from the government of the specified province or territory.
    """

    try:
        province_df = pd.read_csv(_csv_path(province))
        province_df = province_df.drop('Unnamed: 0', axis=1)

        start_length = len(province_df.index)

        province_df["start_date"] = pd.to_datetime(province_df["start_date"])
        
        # Get dates later than in the CSV, unless the `start_date` parameter is not None and gives a later date on which to begin searching. If it's None, a default value of Jan 1 2020 is used.
        largest_date = province_df["start_date"].max()
        new_start = max(largest_date, start_date or datetime(2020, 1, 1))    
        late_additions = _load_province(province, start_date=new_start, end_date=end_date, verbose=verbose)
        df = late_additions.append(province_df)

        # Get dates earlier than in the CSV, unless the `end_date` parameter gives an earlier date on which to stop searching
        # end_date=datetime.today() sets the parameter to a default value and allows the program to avoid coslty searches before beginning date.
        if start_date is not None:
            if start_date < datetime(2020, 1, 1):
                warn('WARNING: Going back further than government news websites extend may lead to unexpected behaviour.')

            earliest_date = province_df["start_date"].min()
            early_additions = _load_province(province, start_date=start_date, end_date=min(end_date, earliest_date), verbose=verbose)  
            df = df.append(early_additions)
                
    except:
        start_length = 0
        print("Could not read file with path", _csv_path(province))
        df = _load_province(province, start_date=(start_date or datetime(2020, 1, 1)), end_date=end_date, verbose=verbose)
        

    object_columns = df.dtypes[df.dtypes == 'object'].index.values
    df[object_columns] = df[object_columns].replace('\n',' ', regex=True)
    df[object_columns] = df[object_columns].replace('\r',' ', regex=True)
    
    df = df.drop_duplicates(['source_full_text']) # Potentially useful to look into dropping duplicates based on other attributes
    end_length = len(df.index)

    if update_csv:
        df.to_csv(_csv_path(province))

    if verbose:
        print('Articles added: ' + str(end_length - start_length))

    return df

def load_provinces(start_date=None, end_date=datetime.today(), update_csv=False, verbose=False):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, this is set to None, which indicates that the program should begin searching from the last possible date in the CSV
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date.
        - `update_csv`
            boolean, whether or not the results from the search should be saved to a CSV. By default, this is set to False.
        - `verbose`
            boolean, whether or not the function should print updates. By default, this is set to False.

    Returns: a dictionary mapping the names of provinces and territories to DataFrames containing information about their new releases.
    """

    provinces = ['alberta', 'british columbia', 'manitoba', 'new brunswick', 'newfoundland', 'northwest territories', 'nova scotia', 'nunavut', 'ontario', 'pei', 'quebec', 'saskatchewan', 'yukon']
    province_dfs = [load_province(province, start_date=start_date, end_date=end_date, update_csv=update_csv, verbose=verbose) for province in provinces]

    return dict(zip(provinces, province_dfs))

def load_all(start_date=None, end_date=datetime.today(), update_csv=False, verbose=False):
    """
    Parameters: 
        - `start_date` 
            datetime object, the date of the earliest news release to be retrieved. By default, this is set to None, which indicates that the program should begin searching from the last possible date in the CSV
        - `end_date` 
            datetime object, the date of the latest news release to be retrieved. By default, this is set to the current date
        - `update_csv`
            boolean, whether or not the results from the search should be saved to a CSV. By default, this is set to False.
        - `verbose`
            boolean, whether or not the function should print updates (False by default)

    Returns: a DataFrame containing the information from all provinces and territories.
    """

    full_df = pd.DataFrame([], columns=_columns)
    province_dict = load_provinces(start_date=start_date, end_date=end_date, update_csv=update_csv, verbose=verbose)
    full_df = pd.concat(province_dict.values(), ignore_index=True)
    
    return full_df