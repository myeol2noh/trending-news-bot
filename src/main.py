#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from datetime import datetime
import pytz

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from naver_crawler import NaverNewsCrawler
from issue_generator import IssueGenerator
from telegram_bot import send_to_telegram_simple, send_error_notification_telegram

def main():
    """메인 실행: 네이버 뉴스 → 이슈 정리 → 텔레그램 전송"""
    print("=== 네이버 뉴스 이슈 정리봇 시작 ===")
    
    # 환경 변수 확인
    required_env = ['CLAUDE_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    missing_env = [env for env in required_env if not os.getenv(env)]
    
    if missing_env:
        print(f"❌ 필수 환경 변수 누락: {missing_env}")
        sys.exit(1)
    
    try:
        # 1. 네이버 뉴스 수집
        print("📰 네이버 뉴스 수집 중...")
        crawler = NaverNewsCrawler()
        current_schedule = crawler.get_current_schedule()
        news_items = crawler.get_naver_news(current_schedule)

        if not news_items:
            error_msg = "네이버 뉴스 수집 실패"
            print(f"❌ {error_msg}")
            send_error_notification_telegram(error_msg, current_schedule)
            sys.exit(1)
        
        print(f"✅ {len(news_items)}개 뉴스 수집 완료")
        
        # 2. 이슈 정리 생성
        print("📝 이슈 정리 생성 중...")
        generator = IssueGenerator()
        
        if current_schedule == '20:00':
            # 핫이슈 생성
            content = generator.generate_hot_issue(news_items)
        else:
            # 이슈 리스트 생성
            content = generator.generate_issue_list(news_items, current_schedule)
        
        if not content:
            error_msg = "이슈 정리 생성 실패"
            print(f"❌ {error_msg}")
            send_error_notification_telegram(error_msg, current_schedule)
            sys.exit(1)
        
        # 3. 생성 결과 출력
        print(f"\n=== 생성된 이슈 정리 ({current_schedule}) ===")
        print(content)
        
        # 4. 텔레그램 전송 (본문만)
        print("\n📤 텔레그램 전송 중...")
        success = send_to_telegram_simple(content)
        
        if success:
            print("✅ 텔레그램 전송 성공!")
            print("📱 텔레그램에서 복사해서 스레드에 붙여넣으세요!")
        else:
            error_msg = "텔레그램 전송 실패"
            print(f"❌ {error_msg}")
            send_error_notification_telegram(error_msg, current_schedule)
            sys.exit(1)

    except Exception as e:
        error_msg = f"예상치 못한 오류: {str(e)}"
        print(f"❌ {error_msg}")
        send_error_notification_telegram(error_msg, current_schedule if 'current_schedule' in locals() else 'Unknown')
        sys.exit(1)

if __name__ == "__main__":
    main()
