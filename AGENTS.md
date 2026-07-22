# DDS 저장소 작업 지침

## 저장소 목적

이 저장소의 `Codex Plugins/`는 단디메카 공용 Codex 플러그인과 문서 템플릿을 배포·관리하기 위한 팀 마켓플레이스이다.

현재 등록된 `dhandy-word-template` 플러그인은 Codex에 `artifact-template-word` 스킬을 제공한다. 이 스킬의 목적은 URS, 기술보고서, 설계 사양서, 수행계획서 및 검증·인수 문서를 단디메카 Word 표준 포맷으로 일관되게 작성하는 것이다.

## 작업 시작 시 확인할 파일

1. `Codex Plugins/README.md`: 설치, 공유 및 업데이트 절차
2. `Codex Plugins/.agents/plugins/marketplace.json`: 팀 마켓플레이스 목록
3. `Codex Plugins/plugins/dhandy-word-template/.codex-plugin/plugin.json`: 플러그인 이름과 버전
4. `Codex Plugins/plugins/dhandy-word-template/skills/artifact-template-word/SKILL.md`: 문서 생성 절차
5. `Codex Plugins/plugins/dhandy-word-template/skills/artifact-template-word/assets/style-guide.md`: 문서 디자인 및 편집 규칙

## 기준 파일

- Word 템플릿 기준본: `Codex Plugins/plugins/dhandy-word-template/skills/artifact-template-word/assets/reference-v1.10.docx`
- 템플릿 미리보기: `Codex Plugins/plugins/dhandy-word-template/assets/template-preview.png`
- 스킬 미리보기: `Codex Plugins/plugins/dhandy-word-template/skills/artifact-template-word/assets/preview.png`

기준 DOCX에는 외부 전달 시 글꼴 문제가 발생하지 않도록 글꼴이 포함되어 있다. 템플릿을 수정할 때 글꼴 포함 상태를 유지한다.

## 다른 사용자에게 배포되는 방식

GitHub 저장소 초대와 Codex의 GitHub 계정 연결만으로 플러그인이 자동 설치되지는 않는다. 사용자는 다음 절차를 완료해야 한다.

1. `Dhandymecha/DDS` 저장소 초대를 수락한다.
2. 저장소를 로컬 컴퓨터에 복제한다.
3. `Codex Plugins` 폴더를 마켓플레이스로 등록한다.
   - `codex plugin marketplace add "<DDS 저장소 경로>/Codex Plugins"`
4. ChatGPT/Codex 데스크톱 앱을 재시작한다.
5. Plugins에서 `단디메카 Codex Plugins`를 선택하고 `dhandy-word-template`을 설치·활성화한다.
6. 새 작업에서 `$artifact-template-word`를 사용한다.

## 업데이트 흐름

관리자가 템플릿을 변경할 때:

1. 기준 DOCX와 필요한 미리보기·스타일 가이드·스킬 지침을 함께 수정한다.
2. `.codex-plugin/plugin.json`의 버전을 올린다.
3. `Codex Plugins/README.md`의 현재 버전을 동일하게 맞춘다.
4. Word 렌더링, 글꼴 포함 여부, 플러그인 구조와 마켓플레이스 경로를 검증한다.
5. 변경 사유가 분명한 커밋으로 GitHub에 반영한다.

사용자가 최신 버전을 받을 때:

1. 로컬 DDS 저장소에서 `git pull`을 실행한다.
2. ChatGPT/Codex 데스크톱 앱을 재시작한다.
3. Plugins에서 업데이트하거나, 반영되지 않으면 플러그인을 재설치한다.
4. 이미 열려 있던 작업이 아니라 새 작업에서 스킬을 사용한다.

## 변경 원칙

- 사용자가 명시하지 않은 기존 플러그인이나 템플릿을 삭제하지 않는다.
- `marketplace.json`의 `source.path`는 `./plugins/dhandy-word-template`을 유지한다.
- 플러그인 폴더명, 매니페스트의 `name`, 마켓플레이스의 `name`을 서로 일치시킨다.
- Word 원본의 표지, 스타일, 문단 계층, 표·그림, 강조박스 및 상태 색상 규칙을 임의로 단순화하지 않는다.
- 템플릿 변경 후 미리보기와 스타일 가이드가 실제 기준본과 일치하는지 확인한다.
- 문서 작성 요청에서는 최신 기준 DOCX를 복제해 사용하며 기준본 자체를 결과 문서로 덮어쓰지 않는다.
- 삭제, 구조 변경 또는 호환성에 영향을 주는 작업은 사용자 요청 범위인지 먼저 확인한다.

## 완료 기준

- JSON 파일이 정상적으로 파싱된다.
- 마켓플레이스 경로에서 플러그인 폴더를 찾을 수 있다.
- 플러그인에서 `artifact-template-word` 스킬을 발견할 수 있다.
- 기준 DOCX가 열리고 내장 글꼴과 Word 스타일이 유지된다.
- 작업 트리가 의도한 파일만 변경한 상태이며 원격 저장소에 반영된다.
