import requests
import os
from datetime import datetime

def send_to_telegram_simple(content):
    """텔레그램 봇으로 본문만 전송 (바로 복사용)"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("텔레그램 봇 토큰 또는 채팅 ID가 설정되지 않았습니다.")
        return False
    
    # 본문만 전송 (다른 정보 없이)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': content,  # 본문만
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print("✅ 텔레그램 전송 성공!")
            return True
        else:
            print(f"❌ 텔레그램 전송 실패: HTTP {response.status_code}")
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
    
    message = f"🚨 뉴스봇 오류\n시간: {time_slot}\n오류: {error_message}"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except:
        return False
