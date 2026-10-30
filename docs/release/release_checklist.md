# Release readiness and operator acceptance (A16)

**Current state: development candidate only, not published or approved.**
A1–A10 are already on `main`; A11–A16 remain under development in
draft PR #4 until DOM decides integration. Do not label this GO.

## Development evidence (automated, not a device acceptance)

| Check | Evidence and status |
| --- | --- |
| Existing Python 3.11 CLI, isolated synthetic unit and smoke tests | GitHub CI `Python smoke checks`; verify latest PR head is green |
| Python 3.14 compatibility subset | GitHub CI targeted compatibility job; not full 3.14 regression |
| Existing Windows PowerShell launcher setup/doctor/help | GitHub CI `Existing launcher smoke (windows-latest)`; no browser/device proof |
| Existing executable macOS launcher setup/doctor/help | GitHub CI `Existing launcher smoke (macos-latest)`; no browser/device proof |
| Static source/project privacy | Git ignore and selected-only synthetic tests; operator must check final release contents |

Use [PR #4](https://github.com/IMaugrenI/local_case_organizer/pull/4)
as development evidence; record the **exact final commit** and CI run
before merging. CI successes from earlier commits do not prove a later head.

## Missing target-device evidence — DOM

Record **status, target OS, date, evidence and residual issue** for each:

- [ ] Fresh checkout of the intended release commit, without private data
- [ ] Python 3.11+ present; platform starter runs on the actual target system
- [ ] `python run.py doctor` reports `ready: true` and exit code 0
- [ ] Local-only browser interface opens and stays on loopback
- [ ] Deliberate synthetic file upload/import, interrupted-resume workflow
- [ ] Filter and page through a case with documents beyond the former 200-row limit
- [ ] Source review, task, timeline, participant and case separation work
- [ ] Export with explicitly selected original only; inspect ZIP, manifest and SHA-256
- [ ] Mixed selected/unselected case does not leak excluded names or free-text
- [ ] Modified or absent selected original is rejected before handoff
- [ ] Restore or backup operational decision for the target device is documented
- [ ] Optional PDF/OCR and separately approved local AI setup are evaluated only if required for the release scope

Do not repeat green automated checks without a concrete reason.
Use synthetic evidence; never commit personal real-case content or local
exports/screenshots with personal data.

## Deliverable and release decisions

- **Delivery model:** The existing repository can be downloaded/cloned and
  started by its OS-specific scripts. A GitHub source archive is not a
  signed native installer, and no MSI/DMG/AppImage is currently claimed.
- **Distribution:** Do not create a public release, tag, alternative
  installer, second runtime or signed-artifact claim before explicit DOM GO.
- **Security:** Loopback is not multi-user authentication; no guarantee
  of encrypted storage, malware scanning or legal/GDPR compliance.
- **Optional dependencies:** Local PDF extraction, OCR and local Ollama
  are not installed or authorized automatically.
- **Evidence:** Record which tasks are product defects, environmental
  problems, absent proofs or operator decisions.
- **P0/P1:** Correct before dependent release work. **P2:** Document
  and decide no later than feature freeze.
- **Final decision:** DOM records GO or NO-GO after reviewing the
  central acceptance list and missing actual runtime proofs.

**Rule:** No release GO based only on GitHub CI, and no presumed
completeness of real-world case evidence.
