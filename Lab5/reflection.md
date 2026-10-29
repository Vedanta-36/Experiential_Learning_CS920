# Reflection

(The handout lists the questions only in the lab sheet; these answers cover the usual four. Match the headings to your sheet.)

**1. Which tool was most useful, and why?**
Bandit surfaced the issues with the highest real-world impact (disabled TLS verification, shell injection through `tar *.csv`, a deprecated TLS version). Pylint found the most items and caught a real bug (mutable default argument). Flake8 was quick and mechanical, mostly layout.

**2. Were there false positives or things the tools missed?**
Bandit's `B404` (importing `subprocess`) is informational and disappears once subprocess is not needed. More important are the misses: no tool flagged the hardcoded API key, the `> 75` eligibility bug, the string comparison of dates, or CSV formula injection. I only found them by running the program and reading the output.

**3. How did you prioritise fixes?**
By severity and impact: Bandit High (verify=False, wildcard/shell injection), then Medium (timeout, TLS version, shell=True), then correctness bugs, then Pylint quality items, then Flake8 formatting last because it is cosmetic and cheap.

**4. How does static analysis help long-term, and what are its limits?**
It gives a consistent, automatic review before code is merged, makes style uniform and catches well-known insecure patterns early. It cannot understand intent (an off-by-one against a business rule) or secrets in context, so it complements tests and human review. Running it in CI keeps the score from regressing.
