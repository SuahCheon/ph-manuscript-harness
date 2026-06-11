# Manuscript Harness

*📖 [English](README.md) · 한국어*

**공중보건 원고를 위한 마구(harness) — 거드는 도구가 아니라 강제하는 규율.**

Manuscript Harness는 원고를 *쓰는 그 순간* 규율에 옭아매는 두 개의 Claude Code
skill이다 — 인용을 검증하고, 보고지침(reporting guideline) 충족 여부를 점검하되,
"도와드릴까요"가 아니라 **hook으로 강제한다**. 마구는 서비스가 아니다. 그것은
말에 채우는 가죽끈(tack)이다 — 힘을 더해주는 게 아니라, 있는 힘이 한 방향으로만
나가도록 구속한다. 이 skill들은 논문을 더 빨리 써주지 않는다. 신중한 저자라면
당연히 돌렸을 점검을 *조용히 건너뛰는 것을 불가능하게* 만든다.

---

## 문제

AI와 함께 글을 쓰는 의학 저자는 이미 좋은 도구를 갖고 있다. PubMed 커넥터는 물어보면
답하고, 프로젝트는 이 논문이 무엇인지 기억한다. 그러나 **둘 다 실수를 *막지*는 않는다**:

- **커넥터는 요청할 때 검증하지, 쓰는 순간 검증하지 않는다.** PMID를 물어보면 찾아주지만,
  환각 인용이 초고에 박히는 *그 순간* 가로막지는 않는다.
- **프로젝트는 맥락을 저장하지, 체크리스트를 돌리지 않는다.** 연구가 무엇인지는 기억하나,
  "STROBE 12번 항목이 빠졌다"고 짚어주지는 않는다.
- **가장 까다로운 1/3의 공중보건 인용은 이 모두에게 보이지 않는다.** WHO·CDC·KDCA·MFDS
  가이드라인 — 공중보건 글쓰기가 기대는 회색문헌(grey literature) — 은 PMID도 DOI도 없어,
  Crossref·PubMed 기반 검사기로는 *애초에 안 잡힌다*.

유능한 인용 게이트는 이미 존재한다(ARS, medsci-skills — [`docs/CURATION.md`](docs/CURATION.md)
참조). 그러나 그것들은 DOI에 묶여 있고, 강제는 약하게 둔다(권고형이거나, 사용자가 직접
설치해야 하는 opt-in hook). Manuscript Harness는 검증을 *재발명*한 게 아니다. 기존 도구가
못 보는 출처로 검증을 *겨냥을 다시 맞추고*, *언제* 발동하는지를 단단하게 한 것이다.

---

## 왜 "마구(harness)"인가

업계는 harness 엔지니어링을 대부분 *견인(traction)* 에 써왔다 — 에이전트가 더 많이
스스로 하도록 떠받치는 비계. 반쪽인 *제동(braking)* — 에이전트를 책임의 궤도 안에
구속하는 비계 — 을 만드는 사람은 훨씬 적다. 엔진과 브레이크는 같은 설계 원칙을 쓸 수 없다.
브레이크를 엔진처럼 설계하면 차가 못 가고, 브레이크 없는 차를 시장에 내놓는 건 운전자의
목숨을 담보로 한 장난이다.

이 skill들은 브레이크다. 관통하는 설계 원칙은 **designed deference(설계된 양보)** 다:
*입증되게 틀렸거나 명백히 빠진 것만* 막거나 표시하고, 진짜 판단은 차단이 아니라 라벨링으로
사람에게 남긴다. 아래의 모델이 똑똑해질수록 제동 harness는 *얇아지는 게 아니라 더 단단해져야*
한다 — 똑똑한 모델일수록 더 그럴듯한 환각 인용을 만들고, 그것은 잡기가 더 어렵지 더 쉽지 않다.

---

## 두 규율, 두 강제 강도

이 묶음은 두 skill이며, **실패가 얼마나 회복 가능한가**에 따라 강제 강도를 달리한다.

