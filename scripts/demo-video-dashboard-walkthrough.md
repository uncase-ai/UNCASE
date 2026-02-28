# UNCASE Dashboard Walkthrough — Video Demo Script

> **Duration:** ~16–18 minutes
> **Format:** Screen recording with voiceover narration
> **Author:** Mariano Morales
> **Audience:** Technical decision-makers, ML engineers, data teams in regulated industries
>
> **Tone:** Conversational and confident. You're showing a colleague something you built.
> Not a sales pitch. Not a lecture. Just walking through it and explaining what you see.
>
> **Conventions:**
> - `[DO]` = what to do on screen (not spoken)
> - `[WAIT X]` = hold X seconds for the UI to settle before continuing
> - Lines without markers = narration (read aloud)
> - Keep a natural pace. Don't rush. Let the UI breathe after each click.

---

## 1. Opening — What You're Looking At (0:00–1:20)

`[DO] Browser open at /dashboard. Overview page fully loaded.`
`[WAIT 3]`

Hey. Welcome to the UNCASE dashboard.

If this is your first time seeing it — UNCASE is an open-source framework for generating synthetic conversational data. The kind you'd use to fine-tune a LoRA or QLoRA adapter for a specific industry.

The whole idea is that in regulated industries — healthcare, finance, legal, automotive — you can't just hand real customer conversations to a model. Privacy rules won't let you. So instead, you define what a good conversation looks like, and the system generates thousands of them — without a single real data point involved.

`[DO] Move cursor slowly across the pipeline visualization in the center of the page.`
`[WAIT 2]`

This diagram right here is the core of the system. Six stages, in order. You define seeds, upload knowledge, import data, evaluate quality, generate conversations, and export them as training-ready datasets. Everything flows left to right.

Today I'm going to walk through this entire pipeline, from scratch. By the end, we'll have a certified dataset ready for fine-tuning.

Let's start.

---

## 2. The Pipeline Map (1:20–2:20)

`[DO] Click "Pipeline" in the sidebar.`
`[WAIT 3]`

This is the pipeline view. Each card is one stage, and they're connected in sequence.

`[DO] Hover slowly over each card, left to right, pausing 2 seconds on each.`

Seed Engineering — where you design the conversation blueprints. Knowledge Base — where you upload domain literature so the generator has real facts to work with. Data Import — for bringing in existing conversations from CSV or JSONL files. Quality Evaluation — where every conversation gets scored against six metrics. Synthetic Generation — where the LLM produces new conversations based on your seeds. And Dataset Export — where you package everything for fine-tuning.

`[DO] Point to the lock icon on the Evaluation card.`

Notice some stages show a lock. You can't evaluate conversations that don't exist yet. The system enforces the right order, so you don't accidentally skip a step.

`[DO] Point to the "Recent Pipeline Jobs" card at the bottom.`

And down here you can track any running or completed jobs — their status, progress, and what stage they belong to.

Let me jump into the first stage.

---

## 3. Creating a Seed (2:20–6:00)

`[DO] Click "Open" on the Seed Engineering card. The Seed Library page loads — empty state.`
`[WAIT 2]`

This is the Seed Library. Right now it's empty because we're starting from zero.

So what is a seed? A seed is a complete blueprint for a conversation. It defines who's talking, what they're talking about, how long the conversation should be, what tone to use, and — this is the important part — what quality standards every generated conversation must meet. If the output doesn't match the seed's quality thresholds, it gets flagged.

Let me create one.

`[DO] Click "+ New Seed". The creation form opens.`
`[WAIT 2]`

I'll click New Seed and here's the creation form.

`[DO] Select "Automotive Sales" as the domain.`
`[WAIT 1]`

First, the domain. I'll pick Automotive Sales. UNCASE comes with six industry domains built in — automotive, medical, legal, finance, industrial, and education. Each domain has its own set of tools, vocabulary, and conversation patterns. You can also define custom domains, but these six cover the most common regulated industries.

`[DO] Select "Spanish" as the language.`

