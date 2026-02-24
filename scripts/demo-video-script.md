# UNCASE Framework — Full Demo Video Script

**Duration:** ~20-25 minutes
**Format:** Screen recording + voiceover
**Author:** Mariano Morales

---

## INTRO [0:00 - 1:30]

Welcome, my name is Mariano Morales and I am going to guide you through the UNCASE framework to demonstrate how powerful it can be and how it brings regulated industries, or any person dealing with sensitive data, closer to a specialized, highly effective fine-tuning.

The outcome today is to produce a mouthful amount of quality, certified, industry-specific, mathematically guardrailed and computationally audited conversations in 10 different formats ready to feed the fine-tuning process. If you stick until the end I will show the process and the results setting up a vLLM inference instance with the merged model.

Before we jump in, let me give you the 30-second pitch. UNCASE stands for Unbiased Neutral Convention for Agnostic Seed Engineering. It is an open-source framework designed to generate synthetic conversational data for fine-tuning LoRA and QLoRA adapters — specifically for industries where you cannot just throw real data at a model. Healthcare, finance, legal, automotive, manufacturing — if your data has PII or regulatory constraints, this is your pipeline.

The framework follows a 5-layer architecture we call SCSF. Layer 0 strips PII from real conversations and turns them into seeds. Layer 1 parses and validates. Layer 2 evaluates quality with six mathematical metrics. Layer 3 generates synthetic conversations using any LLM provider through a unified gateway. And Layer 4 handles the actual LoRA fine-tuning with differential privacy baked in. Every single conversation that comes out of this pipeline is traceable back to its seed, scored against six quality dimensions, and certified with zero PII residual. Zero. Not low — zero.

So let's get into it.

---

## INSTALLATION [1:30 - 4:00]

*[Screen: terminal]*

Let's start by installing the framework. I am going to open my terminal and copy the git clone command to download it to my Projects folder.

```
git clone https://github.com/uncase-ai/UNCASE.git
cd UNCASE
```

You can also use Docker or pip, although I recommend using `uv` if you won't be using git. For pip you'd do `pip install uncase` for the core, or `pip install "uncase[all]"` to get everything — ML dependencies, privacy tools, dev tooling, the whole stack. For Docker, a simple `docker compose up -d` gives you the API server plus PostgreSQL ready to go.

Once downloaded, I will use `uv` to set up the environment. `uv` is a fast Python package manager — think of it as pip on steroids.

```
cd uncase
uv sync --extra all
```

*[Screen: uv installing dependencies]*

This installs the core framework plus all extras — that includes transformers, peft, trl for fine-tuning, spaCy and Presidio for PII detection, pytest and ruff for development, MLflow for experiment tracking. The `uv.lock` file ensures reproducibility, so everyone on your team gets the exact same environment.

Now let me spin up the backend API.

```
uv run uvicorn uncase.api.main:app --reload --port 8000
```

And in a second terminal, the frontend dashboard.

```
cd ../frontend
npm install
npm run dev
```

I should now be able to visit the framework by opening my browser on localhost port 3000.

*[Screen: browser opening localhost:3000]*

And there it is. This is the UNCASE landing page — it gives you an overview of the framework, the architecture, links to the whitepaper. But what we care about today is the dashboard. Let me click on "App" in the navigation.

---

## DASHBOARD OVERVIEW [4:00 - 5:30]

*[Screen: dashboard overview page]*

As you see, this is the main dashboard. On the left sidebar you have the full pipeline laid out in order: Seeds, Knowledge Base, Import, Evaluate, Generate, Export. Below that you have your Workbench — Conversations, Templates, Tools. And at the bottom, Insights for your evaluation metrics and Activity for the event log.

The overview page shows you a visual representation of the 6-stage pipeline, your current stats — how many seeds you've created, how many conversations generated, evaluations completed — and a getting started guide if this is your first time.

