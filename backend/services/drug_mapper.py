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
            # 이 파일의 위치를 기준으로 프로젝트 루트를 찾고, data 폴더의 경로를 조합
            base_dir = Path(__file__).resolve().parent.parent.parent
            mapping_file_path = base_dir / 'data' / 'drug_map.json'
            
            with open(mapping_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # {'별칭': '표준명'} 형태의 룩업 딕셔너리 생성 (키는 소문자)
            for canonical_name, aliases in data.items():
                for alias in aliases:
                    self._lookup_map[alias.lower()] = canonical_name
            
        except (FileNotFoundError, json.JSONDecodeError, IOError):
            # 파일이 없거나 읽기 실패 시, 빈 딕셔너리로 설정
            self._lookup_map = {}
    
    @classmethod
    def get_instance(cls) -> 'DrugNameMapper':
        """
        클래스의 싱글턴 인스턴스를 반환하는 정적 메서드
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def normalize_name(self, drug_name: str) -> str:
        """
        주어진 약물명을 표준화된 이름으로 변환

        Args:
            drug_name (str): 변환할 약물명 (예: '타이레놀', 'Advil').

        Returns:
            str: 매핑된 표준 약물명. 매핑되는 이름이 없으면 입력된 원본 이름을 반환
        """
        if not self._lookup_map:
            return drug_name
            
        normalized_input = drug_name.lower()
        return self._lookup_map.get(normalized_input, drug_name)

# --- 사용 예시 ---
if __name__ == '__main__':
    # 싱글턴 인스턴스를 얻는 방법
    mapper1 = DrugNameMapper.get_instance()
    mapper2 = DrugNameMapper.get_instance()

    # 두 인스턴스가 동일한지 확인 (True가 출력되어야 함)
    print(f"mapper1과 mapper2는 동일한 인스턴스인가? {mapper1 is mapper2}\n")

    test_names = ['Tylenol', '타이레놀', 'ibuprofen', '애드빌', 'Aspirin']
    print("--- 약물명 표준화 테스트 ---")
    for name in test_names:
        standard_name = mapper1.normalize_name(name)
        print(f"입력: '{name}' -> 표준명: '{standard_name}'")
