import re
import hashlib
from scrapy.http import HtmlResponse
import scrapy

class ReviewsSpider(scrapy.Spider):
    name = "indeed"

    start_urls = [
        'https://www.indeed.com/cmp/Accurate-Personnel/reviews',
    ]

    data = {}
    reviews = []
    pagination = []
        
    def __init__(self):
        self.called = False
        
    def parse(self, response):

        global data, reviews, pageNum
        
        if not self.called:
            self.called = True
            
            self.data["website"] = response.css('title::text').get()
            self.data["biz_logo_link"] = response.css('img.cmp-CompactHeaderCompanyLogo-logo::attr(src)').get()
            post_site_url = response.request.url
            self.data["post_site_url"] = post_site_url
            base_url = re.search('https?://([A-Za-z_0-9.-]+).*', post_site_url)
            reviews_link = response.css('div.cmp-WriteReviewButton-container a::attr(href)').get()
            self.data["post_review_link"] = f'{base_url.group(1)}{reviews_link}'
            favicon_link = response.css('link[rel="icon"]::attr(href)').get()
            self.data["biz_favicon"] =  f'{base_url.group(1)}{favicon_link}'

            next_pages = response.css('li.cmp-Pagination-item a::attr(href)').getall()

            if next_pages is not None:
                for nextpage in next_pages:
                    paginationNum = re.findall(r'[0-9]+', nextpage)
                    number = paginationNum[0]
                    if number not in self.pagination:
                        self.pagination.append(number)
       
            self.pagination.sort()
            
        for tag in response.css('div[data-testid="reviewsList"] div[itemprop="review"]').getall():
            tag_response = HtmlResponse(url="HTML string", body=tag, encoding='utf-8')
            try:
                date_ = tag_response.css('div.cmp-Review-content div.cmp-Review-author span[itemprop="author"]::text').get()
            except:
                date_ = ''
            
            try:
                text_list =[]
                name_ = ''
                source_ = ''
                for author in tag_response.css('div.cmp-Review-container div.cmp-Review-content div.cmp-Review-author a::text').getall():
                    text_list.append(author)
                if len(text_list) == 1:
                    name_ = text_list[0]
                    source_ = ''
                if len(text_list) == 2:
                    name_ = text_list[0]
                    source_ = text_list[1]
            except:
                name_ = ''
                source_ = ''
            try:
                title_ = tag_response.css('div.cmp-Review-content div.cmp-Review-title a::text').get() 
            except:
                title_ = ''
            try:
                rating_ = tag_response.css('div[itemprop="reviewRating"] button.cmp-ReviewRating-text::text').get()
            except:
                rating_ = ''
            try:
                desc_text = []
                for text in tag_response.css('div.cmp-Review-content div.cmp-Review-text span[itemprop="reviewBody"] span.cmp-NewLineToBr span.cmp-NewLineToBr-text::text').getall():
                    try:
                        desc_text.append(text)
                    except:
                        pass
                review_ = ': '.join(desc_text)
            except:
                review_ = ''
            
            data_items = {}

            data_items['name'] = name_
            data_items['date'] = date_
            data_items['avatar'] = avatar_
            data_items['rating'] = rating_
            data_items['title'] = title_
            data_items['description'] = review_
            data_items['source'] = source_
            
            strId = f'{name_}{date_}'
            #Assumes the default UTF-8
            hash_object = hashlib.md5(strId.encode())
            data_items['reviewId'] = hash_object.hexdigest()

            self.reviews.append(data_items)

        if len(self.pagination) > 0:
            page = "?start=" + self.pagination[0]
            self.pagination.pop(0)
            yield response.follow(page, callback=self.parse)
        else:
                    
            self.data["reviews"] = self.reviews   
            yield self.data

