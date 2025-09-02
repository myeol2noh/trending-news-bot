import requests
import feedparser
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pytz
import re

class TrendingNewsCrawler:
    def __init__(self):
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_current_schedule(self):
        """현재 시간에 맞는 스케줄 반환 (7시 추가)"""
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        current_hour = now.strftime('%H:00')
        
        schedules = ['07:00', '09:00', '12:00', '15:00', '18:00', '21:00']
        if current_hour not in schedules:
            hour = int(now.strftime('%H'))
            for schedule in schedules:
                schedule_hour = int(schedule.split(':')[0])
                if hour <= schedule_hour:
                    current_hour = schedule
                    break
            else:
                current_hour = '21:00'
        
        return current_hour
    
    def crawl_google_news_trending(self, rss_url, limit=5):
        """구글 뉴스 인기 기사 크롤링"""
        news_items = []
        try:
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:limit]:
                # 제목에서 불필요한 정보 제거
                title = entry.title
                title = re.sub(r'\s*-\s*[^-]*', '', title)
                
                news_item = {
                    "title": title,
                    "link": entry.link
                }
                news_items.append(news_item)
                
        except Exception as e:
            # 예외가 발생했을 때 처리하는 블록
            print(f"오류가 발생했습니다: {e}")
            return None # 오류 발생 시 None 반환
            
        return news_items
