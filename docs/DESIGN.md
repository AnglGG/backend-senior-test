# Design — <feature you picked>

<!--
Replace <feature you picked> in the title with the option you chose (e.g. "AI workout coach", "Exercise search", "What should I train today?", or your own title for Option D).

Write your design directly under each heading below. The structure is fixed; the content is yours. Don't rename the sections or add new ones.
-->

## 1. Solution overview

<!--
A short, plain-language description of the approach. Reader-first: someone who hasn't been in your head should be able to read this in two minutes and walk away with the shape of the solution.

Cover:
- The problem and the consumer. What are we solving and for whom? What signals from the existing schema matter?
- The high-level idea. What's the approach? What are the main moving parts?
- The public surface, if any. Route, method, query params, request body, response body. Pseudocode is fine.
-->

## 2. Reasoning & decisions

<!--
The interesting half of the document. For each non-trivial decision, say what you chose, what alternatives you considered, and why you landed where you landed. Argument, not assertion. Citing how other apps approach the same problem (Hevy, Strava, Whoop…), a benchmark you ran, a paper or library you read — all of these count.

Address explicitly:
- Approach end-to-end. How does a request flow from URL conf to response? Show the service signatures and the data flow between them; don't write the bodies.
- Data model touches. New tables, columns, indexes? Any denormalization? Any background job? If your design caches anything, name the key, the TTL, and who invalidates it. If nothing applies, say why.
- Performance & scale. Where does it hurt at 100 / 10k / 1M users? Read volume, write volume, cache hit rate. First bottleneck? If you add an index or a column, how do you ship it on a 50M-row table without locking it?
- Tradeoffs and what you'd cut. What did you choose NOT to do, and why? What would you build first if you only had a sprint?
-->

## 3. Codebase tree

<!--
A folder/file sketch showing where the new code would live and how it relates to the existing structure of this repo. Reader should be able to glance at it and see whether you respect the vertical-slice layout, where the cross-domain boundaries are, and what new modules or models you're introducing.
-->

## 4. Task breakdown

<!--
A list of the tickets that would come out of this design. Tasks should be parallelisable, not sequential — ideally one "core" task that unblocks N tasks others can pick up in parallel. Each task: a one-line description, a rough estimate, and the dependency it has (if any).

Close with **open questions**: what you'd need to ask the team before opening the first ticket.
-->
