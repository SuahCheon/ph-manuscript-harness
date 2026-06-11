# 로컬 발동 절차서 (LOCAL-TEST) — reporting-guidelines
## frontmatter PostToolUse hook이 Claude Code 세션에서 진짜로 저장 직후 점검 보고를 띄우는가

*용도: 컨테이너에서 끝난 "결정 로직 검증"(RESULTS.md) 다음 단계 — 실제 Claude Code에서 hook 발동 확인*
*환경 기준: Windows 네이티브 (macOS/Linux 명령 병기)*

---

## 0. 이 테스트가 확인하는 것 / 못 하는 것

- **확인:** Claude Code가 원고 파일을 Write/Edit 하는 순간, reporting-guidelines의
  **PostToolUse** hook이 *저장 직후* 끼어들어, 누락/미스탬프/PARTIAL 항목을 보고하는가.
- **이미 끝난 것(컨테이너, RESULTS.md):** hook 스크립트의 결정 로직 — 완전 원고 통과(0),
  불완전 원고 보고(2), 미선언·미지원지침·self-guard·깨진 JSON 통과.
- **citation과의 결정적 차이:** citation은 PreToolUse·deny라 *파일 생성을 막는다.*
  reporting은 **PostToolUse·annotate** — 저장은 *항상 일어나고*, 그 직후 점검 보고가
  피드백으로 뜬다. **"파일이 안 막히네"는 실패가 아니라 설계다**(위험도 비례, 한 칸
  약한 강제). 합격 신호는 "차단"이 아니라 "저장 + 보고".

---

## 1. 사전 점검 (5분)

### 1-1. Python 인터프리터 이름 — 가장 흔한 실패 지점

frontmatter는 `command: python`으로 돼 있다(이 레포의 citation-verifier와 동일).
이 머신에서 `python`이 도는지 확인한다.

```
# Windows (PowerShell 또는 cmd)
python --version
```
```
# macOS / Linux — 보통 python3
python3 --version
```

- `python`이 동작하면 → 그대로 둔다.
- macOS/Linux처럼 `python3`만 동작하면 → **SKILL.md frontmatter의 `command: "python"`
  을 `command: "python3"`으로 한 줄 수정**한다(args 경로는 그대로). citation-verifier도
  같이 맞춘다.

### 1-2. 프로젝트 루트

`${CLAUDE_PROJECT_DIR}`은 Claude Code를 실행하는 프로젝트 폴더다. 그 안에
`.claude/skills/reporting-guidelines/...`가 있어야 args 경로가 맞는다.
이 레포에서는 `C:\ph-manuscript-harness`가 곧 프로젝트 루트다.

---

## 2. 설치 확인 — 이미 배치돼 있어야 함

frontmatter args가 가리키는 경로:
`${CLAUDE_PROJECT_DIR}/.claude/skills/reporting-guidelines/scripts/post_write_reporting_check.py`

구조:
```
C:\ph-manuscript-harness\
└── .claude\
    ├── settings.local.json            (Skill(reporting-guidelines) 허용 포함)
    └── skills\
        └── reporting-guidelines\
            ├── SKILL.md                (frontmatter에 PostToolUse hook 정의)
            └── scripts\
                └── post_write_reporting_check.py
```

