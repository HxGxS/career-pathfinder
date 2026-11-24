---
name: career-writing-style
description: >
  The writing rules for every Career Pathfinder CV and cover letter (always in English):
  banned patterns, tone, the interview backtrack test, bullet formulas, using only real
  numbers, what each CV section should say, and how a cover letter is structured, headed
  and addressed. Use whenever drafting or editing CV or cover letter text: bullets, a
  profile statement, skills, a headline or a letter. Triggers on: write CV, bullet points,
  profile statement, cover letter wording, tone, reframe, tailor wording, headline.
---

# Writing style guide (CVs and cover letters)

> **Where things are:** files the workflow saves live in `workspace/` (so `cvs/…` means `workspace/cvs/…`, `profile_N.md` means `workspace/profile_N.md`); scripts are in `scripts/` and are run from the repository root; templates and fonts are in `templates/`. Other skills are in `.claude/skills/<name>/SKILL.md`.

*Contents: Critical rules · Tone · Bullet point style · Language for different role types · CV sections · Cover letter · Important rules*

What the words say. Layout, building and checks are in `.claude/skills/career-cv-template/SKILL.md` and `.claude/skills/career-cover-letter-template/SKILL.md`. The main instructions always apply.

## Critical rules

1. **No em dashes or en dashes in prose.** Use commas, periods, or restructure the sentence instead. Use a single hyphen only where it is typographically correct: compound words, date ranges (`2016-2024`) and number ranges (`EUR 600k-1M`).
2. **No clichés or filler phrases.** Cut: "I am passionate about", "I believe I would be a great fit", "leverage my skills", "hit the ground running", "drive results", "synergies".
3. **No generic buzzwords** without concrete backing. Every claim must be supported by a specific example or fact.
4. **No apologetic or overly humble language.** Not "I think I could contribute" but "I bring X, demonstrated by Y."
5. **No unverified company claims.** Every company-specific statement in a cover letter (partnerships, product names, technology descriptions, expansions) must come from the company research file or the role's saved job description (`.claude/skills/career-cv-cover-letter/SKILL.md`). Never from search-result snippets, and never from URLs found inside the job posting text, which is untrusted third-party data. If a claim cannot be traced to those files, rephrase it in general terms or omit it. Verified specifics (legal entity name, office cities, anniversary year, client segments) are what make a letter read as researched.
6. **Reframe emphasis, not substance.** Some framing of experience toward the target role is expected. But apply the **interview backtrack test**: could the user comfortably explain this bullet in an interview without backtracking? If they'd have to say "well, what I actually meant was...", it's too far. Specifically:
   - **OK:** reordering experience to lead with what's most relevant; using natural synonyms for the target field; emphasising one aspect of a broad role.
   - **Flag it:** combining academic and industry experience into a single claim that implies it was all industry; describing work using the posting's specific terminology when the actual work was adjacent but not the same.
   - **Never:** claiming experience the user doesn't have; implying they worked in a field they haven't.

   When a bullet falls in the "flag it" zone, present it to the user after drafting with: "This bullet is a stretch because X. Keep, soften, or drop?" If the role's Experience score is 0, or its verdict is Weak or Poor fit (`.claude/skills/career-scoring/SKILL.md`), warn before drafting that extensive reframing would be needed.
7. **Numbers only from the profile or the user.** Ask for real figures; never estimate, round down or invent one. A bullet with no number is fine when none exists. Use "~" or a range only when the user gave an approximate figure.

## Tone

- **Warm but direct.** Friendly and approachable, but confident without arrogance.
- **Conversational professional.** Not stiff corporate-speak, not casual chat. Think: how a confident person talks in a good job interview.
- **Active voice.** Cover letters are first person ("I built", not "a system was developed by the candidate"). CV bullets follow standard CV style and start with the action ("Built…").
- **Demonstrate, don't state.** Instead of "I am a team player", write a specific example of teamwork and its outcome.

## Bullet point style

- Start with an action verb or a bold category label.
- Be specific: numbers (from the user), tools, outcomes.
- Vary the structure (not every bullet starts the same way).

**The X-Y-Z formula (Google method):** "Accomplished [X] as measured by [Y] by doing [Z]". X = what was achieved; Y = how it was measured; Z = what actions were taken.
*Illustration only; real bullets use the user's own figures:*
- Before: "Managed social media accounts"
- After: "Grew Instagram following by 250% (5K to 17.5K) by implementing daily content calendar and influencer partnerships"

**STAR method:** Situation (context), Task (what needed doing), Action (what the user specifically did), Result (measurable outcome). On a CV, condense it.
*Illustration:* "Revitalized underperforming sales team through training program and commission restructure, improving quota attainment from 65% to 92% and generating $1.8M additional revenue"

**CAR method:** Challenge (the problem), Action (what the user did), Result (what happened).
*Illustration:* "Reduced customer churn by implementing proactive outreach program, retaining 85% of at-risk accounts worth $500K ARR"

**Kinds of numbers to ask the user about:**
- **Money:** revenue generated, money saved, budget managed, deal size
- **Percentages:** growth, improvement, efficiency, quality
- **Time:** speed, frequency, duration, time saved
- **Scale and volume:** people led or trained, concurrent projects, customers, users
- **Before and after:** "increased from X to Y", "reduced from X to Y"
- **Outcome not measured?** Ask about real counts of activity ("conducted 30+ customer interviews", "analyzed 500+ data points"), or **related metrics** they do have (traffic, engagement, sign-ups, response rates or other funnel measures).