Language — Spanish. This determines the language of the generated conversations. The system supports English and Spanish natively.

`[DO] Type the objective: "Customer interested in a mid-range SUV, comparing financing options and evaluating their trade-in."`
`[WAIT 2]`

The objective is the scenario. Think of it as the one-sentence summary of what this conversation is about. In this case, a customer looking at SUVs with financing questions.

`[DO] Add roles: "customer" and "sales_agent". Type a short description for each.`
`[WAIT 2]`

Roles — I need at least two. A customer and a sales agent. For each role I add a short description that tells the generator how this person behaves, what they know, what kind of language they use. The customer is browsing options and has budget concerns. The sales agent is knowledgeable about inventory and financing programs.

These descriptions directly influence how the generator writes each turn. The more specific you are here, the better the output.

`[DO] Set min turns to 6, max turns to 12. Select "professional" tone.`
`[WAIT 1]`

Turn structure — I want conversations between 6 and 12 turns. Long enough to cover a real sales interaction, short enough to stay focused. Tone is professional.

`[DO] Scroll down to the quality thresholds section. Point to each slider.`
`[WAIT 3]`

Now this is where UNCASE gets serious. These are the quality thresholds — the minimum scores that every generated conversation must hit.

ROUGE-L at 0.65 — that's structural coherence. Does the conversation follow the flow I defined in the seed? Factual Fidelity at 0.90 — are the facts accurate for this domain? Lexical Diversity at 0.55 — is the vocabulary varied enough, or is it just repeating the same phrases? Dialogue Coherence at 0.85 — does the conversation make sense turn by turn?

These defaults are already strong, but you can tighten them if you need higher quality. The important thing is that these aren't suggestions — they're enforced. If a conversation scores below any threshold, it fails.

`[DO] Scroll to the privacy section.`
`[WAIT 2]`

And then there's privacy. PII removal is always enabled. Anonymization runs through Presidio — Microsoft's open-source PII detection engine. The privacy score must be exactly zero. Not low. Zero. That means zero names, zero phone numbers, zero emails, zero government IDs in the final output. This is the one metric that has no flexibility.

`[DO] Click "Create Seed".`
`[WAIT 2]`

I'll create it. And there it is in the library — domain, language, objective, roles, turn range. Everything defined.

`[DO] The seed appears in the table. Let it settle for 2 seconds.`
`[WAIT 2]`

Let me create a second seed quickly for a different scenario.

`[DO] Click "+ New Seed" again. Select "Medical Consultation". Objective: "Patient with recurring headaches scheduling a follow-up and discussing medication options." Roles: patient, doctor. Turns: 8–14. Click "Create Seed".`
`[WAIT 3]`

Good. Two seeds, two different industries. Each one with its own constraints and quality requirements.

---

## 4. Uploading Knowledge (6:00–7:30)

`[DO] Click "Knowledge" in the sidebar. The Knowledge Base page loads.`
`[WAIT 2]`

Before generating conversations, it's a good idea to feed the system some domain knowledge. This is what grounds the generated conversations in real facts instead of letting the model hallucinate.

`[DO] Point to the upload zone.`

The Knowledge Base accepts text files — markdown, plain text, CSV. You can categorize each document as facts, procedures, terminology, or reference material. Each type serves a different purpose during generation.

`[DO] Click "Upload" or drag a sample file. Select domain "automotive.sales", type "Facts". Add tags: "inventory, pricing".`
`[WAIT 3]`

I'll upload a product catalog — it has vehicle specs, pricing tiers, and financing terms. I'll tag it as "facts" under the automotive sales domain.

`[DO] The file uploads and gets chunked. Expand one document to show chunks.`
`[WAIT 3]`

You can see the system automatically broke it into chunks. Each chunk is a digestible piece of information that the generator can reference when building conversations. If the seed says the agent should discuss SUV pricing, the generator can pull actual numbers from this catalog instead of making them up.

That's the link between knowledge and fidelity. The Factual Fidelity metric we saw in the seed? It checks whether the conversation's facts match what's in the Knowledge Base.

---

