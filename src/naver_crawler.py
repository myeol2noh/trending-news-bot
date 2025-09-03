import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz

class NaverNewsCrawler:
    def __init__(self):
        with open('../config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_current_schedule(self):
        """현재 시간에 맞는 스케줄 반환"""
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        current_hour = now.strftime('%H:00')
        
        schedules = ['07:00', '12:00', '18:00', '20:00']
        if current_hour not in schedules:
            hour = int(now.strftime('%H'))
            for schedule in schedules:
                schedule_hour = int(schedule.split(':')[0])
                if hour <= schedule_hour:
                    current_hour = schedule
                    break
            else:
                current_hour = '20:00'
        
        return current_hour
    
    def crawl_naver_ranking_news(self, limit=10):
        """네이버 뉴스 랭킹에서 상위 뉴스 수집"""
        try:
            url = "https://news.naver.com/main/ranking/popularDay.naver"
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_items = []
            
            # 랭킹 뉴스 추출 (여러 섹션에서)
            ranking_sections = soup.select('.rankingnews_box')
            
            for section in ranking_sections[:3]:  # 상위 3개 언론사
                news_links = section.select('.list_title')
                
                for link in news_links[:5]:  # 각 언론사에서 5개씩
                    title = link.get_text(strip=True)
                    news_url = link.get('href', '')
                    
                    if title and len(title) > 10:  # 너무 짧은 제목 제외
                        if news_url.startswith('/'):
                            news_url = f"https://news.naver.com{news_url}"
                        
                        news_items.append({
                            'title': title,
                            'link': news_url,
                            'source': '네이버뉴스',
                            'rank': len(news_items) + 1
                        })
                        
                        if len(news_items) >= limit:
                            break
                
                if len(news_items) >= limit:
                    break
            
            return news_items[:limit]
            
        except Exception as e:
            print(f"네이버 뉴스 크롤링 오류: {e}")
            return []
    
    def get_naver_news(self, time_slot=None):
        """네이버 뉴스 수집"""
        if not time_slot:
            time_slot = self.get_current_schedule()
        
        # 핫이슈 시간대는 1개만, 나머지는 10개
        limit = 1 if time_slot == '20:00' else 10
        
        news_items = self.crawl_naver_ranking_news(limit=limit)
        return news_items

if __name__ == "__main__":
    crawler = NaverNewsCrawler()
    news = crawler.get_naver_news()
    
    print(f"수집된 뉴스: {len(news)}개")
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']}")
