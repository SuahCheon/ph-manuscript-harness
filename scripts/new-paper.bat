@echo off
REM new-paper.bat - set up a fresh manuscript folder wired for Manuscript Harness.
REM
REM Usage:   scripts\new-paper.bat <target-folder>
REM Example: scripts\new-paper.bat C:\papers\2026-aefi
REM
REM Copies this repo's .claude\skills\ into <target-folder>\.claude\skills\ so that
REM running Claude Code from <target-folder> finds the citation-verifier and
REM reporting-guidelines skills (and their write-time hooks). Creates an empty
REM manuscript.md if none exists. Paths resolve relative to this script, so the
REM repo can live anywhere.
setlocal

set "TARGET=%~1"
if "%TARGET%"=="" (
  echo usage: %~nx0 ^<target-folder^>
  echo example: %~nx0 C:\papers\2026-aefi
  exit /b 2
)

REM Repo root = parent of this script's folder (scripts\ sits at the repo root).
set "SRC=%~dp0..\.claude\skills"

if not exist "%SRC%\citation-verifier\" (
  echo error: skills not found under "%SRC%"
  echo run this from a clone of the Manuscript Harness repo.
  exit /b 1
)
if not exist "%SRC%\reporting-guidelines\" (
  echo error: skills not found under "%SRC%"
  exit /b 1
)

if exist "%TARGET%\.claude\skills\citation-verifier\"   rmdir /s /q "%TARGET%\.claude\skills\citation-verifier"
if exist "%TARGET%\.claude\skills\reporting-guidelines\" rmdir /s /q "%TARGET%\.claude\skills\reporting-guidelines"
xcopy /E /I /Q "%SRC%\citation-verifier"    "%TARGET%\.claude\skills\citation-verifier" >nul
xcopy /E /I /Q "%SRC%\reporting-guidelines" "%TARGET%\.claude\skills\reporting-guidelines" >nul

if not exist "%TARGET%\manuscript.md" (
  > "%TARGET%\manuscript.md" echo # (new manuscript)
)

if not exist "%TARGET%\HOWTO.md" if exist "%~dp0paper-howto-template.md" copy /y "%~dp0paper-howto-template.md" "%TARGET%\HOWTO.md" >nul

echo Manuscript Harness: set up "%TARGET%".
echo   copied skills: citation-verifier, reporting-guidelines
echo   created: manuscript.md (edit this), HOWTO.md (how to use this folder)
echo.
echo Next: open a terminal in "%TARGET%", start Claude Code there, then ask e.g.:
echo   - verify the citations in manuscript.md with citation-verifier
echo   - check manuscript.md against the reporting guideline
echo (The hooks call "python"; this matches a typical Windows install.)
endlocal