## 5. Generating Conversations (7:30–10:30)

`[DO] Click "Generate" in the sidebar. The Generate page loads.`
`[WAIT 3]`

Alright, this is where it all comes together. The Generate page.

`[DO] Point to the left panel with seeds listed.`

On the left, I can see my seeds. Each one shows its domain, language, and objective. I'll check both of them.

`[DO] Check both seeds.`
`[WAIT 1]`

`[DO] Point to the configuration panel on the right.`

On the right side, the generation settings.

`[DO] Point to the API status badge.`

This badge tells me whether the backend is connected. When it says "API Connected," the generation runs through your configured LLM provider — Claude, GPT, Gemini, Ollama, whatever you've set up. If the API isn't available, there's a demo mode toggle that generates locally with mock data, so you can still explore the full pipeline without a backend.

`[DO] Set conversations per seed to 5.`
`[WAIT 1]`

I'll generate 5 conversations per seed. That's 10 total — enough to see the pipeline in action. In production you'd typically do 50 or 100 per seed.

`[DO] Point to the temperature slider. Adjust it slightly.`
`[WAIT 1]`

Temperature controls how creative the LLM gets. Lower values mean more predictable output, higher values mean more variation. I'll leave it at 0.7 — a good balance between consistency and diversity.

`[DO] Point to the generation summary.`
`[WAIT 2]`

The summary confirms everything before I commit — 2 seeds, 5 conversations each, 10 total, temperature 0.7. No surprises.

`[DO] Click "Generate 10 Conversations".`
`[WAIT 1]`

Let's generate.

`[DO] The progress bar starts filling. Let it run without narrating for 3 seconds.`
`[WAIT 3]`

You can see the progress bar moving. Behind the scenes, for each conversation the system takes the seed definition, builds a prompt that includes the role descriptions, the expected flow, the quality constraints, and any relevant knowledge chunks. It sends that through the LLM gateway with a privacy interceptor that scans both the prompt and the response for PII. Then it parses the output into the structured conversation format.

`[DO] Wait for generation to complete. Success banner appears.`
`[WAIT 3]`

Done. 10 conversations generated. I can see the success message and a link to view them. But first, let's look at how they scored.

---

## 6. Evaluating Quality (10:30–12:30)

`[DO] Click "Evaluations" in the sidebar. The evaluation page loads.`
`[WAIT 3]`

This is the evaluation dashboard, and honestly this is what makes UNCASE different from just prompting an LLM and hoping for the best.

`[DO] Point to the four summary cards at the top.`

At the top — total evaluations, pass rate, average composite score, and privacy violations. That last one should always be zero. If it's not, something went wrong.

`[DO] Point to the bar chart.`
`[WAIT 2]`

This histogram shows the distribution of composite scores. Blue bars are passing conversations, gray bars are failing. You want most of the data on the right side of the chart — that means high quality across the board.

`[DO] Point to the radar chart.`
`[WAIT 3]`

And this radar chart is probably the most useful visual in the entire dashboard. The dashed line shows the minimum threshold for each metric — that's what you defined in the seed. The solid line shows the actual performance of your generated data. If the solid line dips below the dashed line on any axis, you know exactly which dimension needs work.

For example, if lexical diversity is low, your conversations might be too repetitive. If fidelity is low, the model is getting facts wrong. If coherence is low, the conversation flow doesn't make sense.

`[DO] Scroll down to the failure analysis section, if there are failures.`
`[WAIT 2]`

If any conversations failed, you can see the breakdown here — which metric caused the failure and how often. This tells you exactly what to fix. Maybe you need to refine a seed's constraints, or adjust the temperature, or add more knowledge base documents.

`[DO] Scroll to the results table. Point to a passing row and a failing row.`
`[WAIT 3]`

And here's the full table. Every conversation, every metric, every score. Anything below threshold is highlighted in red so it jumps out immediately. This conversation passed across the board. This one fell short on coherence — the dialogue didn't flow naturally enough between turns.

