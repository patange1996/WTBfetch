#MartinGuitar_New QA Doc: zlszyeFjBkW_xez_6RWTqg
#Clorox_Clorox: NZY4XZQJqUGrOsfhrdupIw
import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import numpy as np

# read data from excel
df_excel = pd.read_excel(r"WTB.xlsx")
client_dict={}
urls=[]

for i in df_excel.columns:
    for j in df_excel[i]:
        if j is not np.nan:
            urls.append(j)
    client_dict.update({i:urls})
    urls=[]

#client list from dict
client_list = list(client_dict)

#last link of each client
link_last = []
for i in client_dict:
    s = client_dict[i]
    link_last.append(s[-1])

#Create a panda dataframe for pasting the exteracting data "PremierNutrition_QA Audit (USA)"
data = {"WTB": client_dict[i]}
df = pd.DataFrame(data)
df.set_index('WTB', inplace=True)

# creating pandas(for all the retailer mentioned) (LOOP)
'''
for i in client_dict:
    print("this is" + i)
    data = {"WTB": client_dict.get(i)}
    df = pd.DataFrame(data)
    df.set_index('WTB', inplace=True)
'''


class WTBSpider(scrapy.Spider):
    name = 'wtb'
    final_urls = client_dict.get(i)
    allowed_domains = ["wtb.app.channeliq.com/"]
    start_urls = final_urls

    def parse(self, response):

        # items = WtbAutomationItem()

        retailer = response.xpath("//div[starts-with(@class , 'ciq-seller')]/text()").extract()
        # items['retailers'] = retailer

        # update the list of retailer(Pandas)
        for j in retailer:
            if j.strip() not in df.columns:
                variable_list = []
                for k in df.index:
                    variable_list.append("-")
                df.insert(len(df.columns), j.strip(), variable_list, True)

        #print(df)
        # update the checkbox(pandas)
        for s in retailer:
            row = response.url
            column = s.strip()
            df.loc[row, column] = "[✔]"

        yield {"ret":retailer}

# Run the spider
process = CrawlerProcess()
process.crawl(WTBSpider)
process.start()

df.to_csv("wtbv2.csv")