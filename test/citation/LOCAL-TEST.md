# 로컬 hook 실제 발동 절차서 (LOCAL-TEST)
## frontmatter hook이 Claude Code 세션에서 진짜로 Write를 가로막는가

*용도: 컨테이너에서 끝난 "로직 검증" 다음 단계 — 실제 Claude Code에서 hook 발동 확인*
*환경 기준: Windows 네이티브 (macOS/Linux 명령 병기)*

---

## 0. 이 테스트가 확인하는 것 / 못 하는 것

- **확인:** Claude Code가 원고 파일을 Write/Edit 하는 순간, citation-verifier의
  PreToolUse hook이 끼어들어 `[FABRICATED]`가 든 쓰기를 *차단*하는가.
- **이미 끝난 것(컨테이너):** hook 스크립트의 결정 로직 — A 통과, B 차단,
  UNVERIFIED 단독 통과. (`test/citation/RESULTS.md`)
- **함정:** frontmatter hook은 **skill이 활성일 때만** 발동한다. 그래서 아래는
  3단으로 나눠 "스크립트 자체 → frontmatter 동적 → settings.json 폴백" 순으로
  *어디가* 문제인지 가른다.

---

## 1. 사전 점검 (5분)

### 1-1. Python 인터프리터 이름 확인 — 가장 흔한 실패 지점

frontmatter는 `command: python3`으로 돼 있다. **Windows에서는 보통 `python`
(또는 `py`)이고 `python3`이 없을 수 있다.**

```
# Windows (PowerShell 또는 cmd)
python --version
py --version
python3 --version
```
```
# macOS / Linux
python3 --version
```

- `python3`이 동작하면 → 그대로 둔다.
- Windows에서 `python`만 동작하면 → **SKILL.md frontmatter의 `command: "python3"`
  을 `command: "python"`으로 한 줄 수정**한다. (args 경로는 그대로)

### 1-2. 프로젝트 루트 정하기

`${CLAUDE_PROJECT_DIR}`은 Claude Code를 실행하는 프로젝트 폴더다. 그 안에
`.claude/skills/...`가 있어야 args 경로가 맞는다. 작업 폴더를 하나 정한다.
예: `C:\work\ph-manuscript-harness` (Windows) / `~/work/ph-manuscript-harness` (mac).

---

## 2. 설치 — skill을 프로젝트의 `.claude/skills/`에 배치

frontmatter args가 가리키는 경로가 정확히 이것이다:
`${CLAUDE_PROJECT_DIR}/.claude/skills/citation-verifier/scripts/block_fabricated.py`

그러니 **디렉토리 이름(citation-verifier)과 위치를 그대로** 맞춰야 한다.

```
# 프로젝트 루트에서 (Windows PowerShell)
mkdir .claude\skills\citation-verifier\scripts
# 그리고 SKILL.md 와 scripts\block_fabricated.py 를 그 안에 복사
```
```
# macOS / Linux
mkdir -p .claude/skills/citation-verifier/scripts
cp SKILL.md .claude/skills/citation-verifier/
cp scripts/block_fabricated.py .claude/skills/citation-verifier/scripts/
```

배치 후 구조:
```
<프로젝트 루트>/
└── .claude/
    └── skills/
        └── citation-verifier/
            ├── SKILL.md                  (frontmatter에 hook 정의)
            └── scripts/
                └── block_fabricated.py
```

> 실행권한(chmod)은 필요 없다. hook은 exec form(`args`)이라 `python`이 스크립트를
> 인자로 받아 직접 실행한다. Windows에서도 동일.

테스트 원고도 프로젝트 어딘가에 둔다(예: 루트에 복사):
`manuscript_A_clean.md`, `manuscript_B_seeded.md`.

---

## 3. 단계 1 — 스크립트 자체가 도는지 (skill·Claude 무관)

가장 먼저, hook 스크립트가 이 머신에서 실행되는지부터 확인한다. 이게 안 되면
나머지는 볼 것도 없다.

```
# Windows (PowerShell) — 프로젝트 루트에서
Get-Content manuscript_B_seeded.md -Raw | python -c "import sys,json; print(json.dumps({'tool_name':'Write','tool_input':{'file_path':'m.md','content':sys.stdin.read()}}))" | python .claude\skills\citation-verifier\scripts\block_fabricated.py; echo "exit=$LASTEXITCODE"
```
```
# macOS / Linux
python3 -c "import json;print(json.dumps({'tool_name':'Write','tool_input':{'file_path':'m.md','content':open('manuscript_B_seeded.md').read()}}))" | python3 .claude/skills/citation-verifier/scripts/block_fabricated.py; echo "exit=$?"
```

- **기대:** `BLOCKED ...` 메시지 + `exit=2`. (A 원고로 하면 `exit=0`, 메시지 없음.)
- 안 되면 → Python 이름(1-1)이나 경로 문제. 여기서 멈추고 고친다.

---

## 4. 단계 2 — frontmatter hook이 실제로 발동하는지 (핵심)