The composite score formula is simple: it's the minimum of the four quality metrics, but only if privacy is zero and memorization is below 0.01. If either of those two conditions fails, the entire score drops to zero regardless of everything else. Privacy is the hard gate.

---

## 7. Browsing and Editing Conversations (12:30–15:00)

`[DO] Click "Conversations" in the sidebar. The split-panel view loads.`
`[WAIT 3]`

Here's the conversation browser. Left side is the list, right side is the detail view.

`[DO] Point to the filter bar at the top of the list.`

I can filter by domain, by type — real or synthetic — by validation status, and by rating. Useful when you have hundreds of conversations and need to find specific ones.

`[DO] Click on the first conversation in the list.`
`[WAIT 2]`

When I click a conversation, the full dialogue opens on the right. Each message is color-coded by role — blue for the user, gray for the assistant, violet for system messages. If there are tool calls, they show up in amber, and tool results in teal.

`[DO] Scroll slowly through the conversation. Let 3–4 turns be visible.`
`[WAIT 4]`

You can read through the entire exchange. Notice how it follows the scenario from the seed — the customer is asking about SUV options, the agent is presenting models, they discuss financing, a trade-in comes up. The structure, the vocabulary, the tone — it all came from what we defined in the seed.

`[DO] Click on a user message to enter edit mode. A text area appears.`
`[WAIT 2]`

Now here's something important — every turn is editable. I click on this message and it becomes a text area. If the customer's question could be phrased better, or if I want to add a detail, I can do it right here.

`[DO] Make a small change — add a clause to the customer's question. Click "Apply".`
`[WAIT 2]`

I'll refine this question slightly. Apply. Saved immediately.

`[DO] Click on an assistant turn. Type "<" to trigger the tool picker.`
`[WAIT 2]`

And if I'm editing an assistant turn and I type the less-than symbol, a tool picker drops down. These are domain-specific tools — for automotive you'll see things like check inventory, calculate financing, appraise trade-in. The system knows which tools belong to which domain.

`[DO] Select a tool from the dropdown. The tool call template inserts.`
`[WAIT 2]`

I select one and it inserts the tool call with the right structure. I can fill in the arguments right here. This means I can enrich conversations with realistic tool usage without having to manually write the JSON.

`[DO] Scroll down to the review panel — tags, rating, notes.`
`[WAIT 2]`

Below the messages there's a review panel. I can tag conversations to organize them — "financing," "trade-in," "edge case." I can rate them from one to five stars. And I can write notes for my team — "good example of objection handling" or "needs more detail on warranty."

`[DO] Add a tag "financing". Rate it 4 stars. Click "Validate".`
`[WAIT 2]`

I'll tag this one, give it four stars, and mark it as valid. Only valid conversations will be included in the final export. Anything marked invalid gets excluded automatically.

`[DO] Point to the "Compatible Templates" section.`

One more thing — down here, the system tells me which fine-tuning templates are compatible with this conversation based on its structure. If it has tool calls, multi-turn dialogue, a system prompt — it calculates which formats can represent all of that. ChatML, Llama 3, Mistral, OpenAI — they each have different capabilities, and the system matches them automatically.

---

## 8. Exporting for Fine-Tuning (15:00–17:00)

`[DO] Click "Export" in the sidebar. The export page loads.`
`[WAIT 3]`

This is the last stage. Everything we've done — defining seeds, uploading knowledge, generating conversations, evaluating quality, reviewing and editing — it all comes down to this.

`[DO] Point to the export builder on the left.`

The export builder is straightforward. I give my dataset a name.

`[DO] Type "automotive-sales-v1" as the export name.`
`[WAIT 1]`

I can filter by domain if I only want conversations from a specific industry.

`[DO] Select a template from the dropdown — e.g. "ChatML".`
`[WAIT 1]`

Then I pick a template. This is the output format — it determines how the conversation gets structured for your training framework. UNCASE ships with templates for ChatML, Llama 3, Mistral, Alpaca, OpenAI, Qwen, Nemotron, and more. Each one formats the roles, the special tokens, and the tool calls differently. I'll go with ChatML since it's the most widely supported.