Let me also point out something important: this dashboard works in two modes. If your backend API is running on port 8000, everything connects to real services — PostgreSQL, LLM providers, the full evaluator. If the API is not available, the dashboard falls back to localStorage — demo mode. Everything still works, you just don't get real LLM generation. For this demo, I will show you both.

Let's start where every pipeline starts: with a seed.

---

## SEED CREATION [5:30 - 9:30]

*[Screen: Seeds page]*

This is the Seed Library. Seeds are the DNA of your synthetic conversations. A seed defines everything about what a conversation should look like — the domain, the participants, the structure, the constraints, the quality thresholds. Think of it as a blueprint that the generator will follow to produce conversations that are structurally coherent and factually grounded.

Let me create one. I'll click "Create Seed."

*[Screen: seed creation wizard]*

The wizard walks you through six steps. First, **Basic Information**. I need to pick a domain — the framework supports six industry namespaces out of the box: `automotive.sales`, `medical.consultation`, `legal.advisory`, `finance.advisory`, `industrial.support`, and `education.tutoring`. I'm going to pick `automotive.sales` since that's our pilot domain.

Language — I'll set it to Spanish, `es`. And I'll add some tags: "ventas", "financiamiento", "SUV".

Next step, **Roles**. I need at least two roles. For automotive sales, that's "vendedor" — the sales advisor — and "cliente" — the customer. For each role I write a description. The vendedor is "Asesor de ventas certificado con conocimiento de inventario, financiamiento y proceso de entrega." The cliente is "Prospecto interesado en adquirir un vehículo nuevo, comparando opciones y condiciones de financiamiento."

These descriptions matter. They tell the generator how each role should behave, what vocabulary they should use, what knowledge they have access to.

Step three, **Turn Structure**. The objective — what should this conversation achieve? I'll write: "Guiar al cliente desde la consulta inicial hasta la cotización formal de un vehículo, abordando necesidades, presupuesto y opciones de financiamiento."

Tone: "profesional". Turn range: minimum 4, maximum 8. And the expected flow — this is the skeleton of the conversation. I'll define: "saludo", "detección de necesidades", "presentación de opciones", "discusión de financiamiento", "cotización", "cierre". This flow tells the generator what the conversation should look like structurally, and later the evaluator will measure coherence against it.

Step four, **Factual Parameters**. This is where it gets industry-specific. Context: "Agencia automotriz premium con inventario de sedanes, SUVs y pickups. Temporada de ofertas de fin de año." Constraints — these are the rules the conversation must follow: "No mencionar descuentos superiores al 15%", "Siempre ofrecer prueba de manejo", "Mencionar garantía extendida en todas las cotizaciones." Tools available: "cotizador", "inventario_consulta", "calculadora_financiamiento".

Step five, **Privacy Settings**. PII removal is enabled by default using Presidio with a confidence threshold of 0.85. These come pre-configured — in most cases you'll leave them as-is.

And step six, **Review**. Here you see the complete seed before confirming — domain, roles, turn structure, constraints, quality thresholds. The quality thresholds come pre-filled with the framework defaults — ROUGE-L at 0.65, Factual Fidelity at 0.90, Lexical Diversity at 0.55, Dialogic Coherence at 0.85. You can tighten these if you want stricter quality. The privacy score is locked at zero — that's non-negotiable. And memorization must stay below 0.01.

*[Click "Create"]*

There we go. Seed created. You can see it in the library now with its unique ID, the domain badge, turn range, objective preview, and all the technical specs. Let me create two or three more seeds quickly — one for a trade-in scenario, one for a fleet purchase, and one for a financing-only consultation.

*[Fast-forward creating 3 more seeds]*

Now I have four seeds in my library. Each one defines a different automotive sales scenario, with different constraints, different flows, different tool requirements. This is the foundation of diverse, high-quality synthetic data.

---

## KNOWLEDGE BASE [9:30 - 11:00]

*[Screen: Knowledge Base page]*