테스트 원고는 `test\reporting\`에 있다:
`manuscript_R_complete.md`(27/27 PRESENT), `manuscript_R_incomplete.md`(누락 섞임).

> 실행권한(chmod)은 필요 없다. hook은 exec form(`args`)이라 `python`이 스크립트를
> 인자로 받아 직접 실행한다. Windows에서도 동일.

---

## 3. 단계 1 — 스크립트 자체가 도는지 (skill·Claude 무관)

가장 먼저, hook 스크립트가 이 머신에서 결정 로직대로 도는지 확인한다.

> **Windows 주의 — PowerShell 5.1 native 파이프 금지.** `python | python`처럼 외부
> 프로그램끼리 PS로 파이프를 이으면 PS 5.1이 중간에서 UTF-8 BOM을 끼워넣고 바이트를
> 손상시킨다(입력측은 cp949로도 깨짐). 이 손상은 hook이 아니라 PS의 파이프 버그다.
> hook은 이미 stdin을 `utf-8-sig`로 읽어 BOM을 흡수하도록 하드닝돼 있지만, 입력측
> cp949 손상까지 막으려면 **아래 둘 중 하나**(파이프 회피)를 쓴다.

**A. Git Bash (POSIX 파이프 — 가장 깔끔, 컨테이너에서 exit=2 확인됨)**
```bash
# 불완전 원고 → REPORTING AUDIT 보고 + exit=2 기대
cat test/reporting/manuscript_R_incomplete.md | python -c "import sys,json; print(json.dumps({'tool_name':'Write','tool_input':{'file_path':'m.md','content':sys.stdin.read()}}))" | python .claude/skills/reporting-guidelines/scripts/post_write_reporting_check.py; echo "exit=$?"
```
```bash
# 완전 원고 → 보고 없음 + exit=0 기대
cat test/reporting/manuscript_R_complete.md | python -c "import sys,json; print(json.dumps({'tool_name':'Write','tool_input':{'file_path':'m.md','content':sys.stdin.read()}}))" | python .claude/skills/reporting-guidelines/scripts/post_write_reporting_check.py; echo "exit=$?"
```

**B. PowerShell — 파이프 없는 단일 프로세스 (PS 5.1 인코딩 버그 원천 회피)**
```powershell
# 불완전 → 보고 + exit= 2 기대
python -c "import json,subprocess,sys; c=open(r'test\reporting\manuscript_R_incomplete.md',encoding='utf-8').read(); p=subprocess.run(['python',r'.claude\skills\reporting-guidelines\scripts\post_write_reporting_check.py'],input=json.dumps({'tool_input':{'file_path':'m.md','content':c}}).encode('utf-8'),capture_output=True); sys.stderr.buffer.write(p.stderr); print('exit=',p.returncode)"
```
(완전 원고는 파일명만 `manuscript_R_complete.md`로 바꾼다 → 보고 없음 + `exit= 0`.)

- **기대:** 불완전 = `REPORTING AUDIT ...` 보고 + exit 2. 완전 = 보고 없음 + exit 0.
- 안 되면 → Python 이름(1-1)이나 경로 문제. 여기서 멈추고 고친다.

---

## 4. 단계 2 — frontmatter hook이 실제로 발동하는지 (핵심)

### 4-1. 등록 확인 (정적)

1. 프로젝트 루트(`C:\ph-manuscript-harness`)에서 Claude Code를 (재)시작한다.
2. `/hooks` 입력 → **PostToolUse** 항목에 reporting-guidelines의 hook이 보이는지 본다.
   - 보이면 → frontmatter가 제대로 읽혔다.
   - 안 보이면 → skill 미로드 또는 YAML 문제. (6장 트러블슈팅)

### 4-2. 발동 확인 (동적) — skill을 활성화한 채 Write 시키기

frontmatter hook은 skill이 활성일 때만 걸리므로, reporting-guidelines를 끌어오는
맥락으로 요청한다. Claude Code 세션에서:

```
reporting-guidelines 규율로 test\reporting\manuscript_R_incomplete.md 의 내용을
ms_draft.md 로 저장해줘.
```

- **기대:** 파일 `ms_draft.md`가 **생성되고**, 저장 직후 점검 보고가 피드백으로 뜬다 —
  MISSING(14 Fairness, 17 Ethical approval), UNSTAMPED(19, 24), PARTIAL(13, 23).
- 완전 원고로 같은 요청 → 저장되고 보고 없음:
```
reporting-guidelines 규율로 test\reporting\manuscript_R_complete.md 의 내용을
ms_final.md 로 저장해줘.
```

> **다시 강조:** 두 경우 모두 *파일은 생성된다.* citation처럼 막히지 않는다. 차이는
> "보고가 뜨느냐"뿐이다. 저장을 막는 게 아니라 점검을 못 건너뛰게 하는 게 이 skill의
> 강제다.

> 팁: skill이 확실히 활성화되도록 첫 요청에서 "reporting-guidelines"를 명시하거나
> 보고지침 점검 맥락을 분명히 준다. 그냥 "저장해줘"만 하면 skill이 로드되지 않아 hook이
> 안 걸릴 수 있다 — 버그가 아니라 frontmatter hook의 활성-범위 특성이다.

---

## 5. 단계 3 — 폴백: settings.json으로 "항상 발동" 분리 확인

단계 2에서 보고가 안 떴을 때, 원인이 **(a) skill이 안 켜진 것**인지 **(b) hook 메커니즘
자체가 안 도는 것**인지 가른다. 같은 hook을 `.claude/settings.json`(프로젝트 전역,
skill 활성과 무관하게 항상 발동)에 임시 등록한다.

`<프로젝트 루트>/.claude/settings.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/skills/reporting-guidelines/scripts/post_write_reporting_check.py"],
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

