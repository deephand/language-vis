import requests
import urllib.request
import re
import string
import time

seed_page = "https://en.0wikipedia.org/index.php?q=aHR0cHM6Ly9lbi53aWtpcGVkaWEub3JnL3dpa2kvTWFpbl9QYWdl"

def download_page(url):
    try:
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req)
        # print(str(type(resp.read())))
        # print(resp.read())
        # print(resp.read().decode('utf-8', 'ignore'))
        # print(url)
        respData = str(resp.read().decode('utf-8', 'ignore'))
        return respData
    except Exception as e:
        print(str(e))


def get_title(raw_html):
    starting_tag = r'<h1 id="firstHeading" class="firstHeading" lang='
    ending_tag = '</h1>'

    starting_place = raw_html.find(starting_tag)
    ending_place = raw_html.find(ending_tag, starting_place + 1)
    return(raw_html[starting_place + 53 : ending_place])

def get_introduction(raw_html):
    starting_tag = r'<p>'
    ending_tag = '<div class="toctitle">'

    starting_place = raw_html.find(starting_tag)
    ending_place = raw_html.find(ending_tag, starting_place + 1)

    if '<div class="toctitle">' not in raw_html:
        ending_place = raw_html.find('</p>', starting_place + 1)
    else:
        pass

    return(raw_html[starting_place : ending_place])

def get_content(raw_html):
    starting_place = raw_html.find(r'<h2><span class="mw-headline" id=')
    starting_place_end = raw_html.find('>', starting_place + 1)
    ending_place = raw_html.find(r'<h2><span class="mw-headline" id="See_also">')

    content = raw_html[starting_place_end + 1 : ending_place]

    punc_list = r'!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~'
    content_purged = re.sub(r'<.+?>', '', content)
    content_purged = content_purged.replace(r'\n', ' ')
    content_purged = re.sub(r'\[.+?\]', '', content_purged)
    content_purged = content_purged.translate(str.maketrans('','',punc_list))
    return(content_purged)

def get_next_link(s):
    start_link = s.find("<a href")
    if start_link == -1:    #If no links are found then give an error!
        end_quote = 0
        link = "no_links"
        return link, end_quote
    else:
        start_quote = s.find('"', start_link)
        end_quote = s.find('"',start_quote+1)
        link = str(s[start_quote+1:end_quote])
        return link, end_quote

def get_all_links(page):
    links = []
    while True:
        link, end_link = get_next_link(page)
        if link == "no_links":
            break
        else:
            links.append(link)      #Append all the links in the list named 'Links'
            #time.sleep(0.1)
            page = page[end_link:]
    return links

def extension_scan(url):
    a = ['.png','.jpg','.jpeg','.gif','.tif','.txt', '.oga']
    j = 0
    while j < (len(a)):
        if a[j] in url:
            flag2 = 1
            break
        else:
            flag2 = 0
            j = j+1
    return flag2

def url_parse(url):
    try:
        from urllib.parse import urlparse
    except ImportError:
        from urlparse import urlparse
    url = url  #.lower()    #Make it lower case
    s = urlparse(url)       #parse the given url
    seed_page_n = seed_page #.lower()       #Make it lower case
    #t = urlparse(seed_page_n)     #parse the seed page (reference page)
    i = 0
    flag = 0
    while i<=9:
        if url == "/":
            url = seed_page_n
            flag = 0  
        elif not s.scheme:
            url = "http://" + url
            flag = 0
        elif "#" in url:
            url = url[:url.find("#")]
            flag = 0
        # elif "?" in url:
        #     url = url[:url.find("?")]
        #     flag = 0
        elif s.netloc == "":
            url = seed_page + s.path
            flag = 0
            
        elif url[len(url)-1] == "/":
            url = url[:-1]
            flag = 0      
        else:
            url = url
            flag = 0
            break
        
        i = i+1
        s = urlparse(url)   #Parse after every loop to update the values of url parameters
    return(url, flag)

if __name__ == "__main__":
    url = "https://en.0wikipedia.org/index.php?q=aHR0cHM6Ly9lbi53aWtpcGVkaWEub3JnL3dpa2kvU3BhY2V0aW1l"
    # url = 'https://tr.0wikipedia.org/index.php?q=aHR0cHM6Ly90ci53aWtpcGVkaWEub3JnL3dpa2kvQWxiZXJ0X0VpbnN0ZWlu'
    # url = 'https://api.opendota.com/api/promatches'

    to_crawl = [url]
    crawled=[]
    database = {}

    lang = 'en'

    for k in range(0, 3):
        i=0        #Initiate Variable to count No. of Iterations
        while i<4:     #Continue Looping till the 'to_crawl' list is not empty
            url_in = to_crawl.pop(0)      #If there are elements in to_crawl then pop out the first element
            url_in,flag = url_parse(url_in)
            flag2 = extension_scan(url_in)
            time.sleep(3)
            
            # If flag = 1, then the URL is outside the seed domain URL
            if flag == 1 or flag2 == 1:
                pass        #Do Nothing

            else:       
                if url_in in crawled:     #Else check if the URL is already crawled
                    pass        #Do Nothing
                else:       #If the URL is not already crawled, then crawl i and extract all the links from it
                    print("Link = " + url_in)
                    
                    raw_html = download_page(url_in)
                    
                    title_upper = str(get_title(raw_html))
                    title = title_upper.lower()     #Lower title to match user queries
                    print("Title = " + title)
                    
                    raw_introduction = get_introduction(raw_html)

                    to_crawl = to_crawl + get_all_links(raw_introduction)
                    crawled.append(url_in)
                    
                    clr_introduction = re.sub(r'<.+?>', '', get_introduction(raw_html))
                    clr_introduction = re.sub(r'\[.+?\]', '', clr_introduction)
                    clr_introduction = clr_introduction.replace('\n', '')

                    content = get_content(raw_html)

                    database[title] = clr_introduction      #Add title and its introduction to the dict

                    #Writing the output data into a text file
                    file = open('dataset/wiki/wiki_{}_{}.txt'.format(title, lang), 'a', encoding = 'utf-8')        #Open the text file called database.txt
                    file.write(title + ": " + "\n")         #Write the title of the page
                    file.write("Introduction" + '\n')
                    file.write(clr_introduction + "\n\n")      
                    file.write("Content" + '\n')
                    file.write(content + "\n") 
                    file.close()                            #Close the file
    
                    print(clr_introduction)

                    #Remove duplicated from to_crawl
                    n = 1
                    j = 0
                    while j < (len(to_crawl)-n):
                        if to_crawl[j] in to_crawl[j+1:(len(to_crawl)-1)]:
                            to_crawl.pop(j)
                            n = n+1
                        else:
                            pass     #Do Nothing
                        j = j+1
                i=i+1
                print(i)
                print(k)