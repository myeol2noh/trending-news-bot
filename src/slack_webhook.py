# src/slack_webhook.py (discord_webhook.py 대신 사용)
import requests
import os
from datetime import datetime

def send_to_slack(thread_data):
    """Slack 웹훅으로 인기 뉴스 쓰레드 전송"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')  # Discord 대신 Slack
    
    if not webhook_url:
        print("Slack 웹훅 URL이 설정되지 않았습니다.")
        return False
    
    # 참고 뉴스 링크들 정리
    news_links = ""
    if 'source_news' in thread_data:
        for i, news in enumerate(thread_data['source_news'][:3], 1):
            popularity = news.get('popularity_score', 0)
            news_links += f"{i}. <{news['link']}|{news['title']}> (인기도: {popularity})\n"
    
    # Slack 메시지 포맷
    message = {
        "text": f"🔥 {thread_data['time_slot']} 인기 뉴스 쓰레드 생성!",
        "attachments": [
            {
                "color": "good",  # 초록색
                "title": f"📱 {thread_data['category']} - {thread_data['time_slot']}",
                "text": thread_data['content'],
                "fields": [
                    {
                        "title": "글자수",
                        "value": f"{len(thread_data['content'])}자",
                        "short": True
                    },
                    {
                        "title": "생성시간",
                        "value": thread_data['generated_at'][:16],
                        "short": True
                    }
                ],
                "footer": "자동 뉴스 쓰레드 봇"
            }
        ]
    }
    
    # 참고 뉴스가 있으면 추가
    if news_links:
        message["attachments"].append({
            "color": "#ff6b35",
            "title": "📰 참고 뉴스",
            "text": news_links,
            "footer": "이 링크들을 참고해서 쓰레드가 생성되었습니다"
        })
    
    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        if response.status_code == 200:
            print("✅ Slack 웹훅 전송 성공!")
            return True
        else:
            print(f"❌ Slack 웹훅 전송 실패: HTTP {response.status_code}")
            print(f"응답: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Slack 웹훅 오류: {e}")
        return False

def send_error_notification(error_message, time_slot):
    """에러 발생시 Slack 알림"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        return False
    
    message = {
        "text": "🚨 뉴스 쓰레드 봇 오류 발생!",
        "attachments": [
            {
                "color": "danger",  # 빨간색
                "title": f"시간: {time_slot}",
                "text": f"오류: {error_message}",
                "footer": "봇 관리자 확인 필요"
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        return response.status_code == 200
    except:
        return False

# 테스트용 함수
if __name__ == "__main__":
    test_data = {
        'time_slot': '09:00',
        'category': '인기 뉴스',
        'content': '🔥 테스트 뉴스가 화제\n💡 이것은 Slack 테스트입니다\n⚡ 곧 실제 뉴스로 대체됩니다',
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
    
    print("Slack 웹훅 테스트 중...")
    success = send_to_slack(test_data)
    print(f"결과: {'성공' if success else '실패'}")
