import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
from tkinter import *
from tkinter.ttk import Progressbar

def runfunction():

    url = e.get(1.0, END)
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
        start_urls = final_urls

        def parse(self, response):

            # items = WtbAutomationItem()
            retailer = response.xpath("//div[starts-with(@class , 'ciq-seller')]/text()").extract()
            #//tr[starts-with(@class , 'ciq-record-row')]
            # items['retailers'] = retailer

            # update the list of retailer(Pandas)
            for i in retailer:
                if i.strip() not in df.columns:
                    variable_list = []
                    for k in df.index:
                        variable_list.append("-")
                    df.insert(len(df.columns), i.strip(), variable_list, True)

            #print(df)
            # update the checkbox(pandas)
            for s in retailer:
                row = response.url
                column = s.strip()
                df.loc[row, column] = "[✔]"

            yield {'ret': retailer}

    # Run the spider

    process = CrawlerProcess()
    process.crawl(WTBSpider)
    process.start()

    file_sav = "C:\\Users\\shubhan.patange\\Desktop\\recent.csv"

    df.to_csv(file_sav)
    df.to_csv("recent.csv")

    done_message = Label(win, text="Done! Your file is saved in desktop")
    done_message.grid(row=4, column=1)

    exit = Button(win, text="Exit", command=des)
    exit.grid(row=5, column=1)


def des():
    win.destroy()

win = Tk()
win.title("WTB project")
win.iconbitmap("numerator.ico")

bar = Progressbar(win, orient=HORIZONTAL, length=200, mode='determinate')
bar.grid(row=1, column=1)

label = Label(win, text="Enter the WTB URLS")
label.grid(row=0, column=0)

e = Text(win, width=100, height=25, borderwidth=5)
e.grid(row=0, column=1)

b = Button(win, text='Run', command=runfunction, borderwidth=5, width=10)
b.grid(row=2, column=1)

win.mainloop()