import re
import scrapy
from scrapy.http import HtmlResponse
import hashlib

class ReviewsSpider(scrapy.Spider):
    name = "homeadvisor"

    start_urls = [
        'https://www.homeadvisor.com/rated.AnyHourServices.29410939.html#ratings-reviews',
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
            reviews_link = response.css('div[id="reviews"] div a::attr(href)').get()
            self.data["post_review_link"] = f'https://{base_url.group(1)}{reviews_link}'
            icon_path = response.css('link[rel="shortcut icon"]::attr(href)').get()
            self.data["biz_favicon"] =  f'https://{base_url.group(1)}{icon_path}'


            next_pages = response.css('div[id="reviews"] div.pagination-bottom div.pagination_right div.pagination_modal ul li a::attr(href)').getall()

            if next_pages is not None:
                for nextpage in next_pages:
                    paginationNum = re.findall(r'[0-9]+', nextpage)
                    number = paginationNum[0]
                    if number not in self.pagination:
                        self.pagination.append(number)    
        for tag in response.css('div[id="reviews"] div.list-body').getall():
            tag_response = HtmlResponse(url="HTML string", body=tag, encoding='utf-8')
            try:
                date_ = tag_response.css('div div div[class="@flex-initial @text-gray @font-semibold md:@self-end"]::text').get().strip()  
            except:
                date_ = ''
            try:
                name_list=[]
                for span_ in tag_response.css("div div div span").getall():
                    span_response = HtmlResponse(url="HTML string", body=span_, encoding='utf-8')
                    name_text = span_response.css('span::text').get()
                    if name_text is not None:
                        name_list.append(name_text.strip())
                name_ = name_list[2].replace(" *.","")

            except:
                name_ = ''
            try:
                title_ = tag_response.css('div ul li a::text').get().strip() 
            except:
                title_ = ''
            try:
                rating_ = (tag_response.css("div div div span span::text").get())
            except:
                rating_ = ''
            try:
                desciption_ = tag_response.css('div div.review-content p::text').get().strip() 

            except:
                desciption_ = ''
            
            data_items = {}

            data_items['name'] = name_
            data_items['date'] = date_
            data_items['avatar'] = ""
            data_items['rating'] = rating_
            data_items['title'] = title_
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
