# The Advice Is Good. The Assumption Behind It Is Wrong.

*On AI disruption, the industries that can't just "adopt AI," and why the real crisis isn't the one people are writing about.*

---

There's a piece circulating right now that I think is one of the most honest things written about AI disruption — and also one of the most recklessly incomplete. Not because the author is wrong. He isn't. The ground is shaking. The models released in the first weeks of 2026 are not incremental improvements. I've run enough fine-tuning experiments — hundreds of training runs with LoRA and QLoRA, tuning hyperparameters across datasets I can't discuss publicly, watching a model go from generating nonsense to generating something I couldn't have written better myself — to know the difference between hype and a phase transition. This is a phase transition.

But there's a version of this conversation that keeps happening in public, and it bothers me more each time I see it.

The version that says: *here's what's coming, here's how fast it's coming, and here's what you should do — sign up for the paid tier, prompt it harder, stop being precious about your expertise.*

That advice is not wrong for most people. It's wrong for exactly the people who need a real answer.

---

## The Doctor in the Room

A few days ago, a story surfaced that I haven't been able to stop thinking about. Under a proposed federal restructuring of rural healthcare, AI avatars would replace physicians in underserved communities — part of a broader push that involves cutting a trillion dollars from health spending. The AI would handle the consultation. The AI would do the triage. The AI would be the first — and in many rural contexts, the only — point of contact between a patient and something resembling medical judgment.

I want to be precise here because precision matters: I don't think AI is categorically incapable of supporting rural healthcare. I think deploying a generic model — one trained on data from urban hospital systems, from medical literature written for specialists, from Q&A datasets scraped from the internet — into the home of a sixty-year-old woman in a community where *"me duele el pecho del cansancio"* has a specific and different diagnostic distribution than anything the model has ever seen, is not AI adoption. It's negligence rebranded as efficiency.

This is what happens when you take the general advice — "AI is here, adopt it now, stop resisting" — and apply it to domains where the advice was never designed to land.

---

## The Industries That Can't Just Adopt

There's a category of organization that appears in every conversation about AI disruption as a cautionary tale: *the reluctant ones*. The law firms that say it's not ready. The hospitals that say it's too risky. The financial advisors who say the model doesn't understand nuance. The manufacturers who say their processes are too specific.

We treat their hesitation as fear. As Luddism. As the same denial pattern that preceded every previous disruption.

I'd like to propose something different: that for a specific and significant subset of these organizations, the hesitation is not fear of the technology. It's an accurate read of a problem that the mainstream conversation refuses to name directly.

**Their most valuable data — the data that would make a specialized AI genuinely useful — is the data they are legally, ethically, and contractually prohibited from using to train one.**

A hospital system that has processed three million patient interactions holds an extraordinary asset for training a clinical AI. It also holds three million instances of information protected under medical privacy law, subject to informed consent requirements, and potentially implicated in privilege and liability frameworks that don't have clean answers yet. The legal team isn't being obstructionist. They're being correct.

A financial advisor whose firm has twenty years of client portfolio conversations, crisis call transcripts, and estate planning discussions has the raw material for one of the most useful AI assistants imaginable. They also have twenty years of fiduciary-protected information that cannot be sent to a cloud API under any reasonable interpretation of their regulatory obligations.

The managing partner who spends hours a day with AI — the one in that viral post, the one who's "blown away" — is doing so with general-purpose models on general-purpose tasks. Not with his clients' privileged communications. That distinction is doing enormous work in the narrative, and it keeps disappearing.

---

## The Five Things Nobody Wants to Say Out Loud

I want to be honest about the counterarguments, because I think they deserve more than dismissal.

If fifty percent of white-collar roles vanish in five years, you don't get an AI economy. You get a deflationary collapse where nobody has the capital to consume what AI is producing. The productivity gains accrue to ownership, not to displaced workers, and the consumption base that sustains the economy contracts faster than the efficiency gains can offset it. This is not a new observation — it's Keynes's technological unemployment problem — but the scale and speed of the current transition creates a version of it with no obvious historical precedent. Nobody in the "$20/month, go adopt AI" conversation is seriously engaging with this.

The exponential growth curves being cited — tasks doubling every seven months, model capability doubling every twelve — are measured in compute. Compute requires electricity. Electricity requires water for cooling. Water is not infinitely available. We are already in a world where data centers compete with irrigation and municipal cooling for grid capacity, where the physical infrastructure of AI expansion is running into thermodynamic and geographic constraints that no amount of optimization fully resolves. The ceiling is visible. Not imminent, but visible. Extrapolating exponentials past physical limits is not analysis; it's faith.

When AI-driven disruption begins to materially threaten the tax base — when unemployment benefits, retraining programs, and social stabilization costs exceed what a concentrated AI economy generates in revenue — governments will intervene. Robot taxes, resource nationalism, mandatory human labor quotas in regulated industries: these are not speculative policy proposals, they're already in circulation in the EU and parts of Latin America. The regulatory environment that makes AI adoption look clean today will not look the same in thirty-six months.