Before I generate anything, let me feed the pipeline some domain knowledge. This is Layer 0 enrichment — the Knowledge Base lets you upload documents that ground your conversations in real facts.

I have a product catalog here — a markdown file with vehicle specifications, pricing tiers, financing terms. Let me drag it in.

*[Drag and drop file]*

The framework auto-chunks the document. You can see it split it into chunks of roughly 800 characters with 100-character overlap between them. Each chunk gets a knowledge type — I have four options: facts, procedures, terminology, or reference. I'll mark this as "facts" — and associate it with the `automotive.sales` domain.

Why does this matter? When the generator creates a conversation about an SUV, it can reference actual specifications from your catalog instead of hallucinating numbers. The factual fidelity metric in Layer 2 will then verify that the generated conversation aligns with these facts.

Let me upload one more — a financing procedures document — and mark it as "procedures."

Good. Two documents uploaded, properly chunked, ready to inform generation.

---

## SYNTHETIC GENERATION [11:00 - 14:30]

*[Screen: Generate page]*

This is where it gets exciting. The Generate page is Layer 3 — the Synthetic Reproduction Engine. Let me walk you through it.

First, I select which seeds to use. I'll check all four. You can see each seed displayed with its ID, domain badge, language, roles, turn range, and objective. I'll select all of them.

Now, generation parameters. **Conversations per seed**: I'll set this to 5. That means 4 seeds times 5 conversations = 20 total conversations. For a real production run you might do 50 or 100 per seed, but 20 is enough to demonstrate.

**Temperature**: 0.7 — this controls the LLM's creativity. Lower means more deterministic, higher means more variation. 0.7 is a sweet spot for conversational data — diverse enough to avoid repetition, controlled enough to stay on track.

**Language override**: I'll leave it on "Use seed default" — each seed already specifies Spanish.

**Evaluate after generation**: I'm going to toggle this on. This tells the pipeline to automatically run Layer 2 quality evaluation on every conversation right after generation. If a conversation doesn't meet the thresholds, I'll know immediately.

*[Check API status indicator]*

I can see the API status indicator shows "API Connected" — the backend is running, so this will use the real LLM gateway. The gateway supports Claude, Gemini, Qwen, LLaMA — any provider you've configured through LiteLLM. For this demo I have Claude configured.

Let me hit "Generate."

*[Click Generate, show progress bar]*

Watch the progress bar. The generator is doing several things right now for each conversation. It takes the seed, builds a domain-specific prompt with the role descriptions, the expected flow, the constraints, and any knowledge chunks from our catalog. It sends that to the LLM through the privacy interceptor — which scans the prompt for any PII on the way out and scans the response on the way back. Then it parses the LLM's response into our structured conversation format, validates the turn count, checks the roles, and stores it.

*[Progress bar completes]*

And done. 20 conversations generated. You can see the summary: 20 generated, and since we toggled "Evaluate after," it already ran quality checks — look at that: 18 passed, 2 failed. Average composite score 0.87. The two that failed — I can see the failure reasons right here. One had a ROUGE-L below 0.65, meaning its structure diverged too much from the expected flow. The other had a fidelity issue — probably hallucinated a price that didn't match our catalog.

This is exactly the point. The pipeline doesn't just generate — it certifies. Those two failing conversations won't make it into the export unless I fix them or mark them as invalid.

---

## QUALITY EVALUATION [14:30 - 17:30]

*[Screen: Evaluate page]*

Let me go deeper into the evaluation. This is the heart of UNCASE — what separates it from just prompting an LLM and hoping for the best.

I can see all 20 conversations listed here. The ones with a green "Passed" badge met all six thresholds. The ones with red "Failed" badges didn't. Let me click on one of the passing conversations to see the full breakdown.

*[Click a conversation row]*

Look at this radar chart. Six axes, six metrics. Let me walk through each one.

**ROUGE-L: 0.78.** This measures structural coherence — how well the conversation follows the expected flow defined in the seed. The threshold is 0.65 and we're at 0.78. It calculated the longest common subsequence between the generated conversation's structure and the expected flow pattern, then computed the F1 score.

