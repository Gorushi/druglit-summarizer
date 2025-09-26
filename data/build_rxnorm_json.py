import json
import os
from collections import defaultdict
from tqdm import tqdm

def create_rxnorm_json(rrf_file_path, json_path='rxnorm_drugs.json'):
    """
    RXNCONSO.RRF 파일을 파싱하여 의약품명 표준화 JSON 파일을 생성

    Args:
        rrf_file_path (str): RXNCONSO.RRF 파일의 전체 경로
        json_path (str): 생성할 JSON 파일 경로
    """
    if not os.path.exists(rrf_file_path):
        print(f"오류: '{rrf_file_path}' 파일을 찾을 수 없습니다.")
        return

    # 1. 모든 RXCUI에 대한 표준명(IN, PIN)을 먼저 찾음
    print("표준 의약품명(주성분)을 찾는 중입니다...")
    standard_names = {}
    with open(rrf_file_path, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="표준명 스캔 중"):
            fields = line.strip().split('|')
            if len(fields) < 15:
                continue
            
            rxcui, tty, str_name = fields[0], fields[12], fields[14]
            
            # 주성분(IN), 정밀 주성분(PIN)을 표준명으로 간주
            if tty in ('IN', 'PIN'):
                if rxcui not in standard_names:
                    standard_names[rxcui] = str_name

    # 2. 모든 별칭을 표준명과 매핑
    print("의약품 별칭과 표준명을 매핑하는 중입니다...")
    # defaultdict를 사용하여 각 RXCUI에 대한 별칭 리스트를 관리
    aliases_by_rxcui = defaultdict(set)
    with open(rrf_file_path, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="별칭 매핑 중"):
            fields = line.strip().split('|')
            if len(fields) < 15:
                continue

            rxcui, str_name = fields[0], fields[14]

            # 해당 RXCUI의 표준명이 존재할 경우에만 별칭으로 추가
            if rxcui in standard_names:
                aliases_by_rxcui[rxcui].add(str_name)

    # 3. JSON 파일로 저장할 최종 데이터 구조를 작성
    print("JSON 구조를 생성하는 중입니다...")
    final_data = {}
    for rxcui, std_name in tqdm(standard_names.items(), desc="JSON 구조 생성 중"):
        # 표준명을 키로 사용
        if std_name not in final_data:
            # 별칭 리스트에서 표준명 자체는 제외하여 순수 별칭만 남김
            aliases = list(aliases_by_rxcui.get(rxcui, set()) - {std_name})
            
            final_data[std_name] = {
                'rxcui': rxcui,
                'aliases': sorted(aliases) # 정렬하여 일관성 유지
            }

    # 4. JSON 파일로 저장
    print(f"'{json_path}' 파일로 저장하는 중입니다...")
    with open(json_path, 'w', encoding='utf-8') as f:
        # indent=2 옵션으로 가독성 좋게 저장, ensure_ascii=False로 유니코드 문자 유지
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        
    print(f"'{json_path}' 파일 생성이 완료되었습니다.")

if __name__ == '__main__':
    # --- 사용법 ---
    
    # RXNCONSO.RRF 파일의 실제 경로를 입력
    # 예: '.../RxNorm_full_09022025/rrf/RXNCONSO.RRF'
    rrf_file = 'RXNCONSO.RRF' 
    
    # 생성될 JSON 파일명을 지정
    json_file = 'drug_map.json'
    
    create_rxnorm_json(rrf_file, json_file)
