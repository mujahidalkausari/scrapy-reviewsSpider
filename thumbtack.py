import re
import scrapy
from scrapy.http import HtmlResponse
import hashlib

class ReviewsSpider(scrapy.Spider):
    name = "thumbtack"

    start_urls = [
        'https://www.thumbtack.com/ut/salt-lake-city/carpet-cleaning/lilos-carpet-cleaning-services/service/358313871403499535?service_pk=358313871403499535&category_pk=219264413294461288&project_pk=415870796860760077&lp_request_pk=411595281117151245&zip_code=84010&click_origin=pro%20list%2Fclick%20pro%20name&sourcePage=&sourceEvent=',
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
            self.data["biz_logo_link"] = ""
            post_site_url = response.request.url
            self.data["post_site_url"] = post_site_url
            base_url = re.search('https?://([A-Za-z_0-9.-]+).*', post_site_url)
            self.data["post_review_link"] = post_site_url
            self.data["biz_favicon"] =  response.css('link[rel="icon"]::attr(href)').get()


            next_pages = response.css('div.ma2 div.ph1 a::attr(href)').getall()
        
            if next_pages is not None:
                for nextpage in next_pages:
                    self.pagination.append(int((re.findall(r'[0-9]+', nextpage))[0]))
            self.pagination.sort()

        for tag in response.css('section[id="stickynav-reviews"] span ul li').getall():
            tag_response = HtmlResponse(url="HTML string", body=tag, encoding='utf-8')
            try:
                date_ = ''
                date_text = tag_response.css('div.review__main div.review__details span.review__label-text span::text').get()
                if date_text is not None:
                    date_ = date_text
            except:
                date_ = ''
            try:
                name_ = tag_response.css('div.review__main div.mr2::text').get()  
            except:
                name_ = ''
            try:
                rating_ = tag_response.css('div.review__main div.-RJZGiexxBbK_jDExpzFh::attr(data-star)').get()
            except:
                rating_ = ''
            try:
                desc_text = []
                for text in tag_response.css('div.review__main div.review__body p span span::text').getall():
                    try:
                        desc_text.append(text)
                    except:
                        pass
                review_ = ' '.join(desc_text)
                desciption_ = re.sub(u"(\u2018|\u2019)", "'", review_)
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
            page = "?page=" + self.pagination[0]
            self.pagination.pop(0)
            yield response.follow(page, callback=self.parse)
        else:
                    
            self.data["reviews"] = self.reviews   
            yield self.data
            
###script author:https://github.com/mujahidalkausari?###