`[DO] Toggle "Synthetic only" to on.`

I'll turn on "Synthetic only" so the export includes only the conversations we generated, not any manually imported ones.

`[DO] Point to the live preview — conversation count, estimated size.`
`[WAIT 2]`

The preview updates in real time. I can see how many conversations are included and the estimated file size. No guesswork.

`[DO] Point to the quality certificate panel on the right.`
`[WAIT 3]`

Now, on the right side — this is something you don't see in other tools. UNCASE generates a quality certificate for every export. It shows the pass rate, the average composite score, and the breakdown by metric. If you're in a regulated industry, this document is your proof that the training data meets quality and privacy standards.

`[DO] Click "Download Certification".`
`[WAIT 2]`

I can download the full certificate as an HTML document. It includes the dataset identification, seed provenance — which seeds contributed and their quality scores — the quality assurance report with all six metrics, compliance mapping for GDPR, HIPAA, EU AI Act, SOX, and LFPDPPP, and a privacy attestation confirming zero PII. There's even a certificate ID and a document hash for audit trails.

This is what makes UNCASE useful in regulated environments. It's not just about generating data — it's about proving the data is safe to use.

`[DO] Click "Export via API" or "Export as JSONL".`
`[WAIT 2]`

And finally — I export. The file downloads, formatted and ready. Every conversation in this file is traceable back to its source seed, scored against six quality metrics, and certified to contain zero personally identifiable information.

`[DO] Let the download complete.`
`[WAIT 2]`

This file goes straight into your LoRA or QLoRA fine-tuning pipeline. No preprocessing. No cleanup. It's already clean.

---

## 9. Closing (17:00–17:45)

`[DO] Navigate back to the Overview page.`
`[WAIT 3]`

That's the full pipeline, end to end. Define what you need in seeds. Ground it with real knowledge. Generate at scale. Measure everything against strict quality gates. Review, edit, refine. And export a certified dataset ready for fine-tuning.

No real data exposed. Full traceability. Quality enforced — not assumed.

And it works across six industries out of the box. Healthcare, finance, legal, automotive, industrial, education.

`[DO] Hold on the overview for 3 seconds.`
`[WAIT 3]`

UNCASE is open source and available on GitHub. Thanks for watching.

---

## Timing Reference

| Section | Start | Duration | Key Focus |
|---------|-------|----------|-----------|
| Opening + Overview | 0:00 | ~1:20 | What UNCASE is, pipeline diagram |
| Pipeline map | 1:20 | ~1:00 | Six stages, locked/ready logic |
| Creating seeds | 2:20 | ~3:40 | Domain, roles, quality thresholds, privacy |
| Knowledge Base | 6:00 | ~1:30 | Upload, chunking, fidelity link |
| Generation | 7:30 | ~3:00 | Seed selection, config, progress, results |
| Evaluation | 10:30 | ~2:00 | Metrics, charts, failure analysis |
| Conversations | 12:30 | ~2:30 | Browse, edit turns, tool picker, review |
| Export | 15:00 | ~2:00 | Template, certificate, download |
| Closing | 17:00 | ~0:45 | Recap |
| **Total** | | **~17:45** | |

---

## Recording Notes

**Screen setup:**
- Browser at 1440×900 or 1920×1080
- Dashboard in dark mode (more visually appealing on video)
- No other tabs visible
- Font size comfortable for reading at 1080p

**Audio:**
- Record in a quiet room with a decent microphone
- Speak at a natural pace — slightly slower than your conversational speed
- Don't read the script word-for-word if it doesn't feel natural. The script is a guide.
- Pauses are good. Let the UI speak for itself sometimes.

**Editing tips:**
- Use jump cuts when creating the second seed (don't show the full form twice)
- Let the generation progress bar run at real speed — don't skip it
- The radar chart on the evaluation page is visually strong — hold on it for 3–4 seconds
- The quality certificate download is a "wow" moment for regulated industry viewers
- End on the overview page pipeline diagram — it ties the whole thing together
