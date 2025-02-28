import pandas as pd

# Step 1: 빈 DataFrame 생성
df = pd.DataFrame(columns=['Date', 'EMA5', 'EMA20', 'MACD', 'Signal'])

# Step 2: 여러 행의 데이터를 추가하는 함수
def add_data(date, ema5, ema20, macd, signal):
    global df
    new_data = pd.DataFrame({'Date': [date], 'EMA5': [ema5], 'EMA20': [ema20], 'MACD' : [macd], 'Signal' : [signal]})
    df = pd.concat([df, new_data], ignore_index=True)

# CSV 파일에서 데이터 읽기
file_path = 'HLB_price(20.1~24.7).csv'  # 입력 CSV 파일 경로
data = pd.read_csv(file_path)

# EMA 계산 함수 정의
def calculate_ema(data, period):
    ema = data.ewm(span=period, adjust=False).mean()
    return ema

# Close 컬럼에서 EMA(5)와 EMA(20) 계산
ema5 = calculate_ema(data['Close'], 5)
ema20 = calculate_ema(data['Close'], 20)
ema12 = calculate_ema(data['Close'], 12)
ema26 = calculate_ema(data['Close'], 26)

# MACD, signal 계산
macd = ema12 - ema26
signal = calculate_ema(macd, 9)

# 각 날짜에 대해 EMA 값을 추가
for date, e5, e20, macd, signal in zip(data['Date'], ema5, ema20, macd, signal):
    add_data(date, e5, e20, macd, signal)

# Step 3: DataFrame을 CSV 파일로 저장
csv_file_path = 'output_data.csv'  # 출력 CSV 파일 경로
df.to_csv(csv_file_path, index=False)

print(f'Data saved to {csv_file_path}')

print(ema12)
