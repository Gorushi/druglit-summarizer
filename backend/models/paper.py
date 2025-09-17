from typing import List, Optional
from pydantic import BaseModel, validator  
from datetime import datetime

class Paper(BaseModel):
    pmid: str
    drug: str  # SearchResult 모델과의 일관성을 위해 추가
    title: Optional[str] = None
    abstract: Optional[str] = None
    summary: Optional[str] = None
    pubdate: Optional[str] = None  # ISO8601 문자열 (YYYY-MM-DD)

    # pubdate 필드에 대한 유효성 검사기(validator)를 추가
    @validator('pubdate')
    def validate_pubdate_format(cls, v):
        """pubdate가 None이 아니면 'YYYY-MM-DD' 형식인지 확인"""
        if v is not None:
            try:
                # 지정된 형식으로 날짜 파싱을 시도
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                # 파싱에 실패하면 (형식이 다르면) 오류를 발생
                raise ValueError(f"pubdate '{v}'는 'YYYY-MM-DD' 형식이 아닙니다.")
        
        # 유효성 검사를 통과하면 원래 값을 반환
        return v

class SearchResult(BaseModel):
    drug: str
    papers: List[Paper]
