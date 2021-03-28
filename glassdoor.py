import re
import scrapy
from scrapy.http import HtmlResponse
import hashlib

class ReviewsSpider(scrapy.Spider):
    name = "glassdoor"

    start_urls = [
        'https://www.glassdoor.com/Reviews/Apple-Reviews-E1138.htm',
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
            self.data["biz_logo_link"] = response.css('div.logo a span img::attr(src)').get()
            post_site_url = response.request.url
            self.data["post_site_url"] = post_site_url
            base_url = re.search('https?://([A-Za-z_0-9.-]+).*', post_site_url)
            review_link = response.css('div[id="EmpLinksWrapper"] a.addReview::attr(href)').get()
            self.data["post_review_link"] = f'https://{base_url.group(1)}' + review_link
            self.data["biz_favicon"] =  f'https://{base_url.group(1)}' + response.css('link[rel="shortcut icon"]::attr(href)').get()

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

        for res in response.css('div[data-test="EIReviewsPage"] div[id="ReviewsFeed"] ol.empReviews li.empReview').getall():
            tag_response = HtmlResponse(url="HTML string", body=res, encoding='utf-8')
            try:
                date_ = tag_response.css('div.gdReview time.date::text').get() 
            except:
                date_ = ''
            try:
                title_ = tag_response.css('div.gdReview h2 a::text').get().replace("\"","")
            except:
                title_ = ''
            try:
                name_ = tag_response.css('div.gdReview div.author span.authorInfo span.authorJobTitle::text').get()
            except:
                name_ = ''
            try:
                rating_ = tag_response.css('div.gdReview span.gdRatings div.v2__EIReviewsRatingsStylesV2__ratingInfoWrapper div.v2__EIReviewsRatingsStylesV2__ratingInfo div::text').get()
            except:
                rating_ = ''
            try:
                avatar_ = tag_response.css('div.gdReview span.sqLogo img::attr(src)').get()
            except:
                avatar_ = ''
            try:
                source_ = tag_response.css('div.gdReview div.author span.authorInfo span.authorLocation::text').get()
            except:
                source_ = ''
            try:
                desc = []
                desc.append(tag_response.css('div.gdReview p.mainText::text').get())
                for next_text in tag_response.css('div.gdReview div.v2__EIReviewDetailsV2__fullWidth').getall():
                    text_response = HtmlResponse(url="HTML string", body=next_text, encoding='utf-8')
                    desc.append(text_response.css('p span::attr(data-test)').get())
                    desc.append(text_response.css('p span::text').get())
                desciption_ = ". ".join(desc)
            except:
                desciption_ = ''
            
            data_items = {}

            data_items['name'] = name_
            data_items['date'] = date_
            data_items['avatar'] = avatar_
            data_items['rating'] = rating_
            data_items['title'] = title_
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
