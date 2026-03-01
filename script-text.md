Hey — welcome to the UNCASE dashboard.

If this is your first time seeing it, quick context.
UNCASE is an open-source framework for generating synthetic conversational data — basically the kind of conversations you’d use to fine-tune a LoRA or QLoRA adapter for a specific industry.

The idea is pretty simple.

In regulated industries — healthcare, finance, legal, automotive, you name it — you can’t just take real customer conversations and train a model on them. Privacy rules make that a non-starter.

So instead, what you do is define what a good conversation should look like, and the system generates thousands of them without touching real customer data.

This diagram right here is really the heart of the system.

Six stages, left to right.
You define seeds, upload knowledge, import data if you have it, evaluate quality, generate conversations, and then export everything as a dataset that’s ready for training.

Today I’ll walk through the whole thing from scratch, end to end. By the end we’ll have a certified dataset ready for fine-tuning.

So let’s start here.

Alright — this is the pipeline view.

Each card is one stage in the process, and everything flows in order.

Seed Engineering is where you design the conversation blueprints.

Knowledge Base is where you upload domain material so the generator has real facts to work with.

Data Import is for bringing in conversations if you already have them in CSV or JSONL.

Quality Evaluation is where every conversation gets scored.

Synthetic Generation is where the LLM produces new conversations.

And Dataset Export is where everything gets packaged for fine-tuning.

You’ll notice some stages are locked, and that’s intentional.

You can’t evaluate conversations that don’t exist yet, right? So the system enforces the correct order so you don’t accidentally skip steps.

And down here you can track any jobs that ran — generation, evaluation, exports, all that.

Alright, let’s jump into the first stage.

This is the Seed Library.

Right now it’s empty because we’re starting from scratch.

So what’s a seed?

A seed is basically a blueprint for a conversation.

It defines who’s talking, what the situation is, how long the conversation should be, the tone, and — this is the important part — the quality standards the output has to meet.

If a generated conversation doesn’t meet those standards, it gets flagged.

So let me create one real quick.

First thing — domain.

I’ll pick Automotive Sales.

UNCASE comes with six domains built in — automotive, medical, legal, finance, industrial, education. You can add your own too, but honestly these cover most regulated environments already.

Next, language — Spanish.

That determines the language of the generated conversations.

For the scenario, I’ll write something like:
Customer interested in a mid-range SUV, comparing financing options and maybe trading in their current car.

Something realistic.

Now roles.

We need at least two — customer and sales agent.

The customer is browsing options and thinking about budget.
The sales agent knows inventory, financing programs, and how to guide the conversation.

The more specific you get here, the better the conversations turn out. This part actually matters a lot.

Now I’ll set the conversation length between six and twelve turns.

Long enough to feel real, but still focused.

Tone — professional. Although honestly, that part is a bit of personal preference.

Now this section is where things get interesting.

These are the quality thresholds — basically the minimum scores every conversation has to hit.

ROUGE-L measures structure and flow.
Factual fidelity checks if the facts are correct.
Lexical diversity makes sure the language isn’t repetitive.
Dialogue coherence checks if the conversation actually makes sense turn by turn.

These defaults are already pretty strong, but you can tighten them if you want higher quality datasets.

The important thing is that these aren’t suggestions — they’re enforced.

If a conversation misses even one threshold, it fails.

And of course, privacy.

PII removal is always on.

Under the hood this runs through Microsoft Presidio for detection and anonymization.

And the privacy score has to be zero.

Not low. Zero.

No names, no emails, no phone numbers, nothing.

That’s a hard gate.

Alright — seed created.

You can see it here in the library.

Let me create one more quickly for a different scenario.

This one will be a medical consultation — a patient with recurring headaches discussing medication options.

Roles are patient and doctor.

Slightly longer conversation range.

Done.

So now we’ve got two seeds across two industries, each with its own constraints and quality requirements.

Before generating conversations, it helps to give the system some domain knowledge.

Otherwise the model might hallucinate details.

Here you can upload documents — markdown files, text files, CSV.

You categorize them as facts, procedures, terminology, or reference material.

I’ll upload a product catalog — vehicle specs, pricing tiers, financing terms.

Tag it as facts under automotive sales.

Once uploaded, the system chunks the document automatically.

Each chunk becomes something the generator can reference when creating conversations.

For example, if the seed mentions SUV pricing, the generator can pull actual numbers from here instead of making them up.

That’s what helps the factual fidelity score stay high.

Alright — now this is where things get interesting.

This is the generation stage.

On the left we can see the seeds we created earlier.

I’ll select both of them.

This badge shows whether the backend is connected.

If it says API Connected, generation runs through whatever LLM provider you configured — Claude, GPT, Gemini, Ollama, whatever you’re using.

