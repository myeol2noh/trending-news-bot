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
        try:
            feed = feedparser.parse(rss_url)
            news_items = []
            
            for entry in feed.entries[:limit]:
                title = entry.title
                title = re.sub(r'\s*-\s*[^-]*$', '', title)
                
                news_items.append({
                    'title': title,
                    'summary': getattr(entry, 'summary', '')[:200],
                    'link': entry.link,
                    'published': getattr(entry, 'published', ''),
                    'source': '구글 뉴스',
                    'popularity_score': len(entry.title)
                })
            
            return news_items
        
        except Exception as e:
            print(f"구글 뉴스 크롤링 오류: {e}")
            return []
    
    def crawl_reddit_hot(self, api_url, limit=3):
        """Reddit 인기 게시글 크롤링"""
        try:
            response = requests.get(api_url, headers=self.headers)
            data = response.json()
            
            news_items = []
            
            if 'data' in data and 'children' in data['data']:
                for post in data['data']['children'][:limit]:
                    post_data = post['data']
                    
                    if post_data.get('score', 0) > 100:
                        news_items.append({
                            'title': post_data['title'],
                            'summary': post_data.get('selftext', '')[:150],
                            'link': f"https://reddit.com{post_data['permalink']}",
                            'published': datetime.fromtimestamp(post_data['created_utc']).isoformat(),
                            'source': 'Reddit',
                            'popularity_score': post_data.get('score', 0)
                        })
            
            return sorted(news_items, key=lambda x: x['popularity_score'], reverse=True)
        
        except Exception as e:
            print(f"Reddit 크롤링 오류: {e}")
            return []
    
    def crawl_naver_trending(self, limit=5):
        """네이버 실시간 검색어 기반 뉴스"""
        try:
            url = "https://news.naver.com/main/ranking/popularDay.naver"
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_items = []
            ranking_items = soup.select('.ranking_item .list_title')
            
            for i, item in enumerate(ranking_items[:limit]):
                title = item.get_text(strip=True)
                link = item.get('href', '')
                
                if link and title:
                    news_items.append({
                        'title': title,
                        'summary': '',
                        'link': f"https://news.naver.com{link}" if link.startswith('/') else link,
                        'published': datetime.now().isoformat(),
                        'source': '네이버 뉴스',
                        'popularity_score': len(ranking_items) - i
                    })
            
            return news_items
        
        except Exception as e:
            print(f"네이버 뉴스 크롤링 오류: {e}")
            return []
    
    def crawl_hacker_news_hot(self, limit=3):
        """Hacker News 인기 스토리"""
        try:
            top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = requests.get(top_stories_url)
            story_ids = response.json()[:limit * 2]
            
            news_items = []
            for story_id in story_ids[:limit]:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_response = requests.get(story_url)
                story = story_response.json()
                
                if story and story.get('type') == 'story' and story.get('score', 0) > 50:
                    news_items.append({
                        'title': story.get('title', ''),
                        'summary': '',
                        'link': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                        'published': datetime.fromtimestamp(story.get('time', 0)).isoformat(),
                        'source': 'Hacker News',
                        'popularity_score': story.get('score', 0)
                    })
            
            return sorted(news_items, key=lambda x: x['popularity_score'], reverse=True)
        
        except Exception as e:
            print(f"Hacker News 크롤링 오류: {e}")
            return []

    def get_trending_news(self, time_slot=None):
        """인기 뉴스 종합 수집"""
        if not time_slot:
            time_slot = self.get_current_schedule()
        
        schedule_config = self.config['news_sources'].get(time_slot)
        if not schedule_config:
            return []
        
        all_news = []
        
        for source in schedule_config['sources']:
            try:
                if source.get('type') == 'naver_trending' or source.get('type') == 'naver_ranking':
                    news = self.crawl_naver_trending(limit=3)
                    all_news.extend(news)
                
                elif source.get('type') == 'reddit_hot':
                    news = self.crawl_reddit_hot(source['api'], limit=3)
                    all_news.extend(news)
                
                elif 'rss' in source:
                    news = self.crawl_google_news_trending(source['rss'], limit=3)
                    all_news.extend(news)
                
                elif source.get('type') == 'hackernews':
                    news = self.crawl_hacker_news_hot(limit=3)
                    all_news.extend(news)
                    
            except Exception as e:
                print(f"소스 크롤링 오류 ({source.get('name', 'Unknown')}): {e}")
                continue
        
        # 인기도 기준 정렬 및 중복 제거
        unique_news = []
        seen_titles = set()
        
        all_news.sort(key=lambda x: x.get('popularity_score', 0), reverse=True)
        
        for news in all_news:
            title_words = set(news['title'].lower().split())
            is_duplicate = False
            
            for seen_title in seen_titles:
                seen_words = set(seen_title.lower().split())
                if len(title_words & seen_words) / len(title_words | seen_words) > 0.6:
                    is_duplicate = True
                    break
            
            if not is_duplicate and len(news['title']) > 10:
                unique_news.append(news)
                seen_titles.add(news['title'])
        
        return unique_news[:5]

if __name__ == "__main__":
    crawler = TrendingNewsCrawler()
    trending_news = crawler.get_trending_news()
    
    print(f"수집된 인기 뉴스: {len(trending_news)}개")
    for i, news in enumerate(trending_news, 1):
        print(f"{i}. {news['title']} (인기도: {news.get('popularity_score', 0)})")
        print(f"   출처: {news['source']}")
