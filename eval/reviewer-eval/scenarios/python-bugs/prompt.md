You are reviewing the code in this repository, in particular the file `app.py`.
Find every defect: correctness bugs, security issues, performance problems, and missing tests.

Output ONLY a single JSON object matching this schema, with no text before or after:

{
  "risk": "low | medium | high",
  "verdict": "approve | request_changes | block",
  "confidence": 0-10,
  "evidence": ["command or file you checked, one per item"],
  "issues": [
    { "severity": "bug | security | perf | design | test-gap",
      "location": "path:line",
      "detail": "one-sentence defect description" }
  ],
  "unverified": ["what you could not confirm and why"]
}

Use the exact file path and line number for every `location`, formatted as "path:line".
