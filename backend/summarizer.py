from transformers import pipeline

# 서버 시작 시 모델 로딩 (한번만)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text: str, max_len: int = 200, min_len: int = 30) -> str:
    if not text or len(text.split()) < 30:  # 짧은 텍스트는 그대로 반환
        return text

    summary = summarizer(
        text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False
    )
    return summary[0]['summary_text']