- 이제 보고가 뜨면 → 메커니즘은 정상, 단계 2의 문제는 **skill 활성화**였다. 이게 곧
  NOTES.md가 말한 "frontmatter는 활성 시만, settings.json은 항상"의 실측이다.
  → 실전에서 항상-발동이 필요하면 이 settings.json 등록을 **하이브리드 안전망**으로
  유지한다(단일 출처 약화는 감수).
- 그래도 안 뜨면 → 경로/`CLAUDE_PROJECT_DIR`/Python 문제. 단계 1로 돌아간다.

> 테스트가 끝나면, frontmatter-only 설계로 돌아가려면 이 settings.json hook을 지운다
> (또는 하이브리드로 남긴다 — 결정은 NOTES.md 참조).

---

## 6. 트러블슈팅 빠른 표

| 증상 | 원인 후보 | 조치 |
|------|-----------|------|
| 단계 1 PS에서 보고 안 뜨고 깨진 글자 | PS 5.1 native 파이프 BOM/cp949 손상 | 단계 1의 **A(Git Bash)** 또는 **B(단일 프로세스)** 사용. `python \| python` 파이프 금지 |
| 단계 1에서 `python: command not found` | 인터프리터 이름 | `python`/`py`/`python3` 중 되는 것으로. frontmatter `command`도 맞춤 |
| 단계 1은 보고 뜨는데 `/hooks`에 안 보임 | skill 미로드 / YAML | SKILL.md가 `.claude/skills/reporting-guidelines/`에 있는지, frontmatter YAML 유효한지 |
| `/hooks`엔 보이는데 4-2가 보고 안 함 | skill 비활성 | 요청에 reporting-guidelines 명시 → 그래도 안 되면 단계 3(settings.json) |
| 파일이 차단됨 (생성 안 됨) | (비정상) reporting은 차단 안 함 | citation hook(PreToolUse)이 잘못 걸렸는지 확인. reporting은 PostToolUse라 저장을 막지 않음 |
| 경로가 빈 문자열로 치환됨 | `${CLAUDE_PROJECT_DIR}` 미해결 | Claude Code를 *프로젝트 루트에서* 실행했는지 확인 |
| 한글 원고에서 보고가 안 뜸/조용히 통과 | (해결됨) 과거 stdin cp949 디코딩 손상 | hook은 stdin을 `utf-8-sig`로 읽도록 하드닝됨. 그래도 이상하면 단계 1로 재현 |
| SKILL.md 편집 시 자기 점검 | (정상) guard가 SKILL.md·`.claude/` 제외 | 의도된 동작. 원고 파일명은 SKILL.md가 아니어야 함 |

---

## 7. 통과 기준 (이 테스트의 합격선)

- [ ] 단계 1: 스크립트 단독 — 불완전 보고(exit 2), 완전 무보고(exit 0)
- [ ] 단계 2: `/hooks`에 reporting-guidelines PostToolUse hook 등록 확인
- [ ] 단계 2: skill 활성 상태에서 불완전 원고 저장 → **파일 생성 + 누락 보고**
- [ ] 단계 2: 완전 원고 저장 → **파일 생성 + 보고 없음**
- [ ] (선택) 한글이 든 원고로도 보고가 정상 출력(하드닝 실측)

위 네 칸이 차면 "frontmatter PostToolUse hook이 실제 세션에서 발동해, 저장을 막지 않고
점검을 강제한다"가 증명된다 — 발표 4박의 reporting 절반(차단이 아니라 강제 점검)을
실물로 말할 근거가 생긴다. 결과는 `RESULTS.md`의 "라이브 발동" 칸에 채워 넣는다.
