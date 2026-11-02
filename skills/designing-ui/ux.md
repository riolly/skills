# Jobs and structure

The steps make a screen read well. This file checks that it is the right screen for the people who use it: that each job they come for has a short path, and that the controls take the shape of the data. Use it after step 2 has named the jobs.

## Walk each job

Walk each job from step 2 on the rendered screen, at about 400px wide and then wider, with realistic data: the project's seed or fixture data, or the most realistic records you can make. Say which you used. Start where the person arrives, such as a nav item, a notification or a shared link, and end where they go next. Count the taps, the screens, and the things the person must remember from one screen to the next. Done when every job has a path and a count, or is reported as having no path.

## Lenses

Check each job against each lens and record pass or fail with what you saw. Each failure becomes a proposal.

- **Hidden state.** A value that changes how a record is treated, such as a status, a role, a pending change or an override, is visible wherever the record is shown, without opening anything.
- **Model match.** Controls take the shape of the data. Exclusive choices are one control; independent flags are separate switches; the same kind of setting uses the same control everywhere.
- **Domain words.** Labels, options and messages use the words the people use, never field, enum or table names such as `is_active` or `ROLE_ADMIN`.
- **One concept, one place.** Controls that serve the same job, such as the filters of a list or the settings of one thing, live together.
- **Effort.** The most frequent job's control comes first, on phones too. The app fills in what it knows: defaults, prefilled values, the last choice. Work done on many records at once has a bulk action.
- **Roles.** Each role sees the controls it can use. A control the person cannot use is hidden, or shown disabled with the reason when knowing it exists helps them.
- **True at every moment.** What the screen claims stays correct across time: first use, the day of the event, after a period ends, a month with nothing in it. Step 6 owns the loading and empty states; this lens checks what the screen says.
- **Cost of mistakes.** A reversible action takes effect at once and offers undo. An irreversible one asks for confirmation and names what will be lost.
- **Way in and way out.** The person reaches the screen from where the job starts, and after the job the screen links to where they go next.

## Proposals

Label each proposal with its level, which decides what happens to it:

- **Polish** changes how a control looks or reads. Apply it under the usual rules.
- **Restructure** moves, merges, reveals or removes controls on a screen. Apply it when building; propose it in a review or a restyle. Removing a control that exists always needs the user's approval, because someone may depend on it.
- **Rethink** changes the flow or the data model. Propose it with its trade-off; never apply it.

A restructure or a rethink names what it fixes: a lens failure, with the job's count before and after, or the state it reveals. A screen that passes every lens gets one sentence on how its structure serves its jobs, in place of a proposal.

## Report order

Report the jobs first, with their sources and counts, then restructure and rethink proposals, then floor failures, then polish. Mark each assumed job, so the user can correct it before acting on the proposals that rest on it.
