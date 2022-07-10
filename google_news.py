from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests
from datetime import date, timedelta
import psycopg2

root = "https://www.google.com/"
link = "https://www.google.com/search?q=economy&tbm=nws&sxsrf=ALiCzsYeP1CvP4J6_kQ8Yq1_vULZh9HYRA:1657347553017&source=lnt&tbs=qdr:w&sa=X&ved=2ahUKEwjXrqrhlOv4AhXqR2wGHdmMD1QQpwV6BAgBEBc&biw=1440&bih=674&dpr=2"

def news(link):
    # Get website content
    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    with requests.Session() as c:
        soup = BeautifulSoup(webpage, 'html5lib')
        #print(soup)
        
        try:
            # Create connection to DB
            connection = psycopg2.connect(user="",
                                        password="",
                                        host="",
                                        port="",
                                        database="")
            cursor = connection.cursor()
            
            # Get only news items from the website
            for item in soup.find_all('div', attrs={'class': 'Gx5Zad fP1Qef xpd EtOod pkphOe'}):
                raw_link = (item.find('a', href=True)['href'])
                link = (raw_link.split("/url?q=")[1]).split('&sa=U&')[0]

                # Get news titles, descriptions etc based on class attributes
                title = (item.find('div', attrs={'class': 'BNeawe vvjwJb AP7Wnd'}).get_text())
                description = (item.find('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'}).get_text())
                title = title.replace(",", "")
                description = description.replace(",", "")

                time = (item.find('span', attrs={'class': 'r0bn4c rQMQod'}).get_text())
                agency = (item.find('div', attrs={'class': 'BNeawe UPmit AP7Wnd'}).get_text())
                descript = description.split("...")[0]

                # Calculate date from text
                if "hour" in time:
                    published_on = date.today()
                else:
                    published_on = date.today() - timedelta(days=int(time[0]))

                # Insert data into database
                postgres_insert_query = """ INSERT INTO google_news (agency_name, published_date, title, description, article_link) VALUES (%s,%s,%s,%s,%s)"""
                record_to_insert = (agency, published_on, title, descript, link)
                cursor.execute(postgres_insert_query, record_to_insert)

                connection.commit()
                count = cursor.rowcount
                print(count, "Record inserted successfully into google_news table")

            # Go to the next page of news articles list
            next = soup.find('a', attrs={'aria-label':'Next page'})

            # Stop going to next page if this is the last page
            if (next):
                next = (next['href'])
                link = root + next
                news(link)

        # Exception handling if DB connection fails
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into mobile table", error)

        finally:
            # closing database connection.
            if connection:
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")

news(link)