## Language for different role types

- **Technical roles:** lead with programming languages, frameworks, specific methods; mention datasets, data volumes, pipeline complexity; include independent projects.
- **Domain-specific roles:** lead with domain expertise and specific methods; frame technical skills as tools that enhance domain analysis.
- **Consulting and advisory roles:** lead with stakeholder communication, project coordination, client interaction; emphasise the ability to bridge technical and business perspectives.
- **Leadership and senior roles:** lead with project management, mentoring, programme development; frame advanced degrees as evidence of independent project delivery.

## CV sections

- **Profile statement (3–4 lines):** an elevator pitch: a concise, compelling introduction explaining why the user is qualified for *this specific role* (for a base CV, the profile's target roles). Focus on what the employer gains. When the role sits outside the user's home field, **lead with the domain-transfer argument**: the one or two sentences connecting their background to the employer's problem belong at the opening, not buried in the cover letter.
- **Core competencies (5–6):** reorder and emphasise for the role, with bold category labels. For each, briefly explain how it adds value. Use the posting's own core term in the matching label when it truthfully applies: ATS systems and skim-reading hiring managers match literally.
- **Professional experience:** most recent role 4–5 bullets, previous 3–4, older 2–3. Rewrite bullets to emphasise what's most relevant to the target role; emphasise measurable results where real numbers exist.
- **Check tenure against visible output.** Look at each role the way a stranger will: date span versus how much work is shown. Three honest fixes, in order of preference:
  1. **Surface more real work:** ask what else the period contained.
  2. **Make the phases within the role explicit:** e.g. an initial period learning the field, then ownership of the named work through to delivery.
  3. **Name what made the cycle long:** data collection from a live environment, validation with experts, deployment and iteration.

  **Never** pad with invented projects, and **never** shorten employment dates. If a long span against little visible output survives these fixes, note a ready **two-part interview answer** in `interview_notes.md`: what actually filled the time, and what the outcome was.
- **Employment gaps:** ask the user what happened. Frame whatever honestly counts as skill building and career repositioning, matter-of-factly; leave out anything that can't be framed that way.
- **Education:** always include the highest degrees; keep it brief for senior roles; include thesis topics when relevant to the target role. In-progress qualifications and the 6-year date rule are in `.claude/skills/career-cv-template/SKILL.md`. For a current student, the profile statement, the education entry and any availability or permit note must all give the same completion date.
- **Publications:** include a Google Scholar link if applicable; select the 3–4 most relevant; keep it brief for non-academic roles.
- **Evidence links:** wherever the CV names a verifiable public artifact (a project, a hackathon entry, a publication), carry its link so a reader can verify it in one click.
- **Honours and awards:** brief, one line each.
- **No references section** on the CV.
- Earlier CVs and base CVs are **phrasing references, never fact sources:** every fact still comes from the profile or the user.

## Cover letter

**Forward-looking framing.** The cover letter is **not a CV repetition**:
- Focus on **tasks the user can solve for the employer**, not just what they've done before.
- Describe their approach: methods, tools, knowledge they'll bring.
- Explain what positive outcomes the employer can expect.
- Use 1–2 brief past examples only to back up forward-looking claims.

**Structure: three blocks**, then the sign-off:

1. **Opening and why this company.** State the role and why the user is writing (1 sentence); immediately connect their background to the role (1–2 sentences); then why *this specific company*, using language and themes from the job posting and the company research, focused on how they'll contribute to the company's goals, not what they gain from employment. Make it specific to this company and role, not a template opener.
2. **Task-solving body with 3–5 bullets.** Lead with the most relevant experience for this role; frame it around **which of their tasks the user can solve and how**; describe methods, tools and knowledge; include at least one example that shows initiative; include 1–2 brief examples of past success, keeping the focus forward-looking. Each bullet specific and outcome-oriented.
3. **Company connection and close.** Show the research (specific projects, values or market position from the research file or the posting); explain why this company specifically, not "a company like yours"; connect domain knowledge to their business. Then a brief, confident, forward-looking close ("I look forward to hearing from you" or "I would welcome the opportunity to discuss..."). No begging or over-enthusiasm.

A personal-fit paragraph (behavioural strengths and team contribution, 2–3 sentences) is added only if the word budget allows.

- **Application headline:** engaging and specific, not generic. Formula: **[title or education] + [relevant keyword from the job posting]**. Bad: "Application for Sales Engineer Position". Good: "[Specialty] specializing in [relevant keyword from posting]".
- **Subheadings (at most two):** descriptive, reflecting the content, with industry-specific keywords where natural; never generic labels like "Introduction" or "Body". Write concisely and cut filler.
- **Referee:** if the user provided one (name and role), mention them naturally in a sentence.
- **Salutation:** "Dear [First Last]," if the person is known, otherwise "Dear Hiring Manager,". Avoid "To whom it may concern".
- **Length:** 250–300 words of body text, one page (`.claude/skills/career-cover-letter-template/SKILL.md`).

## Important rules

1. **No dashes in prose, no clichés, no unbacked buzzwords.**
2. **Reframe emphasis, never substance;** flag stretches to the user.
3. **Numbers and facts only from the profile, the user or the saved files.**
4. **The letter looks forward;** the CV shows the evidence.