**Factual Fidelity: 0.93.** This checks whether the conversation got the facts right. Did the vendedor mention the correct pricing tier? Did they follow the constraint about not exceeding 15% discount? Did they offer the test drive as required? 0.93 means it hit almost every factual marker.

**Lexical Diversity: 0.62.** This is the Type-Token Ratio — unique words divided by total words across all turns. We want at least 0.55 to ensure the conversations aren't repetitive or formulaic. 0.62 is healthy.

**Dialogic Coherence: 0.89.** This measures whether the conversation makes sense turn-by-turn. Are the roles alternating properly? Does each turn reference or build on the previous one? Is there a logical progression? 0.89 is strong.

**Privacy Score: 0.00.** Zero. Exactly where it needs to be. The Presidio scanner ran across every turn of this conversation and found zero PII residual — no names, no phone numbers, no emails, no credit card numbers, no CURP, no RFC. This is the hard gate. If this number is anything other than zero, the entire conversation fails regardless of how good the other metrics are.

**Memorization: 0.00.** This metric becomes critical during Layer 4 fine-tuning — it measures whether the model can be tricked into regurgitating training data. At generation time it's zero by default, but during training we enforce it stays below 0.01 using differential privacy with an epsilon of 8.0.

The **composite score** is calculated as the minimum of the four quality dimensions — so 0.62 in this case, bounded by lexical diversity. That's above zero, privacy is clean, memorization is clean — this conversation **passes**.

Now let me look at one of the failing conversations.

*[Click a failed conversation]*

See? ROUGE-L dropped to 0.58 — below the 0.65 threshold. Looking at the conversation, the generator went off-script. The expected flow was greeting, needs assessment, presentation, financing, quote, close — but this conversation skipped the needs assessment entirely and jumped straight to presenting a vehicle. Structurally incoherent for our use case. The composite score collapses to zero because it failed a threshold.

This is what I mean by mathematically guardrailed. We don't rely on vibes or manual review — the math tells us which conversations are production-ready and which aren't.

Let me scroll down to the **Quality Gate Summary**. 18 out of 20 passed — that's a 90% pass rate. The batch average composite score is 0.87. Failure breakdown: 1 ROUGE-L failure, 1 fidelity failure. If I wanted to improve this, I could refine my seed constraints or adjust the temperature.

---

## CONVERSATIONS & EDITING [17:30 - 19:00]

*[Screen: Conversations page]*

Let me jump to the Conversations page. Here I can see all 20 conversations in a table — conversation ID, domain, language, turn count, whether it's synthetic, and the status.

I can filter by domain, by synthetic or real, and by status. Let me filter to show only the failed ones. There they are — the two that didn't pass evaluation. I have three options for each in this dropdown: I can edit the conversation, mark it as invalid so it's excluded from export, or delete it entirely.

Let me click into one to edit it.

*[Screen: conversation detail page]*

This is the full conversation. Every turn displayed as a chat bubble — role, content, tools used if any. I can see the metadata on the right: seed ID, domain, language, creation time.

See that turn where the vendedor skipped the needs assessment? I can click the edit icon on any turn, modify the content right here inline — add the missing needs assessment — save it, and then re-evaluate. For this demo I'll just mark it as invalid so it doesn't pollute the export.

*[Click "Mark as Invalid"]*

Done. It's now tagged with an "Invalid" banner. The export stage will automatically exclude it.

---

## EXPORT [19:00 - 21:00]

*[Screen: Export page]*

Now the fun part — packaging this data for fine-tuning. The Export page is where your certified data becomes training-ready.

I need to select which conversations to export. I'll filter to only passed, valid conversations — that gives me 18. Select all.

