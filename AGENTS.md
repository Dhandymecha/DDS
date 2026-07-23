# DDS 저장소 작업 지침

## 저장소 목적

이 저장소의 `Codex Plugins/`는 단디메카 공용 Codex 플러그인과 문서·견적 템플릿을 배포·관리하기 위한 팀 마켓플레이스이다.

현재 등록된 플러그인은 다음과 같다.

- `dhandy-word-template`: Codex에 `artifact-template-word` 스킬을 제공한다. URS, 기술보고서, 설계 사양서, 수행계획서 및 검증·인수 문서를 단디메카 Word 표준 포맷으로 작성한다.
- `dhandy-excel-quote-template`: Codex에 `artifact-template-dhandy` 스킬을 제공한다. 견적서와 상세 견적을 단디메카 Excel 견적서 표준 포맷으로 작성하고 고객 제출용 PDF를 함께 만든다.

## 작업 시작 시 확인할 파일

1. `Codex Plugins/README.md`: 설치, 공유 및 업데이트 절차
2. `Codex Plugins/.agents/plugins/marketplace.json`: 팀 마켓플레이스 목록
3. 각 플러그인의 `.codex-plugin/plugin.json`: 플러그인 이름과 버전
4. 각 플러그인의 `skills/*/SKILL.md`: 산출물 생성 절차
5. 각 스킬의 `assets/`: 기준 원본, 미리보기 및 관련 규격

## 기준 파일

### Word 표준 포맷

- 기준본: `Codex Plugins/plugins/dhandy-word-template/skills/artifact-template-word/assets/reference-v1.11.docx`
- 템플릿 미리보기: `Codex Plugins/plugins/dhandy-word-template/assets/template-preview.png`
- 스킬 미리보기: `Codex Plugins/plugins/dhandy-word-template/skills/artifact-template-word/assets/preview.png`
- 스타일 가이드: `Codex Plugins/plugins/dhandy-word-template/skills/artifact-template-word/assets/style-guide.md`

기준 DOCX에는 외부 전달 시 글꼴 문제가 발생하지 않도록 글꼴이 포함되어 있다. 템플릿을 수정할 때 글꼴 포함 상태를 유지한다.

Word의 의미 기반 데이터 표는 머리행과 본문 모두 9 pt로 유지한다. ID·코드·문서번호·개정번호 열은 가장 긴 값이 한 줄에 들어오도록 고정 폭을 확보하고 줄바꿈 금지 속성을 적용한다. `URS-01-001`·`OI-001` 같은 추적 ID 열은 최소 1800 DXA를 사용한다.

Word 기준본이나 산출물을 수정한 뒤 다음 검사를 반드시 통과시킨다.

`python "Codex Plugins/plugins/dhandy-word-template/skills/artifact-template-word/scripts/qa_word_template.py" "<검사할 DOCX>" --require-id-column`

ID 열이 없는 일반 문서는 `--require-id-column`만 제외한다. 구조 검사 통과 후 전 페이지를 렌더링해 표의 잘림, ID 줄바꿈, 겹침과 비정상 페이지 나눔을 시각적으로 확인한다.

### Excel 견적서 표준 포맷

- 기준본: `Codex Plugins/plugins/dhandy-excel-quote-template/skills/artifact-template-dhandy/assets/reference.xlsx`
- 기준 PDF: `Codex Plugins/plugins/dhandy-excel-quote-template/skills/artifact-template-dhandy/assets/reference.native.pdf`
- 템플릿 미리보기: `Codex Plugins/plugins/dhandy-excel-quote-template/assets/template-preview.png`
- 스킬 미리보기: `Codex Plugins/plugins/dhandy-excel-quote-template/skills/artifact-template-dhandy/assets/preview.png`

기준 XLSX의 수식, 인쇄 영역, 시트 구조, 도형, 이미지 및 내부 분석 영역 제외 규칙을 유지한다. Excel 파일은 글꼴 파일을 내장하지 않으므로 편집 컴퓨터에 Pretendard 설치를 권장한다.

## 다른 사용자에게 배포되는 방식