### 4-1. 등록 확인 (정적)

1. 프로젝트 루트에서 Claude Code를 (재)시작한다.
2. `/hooks` 를 입력 → PreToolUse 항목에 citation-verifier의 hook이 보이는지 본다.
   - 보이면 → frontmatter가 제대로 읽혔다.
   - 안 보이면 → skill이 로드 안 됐거나 YAML 문제. (5장 트러블슈팅)

### 4-2. 발동 확인 (동적) — skill을 활성화한 채 Write 시키기

frontmatter hook은 skill이 활성일 때만 걸리므로, citation-verifier를 끌어오는
맥락으로 요청한다. Claude Code 세션에서:

```
citation-verifier 규율로 manuscript_B_seeded.md 의 내용을
manuscript_final.md 파일로 저장해줘.
```

- **기대:** Claude가 Write를 시도하는 순간 hook이 차단하고, `[FABRICATED]` 줄을
  지목한 메시지가 뜬다. 파일은 *생성되지 않는다*.
- A 원고(`manuscript_A_clean.md`)로 같은 요청 → 차단 없이 저장된다.

> 팁: skill이 확실히 활성화되도록, 첫 요청에서 "citation-verifier"를 명시하거나
> 인용 검증 맥락을 분명히 준다. 그냥 "이 파일 저장해줘"만 하면 skill이 로드되지
> 않아 hook이 안 걸릴 수 있다 — 이건 버그가 아니라 frontmatter hook의 활성-범위
> 특성이다(NOTES.md의 "활성 시만 발동" 한계와 같은 것).

---

## 5. 단계 3 — 폴백: settings.json으로 "항상 발동" 분리 확인

단계 2에서 차단이 안 일어났을 때, 원인이 **(a) skill이 안 켜진 것**인지
**(b) hook 메커니즘 자체가 안 도는 것**인지 가른다. 같은 hook을
`.claude/settings.json`(프로젝트 전역, skill 활성과 무관하게 항상 발동)에 임시
등록한다.

`<프로젝트 루트>/.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/skills/citation-verifier/scripts/block_fabricated.py"],
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```
(`python3`이 되는 환경이면 `"command": "python3"`)

재시작 후 다시 4-2를 시도한다.

- 이제 차단되면 → 메커니즘은 정상, 단계 2의 문제는 **skill 활성화**였다. 이게
  바로 NOTES.md가 말한 "frontmatter는 활성 시만, settings.json은 항상"의 실측이다.
  → 실전에서 항상-발동이 필요하면 이 settings.json 등록을 **하이브리드 안전망**
  으로 유지한다(단일 출처 약화는 감수).
- 그래도 차단 안 되면 → 경로/`CLAUDE_PROJECT_DIR`/Python 문제. 단계 1로 돌아간다.

> 테스트가 끝나면, frontmatter-only 설계로 돌아가려면 이 settings.json hook을
> 지운다(또는 하이브리드로 남긴다 — 결정은 NOTES.md 참조).

---

## 6. 트러블슈팅 빠른 표

| 증상 | 원인 후보 | 조치 |
|------|-----------|------|
| 단계 1에서 `python: command not found` | 인터프리터 이름 | `python`/`py`/`python3` 중 되는 것으로. frontmatter `command`도 맞춤 |
| 단계 1은 차단되는데 `/hooks`에 안 보임 | skill 미로드 / YAML | SKILL.md가 `.claude/skills/citation-verifier/`에 있는지, frontmatter YAML 유효한지 |
| `/hooks`엔 보이는데 4-2가 차단 안 함 | skill 비활성 | 요청에 citation-verifier 명시 → 그래도 안 되면 단계 3(settings.json) |
| 경로가 빈 문자열로 치환됨 | `${CLAUDE_PROJECT_DIR}` 미해결 | Claude Code를 *프로젝트 루트에서* 실행했는지 확인. 경로를 절대경로로 임시 치환해 테스트 |
| 정상 원고(A)도 차단됨 | 스크립트 경로 오타로 다른 파일 실행 | args 경로 재확인. 단계 1로 스크립트 단독 재현 |
| SKILL.md 편집 시 자기 차단 | (정상) guard가 SKILL.md·`.claude/` 제외 | 의도된 동작. 원고 파일명은 SKILL.md가 아니어야 함 |

---

## 7. 통과 기준 (이 테스트의 합격선)

- [ ] 단계 1: 스크립트 단독 — B 차단(exit 2), A 통과(exit 0)
- [ ] 단계 2: `/hooks`에 citation-verifier hook 등록 확인
- [ ] 단계 2: skill 활성 상태에서 B 원고 Write → 차단, 파일 미생성
- [ ] 단계 2: A 원고 Write → 정상 저장
- [ ] (선택) UNVERIFIED-only 원고 → 차단 안 됨(정밀강제 실측)

위 네 칸이 차면 "frontmatter hook이 실제 세션에서 발동한다"가 증명된다 —
발표 4박("강제가 런타임에 박힌다")을 실물로 말할 근거가 생긴다.
