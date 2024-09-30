import scrapy
import os

class GlamiraImageSpider(scrapy.Spider):
    name = "glamira"
    # Bắt đầu từ trang chủ của Glamira
    start_urls = ["https://www.glamira.com/"]

    def parse(self, response):
        # In mã trạng thái HTTP
        self.logger.info(f"HTTP status: {response.status}")
       
        if response.status != 200:
            self.logger.error(f"Failed: {response.url}")
            return
        
        # Tìm tất cả các liên kết khác trên trang (bao gồm các trang con)
        page_urls = response.css('a::attr(href)').getall()
        self.logger.info(f"Found {len(page_urls)} page URLs")

        # Duyệt qua từng URL trên trang và tiếp tục gửi yêu cầu
        for url in page_urls:
            full_url = response.urljoin(url)
            yield scrapy.Request(full_url, callback=self.parse)

        # Tìm tất cả các URL hình ảnh trên trang hiện tại
        image_urls = response.css('img::attr(src)').getall()

        # Tạo đường dẫn tuyệt đối cho ảnh
        image_urls = [response.urljoin(url) for url in image_urls]

        self.logger.info(f"Found {len(image_urls)} images on {response.url}")

        # Tải từng ảnh và lưu vào folder
        for url in image_urls:
            yield scrapy.Request(url, callback=self.download_image)

    def download_image(self, response):
        # Lấy tên file ảnh từ URL
        image_name = response.url.split('/')[-1]
        self.logger.info(f"Downloading image: {image_name}")

        # Tạo thư mục để lưu ảnh nếu chưa tồn tại
        image_dir = 'downloaded_images'
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        # Lưu ảnh vào thư mục
        with open(os.path.join(image_dir, image_name), 'wb') as f:
            f.write(response.body)
