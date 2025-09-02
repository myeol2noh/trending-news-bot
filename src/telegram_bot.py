import requests
import os
from datetime import datetime

def send_to_telegram(thread_data):
    """텔레그램 봇으로 뉴스 쓰레드 전송"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("텔레그램 봇 토큰 또는 채팅 ID가 설정되지 않았습니다.")
        return False
    
    # 메시지 구성
    message = f"""🔥 {thread_data['time_slot']} 인기 뉴스 쓰레드

📱 **쓰레드 내용:**
{thread_data['content']}

📊 **정보:**
- 카테고리: {thread_data['category']}
- 글자수: {len(thread_data['content'])}자
- 생성시간: {thread_data['generated_at'][:16]}

📰 **참고 뉴스:**"""
    
    # 참고 뉴스 추가
    if 'source_news' in thread_data:
        for i, news in enumerate(thread_data['source_news'][:3], 1):
            popularity = news.get('popularity_score', 0)
            message += f"\n{i}. [{news['title']}]({news['link']}) (인기도: {popularity})"
    
    message += "\n\n📱 위 내용을 복사해서 Threads에 올려주세요!"
    
    # 텔레그램 API 호출
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print("✅ 텔레그램 전송 성공!")
            return True
        else:
            print(f"❌ 텔레그램 전송 실패: HTTP {response.status_code}")
            print(f"응답: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 텔레그램 오류: {e}")
        return False

def send_error_notification_telegram(error_message, time_slot):
    """에러 발생시 텔레그램 알림"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        return False
    
    message = f"""🚨 **뉴스 쓰레드 봇 오류**

⏰ 시간: {time_slot}
❌ 오류: {error_message}
📅 발생시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 관리자 확인이 필요합니다."""
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except:
        return False

# 테스트용 함수
if __name__ == "__main__":
    test_data = {
        'time_slot': '09:00',
        'category': '인기 뉴스',
        'content': '🔥 테스트 뉴스가 화제\n💡 이것은 텔레그램 테스트입니다\n⚡ 곧 실제 뉴스로 대체됩니다',
        'generated_at': datetime.now().isoformat(),
        'source_news': [
            {
                'title': '테스트 뉴스 1',
                'link': 'https://example.com',
                'popularity_score': 100
            }
        ]
    }
    
    print("텔레그램 봇 테스트 중...")
    success = send_to_telegram(test_data)
    print(f"결과: {'성공' if success else '실패'}")
