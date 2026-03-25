import requests
import datetime
import pandas as pd
from pykrx import stock
import google.generativeai as genai
import os

# 보안 키 가져오기
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

def main():
    # 1. 오늘 날짜 확인
    target_date = datetime.datetime.now().strftime("%Y%m%d")
    
    try:
        # 2. 데이터 수집 시도 (안전하게)
        df_kse = stock.get_market_cap_by_ticker(target_date, market="KOSPI")
        df_ksd = stock.get_market_cap_by_ticker(target_date, market="KOSDAQ")
        
        if df_kse.empty and df_ksd.empty:
            print("아직 오늘자 장중 데이터가 업데이트되지 않았습니다.")
            return

        combined = pd.concat([df_kse, df_ksd])

        # 3. 거래대금 상위 30개 종목명 추출
        top_30 = combined.sort_values(by="거래대금", ascending=False).head(30)
        stock_names = [stock.get_market_ticker_name(ticker) for ticker in top_30.index]

        # 4. Gemini AI 분석
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"다음 한국 주식 종목들을 현재 시장 테마별로 분류하고 요약해줘: {', '.join(stock_names)}"
        response = model.generate_content(prompt)

        # 5. 텔레그램 전송
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": response.text})
        print("✅ 전송 성공!")
        
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
