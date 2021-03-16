import scrapy
import re

class ReviewsSpider(scrapy.Spider):
    name = "indeed"

    start_urls = [
        'https://www.indeed.com/cmp/Accurate-Personnel/reviews',
    ]

    data = {}
    reviews, pageNum, title_list, rating_list, name_list, date_list, avatar_list, desc_list, source_list = ([] for x in range(9))
        
    def __init__(self):
        self.called = False
        
    def parse(self, response):

        global data, reviews, pageNum, title_list, rating_list, name_list, date_list, avatar_list, desc_list, source_list 
        
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
                    if number not in self.pageNum:
                        self.pageNum.append(number)
       
            self.pageNum.sort()
            
        for title in response.css('div.cmp-Review-title a::text').getall():
            self.title_list.append(re.sub(u"(\u2018|\u2019)", "'", title))
            self.name_list.append("")
            self.avatar_list.append("")
            self.date_list.append("")
            self.desc_list.append("")
            self.source_list.append("")

        
        #for date in response.css("a.cmp-ReviewAuthor-link::text").getall():
            #yield{'date':date}
        
        for ratings in response.css("button.cmp-ReviewRating-text::text").getall():
            self.rating_list.append(ratings)

        if len(self.pageNum) > 0:
            page = "?start=" + self.pageNum[0]
            self.pageNum.pop(0)
            yield response.follow(page, callback=self.parse)
        else:
           
            keys = ['name','date','avatar','rating','title','description','source']
            zip_lists = list(zip(self.name_list, self.date_list, self.avatar_list, self.rating_list, self.title_list, self.desc_list, self.source_list))
            for item in zip_lists: 
                self.reviews.append(dict(list(zip(keys, item))))
                    
            self.data["reviews"] = self.reviews
                
            yield self.data

        
        
        

        

