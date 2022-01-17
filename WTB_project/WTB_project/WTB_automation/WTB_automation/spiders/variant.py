import scrapy
from scrapy.crawler import CrawlerProcess

with open("sony.csv", "r") as f:
    sony_links = f.read()

final = sony_links.split("\n")


class WTBSpider(scrapy.Spider):
    name = 'variant'
    # allowed_domains = ['http://wtb.app.channeliq.com/']

    def start_requests(self):
        for i in final:
            yield scrapy.Request(
                url=i,
                callback=self.parse,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"
                }
            )

    def parse(self, response):
        link = response.xpath("//link[contains(@href,'/buy/')]/@href").get()
        link2 = response.xpath("//a[contains(@href,'/buy/')]/@href").extract()

        with open("sony_all.txt", "w+") as f:
            f.write(link + "\n")
            for i in link2:
                f.write(i.split("//")[1] + "\n")

        yield {
            "link": link,
            "link2" : link2
        }

process = CrawlerProcess()
process.crawl(WTBSpider)
process.start()