Now, the **template**. This is where UNCASE shines for interoperability. The framework ships with 10 output templates — Alpaca, ChatML, Llama 3/4, Mistral v3, OpenAI API, Qwen 3, Nemotron, Harmony by Cohere, MiniMax, and Moonshot Kimi. Each template structures the conversation differently for different training frameworks and model families.

I'll select **ChatML** — it's widely supported by training tools like Axolotl and LLaMA-Factory, and it supports tool calls natively. The template will format each conversation with the proper `<|im_start|>` and `<|im_end|>` special tokens.

**Tool call mode**: "inline" — this embeds any tool calls directly in the conversation text, which is what most LoRA training setups expect.

Let me hit "Export."

*[Click Export]*

Done. 18 conversations exported. The file downloaded to my machine. Let me open it quickly in the terminal.

*[Switch to terminal]*

```
head -1 uncase_export_chatml.txt | python -m json.tool
```

*[Show formatted JSON output]*

There it is. Each conversation is properly formatted with the system prompt, all turns wrapped in ChatML tokens, tool calls inlined, and metadata preserved. This file is ready to feed directly into your fine-tuning pipeline.

---

## PIPELINE VIEW [21:00 - 21:30]

*[Screen: Pipeline page]*

Before we move to fine-tuning, let me show you the Pipeline page. This gives you the bird's-eye view of the entire SCSF workflow — six stages, connected in sequence.

Seed Engineering → Knowledge Base → Data Import → Quality Evaluation → Synthetic Generation → Dataset Export.

Each stage shows a readiness indicator — how many seeds created, documents uploaded, conversations evaluated. And each stage links directly to its page. This is your control center.

---

## FINE-TUNING WITH LoRA [21:30 - 24:00]

*[Screen: terminal]*

Now let's take that exported file and actually fine-tune a model. The UNCASE framework includes all the ML dependencies you need — transformers, peft, trl, bitsandbytes, accelerate — they're all part of the `[ml]` extra we installed earlier.

For this demo, I'll use LLaMA 3.1 8B as the base model with QLoRA 4-bit quantization. I have an A100 available, but this setup works on a consumer GPU with 24GB VRAM too.

```
uv run python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset
import torch

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_compute_dtype=torch.bfloat16,
)

# Load base model
model = AutoModelForCausalLM.from_pretrained(
    'meta-llama/Llama-3.1-8B-Instruct',
    quantization_config=bnb_config,
    device_map='auto',
)
tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-3.1-8B-Instruct')

# LoRA adapter config
lora_config = LoraConfig(
    r=64, lora_alpha=128,
    target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'],
    lora_dropout=0.05,
    task_type='CAUSAL_LM',
)

# Load our UNCASE export
dataset = load_dataset('json', data_files='uncase_export_chatml.txt')

# Train
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset['train'],
    peft_config=lora_config,
    args=SFTConfig(
        output_dir='./adapters/automotive-v1',
        num_train_epochs=3,
        per_device_train_batch_size=4,
        learning_rate=2e-4,
    ),
)
trainer.train()
trainer.save_model('./adapters/automotive-v1')
"
```

A few things to notice here. We're using QLoRA with rank 64 and alpha 128. The 4-bit NF4 quantization keeps memory usage low. And all of this runs with the dependencies that UNCASE already installed through the `[ml]` extra — transformers, peft, trl, bitsandbytes, accelerate.

For differential privacy, you would add DP-SGD via the `dp-transformers` library with an epsilon of 8.0. This mathematically bounds how much any single conversation can influence the model weights, which prevents memorization.

MLflow can track this run if you have it configured. Every epoch, every loss value, every gradient norm — all logged and versioned.

*[Fast-forward training, show loss curve]*

Training complete. The LoRA adapter is saved at `./adapters/automotive-v1`. Let me merge it with the base model for inference.

```
uv run python -c "
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

model = AutoPeftModelForCausalLM.from_pretrained('./adapters/automotive-v1')
merged = model.merge_and_unload()
merged.save_pretrained('./models/automotive-llama-8b-v1')
AutoTokenizer.from_pretrained('meta-llama/Llama-3.1-8B-Instruct').save_pretrained('./models/automotive-llama-8b-v1')
"
```