| | [`citation-verifier`](.claude/skills/citation-verifier/SKILL.md) | [`reporting-guidelines`](.claude/skills/reporting-guidelines/SKILL.md) |
|---|---|---|
| 막는 실패 | 조작된 인용 — **회복 불가**, 닿는 순간 신뢰가 깨짐 | 보고 항목 누락 — **회복 가능**, 여러 번의 편집으로 채워짐 |
| hook 시점 | `PreToolUse` (쓰기 *전*) | `PostToolUse` (저장 *후*) |
| 결정 | **deny** — 입증되게 틀린 인용은 원고에 못 들어옴 | **annotate** — 저장은 항상 유지, 누락만 표면화 |
| 발동 조건 | 본문의 `[FABRICATED]` 라벨 | `PRESENT`로 찍히지 않은 필수 체크리스트 항목 |
| 분업 | Claude가 업스트림에서 검증(PubMed MCP)하고 라벨을 박음; hook은 라벨만 읽어 강제 | Claude가 업스트림에서 체크리스트를 대조해 항목을 찍음; hook은 찍힌 것을 읽어 누락을 보고 |

이 비대칭이 곧 주제다: harness는 획일적으로 막지 않는다. **브레이크의 강도를 실패의
비용에 맞춘다.**

### citation-verifier — 갈래로 나누고, 라벨 붙이고, 입증된 가짜만 막는다

모든 인용을 **출처 종류**에 따라 세 갈래로 나눈다. 공중보건 인용 위험은 출처가 어디서
왔느냐가 좌우하기 때문이다:

- **갈래 A — 영어권 학술** → PubMed로 검증.
- **갈래 B — 한국 의학**(KoreaMed / KMbase / RISS) → 태깅(DB 스크래핑은 v1 범위 밖).
- **갈래 C — 회색문헌**(WHO / CDC / KDCA / MFDS) → PMID·DOI가 없음. 발간 기관을 기록하며,
  색인에 안 잡히는 것이 *정상*이다.

각 인용은 정확히 하나의 라벨을 달고, 그중 하나만 차단한다:

| 라벨 | 뜻 | 결정 |
|------|----|------|
| `[PMID-VERIFIED]` | PubMed에서 찾았고 서지정보 일치 | allow + 라벨 강제 |
| `[KOREAMED]` | 한국 DB에 매칭/태깅 | allow + 라벨 강제 |
| `[GREY-LIT-WHO/CDC/KDCA/MFDS]` | 회색문헌, 발간 기관 기록 | allow + 라벨 강제 |
| `[UNVERIFIED]` | 조회가 *완료되지 못함*(API 장애·타임아웃) | allow + 강한 라벨 |
| `[FABRICATED]` | 조회가 *완료됐고 틀림이 입증됨*(없는 PMID, 또는 모순되는 서지) | **deny** |

좁힌 칼날이 핵심이다. `[UNVERIFIED]` — "확인 불능" — 은 차단하지 **않는다**. 장애는
조작의 증거가 아니기 때문이다. `[FABRICATED]` — 확인했고 부재함 — 만 막는다. 가장 센
강제 지점(PreToolUse·deny·동봉)에 서면서도, 무차별 차단형 게이트보다 거짓양성 비용을
한 칸 낮춘다.

### reporting-guidelines — 하나의 체크리스트로 라우팅하고, 모든 항목을 찍는다

연구 설계가 하나의 EQUATOR 지침을 고르고, 원고는 그 지침의 전 항목에 대해 점검된다:

| 연구 설계 | 지침 (v1) | 항목 수 |
|-----------|-----------|:------:|
| 관찰연구(코호트·환자대조군·단면·감시) | STROBE | 22 |
| 무작위 대조 임상시험 | CONSORT 2010 | 25 |
| 체계적 문헌고찰 / 메타분석 | PRISMA 2020 | 27 |
| 진단·예후 예측모델(ML/AI 포함) | TRIPOD+AI 2024 | 27 |

