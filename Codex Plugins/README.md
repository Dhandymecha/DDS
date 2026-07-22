# 단디메카 Codex Plugins

단디메카에서 공용으로 사용하는 Codex 플러그인과 문서 템플릿을 한곳에서 관리합니다.

## 등록된 플러그인

| 플러그인 | 용도 | 현재 버전 |
|---|---|---|
| `dhandy-word-template` | 단디메카 Word 표준 포맷 기반 문서 생성 | `1.0.0+codex.20260722162128` |

## 디렉터리 구조

```text
DDS/
├─ .agents/plugins/marketplace.json
└─ Codex Plugins/
   └─ plugins/
      └─ dhandy-word-template/
         ├─ .codex-plugin/plugin.json
         ├─ README.md
         └─ skills/artifact-template-word/
```

## 설치 및 공유

1. 이 저장소를 내려받거나 복제합니다.
2. Codex에서 저장소 루트의 `.agents/plugins/marketplace.json`을 마켓플레이스 파일로 등록합니다.
3. `dhandy-word-template` 플러그인을 설치합니다.

## 업데이트 관리 규칙

1. 원본 템플릿은 `plugins/dhandy-word-template/skills/artifact-template-word/assets/reference-v1.10.docx`에서 관리합니다.
2. 템플릿을 바꾸면 미리보기, 스타일 가이드, 스킬 지침도 함께 점검합니다.
3. `.codex-plugin/plugin.json`의 버전을 올리고, 위 표의 현재 버전도 동일하게 맞춥니다.
4. 이전 파일을 덮어쓰기 전에 Word 렌더링과 플러그인 검증을 완료합니다.
5. 변경 사유가 드러나는 커밋 메시지로 `main` 브랜치에 반영합니다.

파일명은 기존 문서와의 연결을 위해 유지하되, 큰 규격 변경 시 `reference-v1.11.docx`처럼 버전을 올립니다.
