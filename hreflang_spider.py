import scrapy

class HreflangSpider(scrapy.Spider):
  name = "hreflang"
  start_urls = []

  def start_requests(self):
    with open('urls.txt', 'r') as f:
      urls = f.readlines()
      urls = [url.strip() for url in urls]
      self.start_urls = urls

    for url in self.start_urls:
      yield scrapy.Request(url=url, callback=self.parse)

  def parse(self, response):
    # Find all the hreflang tags on the page
    hreflang_tags = response.css('link[rel="alternate"][hreflang]')

    # Create a dictionary to store the hreflang URLs for each language
    hreflang_dict = {}
    for tag in hreflang_tags:
      lang = tag.attrib['hreflang']
      href = tag.attrib['href']
      hreflang_dict[lang] = href

    # Add the default URL to the dictionary
    default_href = hreflang_dict.pop('x-default', None)
    if default_href:
      hreflang_dict['x-default'] = default_href

    hreflang_list = [(lang, href) for lang, href in hreflang_dict.items()]

    with open('sitemap.xml', 'a') as f:
      if f.tell() == 0:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n')
        f.write('        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n')
      f.write('    <url>\n')
      f.write(f'        <loc>{response.url}</loc>\n')
      for lang, href in hreflang_list:
        f.write(
          f'        <xhtml:link rel="alternate" hreflang="{lang}" href="{href}" />\n'
        )
      f.write('    </url>\n')

  def close(self, reason):
    with open('sitemap.xml', 'a') as f:
      if f.tell() > 0:
        f.write('</urlset>\n')