The thing being called "taste" and "judgment" in the most capable current models is something more specific and more limited: extraordinary statistical consensus about what the best option looks like given everything that's been done before. That is genuinely impressive and genuinely useful. It is not the same as the capacity to generate something net new from a position of motivated ignorance — to ask the question nobody thought to ask, to see the structure nobody saw, to be wrong in the specific way that turns out to be more right than being right. I say this not to diminish the models but to be precise about what they are, because precision matters when you're deciding what to trust them with.

And hardware. The final ceiling in model scaling isn't algorithmic. It's physical. We are approaching the limits of what current fab processes can deliver, the limits of what available power grids can supply to training clusters, the limits of what the global supply chain for specialized silicon can produce. These constraints don't halt progress. But they do create discontinuities — periods where capability improvement stalls while infrastructure catches up — that the smooth extrapolation curves don't capture.

I'm not raising these to say the disruption isn't real. It is. I raise them because the organizations being advised to "just adopt" are often the ones with enough operational complexity to understand that these constraints exist, and dismissing their caution as ignorance is both unfair and counterproductive.

---

## What I Know From the Inside

I work with fine-tuning. Specifically, I work with LoRA and QLoRA on domain-specific datasets — automotive sales conversations, customer interaction logs, structured dialogues where the goal is a model that speaks the specific language of a specific operation in a specific region. I've done enough training runs to develop intuitions about what makes a dataset good, what makes a model overfit, what the difference feels like between a model that has learned a domain and a model that has memorized an artifact.

I also work, with significant care, with data that I cannot send anywhere.

This is not an abstract problem. It is a daily operational reality. The conversations that would make my models best are exactly the conversations I have the most obligation to protect. The gap between "what I can legally train on" and "what would produce the best model" is not a technical problem. It is a structural one, and it requires a structural answer.

The answer I've been developing — and this is where I want to be honest about where I'm working rather than just where I'm observing — is a framework for abstracting the knowledge of a domain into what I call seed structures: parametrized representations of conversational patterns that carry the factual and qualitative essence of an interaction without carrying any of the sensitive content. From those seeds, you generate synthetic data. From synthetic data, you train. The model learns the domain from the pattern, not from the instance.

We call this UNCASE — Unbiased Neutral Convention for Agnostic Seed Engineering Privacy-Sensitive Synthetic Asset Design Architecture. The name is a mouthful. The problem it solves is not.

The empirical backing for this approach is not speculative. Microsoft's Phi-2 demonstrated that models trained exclusively on high-quality synthetic data can outperform models trained on real data many times larger. The MIMIC-III synthetic dataset proved that clinical data can be generated with sufficient fidelity for medical research without exposing a single real patient record. Stanford's Alpaca proved that 52,000 generated instructions can produce a specialized model competitive with systems that cost orders of magnitude more to train. The precedent exists. The tools exist. What hasn't existed, until now, is a systematic framework for applying this approach to the specific problem of organizations with sensitive data and domain-specific knowledge they cannot share.

---

## The Real Crisis, Precisely Stated

The crisis is not that AI is arriving fast. It is.

The crisis is not that some industries are resisting. Some resistance is well-founded.

The crisis is this: the industries with the most to gain from AI specialization — and the most to lose if they get it wrong — are being handed advice designed for a different problem. They're being told to adopt tools built on other people's data, deployed on infrastructure they don't control, producing outputs they can't fully audit, for decisions that carry liability their vendors don't share.

And in the gap between "here's what AI can do" and "here's how you do it without compromising what makes you who you are," there is an AI avatar sitting in a rural clinic, generating a diagnosis from a training set that has never heard the way a farmer in Tamaulipas describes chest pain.

That gap is not a technology problem. It is an infrastructure problem. And infrastructure problems require frameworks, not advice.

---

## On the People Who Know

I want to say something directly to the clinicians, lawyers, financial advisors, and domain experts in regulated industries who have read the disruption literature and felt a specific kind of frustration I recognize — the frustration of watching someone describe a problem you live and offer a solution that doesn't fit your constraints.

You are not wrong to be cautious. You are not Luddites. You are people who understand that the obligation of care you carry — to patients, to clients, to the information entrusted to you — is not a weakness to overcome on the way to AI adoption. It is the thing that makes your expertise worth replicating in the first place.

The solution is not to abandon that obligation. It is to build the infrastructure that honors it.

The question is not *whether* AI arrives in your industry. It will. The question is whether it arrives on your terms — with your knowledge encoded, your constraints respected, your data protected — or on someone else's.

I know which version produces a better model. I also know which version produces a better world.

The work is harder than "$20 a month." The result is also worth considerably more.

---

*This post is part of ongoing work on UNCASE — a framework for generating high-quality synthetic conversational data for LoRA fine-tuning in privacy-sensitive industries. If you work in healthcare, law, finance, or any field where your most valuable knowledge is also your most protected data, I'd like to hear from you.*

