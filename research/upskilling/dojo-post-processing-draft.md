# Dojo: post-processing, soft draft (2026-11-20)

Status: soft draft, to elaborate later. More material will come from void when it is back
(the curriculum draft `upskilling/curriculum-draft.md` from W33 is not on nixed).

The dojo (PLAN.md W33) teaches from the owner's Readwise library and current work. Raw sources
(video transcripts, podcasts, articles, agent sessions) are not fit to learn from as they stand.
This pipeline turns them into material that is faster to read, more likely to stick and more
meaningful.

## Stages

1. **Repair the text.** Fix the failures that technology introduces before anything reads for
   meaning:
   - speech-to-text oddities: words run together ("Iwas", "thisone"), homophones and misheard
     names (model names, people, products), missing punctuation, rolling-caption repeats;
   - structural junk: sponsor reads, intros and outros, filler, timestamps in the wrong place;
   - format damage from scraping: broken lists, lost headings, duplicated paragraphs.
   Keep a link from every repaired passage back to the original span (offset or timestamp), so a
   repair can always be checked.
2. **Segment.** Split into ideas, not paragraphs: one claim or technique per unit, with its
   evidence and the speaker's confidence.
3. **Sentiment and stance.** For each unit: is the speaker for, against or unsure, and how strongly?
   Is it experience, opinion, rumour, or a vendor claim? Vendor and AI-lab announcements are weighted
   low (`build-loop` `roles.md` §2b). Track how the collective temperature on a topic moves over time.
4. **Relate.** Link each unit to the owner's work: which skill, project or decision it bears on, what it
   agrees or conflicts with, and what is new relative to earlier digests.
5. **Shape for a human.** Rewrite for the owner:
   - shortest faithful form first, with the source quote one click away;
   - a worked example or failure mode where the source has one;
   - one practical exercise or check question per lesson;
   - plain language, no jargon the source did not need.
6. **Make it stick.** Turn the best units into spaced-repetition items: Readwise highlights with a
   short note saying why it matters. At most one per automated read, approved by the owner first
   (`practice-watch` "Readwise"). Track recall and drop items that stop being useful.

## Open questions

- Which sources go first: videos (the worst text), or the Reader shortlist?
- Repair with a model, or rules first and a model only for what the rules cannot fix?
  How do we check that a repair did not change the meaning?
- Where does sentiment come from: a small local classifier, or the reading model with a rubric?
  How is it scored?
- What does a lesson look like on the phone (Reader, Taildrop, an HTML page)?
- How does the dojo schedule lessons around active projects (W33: at least one a week per project)?
