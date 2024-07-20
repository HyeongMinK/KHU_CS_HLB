import pandas as pd
from transformers import pipeline
from tqdm import tqdm

# BERT 기반 한국어 감성 분석 모델을 로드합니다.
sentiment_analysis = pipeline("sentiment-analysis", model="doya/klue-sentiment-nsmc")

def analyze_sentence(sentence, max_length=512):
    # 문장을 최대 길이로 자르기
    sentence = sentence[:max_length]
    # 감성 분석 수행
    result = sentiment_analysis(sentence)
    # 결과에서 감성 레이블을 추출
    sentiment_label = result[0]['label']
    sentiment_score = result[0]['score']
    return sentiment_label, sentiment_score

# CSV 파일 로드
file_path = '10000_10300.csv'
df = pd.read_csv(file_path)

# 결과를 저장할 리스트
results = []

# 각 행에 대해 감성 분석 수행
for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing rows"):
    sentence = str(row['title'])
    date = row['date']  # 날짜 정보 추출
    label, score = analyze_sentence(sentence)
    results.append({
        'date': date,  # 날짜 정보 추가
        'combined_text': sentence,
        'label': label,
        'score': score
    })

# 결과를 데이터프레임으로 변환
results_df = pd.DataFrame(results)

# 새로운 CSV 파일로 저장
output_file_path = 'sentiment_analysis_results_miss.csv'
results_df.to_csv(output_file_path, index=False)

print(f"Sentiment analysis results saved to {output_file_path}")
