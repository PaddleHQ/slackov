from crawler.ChannelCrawler import ChannelCrawler
from crawler.ChannelHistoryCrawler import ChannelHistoryCrawler
from crawler.EmployeeCrawler import EmployeeCrawler

ChannelCrawler().run()
EmployeeCrawler().run()
ChannelHistoryCrawler().run()