translation_prompt = """You will be given an English text, a component from a multiple-choice question, in the following format:

[Source Text]
<src>
 ...(source text)...
</src>

Your task is to return a translation of the source text. Before translation, you must review the following things.

1. What is the text? Is it a question or option?

    1-1 . Culturally Sensitivity: If it is a question, is it sensitive to a specific culture? We do not want questions on American culture to be translated into Korean. Inspect whether the question is culturally agnostic or sensitive.
    
    1-2. Question Type: Is the question asking for knowledge? Or is it a reasoning question?

2. Are there any standard nomenclatures or professional language that should be translated with care? If so which ones?

After reviewing, return the translation. This should be done in the following format:

<review1>
 ...(review the type of text, whether its a question or option, if it is a question check <1-1> and <1-2>)...
</review1>

<review2>
 ...(go over the source text and look for standard nomenclatures or professional language if there are some choose the best translation for the words)...
</review2>

<translation>
 ...(the translation, consider whether it's a question or option; the translation must be done accordingly so it is natural. Take into account the word translations you have discussed in review2)...
</translation>

--------------------------------------------------
The following is the text for your task, translate to natural and fluent Korean:
{source}"""

dataset_class_prompt = """
아래 지침을 따라 번역된 데이터셋을 위한 Python 클래스를 작성하세요.

지침:
1. Haerae-evaluation-toolkit의 BaseDataset 클래스를 상속받아 번역된 데이터셋 클래스 `{dataset_name}`을 구현하세요.
2. 이 클래스는 주어진 dataset_name과 subset 정보를 활용하여 Hugging Face Hub에서 번역된 데이터셋을 로드합니다.
3. `load()` 메서드를 구현하여 데이터셋을 로드하고, 각 샘플이 다음과 같은 형태의 딕셔너리로 구성되도록 합니다:
   [
     "input": 번역된 텍스트,
     "reference": 원본 영어 텍스트,
     "metadata": 추가 정보 (예: 원본 데이터셋 정보, subset 등)
   ]
4. 필요 시 `get_raw_samples()` 및 `info()` 메서드도 구현하세요.
5. BaseDataset 클래스와 참고용 HaeraeDataset 코드는 참고용이며, 실제 코드에 포함하지 않습니다.
6. 번역된 데이터셋 클래스와 관련된 세부 사항은 다음과 같습니다. {explaination}

참고(BaseDataset 클래스):
from typing import List, Dict, Any, Optional

class BaseDataset:
    (개발 용이를 위해 개발 단계에서는 한국어로 작성, 이후 영어로 대체)
    모든 데이터셋 클래스가 상속해야 할 기본(추상) 클래스
    목적:
      1) 평가 파이프라인에서 기대하는 일관된 인터페이스(특히 'input'과 'reference') 제공
        1-1) input: LLM에게 전달되는 prompt, context, instruction 등을 모두 합쳐 "모델이 실제로 받게 될 텍스트"
        1-2) reference: 정답, 정답 label, gold output 등에 해당하는 "모델이 만들어야 하는 기대 출력"
      2) 각 데이터셋별 로드/전처리 로직을 쉽게 커스터마이징징

    필수 구현 메서드
      - load(): 데이터를 로드하고 최종적으로 [{"input":..., "reference":...}, ...] 형태 반환.
    
    선택적 구현 메서드
      - get_raw_samples(): 원본(raw) 데이터 접근
      - info(): 데이터셋 정보

    def __init__(self, dataset_name: str, split: str = "test", subset:str = None, **kwargs):
        Args:
            dataset_name (str): 
                데이터셋 고유 식별자
            split (str): 
                train/validation/test 등을 구분하기 위한 문자열 (load 시)
            subset (str): 
                하위 태스크나 config (예: "abstract_algebra")
            kwargs: 
                기타 데이터셋 로딩에 필요한 파라미터(예: HF config, version, 인증 토큰 등)
        self.dataset_name = dataset_name
        self.split = split
        self.subset = subset
        self.kwargs = kwargs  # 확장 가능하도록 저장

    def load(self) -> List[Dict[str, Any]]:
        (필수) 전제 pipeline 에서 사용할 데이터 List 반환.

        raise NotImplementedError("Subclasses must implement load().")

    def get_raw_samples(self) -> Any:
        (선택) 원본 데이터(raw)를 반환하거나, 
        필요하다면 객체 형태로 caching하여 접근할 수 있도록 제공.
        raise NotImplementedError("This is optional. Override if needed.")

    def info(self) -> Dict[str, Any]:

        (선택) 데이터셋에 대한 메타 정보(고민중..)를 딕셔너리로 반환.
        return {"name": self.dataset_name, "split": self.split}


클래스 구현 코드를 작성해 주세요.
"""