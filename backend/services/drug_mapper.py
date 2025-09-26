import json
from pathlib import Path
from typing import Dict, Optional

class DrugNameMapper:
    """
    약물명을 표준화하는 싱글턴(Singleton) 클래스.
    
    애플리케이션 전체에서 단 하나의 인스턴스만 생성되어 메모리 효율성을 높임
    JSON 파일을 한 번만 로드하여 룩업 딕셔너리를 구성
    """
    _instance: Optional['DrugNameMapper'] = None
    _lookup_map: Dict[str, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DrugNameMapper, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        매핑 파일을 로드하고 룩업 딕셔너리를 초기화
        이 메서드는 첫 인스턴스 생성 시에만 호출됨
        """
        try:
            # 프로젝트 구조에 맞게 파일 경로를 설정
            # 이 파일의 위치를 기준으로 상위 폴더의 'data' 폴더를 찾음
            base_dir = Path(__file__).resolve().parent.parent.parent
            mapping_file_path = base_dir / 'data' / 'drug_map.json'
            
            print(f"데이터 파일 로딩 시도: {mapping_file_path}")
            with open(mapping_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 새로운 JSON 구조({'표준명': {'aliases': [...]}})를 파싱하여
            # {'별칭': '표준명'} 형태의 룩업 딕셔너리를 생성
            for standard_name, details in data.items():
                # 1. 표준명 자체를 맵에 추가 (예: 'acetaminophen' -> 'Acetaminophen')
                self._lookup_map[standard_name.lower()] = standard_name
                
                # 2. 모든 별칭(aliases)을 맵에 추가
                for alias in details.get('aliases', []):
                    self._lookup_map[alias.lower()] = standard_name
            
            print("약물명 매핑 데이터 로딩 완료!")

        except FileNotFoundError:
            print(f"오류: 매핑 파일 '{mapping_file_path}'를 찾을 수 없습니다.")
            self._lookup_map = {}
        except (json.JSONDecodeError, IOError) as e:
            print(f"오류: 파일 읽기 또는 JSON 파싱 중 에러 발생 - {e}.")
            self._lookup_map = {}
            
    def normalize_name(self, drug_name: str) -> str:
        """
        주어진 약물명을 표준화된 이름으로 변환

        Args:
            drug_name (str): 변환할 약물명 (예: 'Tylenol', 'Advil').

        Returns:
            str: 매핑된 표준 약물명. 매핑되는 이름이 없으면 입력된 원본 이름을 그대로 반환
        """
        # 맵이 비어있으면 원본 이름 반환
        if not self._lookup_map:
            return drug_name
            
        # 소문자로 변환하여 검색 후, 매핑된 표준명 또는 원본명 반환
        normalized_input = drug_name.lower()
        return self._lookup_map.get(normalized_input, drug_name)

# --- 사용 예시 ---
if __name__ == '__main__':
    # 싱글턴 인스턴스를 가져옴
    mapper = DrugNameMapper()

    # --- 약물명 표준화 테스트 ---
    test_names = ['Tylenol', 'Advil', 'ibuprofen', 'NonExistentDrug', 'Aspirin']
    print("\n--- 약물명 표준화 테스트 ---")
    for name in test_names:
        standard_name = mapper.normalize_name(name)
        print(f"입력: '{name:<15}' -> 표준명: '{standard_name}'")
