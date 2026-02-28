# UNCASE — Landing Page Overview Video (3 min)

> **Duration:** ~3 minutes
> **Format:** Screen recording with voiceover
> **Purpose:** Quick dashboard overview for the landing page. Nothing is created from scratch — seeds, conversations, and evaluations are already loaded.
> **Tone:** Fast, direct, confident. Like showing a colleague something in 3 minutes.
>
> `[DO]` = on-screen action (not spoken)
> `[WAIT X]` = pause X seconds
> Unmarked lines = spoken narration

---

## Intro (0:00–0:20)

`[DO] Dashboard open at /dashboard. Overview loaded with existing data — seeds, conversations, evaluations.`
`[WAIT 2]`

This is the UNCASE dashboard. From here you manage the entire pipeline for generating synthetic conversational data — the kind you'd use to fine-tune a language model without exposing real data.

`[DO] Move cursor slowly across the pipeline diagram.`

Six stages, in sequence. Seeds, knowledge, import, evaluation, generation, and export. Let's walk through them.

---

## Seeds (0:20–0:55)

`[DO] Click "Seeds" in the sidebar. The seed library shows several seeds already created.`
`[WAIT 2]`

These are seeds — the blueprints for each conversation. Every seed defines the domain, the roles, the objective, the tone, and the quality thresholds that every generated conversation must meet.

`[DO] Click on an "Automotive Sales" seed to see its detail.`
`[WAIT 2]`

For example, this seed is for automotive sales. It has two roles — customer and salesperson — a turn range, and minimum thresholds for each quality metric. If a generated conversation doesn't meet these numbers, it fails.

`[DO] Briefly point at the quality thresholds — ROUGE-L, Fidelity, TTR, Coherence.`
`[WAIT 1]`

And the privacy score must always be zero. Zero PII in the final output. That's not configurable — it's a fixed requirement.

---

## Generation (0:55–1:25)

`[DO] Click "Generate" in the sidebar. The page shows selected seeds and configuration.`
`[WAIT 2]`

On the generation page you select which seeds to use, adjust the temperature, and set the number of conversations per seed.

`[DO] Point to selected seeds on the left, configuration on the right.`

The system connects to your LLM provider — Claude, GPT, Gemini, Ollama, whatever you've configured — and generates conversations through a privacy interceptor that scans every prompt and every response.

`[DO] Point to the generation summary and the history of previous runs.`
`[WAIT 1]`

Here you can see past runs. Each one logs how many conversations were generated, at what temperature, and in which mode.

---

## Evaluation (1:25–2:00)

`[DO] Click "Evaluations" in the sidebar. The page loads with data.`
`[WAIT 3]`

Every generated conversation is automatically evaluated against six metrics.

`[DO] Point to the summary cards — total, pass rate, composite score, privacy violations.`

Pass rate, average composite score, and privacy violations — which must be zero.

`[DO] Point to the histogram.`
`[WAIT 1]`

This histogram shows the score distribution. Blue bars passed, gray bars didn't.

`[DO] Point to the radar chart.`
`[WAIT 2]`

And the radar chart compares actual results against the minimum thresholds. If any axis dips below the line, you know exactly what to fix.

---

## Conversations (2:00–2:30)

`[DO] Click "Conversations" in the sidebar. Split-panel view with list on the left, detail on the right.`
`[WAIT 2]`

From here you can explore every conversation. Filter by domain, status, or rating.

`[DO] Click on a conversation. Detail shows on the right with color-coded messages by role.`
`[WAIT 2]`

Every turn is editable. You can refine the text, insert tool calls with domain-aware autocomplete, add tags, rate from one to five stars, and mark as valid or invalid. Only valid conversations make it into the export.

`[DO] Quick-click on a message to show edit mode, then cancel.`
`[WAIT 1]`

---

## Export (2:30–2:50)

`[DO] Click "Export" in the sidebar. The export page loads.`
`[WAIT 2]`

The final stage. You pick a template — ChatML, Llama 3, Mistral, OpenAI, Qwen — and the system formats all your conversations into that format, ready for fine-tuning.

`[DO] Point to the quality certification panel on the right.`
`[WAIT 2]`

It also generates a quality certificate with full seed traceability, metrics, regulatory compliance mapping, and a zero-PII guarantee. Downloadable as an HTML document for audit.

---

## Closing (2:50–3:00)

`[DO] Navigate back to Overview.`
`[WAIT 2]`

From seed to certified dataset, in minutes. No real data. Quality measured, not assumed. Open source and on GitHub.

`[DO] Hold on overview for 3 seconds.`
`[WAIT 3]`

---

## Timing Reference

| Section | Start | Duration |
|---------|-------|----------|
| Intro | 0:00 | 20s |
| Seeds | 0:20 | 35s |
| Generation | 0:55 | 30s |
| Evaluation | 1:25 | 35s |
| Conversations | 2:00 | 30s |
| Export | 2:30 | 20s |
| Closing | 2:50 | 10s |
| **Total** | | **~3:00** |

---

## Recording Notes

- Dashboard must have pre-loaded data before recording — seeds, generated conversations, completed evaluations
- Use dark mode — looks better on video
- Don't linger too long on any section — this is an overview, not a tutorial
- The radar chart is the strongest visual moment — let it breathe for 2 seconds
- End on the overview to visually close the loop
