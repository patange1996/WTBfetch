import scrapy


class WTB1Spider(scrapy.Spider):
    name = 'wtb'
    # allowed_domains = ['http://wtb.app.channeliq.com/']
    start_urls = final_urls

    def parse(self, response):