This merges the LoRA weights into the base model. The result is a single model directory ready for deployment.

---

## vLLM INFERENCE [24:00 - 27:00]

*[Screen: terminal]*

And now the payoff. Let me spin up a vLLM inference instance with our merged model.

```
python -m vllm.entrypoints.openai.api_server \
  --model ./models/automotive-llama-8b-v1 \
  --host 0.0.0.0 \
  --port 8080 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.90
```

*[Show vLLM server starting]*

vLLM is running. It exposes an OpenAI-compatible API on port 8080. That means any application that speaks the OpenAI chat completions format can use this model out of the box — no code changes needed.

Let me test it with a curl request.

```
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "automotive-llama-8b-v1",
    "messages": [
      {"role": "system", "content": "Eres un asesor de ventas automotriz profesional."},
      {"role": "user", "content": "Hola, estoy buscando una SUV familiar con buen financiamiento. ¿Qué opciones tienen?"}
    ],
    "temperature": 0.7,
    "max_tokens": 512
  }'
```

*[Show response]*

Look at that response. The model greets the customer professionally, asks about budget and family size — exactly the needs assessment step from our seed flow. It mentions the vehicle inventory, offers a test drive — following the constraint we defined. It references financing terms that align with our knowledge base. And it does it all in natural, domain-appropriate Spanish.

This is not a generic LLM being prompt-engineered. This is a model that has internalized the conversational patterns, the domain vocabulary, the regulatory constraints, and the business logic of automotive sales — all from 18 synthetic conversations that we generated, evaluated, and certified in under 30 minutes.

Now imagine this at scale. 500 seeds across six domains. 10,000 certified conversations. Specialized adapters for healthcare intake, legal consultations, financial advisory, manufacturing support — each one trained with differential privacy, each conversation traceable to its seed, each metric auditable.

---

## CLOSING [27:00 - 28:00]

That is the UNCASE framework end to end. From seed to inference in a single pipeline.

Let me recap what we did today. We created seeds that define conversation blueprints with domain constraints and quality thresholds. We uploaded knowledge documents to ground generation in real facts. We generated 20 synthetic conversations using Claude through the privacy-intercepted LLM gateway. We evaluated every single one against six mathematical metrics — ROUGE-L, factual fidelity, lexical diversity, dialogic coherence, privacy score, and memorization rate. We exported the 18 that passed in ChatML format. We fine-tuned LLaMA 3.1 8B with QLoRA using transformers, peft, and trl. And we deployed it on vLLM for production inference.

Every step auditable. Every conversation certified. Zero PII. Mathematically guardrailed.

The framework is open source — the link is in the description. The technical whitepaper covers the formal foundations if you want to go deeper into the math. And if you are in a regulated industry and this resonates with you, I'd love to hear about your use case.

Thank you for watching. I'll see you in the next one.

---

## B-ROLL & SCREEN RECORDING NOTES

**Suggested screen recordings needed:**
1. Terminal: git clone + uv sync + server startup
2. Browser: Landing page → Dashboard overview
3. Browser: Seed creation wizard (all 6 steps, go slow)
4. Browser: Knowledge Base drag-and-drop upload
5. Browser: Generate page — select seeds, configure, generate (show progress)
6. Browser: Evaluate page — radar chart, metric cards, pass/fail badges
7. Browser: Conversation detail with inline editing
8. Browser: Export page — template selection, download
9. Browser: Pipeline page overview
10. Terminal: LoRA training with loss curve
11. Terminal: Model merge with peft
12. Terminal: vLLM server startup + curl test

**Pacing notes:**
- Slow down on seed creation — this is where the differentiation is
- Let the radar chart linger — it's visually compelling
- The curl response is the "wow" moment — give it a beat
- Use jump cuts for repetitive actions (creating multiple seeds, waiting for generation)