If the API isn’t available, there’s also a demo mode so you can still explore the full pipeline.

I’ll generate five conversations per seed.

So ten total — just enough to see the pipeline in action.

In production you’d probably run fifty or a hundred per seed.

Temperature controls how creative the model gets.

Lower values are more predictable, higher values introduce more variation.

I’ll leave it around 0.7 — a good balance.

The summary here confirms everything before running it.

Two seeds, five conversations each, ten total.

Looks good.

Let’s generate.

Behind the scenes, what’s happening is the system builds a prompt from the seed, includes the role definitions, constraints, knowledge chunks, and quality requirements.

Then it sends that through the LLM gateway.

There’s also a privacy interceptor checking both the prompt and the response for PII.

After that, the output gets parsed into the structured conversation format.

Alright — done. Ten conversations generated.

Now let’s see how they performed.

This is the evaluation dashboard, and honestly this is what makes UNCASE different from just prompting an LLM and hoping for the best.

At the top we have total evaluations, pass rate, average composite score, and privacy violations.

That last one should always be zero.

If it’s not, something definitely needs attention.

This chart shows the distribution of scores.

Ideally most of your data ends up on the right side — that means higher quality conversations overall.

And this chart here is probably the most useful visualization in the entire dashboard.

The dashed line represents the minimum thresholds defined in the seed.

The solid line shows how the generated conversations actually performed.

If the solid line dips below the threshold anywhere, you immediately know which dimension needs work.

Maybe diversity, maybe factual grounding, maybe coherence.

It’s very easy to diagnose issues from this view.

And down here you can see every conversation with all its scores.

Anything below threshold is highlighted so it stands out immediately.

The composite score is basically the minimum of the metrics, but only if privacy and memorization pass.

If privacy fails, the whole score drops to zero automatically.

Privacy is always the hard gate.

Now let’s look at the conversations themselves.

Here’s the conversation browser.

On the left you have the list, and on the right you have the full conversation detail.

You can filter by domain, validation status, conversation type, and rating.

That becomes really useful once you have hundreds of conversations in the system.

Let’s open one.

Here’s the full dialogue.

User messages are in blue, assistant responses in gray, system messages in violet.

If the conversation includes tool calls, those appear as well.

You can read through the whole exchange.

You’ll notice it follows the scenario defined in the seed — the customer is asking about SUVs, the agent presents options, financing comes up, trade-in discussion happens.

Everything flows from the structure we defined earlier.

Now one thing I really like here is that every message is editable.

If something could be phrased better, you can just adjust it directly.

So let me do a quick fix here.

Maybe refine the question slightly.

Done.

And if you’re editing an assistant message and type the less-than symbol, the tool picker appears.

These are domain-specific tools.

For automotive you might see inventory checks, financing calculations, trade-in appraisal tools.

I’ll add one here.

The system inserts the tool call structure automatically, so you don’t have to write the JSON manually.

Below the conversation there’s a review panel.

You can tag conversations to organize them, rate them, and leave notes for your team.

For example, maybe this one is about financing.

I’ll tag it, give it four stars, and mark it as valid.

Only validated conversations will be included in the final export.

And down here the system shows which fine-tuning templates are compatible with this conversation structure.

Different models support different formats, so this helps avoid formatting issues later.

Now let’s export the dataset.

This is the final stage of the pipeline.

Everything we’ve done — defining seeds, adding knowledge, generating conversations, evaluating quality, reviewing and editing — it all leads here.

I’ll name this dataset automotive-sales-v1.

Next, choose a template.

UNCASE supports several formats like ChatML, Llama, Mistral, OpenAI formats, and others.

I’ll go with ChatML since it’s widely supported.

I’ll also export synthetic conversations only.

You can see the preview updating in real time — conversation count and estimated size.

Pretty straightforward.

But this part here is something people in regulated industries really appreciate.

The quality certificate.

This shows the pass rate, average scores, privacy validation, and seed provenance.

Basically documentation proving that the dataset meets quality and compliance requirements.

You can download the full report.

It includes compliance mapping, audit details, dataset identification, and verification information.

And finally, we export.

The file downloads ready for training.

Every conversation in it is traceable back to a seed, scored across quality metrics, and certified to contain zero PII.

So yeah — that’s the full pipeline.

Define seeds, ground them with knowledge, generate conversations at scale, measure quality, review them, and export a certified dataset ready for fine-tuning.

No real data exposed. Full traceability. Quality enforced, not assumed.

And it works across multiple industries out of the box.

Healthcare, finance, legal, automotive, industrial, education — you name it.

UNCASE is open source and available on GitHub.

Thanks for watching.

