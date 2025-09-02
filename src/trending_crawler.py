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
                # 제목에서 불필요한 정보 제거
                title = entry.title
                title = re.sub(r'\s*-\s*[^-]*

### src/discord_webhook.py
```python
import requests
import os
from datetime import datetime

def send_to_discord(thread_data):
    """Discord 웹훅으로 인기 뉴스 쓰레드 전송"""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    
    if not webhook_url:
        print("Discord 웹훅 URL이 설정되지 않았습니다.")
        return False
    
    # 참고 뉴스 링크들 정리
    news_links = ""
    if 'source_news' in thread_data:
        for i, news in enumerate(thread_data['source_news'][:3], 1):
            popularity = news.get('popularity_score', 0)
            news_links += f"{i}. [{news['title']}]({news['link']}) (인기도: {popularity})\n"
    
    # 인기 뉴스 전용 임베드 메시지
    embed = {
        "title": f"🔥 {thread_data['time_slot']} 인기 뉴스 쓰레드",
        "description": thread_data['content'],
        "color": 0xff6b35,  # 주황색 (트렌딩 느낌)
        "fields": [
            {
                "name": "📊 카테고리",
                "value": thread_data['category'],
                "inline": True
            },
            {
                "name": "📱 글자수", 
                "value": f"{len(thread_data['content'])}자",
                "inline": True
            },
            {
                "name": "🔥 기반 정보",
                "value": thread_data.get('trending_info', '인기 뉴스 기반'),
                "inline": True
            }
        ],
        "footer": {
            "text": f"생성 시간: {thread_data['generated_at']}"
        }
    }
    
    # 참고 뉴스가 있으면 필드 추가
    if news_links:
        embed["fields"].append({
            "name": "📰 참고 뉴스",
            "value": news_links[:1000],  # Discord 제한 고려
            "inline": False
        })
    
    payload = {
        "content": "🚨 **새로운 인기 뉴스 쓰레드가 생성되었습니다!**\n📱 아래 내용을 복사해서 Threads에 올려주세요:",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 204:
            print("✅ Discord 웹훅 전송 성공!")
            return True
        else:
            print(f"❌ Discord 웹훅 전송 실패: HTTP {response.status_code}")
            print(f"응답: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Discord 웹훅 오류: {e}")
        return False

def send_error_notification(error_message, time_slot):
    """에러 발생시 Discord 알림"""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    
    if not webhook_url:
        return False
    
    embed = {
        "title": "❌ 뉴스 쓰레드 봇 오류",
        "description": f"시간: {time_slot}\n오류: {error_message}",
        "color": 0xff0000,  # 빨간색
        "timestamp": datetime.now().isoformat()
    }
    
    payload = {
        "content": "🚨 **뉴스 쓰레드 봇에서 오류가 발생했습니다!**",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 204
    except:
        return False

def send_daily_summary(threads_list):
    """하루 생성된 쓰레드 요약 전송 (선택사항)"""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    
    if not webhook_url or not threads_list:
        return False
    
    summary_text = f"📊 **오늘의 인기 뉴스 쓰레드 요약 ({len(threads_list)}개)**\n\n"
    
    for i, thread in enumerate(threads_list, 1):
        summary_text += f"**{i}. {thread['time_slot']} - {thread['category']}**\n"
        summary_text += f"```{thread['content'][:100]}...```\n\n"
    
    payload = {
        "content": summary_text[:2000]  # Discord 메시지 길이 제한
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 204
    except Exception as e:
        print(f"일간 요약 전송 오류: {e}")
        return False

# 테스트용 함수
if __name__ == "__main__":
    test_data = {
        'time_slot': '09:00',
        'category': '인기 뉴스',
        'content': '🔥 테스트 뉴스가 화제\n💡 이것은 테스트입니다\n⚡ 곧 실제 뉴스로 대체됩니다',
        'generated_at': datetime.now().isoformat(),
        'trending_info': '테스트 데이터',
        'source_news': [
            {
                'title': '테스트 뉴스 1',
                'link': 'https://example.com',
                'popularity_score': 100
            }
        ]
    }
    
    print("Discord 웹훅 테스트 중...")
    success = send_to_discord(test_data)
    print(f"결과: {'성공' if success else '실패'}")
