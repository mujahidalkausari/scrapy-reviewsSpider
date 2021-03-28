import re
import scrapy
from scrapy.http import HtmlResponse
import hashlib

class ReviewsSpider(scrapy.Spider):
    name = "dealerrater"

    start_urls = [
        'https://www.dealerrater.com/dealer/Haus-Auto-Group-review-31406/',
    ]

    data = {}
    reviews = []
    pagination = []
    pager = 0
    counter = 2
        
    def __init__(self):
        self.called = False
        
    def parse(self, response):

        global data, reviews, pagination, pager, counter
        
        if not self.called:
            self.called = True
            
            self.data["website"] = response.css('title::text').get()
            self.data["biz_logo_link"] = response.css('div[id="logoWrapper"] a img::attr(src)').get()
            post_site_url = response.request.url
            self.data["post_site_url"] = post_site_url
            base_url = re.search('https?://([A-Za-z_0-9.-]+).*', post_site_url)
            reviews_link = response.css('a[id ="warButton"]::attr(href)').get()
            self.data["post_review_link"] = f'https://{base_url.group(1)}{reviews_link}'
            self.data["biz_favicon"] =  response.css('link[rel="icon"]::attr(href)').get()

            try:
                for tag in response.css('div[id="reviewsSection"] div[id="uncertifiedReviews"] div.pager-section div.page_container a::attr(href)').getall():
                    page_num = re.findall(r'[0-9]+', (tag.split("/")[-1]))[0]
                    self.pagination.append(page_num) 
            except:
                pass
            self.pagination.sort()
            self.pager = int(self.pagination[0])
              
        for tag in response.css('div[id="reviewsSection"] div[id="uncertifiedReviews"] div.review-entry').getall():
            tag_response = HtmlResponse(url="HTML string", body=tag, encoding='utf-8')
            try:
                date_ = tag_response.css('div.review-date div::text').get() 
            except:
                date_ = ''
            try:
                name_ = tag_response.css('div.review-wrapper div span::text').get().replace("- ","") 
            except:
                name_ = ''
            try:
                title_ = str(tag_response.css('div.review-wrapper div h3::text').get()).replace('\"', '')
            except:
                title_ = ''
            try:
                rating_ = int(tag_response.css('div.review-date div.dealership-rating div::attr(class)').get().split(" ")[4].split("-")[1])/10
            except:
                rating_ = ''
            try:
                source_ = tag_response.css('div.review-wrapper div.employees-wrapper span::text').get()
            except:
                source_ = ''
            try:
                desciption_ = tag_response.css('div.review-wrapper p.review-content::text').get()
            except:
                desciption_ = ''
            
            data_items = {}

            data_items['name'] = name_
            data_items['date'] = date_
            data_items['avatar'] = ""
            data_items['rating'] = rating_
            data_items['title'] = title_
            data_items['description'] = desciption_
            data_items['source'] = source_

            strId = f'{name_}{date_}'
            #Assumes the default UTF-8
            hash_object = hashlib.md5(strId.encode())
            data_items['reviewId'] = hash_object.hexdigest()

            self.reviews.append(data_items)
            
        if self.counter <= self.pager:
            page = "page" + str(self.counter)
            self.counter += 1
            yield response.follow(page, callback=self.parse)
        else:
                    
            self.data["reviews"] = self.reviews
            yield self.data
            
###script author:https://github.com/mujahidalkausari?###
