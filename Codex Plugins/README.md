# 단디메카 Codex Plugins

단디메카에서 공용으로 사용하는 Codex 플러그인과 문서·견적 템플릿을 한곳에서 관리합니다.

## 등록된 플러그인

| 플러그인 | 용도 | 호출 스킬 | 현재 버전 |
|---|---|---|---|
| `dhandy-word-template` | 단디메카 Word 표준 포맷 기반 문서 생성 | `$artifact-template-word` | `1.0.0+codex.20260722162128` |
| `dhandy-excel-quote-template` | 단디메카 Excel 견적서 표준 포맷 기반 견적서·PDF 생성 | `$artifact-template-dhandy` | `1.0.2+codex.20260723112504` |

## 디렉터리 구조

```text
DDS/
└─ Codex Plugins/
   ├─ .agents/plugins/marketplace.json
   └─ plugins/
      ├─ dhandy-word-template/
      │  ├─ .codex-plugin/plugin.json
      │  ├─ README.md
      │  └─ skills/artifact-template-word/
      └─ dhandy-excel-quote-template/
         ├─ .codex-plugin/plugin.json
         ├─ README.md
         └─ skills/artifact-template-dhandy/
```

## 사용자별 최초 설치

1. GitHub에서 `Dhandymecha/DDS` 저장소 초대를 수락합니다.
2. 이 저장소를 내려받거나 복제합니다.
3. Codex에서 `Codex Plugins` 폴더를 팀 마켓플레이스로 등록합니다.
   - 명령 예시: `codex plugin marketplace add "<DDS 저장소 경로>/Codex Plugins"`
   - 마켓플레이스 파일: `Codex Plugins/.agents/plugins/marketplace.json`
4. ChatGPT/Codex 데스크톱 앱을 재시작합니다.
5. Plugins에서 `단디메카 Codex Plugins`를 선택하고 필요한 플러그인을 설치·활성화합니다.
6. 새 작업에서 Word는 `$artifact-template-word`, Excel 견적서는 `$artifact-template-dhandy`를 사용합니다.

> GitHub 저장소 접근 권한이나 Codex의 GitHub 계정 연결만으로 플러그인이 자동 설치되는 것은 아닙니다. 마켓플레이스 등록과 플러그인 설치를 각각 완료해야 합니다.

## 사용자가 최신 버전을 받는 방법

1. 로컬 DDS 저장소에서 `git pull`을 실행합니다.
2. ChatGPT/Codex 데스크톱 앱을 재시작합니다.
3. Plugins에서 플러그인을 업데이트합니다.
4. 변경 내용이 반영되지 않으면 플러그인을 제거한 뒤 다시 설치합니다.
5. 새 Codex 작업에서 해당 스킬을 사용합니다.

## 업데이트 관리 규칙

1. Word 기준본은 `plugins/dhandy-word-template/skills/artifact-template-word/assets/reference-v1.10.docx`에서 관리합니다.
2. Excel 견적서 기준본은 `plugins/dhandy-excel-quote-template/skills/artifact-template-dhandy/assets/reference.xlsx`에서 관리합니다.
3. 템플릿을 바꾸면 미리보기, 관련 기준 파일 및 스킬 지침도 함께 점검합니다. Excel PDF는 네이티브 출력본과 최종 출력본의 선 개수를 대조하고, 일반선은 `0.50 pt`, 강조선은 최대 `0.72 pt`로 검증합니다.
4. 해당 `.codex-plugin/plugin.json`의 버전을 올리고, 위 표의 현재 버전도 동일하게 맞춥니다.
5. 원본을 덮어쓰기 전에 문서·스프레드시트 렌더링과 플러그인 검증을 완료합니다.
6. 변경 사유가 드러나는 커밋 메시지로 `main` 브랜치에 반영합니다.

파일명은 기존 산출물과의 연결을 위해 유지하되, 큰 규격 변경 시 기준 파일명과 버전을 함께 올립니다.

Codex 에이전트가 이 저장소를 수정할 때는 저장소 루트의 `AGENTS.md`를 기준으로 작업합니다.
