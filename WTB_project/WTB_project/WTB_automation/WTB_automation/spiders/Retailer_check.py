import scrapy
from scrapy.crawler import CrawlerProcess
import numpy as np
import pandas as pd
from tkinter import *
from tkinter.ttk import Progressbar
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from urllib.parse import urlparse


def __main__():
    globals()['win'] = Tk()
    globals()['win'].title("WTB project")
    globals()['win'].iconbitmap("numerator.ico")

    globals()['bar'] = Progressbar(globals()['win'], orient=HORIZONTAL, length=200, mode='determinate')
    globals()['bar'].grid(row=1, column=1)

    label = Label(globals()['win'], text="Enter the WTB URLS")
    label.grid(row=0, column=0)

    globals()['e'] = Text(globals()['win'], width=100, height=25, borderwidth=5)
    globals()['e'].grid(row=0, column=1)

    b = Button(globals()['win'], text='Run', command=runfunction, borderwidth=5, width=10)
    b.grid(row=2, column=1)

    globals()['win'].mainloop()


def runfunction():

    url = globals()['e'].get(1.0, END)
    final_urls = url.split("\n")
    for i in final_urls:
        if i == "":
            final_urls.pop(final_urls.index(i))

    # creating pandas
    data = {"WTB": final_urls}
    df = pd.DataFrame(data)
    df.set_index('WTB', inplace=True)

    class WTBSpider(scrapy.Spider):
        name = 'wtb'
        # allowed_domains = ['http://wtb.app.channeliq.com/']
        custom_settings = {
            'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        }

        def start_requests(self):
            for i in final_urls:
                yield scrapy.Request(
                    url=i,
                    callback=self.parse
                )

        def parse(self, response):

            # items = WtbAutomationItem()

            retailer = response.xpath("//div[starts-with(@class , 'ciq-seller')]/text()").extract()
            # //tr[starts-with(@class , 'ciq-record-row')]
            # items['retailers'] = retailer

            # update the list of retailer(Pandas) and add it as column
            for i in retailer:
                if i.strip() not in df.columns:
                    dash_list = []
                    Link_list = []
                    for k in df.index:
                        dash_list.append("-")
                        Link_list.append("No offer on site")
                    df.insert(len(df.columns), np.nan, dash_list, True)
                    df.insert(len(df.columns), i.strip(), Link_list, True)
                    df.insert(len(df.columns), "Stock", np.nan, True)

            # print(df)
            # update the checkbox(pandas)
            for s in retailer:
                inverted_remove = s.split("'")
                whole_retailer = response.xpath(
                    f"//div[contains(text(),'{inverted_remove[0]}')]/parent::node()/parent::node()")
                # row = response.url
                # column = s.strip()
                link = whole_retailer.xpath("(.//a[@class='ciq-buy-now-button'])[1]/@href").get()
                # df.loc[row, column] = link
                yield scrapy.Request(
                    url=link,
                    callback=self.name_parse,
                    meta={"wtb": response.url, "retailer": s},
                          # 'handle_httpstatus_list': [301]},
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"
                    },
                    errback=self.after_error
                )
                # yield {
                #     "wtb" : response.url,
                #     "retailer" : s,
                #     "link": link
                # }

        def name_parse(self, response):
            # first coloumn and comments coloumn should be edited
            wtb = response.meta["wtb"]
            retailer = response.meta["retailer"]
            row = wtb
            column = retailer.strip()
            df.loc[row, column] = response.url.split("?")[0]
            df.iloc[df.index.get_loc(row), df.columns.get_loc(column) - 1] = "[✔]"
            # df.iloc[df.index.get_loc(row), df.columns.get_loc(column) + 1] = str(response.status)
            #UK TAB
            #Amazon CO UK
            if "amazon.co.uk" in urlparse(response.url).netloc:
                stock = response.xpath("normalize-space(//div[@id='availability']/span/text())").get()
                seller = response.xpath("normalize-space(//div[@id='merchant-info']/text())").get()
                if "Amazon" in seller:
                    if "Currently Unavailable" in stock or "Temporarily Out of Stock" in stock or "Usually dispatched within 1 to 2 months" in stock:
                        isunavailable = True
                    else:
                        isunavailable = False
                else:
                    isunavailable = False

                yield {
                    "wtb": wtb,
                    "retailer": retailer,
                    "link": response.url.split("?")[0],
                    "iserror": False,
                    "isunavailable": isunavailable
                }
                df.iloc[df.index.get_loc(row), df.columns.get_loc(column) + 1] = isunavailable
            # Curry's UK
            elif "currys.co.uk" in urlparse(response.url).netloc:
                stock = response.xpath("normalize-space((//li[@class='home-delivery home-delivery- available'])[2]/text()[3])").get()
                Outofstock = response.xpath("normalize-space((//div[@class='oos oos-no-alt border space-b'])[2]/p/text()[1])").get()

                if "FREE delivery" in stock or "Out of Stock" not in Outofstock:
                    isunavailable = False
                else:
                    isunavailable = True
                yield {
                    "wtb": wtb,
                    "retailer": retailer,
                    "link": response.url.split("?")[0],
                    "iserror": False,
                    "isunavailable": isunavailable
                }
                df.iloc[df.index.get_loc(row), df.columns.get_loc(column) + 1] = isunavailable
            else:
                df.iloc[df.index.get_loc(row), df.columns.get_loc(column) + 1] = str(response.status)
                yield {
                    "wtb": wtb,
                    "retailer": retailer,
                    "link": response.url.split("?")[0],
                    "iserror": False,
                    "isunavailable": False
                }





        def after_error(self, failure):
            wtb = failure.request.meta["wtb"]
            retailer = failure.request.meta["retailer"]
            if failure.check(HttpError):
                response = failure.value.response
                row = wtb
                column = retailer.strip()
                df.loc[row, column] = response.url.split("?")[0]
                df.iloc[df.index.get_loc(row), df.columns.get_loc(column) - 1] = "[✔]"
                df.iloc[df.index.get_loc(row), df.columns.get_loc(
                    column) + 1] = f"{failure.value.response.status} HTTP Error"
                yield {
                    "wtb": wtb,
                    "retailer": retailer,
                    "link": response.url,
                    "iserror": True
                }
            elif failure.check(TimeoutError, TCPTimedOutError):
                request = failure.request
                row = wtb
                column = retailer.strip()
                df.loc[row, column] = request.url.split("?")[0]
                df.iloc[df.index.get_loc(row), df.columns.get_loc(column) - 1] = "[✔]"
                df.iloc[df.index.get_loc(row), df.columns.get_loc(column) + 1] = "Time out Error"
                yield {
                    "wtb": wtb,
                    "retailer": retailer,
                    "link": response.url,
                    "iserror": True
                }

    # Run the spider

    process = CrawlerProcess()
    process.crawl(WTBSpider)
    process.start()

    #links which are there in doc and not in WTB.


    file_sav = "C:\\Users\\shubhan.patange\\Desktop\\recent.csv"

    df.to_csv(file_sav)
    df.to_csv("recent.csv")

    done_message = Label(globals()['win'], text="Done! Your file is saved in desktop")
    done_message.grid(row=4, column=1)

    exit = Button(globals()['win'], text="Exit", command=des)
    exit.grid(row=5, column=1)

    # globals()['bar'].stop()




def des():
    globals()['win'].destroy()


if __name__ == "__main__":
    global e
    global win
    global bar
    __main__()