GitHub 저장소 초대와 Codex의 GitHub 계정 연결만으로 플러그인이 자동 설치되지는 않는다. 사용자는 다음 절차를 완료해야 한다.

1. `Dhandymecha/DDS` 저장소 초대를 수락한다.
2. 저장소를 로컬 컴퓨터에 복제한다.
3. `Codex Plugins` 폴더를 마켓플레이스로 등록한다.
   - `codex plugin marketplace add "<DDS 저장소 경로>/Codex Plugins"`
4. ChatGPT/Codex 데스크톱 앱을 재시작한다.
5. Plugins에서 `단디메카 Codex Plugins`를 선택하고 필요한 플러그인을 설치·활성화한다.
6. 새 작업에서 Word는 `$artifact-template-word`, Excel 견적서는 `$artifact-template-dhandy`를 사용한다.

## 업데이트 흐름

관리자가 템플릿을 변경할 때:

1. 기준 원본과 필요한 미리보기·스타일 가이드·스킬 지침을 함께 수정한다.
2. 해당 `.codex-plugin/plugin.json`의 버전을 올린다.
3. `Codex Plugins/README.md`의 현재 버전을 동일하게 맞춘다.
4. 산출물 렌더링, 플러그인 구조와 마켓플레이스 경로를 검증한다.
5. 변경 사유가 분명한 커밋으로 GitHub에 반영한다.

사용자가 최신 버전을 받을 때:

1. 로컬 DDS 저장소에서 `git pull`을 실행한다.
2. ChatGPT/Codex 데스크톱 앱을 재시작한다.
3. Plugins에서 업데이트하거나, 반영되지 않으면 플러그인을 재설치한다.
4. 이미 열려 있던 작업이 아니라 새 작업에서 스킬을 사용한다.

## 변경 원칙

- 사용자가 명시하지 않은 기존 플러그인이나 템플릿을 삭제하지 않는다.
- `marketplace.json`의 각 `source.path`는 `./plugins/<plugin-name>` 형식을 유지한다.
- 플러그인 폴더명, 매니페스트의 `name`, 마켓플레이스의 `name`을 서로 일치시킨다.
- Word 원본의 표지, 스타일, 문단 계층, 표·그림, 강조박스 및 상태 색상 규칙을 임의로 단순화하지 않는다.
- Word 데이터 표 글꼴을 9 pt가 아닌 크기로 바꾸거나 ID류 열에 줄바꿈을 허용하지 않는다.
- Excel 원본의 수식, 숫자 형식, 도형, 시트 구성, 인쇄 범위 및 고객용 PDF 제외 규칙을 임의로 변경하지 않는다.
- Excel 고객용 PDF는 네이티브 Excel PDF와 최종 PDF의 선 개수와 물리 두께를 페이지별로 비교한다. 전체 화면 확대 과정에서 선이 굵어지지 않도록 보정하며 대응 선의 오차는 `0.02 pt` 이내로 유지한다.
- 템플릿 변경 후 미리보기와 스킬 지침이 실제 기준본과 일치하는지 확인한다.
- 문서 작성 요청에서는 최신 기준 원본을 복제해 사용하며 기준본 자체를 결과 문서로 덮어쓰지 않는다.
- 삭제, 구조 변경 또는 호환성에 영향을 주는 작업은 사용자 요청 범위인지 먼저 확인한다.

## 완료 기준

- JSON 파일이 정상적으로 파싱된다.
- 마켓플레이스 경로에서 등록된 플러그인 폴더를 모두 찾을 수 있다.
- 각 플러그인에서 대응하는 스킬을 발견할 수 있다.
- Word 기준본은 열리고 내장 글꼴과 Word 스타일이 유지되며, 데이터 표 9 pt와 ID류 한 줄 표시 자동 QA 및 전 페이지 렌더 검사를 통과한다.
- Excel 기준본은 열리고 수식 오류가 없으며 시트 1·2만 고객용 PDF에 포함된다. 최종 PDF의 선 두께 검증도 통과해야 한다.
- 작업 트리가 의도한 파일만 변경한 상태이며 원격 저장소에 반영된다.
