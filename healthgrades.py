import re
import scrapy
from scrapy.http import HtmlResponse
import hashlib

class ReviewsSpider(scrapy.Spider):
    name = "healthgrades"

    start_urls = [
        'https://www.healthgrades.com/physician/dr-michael-hinckley-3mmkm',
    ]

    data = {}
    reviews = []
    pagination = []
        
    def __init__(self):
        self.called = False
        
    def parse(self, response):

        global data, reviews, pagination
        
        if not self.called:
            self.called = True
            
            self.data["website"] = response.css('title::text').get()
            base_url = re.search('https?://([A-Za-z_0-9.-]+).*', response.request.url)
            self.data["post_review_link"] = response.request.url
            self.data["biz_logo_link"] = f'https://{base_url.group(1)}' + response.css('div.hgGlobalFooter__logos img::attr(src)').get()
            self.data["biz_favicon"] =  f'https://{base_url.group(1)}' + response.css('link[rel="icon"]::attr(href)').get()

            """
            try:
                for tag in response.css('div.pageContainer button[class="page  css-sed91k"]::text').getall():
                    if tag is not None:
                        if tag not in self.pagination:
                            self.pagination.append(tag)
                self.pagination.sort()
            except:
                pass
            """

        for res in response.css('div.review-section-internal-wrapper section.premium-review-section div.c-comment-list div.c-single-comment').getall():
            tag_response = HtmlResponse(url="HTML string", body=res, encoding='utf-8')
            try:
                date_ = ''
                date_span = tag_response.css('div.l-single-comment-container div[data-qa-target="comment-date"] span::text').getall()
                if len(date_span) == 2:
                    date_ = date_span[0]
                if len(date_span) == 3:
                    date_ = date_span[1]

            except:
                date_ = ''
            try:
                name_ = ''
                name_span = tag_response.css('div.l-single-comment-container div[data-qa-target="comment-date"] span::text').getall()
                if len(date_span) == 2:
                    name_ = ''
                if len(date_span) == 3:
                    name_ = date_span[0].replace("–","")
            except:
                name_ = ''
            try:
                rating_ = tag_response.css('div.l-single-comment-container div.c-single-comment__stars span::attr(aria-label)').get()
            except:
                rating_ = ''
            try:
                desciption_ =  tag_response.css('div.l-single-comment-container div.c-single-comment__comment::text').get()
            except:
                desciption_ = ''
            
            data_items = {}

            data_items['name'] = name_
            data_items['date'] = date_
            data_items['avatar'] = ""
            data_items['rating'] = rating_
            data_items['title'] = ""
            data_items['description'] = desciption_
            data_items['source'] = ""
            
            strId = f'{name_}{date_}'
            #Assumes the default UTF-8
            hash_object = hashlib.md5(strId.encode())
            data_items['reviewId'] = hash_object.hexdigest()

            self.reviews.append(data_items)
            
        if len(self.pagination) > 0:
            page = self.pagination[0]
            self.pagination.pop(0)
            yield response.follow(page, callback=self.parse)
        else:
                    
            self.data["reviews"] = self.reviews
            yield self.data
            
###script author:https://github.com/mujahidalkausari?###