Claude가 적용 지침을 선언하고, 필수 항목마다 `PRESENT` / `PARTIAL` / `MISSING`을
HTML 주석 마커로 찍는다. 저장 시 hook이 선언된 지침의 항목 명단을 읽어, `MISSING`·`PARTIAL`,
**그리고 한 번도 안 찍힌 항목**을 모두 보고한다 — 안 찍힌 항목은 *조용히 건너뛴 점검*이므로,
원고의 완전성뿐 아니라 *점검 자체*의 완전성을 강제한다. 저장은 결코 막지 않는다. 보고가 곧
강제다.

지침은 **이 하나의 skill 라우팅 틀에 더해서** 늘린다(STARD·RECORD·SPIRIT이 다음 자리). 지침마다
skill을 쪼개지 않는다 — medsci의 32개 지침 `check-reporting` 구조에서 빌린 방식이다.

---

## 실제로 발동한다

두 hook 모두 단위 테스트만이 아니라 **실제 Claude Code 세션에서** 발동을 확인했다.
(결정 로직·라이브 발동 기록: [`test/citation/RESULTS.md`](test/citation/RESULTS.md),
[`test/reporting/RESULTS.md`](test/reporting/RESULTS.md); 절차는 각 폴더의 `LOCAL-TEST.md`.)

- **citation-verifier:** `[FABRICATED]` 인용 두 건을 심은 원고를 저장하라고 하자,
  Claude Code의 `PreToolUse` hook이 **쓰기를 차단**하고 문제 줄을 지목했다 — 파일은
  생성되지 않았다. 정상 원고는 **그대로 저장**됐다. 결함이 `[UNVERIFIED]` ×3뿐인 원고도
  **통과**했다 — 칼날은 조작에만 머문다.
- **reporting-guidelines:** 불완전한 원고를 저장하라고 하자, `PostToolUse` hook은 파일을
  **저장**시킨 뒤 정확한 누락(`MISSING 14·17 / UNSTAMPED 19·24 / PARTIAL 13·23`)을
  표면화했다. 완전한 원고는 **보고 없이 저장**됐다.

대조가 곧 증거다: 두 브레이크는 *강도가 다르고* 둘 다 스스로 발동한다. citation-verifier가
차단했을 때, Claude는 인용을 임의로 고치지 않고 사람에게 세 선택지(수정 / 재분류 / override)를
제시했다. 양보(deference)는 hook뿐 아니라 모델의 행동에서도 나타난다.

---

## 왜 MCP가 아니라 git인가

합당한 질문이다 — 왜 MCP 서버가 아니라 git 디렉토리로 배포하나? **강제는 MCP로 나를 수
없기 때문이다.**

- MCP는 *검증 로직*("무엇을 검사하나")은 담을 수 있다. 도구는 호출되면 답한다.
- MCP는 *강제 지점*("언제 막나")은 담을 수 없다. hook은 쓰기 행위 자체에 끼어든다 —
  호출되는 게 아니라 런타임에 박히는 것이다.

harness를 MCP로 싸는 순간 강제가 빠져나가고, 남는 건 *호출하기를 기억해야 하는 도구* —
바로 이 프로젝트가 대체하려는 약한 자세다. 그래서 규율(`SKILL.md`)과 그 강제(같은
frontmatter·디렉토리에 동봉된 hook)는 하나의 git 배포 단위로 함께 움직인다. Claude Code
*플러그인* skill이 hook 정의를 허용받지 못하는 것도 같은 이유다 — 강제는 설계상 런타임에
묶인다.

> **MCP로 배포 안 되는 것은 한계가 아니라 증거다.** 호출형 서비스로 다시 포장될 수 있는
> 도구는 애초에 강제하고 있던 게 아니다.

이식 가능한 Agent Skills 표준이 *규율*은 런타임을 넘어 나르되 *hook*은 런타임 종속으로
남기는 것도 이 때문이다 — 규칙은 옮겨지고, 강제는 박힌다.

---

## 설치

