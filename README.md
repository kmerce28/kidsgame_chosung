# 🎯 한글 초성게임

음성인식을 활용한 한국어 초성게임입니다. 제시된 초성으로 시작하는 단어를 말해서 점수를 획득하는 게임입니다. **최대 4명까지 멀티플레이어**를 지원합니다!

## 🎮 게임 방법

1. **플레이어 설정**: 1~4명의 플레이어 수를 선택하고 이름을 입력합니다.
2. **게임 시작**: "게임 시작" 버튼을 클릭합니다.
3. **음성인식 시작**: "🎤 음성인식 시작" 버튼을 클릭하여 마이크를 활성화합니다.
4. **멀티플레이어**: 2명 이상일 경우, 답변하기 전에 자신의 이름 버튼을 먼저 눌러주세요.
5. **단어 맞추기**: 제시된 초성(예: ㄴㅁ)으로 시작하는 단어를 말합니다.
6. **점수 획득**: 정답을 맞추면 10점을 획득합니다.
7. **시간 제한**: 각 라운드마다 1분의 시간이 주어집니다.
8. **총 5라운드**: 5개의 서로 다른 초성 조합으로 게임이 진행됩니다.

## 🎯 게임 규칙

- **플레이어**: 1~4명 (단일 또는 멀티플레이어)
- **제시어**: 2글자 또는 3글자 초성 조합
- **시간**: 각 라운드당 1분
- **점수**: 정답당 10점
- **중복 답변**: 같은 단어는 한 번만 인정
- **총 라운드**: 5라운드
- **멀티플레이어**: 답변 전에 자신의 이름 버튼을 먼저 눌러야 득점 가능

## 🛠️ 기술 스택

- **HTML5**: 웹 구조
- **CSS3**: 스타일링 및 애니메이션
- **JavaScript**: 게임 로직 및 음성인식
- **Web Speech API**: 음성인식 기능
- **한글 유니코드**: 초성 추출 알고리즘

## 🚀 실행 방법

1. 웹 브라우저에서 `index.html` 파일을 열어주세요.
2. 마이크 권한을 허용해주세요.
3. "게임 시작" 버튼을 클릭하여 게임을 시작하세요.

## 🔊 배경음악/효과음 사용법

1) 프로젝트 루트에 `music/` 폴더를 만들고 mp3 파일을 넣습니다.
   - 예: `music/bgm.mp3`, `music/background.mp3`, `music/correct.mp3`
2) `data/music.js`에서 파일 경로와 볼륨을 조정합니다.
   - `bgm`: 배열의 첫 곡을 루프로 재생합니다.
   - `sfx.correct`: 정답 시 재생할 효과음 파일 경로
   - `volume.bgm` / `volume.sfx`: 0.0 ~ 1.0
3) 게임 시작 시 배경음악이 재생되고, 정답 시 효과음이 재생됩니다.
4) 파일 로드 실패 시 화면에 오류 메시지가 표시됩니다.

## 📚 정답 사전 관리 (대용량)

이 프로젝트는 초성 패턴별 정답을 `data/answers.js`에 보관합니다. 기본 파일이 포함되어 있으며, 더 큰 사전을 원하면 아래 스크립트로 자동 생성하세요.

### 준비물
- 한국어 단어 목록 파일(예: `data/words_ko.txt`) — 한 줄당 한 단어, UTF-8
- 사용할 초성 패턴 목록(예: `data/patterns.txt`) — 한 줄당 한 패턴, 예: `ㅇㄱ`, `ㄴㄹ` 등 30개 내외

### 생성 방법

```bash
python scripts/build_answers.py --source data/words_ko.txt --patterns data/patterns.txt --out data/answers.js
```

answer/ 폴더에서 직접 집계(패턴별 JSON 사용):
```bash
python scripts/build_answers_from_folder.py --answer_dir answer --out_js data/answers.js --out_counts data/counts.json
```

실행 후 `data/answers.js`가 갱신되고, 게임은 자동으로 새로운 사전을 사용합니다.

### 패턴 매칭 규칙
- 단어의 초성 문자열이 패턴의 접두로 시작하면 정답으로 인정됩니다.
  - 예: 패턴 `ㅇㄱ` → 단어 `아기(ㅇㄱㅇ)`, `우군(ㅇㄱㄴ)` 포함
- 초성 추출은 유니코드 음절에서 초성 인덱스를 구해 19자 초성 리스트에 매핑합니다.

### 파일 구조
- `data/answers.js`: `window.ANSWER_DICT`, `window.CHALLENGE_KEYS`를 정의
- `scripts/build_answers.py`: 사전 생성 스크립트
- `scripts/build_answers_hannanum.py`: KoNLPy Hannanum으로 코퍼스에서 명사 추출해 사전 생성
- `scripts/build_answers_kkma.py`: KoNLPy Kkma로 코퍼스에서 명사 추출해 대용량 사전 생성
- `scripts/build_answers_from_folder.py`: `answer/` 폴더의 패턴별 JSON을 모아 사전 생성
- `data/seeds.json`: 30개 패턴과 기본 시드 단어

## 🔤 KoNLPy/Hannanum로 대용량 사전 만들기

사전 품질을 높이기 위해 텍스트 코퍼스에서 명사 후보를 추출해 패턴별로 자동 분류할 수 있습니다.

### 설치
```bash
pip install konlpy
```
Windows라면 Java JDK 설치 후 환경변수(JAVA_HOME) 설정이 필요할 수 있습니다.

### 사용
```bash
python scripts/build_answers_hannanum.py --source data/corpus_ko.txt --seeds data/seeds.json --out data/answers.js
```
- `data/corpus_ko.txt`: 한국어 문장/문단이 줄 단위로 있는 파일
- `data/seeds.json`: 30개 패턴과 시드 단어(결과에 병합)
- 출력은 `data/answers.js`로 저장되며, 게임은 자동으로 최신 파일을 사용합니다.

## 🔤 KoNLPy/Kkma로 대용량 사전 만들기 (권장)

Kkma는 명사 추출 품질이 좋아 대용량 생성에 유리합니다.

### 설치
```bash
pip install konlpy
```
Windows라면 Java JDK 설치 후 환경변수(JAVA_HOME) 설정이 필요할 수 있습니다.

### 사용
```bash
python scripts/build_answers_kkma.py --source data/corpus_ko.txt --seeds data/seeds.json --out data/answers.js
```
설명은 Hannanum 버전과 동일합니다.


## 📱 브라우저 지원

- Chrome (권장)
- Edge
- Safari (제한적 지원)
- Firefox (제한적 지원)

## 🎨 주요 기능

- **멀티플레이어 지원**: 최대 4명까지 동시 플레이 가능
- **실시간 음성인식**: Web Speech API를 활용한 실시간 음성 인식
- **초성 매칭**: 한글 유니코드를 활용한 정확한 초성 추출
- **직관적인 UI**: 깔끔하고 현대적인 디자인
- **반응형 디자인**: 모바일과 데스크톱 모두 지원
- **애니메이션 효과**: 정답 시 시각적 피드백
- **타이머 시스템**: 실시간 시간 표시
- **스코어 시스템**: 실시간 점수 업데이트
- **최종 순위**: 게임 종료 시 순위와 메달 표시

## 🔧 향후 개선 계획

- [x] 다중 플레이어 지원 (완료!)
- [ ] 더 많은 한국어 단어 사전 추가
- [ ] 난이도 조절 기능
- [ ] 성취 시스템
- [ ] 리더보드 기능
- [ ] 배경음악 및 효과음
- [ ] 게임 모드 다양화

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

버그 리포트나 기능 제안은 언제든 환영합니다!

