import re
import scrapy
from scrapy.http import HtmlResponse
import hashlib

class ReviewsSpider(scrapy.Spider):
    name = "wellness"

    start_urls = [
        'https://www.wellness.com/reviews/1846326/dana-bleakney-baylor-scott-white-family-medical-center-baylor-university-medical-center-family-doctor',
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
            self.data["biz_logo_link"] = "https:" + response.css('div[id="header-block"] a.logo img::attr(src)').get()
            post_site_url = response.request.url
            self.data["post_site_url"] = post_site_url
            base_url = re.search('https?://([A-Za-z_0-9.-]+).*', post_site_url)
            self.data["post_review_link"] = post_site_url
            self.data["biz_favicon"] =  "https:" + response.css('link[rel="shortcut icon"]::attr(href)').get()
 
            try:
                for tag in response.css('div.pagination-div ul li.pagination-inactive a::text').getall():
                    if tag is not None:
                        if tag not in self.pagination:
                            self.pagination.append(tag)
                self.pagination.sort()
            except:
                pass

        for res in response.css('div[id="reviews"] div.review').getall():
            tag_response = HtmlResponse(url="HTML string", body=res, encoding='utf-8')
            try:
                date_ = tag_response.css('div.reviewer span.review_date span.profile-review::text').get() 
            except:
                date_ = ''
            try:
                name_ = tag_response.css('div.reviewer div.listing-review-name span.review_name::text').get()
            except:
                name_ = ''
            try:
                rating_ = tag_response.css('div.listing-ratings-container div.item-rating::text').get()
            except:
                rating_ = ''
            try:
                source_ = tag_response.css('div.reviewer div.listing-review-name span.review_ip::text').get()
            except:
                source_ = ''
            try:
                desc = []
                if tag_response.css('div.review-text-container span.listing-review-text::text').get() is not None:
                    desc.append(tag_response.css('div.review-text-container span.listing-review-text::text').get().strip())
                if tag_response.css('div.review-text-container span.listing-review-text span.blurred::text').get() is not None:
                    desc.append(tag_response.css('div.review-text-container span.listing-review-text span.blurred::text').get().strip())
                if tag_response.css('div.review-text-container div.response-question::text').get() is not None:
                    desc.append(tag_response.css('div.review-text-container div.response-question::text').get().strip())
                if tag_response.css('div.review-text-container div.response-answer::text').get() is not None:
                    desc.append(tag_response.css('div.review-text-container div.response-answer::text').get().strip())
                desciption_ = " ".join(desc)
            except:
                desciption_ = ''
            
            data_items = {}

            data_items['name'] = name_
            data_items['date'] = date_
            data_items['avatar'] = ""
            data_items['rating'] = rating_
            data_items['title'] = ""
            data_items['description'] = desciption_
            data_items['source'] = source_

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