[Claude Code](https://code.claude.com)와 Python 3(표준 라이브러리만 — 외부 패키지 없음)이
필요하다.

1. 레포를 clone해 그대로 프로젝트 루트로 쓰거나, 두 skill을 기존 프로젝트로 복사한다:
   `git clone https://github.com/SuahCheon/ph-manuscript-harness` — skill은 이미
   `.claude/skills/` 아래에 있다(`citation-verifier`, `reporting-guidelines`). 다른
   프로젝트에 넣으려면 이 두 디렉토리를 그 프로젝트의 `.claude/skills/`로 복사한다.
2. **프로젝트 루트에서** Claude Code를 시작한다(hook이 `${CLAUDE_PROJECT_DIR}`로 스크립트를
   찾는다).
3. 인터프리터 이름: hook은 `python`을 부른다. macOS / Linux에서는 frontmatter `command`를
   `python3`으로 바꾼다.
4. 첫 사용 시 skill 허용(Claude Code가 물어봄), 또는 로컬 설정에 `Skill(citation-verifier)`·
   `Skill(reporting-guidelines)` 추가. `settings.local.json`은 머신 종속이라 git 제외되며,
   hook 자체는 각 `SKILL.md` frontmatter에 실려 레포와 함께 배포된다.
5. `test/citation/`·`test/reporting/`의 `LOCAL-TEST.md` 절차로 검증한다.

hook은 stdin을 UTF-8(`utf-8-sig`)로 읽으므로, 비-ASCII(예: 한글) 원고 내용이나 Windows
PowerShell 파이프가 끼워넣는 BOM이 있어도 조용히 통과(fail-open)하지 않는다.

---

## 범위와 정직한 경계 (v1)

**범위 안:** 세 갈래 인용 라우팅 + PubMed 검증 + 작성 시점 `[FABRICATED]` 차단; 네 지침
보고 점검(STROBE / CONSORT / PRISMA / TRIPOD+AI) + 저장 시점 누락 보고; 둘 다 동봉된
Claude Code hook으로 강제.

**범위 밖(의도적):**

- 한국 DB·회색문헌 사이트 스크래핑 — 갈래 B/C는 태깅만. 라벨은 *어떤 종류*의 출처인지와
  사람이 확인해야 함을 기록한다.
- 추가 보고지침(STARD·RECORD·SPIRIT)·편향위험(RoB) 도구 — 나중에 같은 라우팅 틀에 추가.
- 항목 수준의 적절성 판단: 보고 hook은 찍힌 마커를 읽는다. 어떤 절이 항목을 실제로 충족하는지는
  hook이 아니라 Claude의 업스트림 판단이다.
- 주장–인용 정합("이 PMID가 *이 문장*을 뒷받침하는가") — ARS에서 빌린 강력한 v2 후보.

---

## 발명이 아니라 큐레이션

여기서의 지적 작업은 인용 검사기를 처음부터 만든 게 아니라, 이미 있는 조각을 **고르고
다시 빚어낸 것**이다. 유능한 게이트는 이미 존재한다. 이 묶음은 가장 가까운 이웃
**medsci-skills**(MIT)에 올라서서, 그 검증 깊이와 네 갈래 인용 분류
(OK/MISMATCH/UNVERIFIED/FABRICATED)를 가져오고, medsci가 *안 하는* 세 가지만 더한다:
회색문헌 분기, 한국 인용 DB, 그리고 더 단단한 강제 자세(PreToolUse·deny·동봉,
`[FABRICATED]`로 좁힘). 138개짜리 bench-science 라이브러리를 *왜 버리는 게 맞았는지*를
포함한 전체 keep/drop 판단은 [`docs/CURATION.md`](docs/CURATION.md)에 있다. 개발 메모와
알려진 한계: [`docs/NOTES.md`](docs/NOTES.md).

## 크레딧 · 라이선스

MIT([`LICENSE`](LICENSE)). 오픈 Agent Skills 표준(agentskills.io) 위에 만들었다. **ARS**
(academic-research-skills, CC-BY-NC)와 **medsci-skills**(Aperivue, MIT)와 비교했고 빚졌다 —
재배포 전 각 상류 라이선스를 재확인할 것. 보고 체크리스트는 EQUATOR Network 지침(STROBE,
CONSORT 2010, PRISMA 2020, TRIPOD+AI 2024)이며, 각 발표 항목 명단을 따른다.
