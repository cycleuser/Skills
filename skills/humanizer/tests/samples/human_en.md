I spent two weeks trying to get the export feature to work. It still doesn't.

The problem is boring: the CSV writer quotes every field, and our downstream parser treats quotes as part of the value. Three engineers looked at it before anyone noticed. The fix was four characters.

What surprised me was how long we tolerated the bug. It shipped in March. Support got maybe a dozen tickets. Nobody connected them, because each report described a different symptom — a stray comma here, a missing column there.

I don't have a clean lesson for you. We got lucky that a customer sent a screenshot. If she hadn't, we'd probably still be guessing.
