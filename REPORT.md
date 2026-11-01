# Prompt Engineering Report: few-shot, chain-of-thought and structured output

All prompts and outputs below were produced by `prompt_lab.py` and are shown exactly as the model returned them. Per-call prompts are also stored in full in `results/*.jsonl`.

| Setting | Value |
|---|---|
| Model | `gemini-3.5-flash-lite` |
| Temperature | 0.7 |
| Runs per input and variant | 2 |
| Date | 2026-11-01 |
| Hidden-thinking setting used for the chain-of-thought test | `thinking_level="minimal"` (see the thinking-tokens column: if the direct prompt still shows thinking tokens, it reasoned internally) |

## 1. Zero-shot vs few-shot: sentiment classification

**Task:** classify each review as `positive`, `negative`, `neutral` or `mixed`. Gold labels were written by me, so a few (sarcasm, mild negation) are debatable. The two prompts are identical except that few-shot adds 5 labelled examples.

**Prompt template: `zero_shot`** (`{input}` is replaced by the review)

```
Classify the sentiment of the following review as one of: positive, negative, neutral, mixed.

Review: {input}
Sentiment:
```

**Prompt template: `few_shot`** (`{input}` is replaced by the review)

```
Classify the sentiment of the following review as one of: positive, negative, neutral, mixed.

Review: The battery life is amazing and setup took two minutes.
Sentiment: positive

Review: Customer support ignored me for a week. Never again.
Sentiment: negative

Review: The package contains a charger and a manual.
Sentiment: neutral

Review: Loved the design, hated the price.
Sentiment: mixed

Review: Yeah, because crashing every hour is exactly what I wanted.
Sentiment: negative

Review: {input}
Sentiment:
```

**Scoring.** *Strict* = output is exactly one label word and it matches gold. *Lenient* = earliest label word mentioned in the output matches gold. *Consistent* = every run on the same input gave the same lenient label.

| Variant | Output is exactly one label | Strict accuracy | Lenient accuracy | Consistent across runs |
|---|---|---|---|---|
| zero_shot | 2/20 (10%) | 2/20 (10%) | 20/20 (100%) | 10/10 (100%) |
| few_shot | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) | 10/10 (100%) |

**Per-input outputs** (cells truncated; ✓ = strict-correct; complete text is in the raw section below)

| ID | Review | Gold | zero_shot | few_shot |
|---|---|---|---|---|
| S1 | Absolutely love this phone, the camera is stunning! | positive | ✓ positive / ✓ positive | ✓ positive / ✓ positive |
| S2 | Stopped working after two days. Total waste of money. | negative | ✗ Sentiment: negative / ✗ Sentiment: negative | ✓ negative / ✓ negative |
| S3 | It arrived on Tuesday in a brown box. | neutral | ✗ Sentiment: neutral / ✗ Sentiment: neutral | ✓ neutral / ✓ neutral |
| S4 | Great screen, but the battery barely lasts half a day. | mixed | ✗ Sentiment: mixed / ✗ Sentiment: mixed | ✓ mixed / ✓ mixed |
| S5 | Oh wonderful, another update that breaks everything. Thanks… | negative | ✗ Sentiment: negative / ✗ Sentiment: negative | ✓ negative / ✓ negative |
| S6 | Not bad at all, honestly better than I expected. | positive | ✗ Sentiment: positive / ✗ Sentiment: positive | ✓ positive / ✓ positive |
| S7 | The food was fine. Nothing special, nothing terrible. | neutral | ✗ Sentiment: neutral / ✗ Sentiment: neutral | ✓ neutral / ✓ neutral |
| S8 | Service was painfully slow, yet the pasta was the best I've… | mixed | ✗ Sentiment: mixed / ✗ Sentiment: mixed | ✓ mixed / ✓ mixed |
| S9 | Wish I had bought this sooner. Zero complaints. | positive | ✗ Sentiment: positive / ✗ Sentiment: positive | ✓ positive / ✓ positive |
| S10 | Would not recommend. The staff were rude and the room was d… | negative | ✗ Sentiment: negative / ✗ Sentiment: negative | ✓ negative / ✓ negative |

### Analysis (write this yourself)

**What changed.** Zero-shot scored 2/20 strict (10%) because in 18 of 20 runs the model put a prefix in front of the label (for example `Sentiment: negative`) instead of returning just the label. Few-shot scored 20/20 (100%) and returned the bare label every time. Lenient accuracy was 100% for both prompts, so the five examples fixed the **output format**, not the model's ability to classify: it already got every review right without examples, including the sarcastic S5 and the negated S6.

**Where it did not help.** Few-shot gave no gain in classification accuracy itself, and neither prompt showed any inconsistency across runs at temperature 0.7. With only 10 fairly clear-cut reviews (and gold labels that I wrote myself), this test is too easy to show a difference in classification quality. A harder, more ambiguous dataset would be needed to test that.

### Complete raw outputs

<details><summary>zero_shot · S1 · run 1 · ✓ strict-correct</summary>

**Input:**

```
Absolutely love this phone, the camera is stunning!
```

**Raw output (unedited):**

```
positive
```

</details>

<details><summary>few_shot · S1 · run 1 · ✓ strict-correct</summary>

**Input:**

```
Absolutely love this phone, the camera is stunning!
```

**Raw output (unedited):**

```
positive
```

</details>

<details><summary>zero_shot · S1 · run 2 · ✓ strict-correct</summary>

**Input:**

```
Absolutely love this phone, the camera is stunning!
```

**Raw output (unedited):**

```
positive
```

</details>

<details><summary>few_shot · S1 · run 2 · ✓ strict-correct</summary>

**Input:**

```
Absolutely love this phone, the camera is stunning!
```

**Raw output (unedited):**

```
positive
```

</details>

<details><summary>zero_shot · S2 · run 1 · ✗ not strict-correct</summary>

**Input:**

```
Stopped working after two days. Total waste of money.
```

**Raw output (unedited):**

```
Sentiment: negative
```

</details>

<details><summary>few_shot · S2 · run 1 · ✓ strict-correct</summary>

**Input:**

```
Stopped working after two days. Total waste of money.
```

**Raw output (unedited):**

```
negative
```

</details>

<details><summary>zero_shot · S2 · run 2 · ✗ not strict-correct</summary>

**Input:**

```
Stopped working after two days. Total waste of money.
```

**Raw output (unedited):**

```
Sentiment: negative
```

</details>

<details><summary>few_shot · S2 · run 2 · ✓ strict-correct</summary>

**Input:**

```
Stopped working after two days. Total waste of money.
```

**Raw output (unedited):**

```
negative
```

</details>

<details><summary>zero_shot · S3 · run 1 · ✗ not strict-correct</summary>

**Input:**

```
It arrived on Tuesday in a brown box.
```

**Raw output (unedited):**

```
Sentiment: neutral
```

</details>

<details><summary>few_shot · S3 · run 1 · ✓ strict-correct</summary>

**Input:**

```
It arrived on Tuesday in a brown box.
```

**Raw output (unedited):**

```
neutral
```

</details>

<details><summary>zero_shot · S3 · run 2 · ✗ not strict-correct</summary>

**Input:**

```
It arrived on Tuesday in a brown box.
```

**Raw output (unedited):**

```
Sentiment: neutral
```

</details>

<details><summary>few_shot · S3 · run 2 · ✓ strict-correct</summary>

**Input:**

```
It arrived on Tuesday in a brown box.
```

**Raw output (unedited):**

```
neutral
```

</details>

<details><summary>zero_shot · S4 · run 1 · ✗ not strict-correct</summary>

**Input:**

```
Great screen, but the battery barely lasts half a day.
```

**Raw output (unedited):**

```
Sentiment: mixed
```

</details>

<details><summary>few_shot · S4 · run 1 · ✓ strict-correct</summary>

**Input:**

```
Great screen, but the battery barely lasts half a day.
```

**Raw output (unedited):**

```
mixed
```

</details>

<details><summary>zero_shot · S4 · run 2 · ✗ not strict-correct</summary>

**Input:**

```
Great screen, but the battery barely lasts half a day.
```

**Raw output (unedited):**

```
Sentiment: mixed
```

</details>

<details><summary>few_shot · S4 · run 2 · ✓ strict-correct</summary>

**Input:**

```
Great screen, but the battery barely lasts half a day.
```

**Raw output (unedited):**

```
mixed
```

</details>

<details><summary>zero_shot · S5 · run 1 · ✗ not strict-correct</summary>

**Input:**

```
Oh wonderful, another update that breaks everything. Thanks a lot.
```

**Raw output (unedited):**

```
Sentiment: negative
```

</details>

<details><summary>few_shot · S5 · run 1 · ✓ strict-correct</summary>

**Input:**

```
Oh wonderful, another update that breaks everything. Thanks a lot.
```

**Raw output (unedited):**

```
negative
```

</details>

<details><summary>zero_shot · S5 · run 2 · ✗ not strict-correct</summary>

**Input:**

```
Oh wonderful, another update that breaks everything. Thanks a lot.
```

**Raw output (unedited):**

```
Sentiment: negative
```

</details>

<details><summary>few_shot · S5 · run 2 · ✓ strict-correct</summary>

**Input:**

```
Oh wonderful, another update that breaks everything. Thanks a lot.
```

**Raw output (unedited):**

```
negative
```

</details>

<details><summary>zero_shot · S6 · run 1 · ✗ not strict-correct</summary>

**Input:**

```
Not bad at all, honestly better than I expected.
```

**Raw output (unedited):**

```
Sentiment: positive
```

</details>

<details><summary>few_shot · S6 · run 1 · ✓ strict-correct</summary>

**Input:**

```
Not bad at all, honestly better than I expected.
```

**Raw output (unedited):**

```
positive
```

</details>

<details><summary>zero_shot · S6 · run 2 · ✗ not strict-correct</summary>

**Input:**

```
Not bad at all, honestly better than I expected.
```

**Raw output (unedited):**

```
Sentiment: positive
```

</details>

<details><summary>few_shot · S6 · run 2 · ✓ strict-correct</summary>

**Input:**

```
Not bad at all, honestly better than I expected.
```

**Raw output (unedited):**

```
positive
```

</details>

<details><summary>zero_shot · S7 · run 1 · ✗ not strict-correct</summary>

**Input:**

```
The food was fine. Nothing special, nothing terrible.
```

**Raw output (unedited):**

```
Sentiment: neutral
```

</details>

<details><summary>few_shot · S7 · run 1 · ✓ strict-correct</summary>

**Input:**

```
The food was fine. Nothing special, nothing terrible.
```

**Raw output (unedited):**

```
neutral
```

</details>

<details><summary>zero_shot · S7 · run 2 · ✗ not strict-correct</summary>

**Input:**

```
The food was fine. Nothing special, nothing terrible.
```

**Raw output (unedited):**

```
Sentiment: neutral
```

</details>

<details><summary>few_shot · S7 · run 2 · ✓ strict-correct</summary>

**Input:**

```
The food was fine. Nothing special, nothing terrible.
```

**Raw output (unedited):**

```
neutral
```

</details>

<details><summary>zero_shot · S8 · run 1 · ✗ not strict-correct</summary>

**Input:**

```
Service was painfully slow, yet the pasta was the best I've ever had.
```

**Raw output (unedited):**

```
Sentiment: mixed
```

</details>

<details><summary>few_shot · S8 · run 1 · ✓ strict-correct</summary>

**Input:**

```
Service was painfully slow, yet the pasta was the best I've ever had.
```

**Raw output (unedited):**

```
mixed
```

</details>

<details><summary>zero_shot · S8 · run 2 · ✗ not strict-correct</summary>

**Input:**

```
Service was painfully slow, yet the pasta was the best I've ever had.
```

**Raw output (unedited):**

```
Sentiment: mixed
```

</details>

<details><summary>few_shot · S8 · run 2 · ✓ strict-correct</summary>

**Input:**

```
Service was painfully slow, yet the pasta was the best I've ever had.
```

**Raw output (unedited):**

```
mixed
```

</details>

<details><summary>zero_shot · S9 · run 1 · ✗ not strict-correct</summary>

**Input:**

```
Wish I had bought this sooner. Zero complaints.
```

**Raw output (unedited):**

```
Sentiment: positive
```

</details>

<details><summary>few_shot · S9 · run 1 · ✓ strict-correct</summary>

**Input:**

```
Wish I had bought this sooner. Zero complaints.
```

**Raw output (unedited):**

```
positive
```

</details>

<details><summary>zero_shot · S9 · run 2 · ✗ not strict-correct</summary>

**Input:**

```
Wish I had bought this sooner. Zero complaints.
```

**Raw output (unedited):**

```
Sentiment: positive
```

</details>

<details><summary>few_shot · S9 · run 2 · ✓ strict-correct</summary>

**Input:**

```
Wish I had bought this sooner. Zero complaints.
```

**Raw output (unedited):**

```
positive
```

</details>

<details><summary>zero_shot · S10 · run 1 · ✗ not strict-correct</summary>

**Input:**

```
Would not recommend. The staff were rude and the room was dirty.
```

**Raw output (unedited):**

```
Sentiment: negative
```

</details>

<details><summary>few_shot · S10 · run 1 · ✓ strict-correct</summary>

**Input:**

```
Would not recommend. The staff were rude and the room was dirty.
```

**Raw output (unedited):**

```
negative
```

</details>

<details><summary>zero_shot · S10 · run 2 · ✗ not strict-correct</summary>

**Input:**

```
Would not recommend. The staff were rude and the room was dirty.
```

**Raw output (unedited):**

```
Sentiment: negative
```

</details>

<details><summary>few_shot · S10 · run 2 · ✓ strict-correct</summary>

**Input:**

```
Would not recommend. The staff were rude and the room was dirty.
```

**Raw output (unedited):**

```
negative
```

</details>

## 2. Chain-of-thought: multi-step reasoning

**Task:** six multi-step word problems with known answers. Both prompts ask for the final answer on a `FINAL:` line so it can be checked automatically; the only difference is whether the model is told to show its working.

**Prompt template: `direct`**

```
{input}

Give only the final answer with no explanation or working. End with exactly one line in this form:
FINAL: <answer>
```

**Prompt template: `chain_of_thought`**

```
{input}

Think step by step, showing your working. Then end with exactly one line in this form:
FINAL: <answer>
```

**Problems and correct answers**

- **P1** (answer: `12:15 PM`): A train leaves a station at 9:15 AM travelling at 60 km/h. A second train leaves the same station on the same track at 10:00 AM, travelling at 80 km/h in the same direction. At what time does the second train catch up with the first?
- **P2** (answer: `2000`): A shop buys a jacket, marks the price up by 40% over its cost, and then gives a 25% discount on the marked price. The jacket sells for ₹2,100. What did the shop originally pay for the jacket (in ₹)?
- **P3** (answer: `20`): Aman is currently twice as old as Bela. Five years ago, Aman was three times as old as Bela. How old is Aman now?
- **P4** (answer: `4.8`): Tap A can fill an empty tank in 6 hours, tap B can fill it in 8 hours, and drain C can empty a full tank in 12 hours. If A, B and C are all opened together on an empty tank, how many hours does it take to fill the tank? Give the answer as a decimal number of hours.
- **P5** (answer: `41`): How many integers from 1 to 100 inclusive are divisible by 3 or by 5, but NOT divisible by 15?
- **P6** (answer: `9900`): Priya invests ₹10,000 at 10% interest compounded annually. At the end of year 1, right after the interest is added, she withdraws ₹2,000. How much is in the account at the end of year 2 (in ₹)?

| Variant | Correct | Gave a FINAL line | Avg output length (chars) | Avg hidden thinking tokens |
|---|---|---|---|---|
| direct | 12/12 (100%) | 12/12 (100%) | 523 | not reported |
| chain_of_thought | 12/12 (100%) | 12/12 (100%) | 1091 | not reported |

**Correct answers per problem** (out of the runs per variant)

| Problem | Expected | direct | chain_of_thought |
|---|---|---|---|
| P1 | 12:15 PM | 2/2  (12:15 PM, 12:15 PM) | 2/2  (12:15 PM, 12:15 PM) |
| P2 | 2000 | 2/2  (₹2,000, 2000) | 2/2  (2000, 2000) |
| P3 | 20 | 2/2  (20, 20) | 2/2  (20, 20) |
| P4 | 4.8 | 2/2  (4.8, 4.8) | 2/2  (4.8, 4.8) |
| P5 | 41 | 2/2  (41, 41) | 2/2  (41, 41) |
| P6 | 9900 | 2/2  (9900, 9900) | 2/2  (9900, 9900) |

### Analysis (write this yourself)

**What changed.** Accuracy was identical: direct 12/12 and chain-of-thought 12/12. The only measurable difference was length. Chain-of-thought outputs averaged 1091 characters against 523 for direct, so it cost about twice the output for no accuracy gain.

**Where it did not help, and why.** The raw outputs show that my "direct" prompt was not really direct: although it said "no explanation or working", the model still wrote out its working before the `FINAL:` line in all 12 direct outputs, so both conditions effectively used step-by-step reasoning. I also set the model's hidden thinking to `thinking_level="minimal"` (my first attempt, `thinking_budget=0`, was rejected by the API with a 400 error), but the API did not report thinking-token counts, so I cannot say how much the model reasoned internally. Small quality differences only show up in the raw text: for P5, direct run 1 reached 41 with a muddled explanation, while chain-of-thought run 1 noticed and corrected its own reading of the question ("Wait, let's re-read carefully"). These problems are also easy for this model, so a test with harder problems and a truly answer-only direct prompt is needed before concluding that chain-of-thought does not help.

### Complete raw outputs

<details><summary>direct · P1 · run 1 · ✓ correct (extracted: 12:15 PM)</summary>

**Input:**

```
A train leaves a station at 9:15 AM travelling at 60 km/h. A second train leaves the same station on the same track at 10:00 AM, travelling at 80 km/h in the same direction. At what time does the second train catch up with the first?
```

**Raw output (unedited):**

```
To find the time the second train catches up with the first:

1. The first train travels for 45 minutes (0.75 hours) before the second train starts. In this time, it covers a distance of $60 \text{ km/h} \times 0.75 \text{ h} = 45 \text{ km}$.
2. The relative speed of the second train compared to the first is $80 \text{ km/h} - 60 \text{ km/h} = 20 \text{ km/h}$.
3. The time it takes for the second train to close the 45 km gap is $\frac{45 \text{ km}}{20 \text{ km/h}} = 2.25 \text{ hours}$ (or 2 hours and 15 minutes).
4. Adding 2 hours and 15 minutes to the second train's departure time of 10:00 AM gives 12:15 PM.

FINAL: 12:15 PM
```

</details>

<details><summary>chain_of_thought · P1 · run 1 · ✓ correct (extracted: 12:15 PM)</summary>

**Input:**

```
A train leaves a station at 9:15 AM travelling at 60 km/h. A second train leaves the same station on the same track at 10:00 AM, travelling at 80 km/h in the same direction. At what time does the second train catch up with the first?
```

**Raw output (unedited):**

```
To find the time when the second train catches up with the first, we can follow these steps:

1. **Calculate the distance the first train travels before the second train starts:**
   - The first train leaves at 9:15 AM and the second train leaves at 10:00 AM. 
   - The time difference between the two departures is 45 minutes, which is $\frac{45}{60} = 0.75$ hours.
   - The first train travels at a speed of 60 km/h.
   - Distance = Speed $\times$ Time = $60 \text{ km/h} \times 0.75 \text{ hours} = 45 \text{ km}$.
   - So, when the second train starts at 10:00 AM, the first train is already 45 km ahead.

2. **Determine the relative speed:**
   - The first train travels at 60 km/h.
   - The second train travels at 80 km/h in the same direction.
   - The relative speed at which the second train closes the gap is $80 \text{ km/h} - 60 \text{ km/h} = 20 \text{ km/h}$.

3. **Calculate the time it takes for the second train to catch up:**
   - Time to catch up = $\frac{\text{Distance gap}}{\text{Relative speed}} = \frac{45 \text{ km}}{20 \text{ km/h}} = 2.25 \text{ hours}$.
   - $2.25$ hours is equal to 2 hours and 15 minutes ($0.25 \times 60 = 15$ minutes).

4. **Determine the exact time:**
   - The second train starts at 10:00 AM.
   - Adding 2 hours and 15 minutes to 10:00 AM gives 12:15 PM.

FINAL: 12:15 PM
```

</details>

<details><summary>direct · P1 · run 2 · ✓ correct (extracted: 12:15 PM)</summary>

**Input:**

```
A train leaves a station at 9:15 AM travelling at 60 km/h. A second train leaves the same station on the same track at 10:00 AM, travelling at 80 km/h in the same direction. At what time does the second train catch up with the first?
```

**Raw output (unedited):**

```
To find the time when the second train catches up with the first, we can calculate the head start the first train has. 

- The first train travels for 45 minutes (from 9:15 AM to 10:00 AM) at 60 km/h. 
- Distance covered in 45 minutes ($0.75$ hours) = $60 \times 0.75 = 45$ km.
- The relative speed of the second train with respect to the first is $80 - 60 = 20$ km/h.
- Time required for the second train to cover the 45 km gap = $\frac{45}{20} = 2.25$ hours (or 2 hours and 15 minutes).
- Adding this time to 10:00 AM gives 12:15 PM.

FINAL: 12:15 PM
```

</details>

<details><summary>chain_of_thought · P1 · run 2 · ✓ correct (extracted: 12:15 PM)</summary>

**Input:**

```
A train leaves a station at 9:15 AM travelling at 60 km/h. A second train leaves the same station on the same track at 10:00 AM, travelling at 80 km/h in the same direction. At what time does the second train catch up with the first?
```

**Raw output (unedited):**

```
To find out when the second train catches up with the first, we can follow these steps:

1. **Calculate the distance the first train travels before the second train starts:**
   - The first train leaves at 9:15 AM and the second train leaves at 10:00 AM. 
   - The time difference between their departures is 45 minutes, which is $\frac{45}{60} = 0.75$ hours.
   - The first train travels at a speed of 60 km/h.
   - Distance = Speed $\times$ Time = $60 \text{ km/h} \times 0.75 \text{ hours} = 45 \text{ km}$.

2. **Determine the relative speed:**
   - The first train travels at 60 km/h.
   - The second train travels at 80 km/h.
   - The rate at which the second train closes the distance (relative speed) is $80 \text{ km/h} - 60 \text{ km/h} = 20 \text{ km/h}$.

3. **Calculate the time it takes for the second train to cover the 45 km gap:**
   - Time = Distance / Relative Speed = $45 \text{ km} / 20 \text{ km/h} = 2.25 \text{ hours}$.
   - 2.25 hours is equal to 2 hours and 15 minutes ($0.25 \times 60 = 15$).

4. **Determine the exact time when they meet:**
   - The second train starts at 10:00 AM.
   - Adding 2 hours and 15 minutes to 10:00 AM gives 12:15 PM.

FINAL: 12:15 PM
```

</details>

<details><summary>direct · P2 · run 1 · ✓ correct (extracted: ₹2,000)</summary>

**Input:**

```
A shop buys a jacket, marks the price up by 40% over its cost, and then gives a 25% discount on the marked price. The jacket sells for ₹2,100. What did the shop originally pay for the jacket (in ₹)?
```

**Raw output (unedited):**

```
To find the original cost of the jacket, let the cost price be $C$.

1. The shop marks the price up by 40%:
   Marked Price (MP) = $C \times 1.40$

2. The shop gives a 25% discount on the marked price, and it sells for ₹2,100:
   Selling Price (SP) = $\text{MP} \times (1 - 0.25) = \text{MP} \times 0.75$

3. Substitute the Marked Price into the equation:
   $2,100 = (C \times 1.40) \times 0.75$
   $2,100 = C \times 1.05$

4. Solve for $C$:
   $C = \frac{2,100}{1.05} = 2,000$

FINAL: ₹2,000
```

</details>

<details><summary>chain_of_thought · P2 · run 1 · ✓ correct (extracted: 2000)</summary>

**Input:**

```
A shop buys a jacket, marks the price up by 40% over its cost, and then gives a 25% discount on the marked price. The jacket sells for ₹2,100. What did the shop originally pay for the jacket (in ₹)?
```

**Raw output (unedited):**

```
To find out what the shop originally paid for the jacket, we can work through the problem step by step using algebra.

1. **Define the variables:**
   Let $C$ be the original cost price of the jacket for the shop (in ₹).

2. **Calculate the marked price:**
   The shop marks the price up by 40% over its cost. 
   Marked Price (MP) = $C + 0.40C = 1.40C$

3. **Calculate the selling price:**
   The shop then gives a 25% discount on the marked price. 
   Selling Price (SP) = Marked Price $- 25\%$ of Marked Price
   SP = $1.40C - 0.25 \times (1.40C)$
   SP = $1.40C \times (1 - 0.25)$
   SP = $1.40C \times 0.75$
   SP = $1.05C$

4. **Equate to the actual selling price and solve for $C$:**
   We are given that the jacket sells for ₹2,100.
   $1.05C = 2100$
   $C = \frac{2100}{1.05}$
   $C = 2000$

FINAL: 2000
```

</details>

<details><summary>direct · P2 · run 2 · ✓ correct (extracted: 2000)</summary>

**Input:**

```
A shop buys a jacket, marks the price up by 40% over its cost, and then gives a 25% discount on the marked price. The jacket sells for ₹2,100. What did the shop originally pay for the jacket (in ₹)?
```

**Raw output (unedited):**

```
To find the original cost of the jacket, let's denote the cost price as $C$.

1. The shop marks up the price by 40%:
   Marked Price (MP) = $C \times 1.40$

2. The shop gives a 25% discount on the marked price:
   Selling Price (SP) = $\text{MP} \times (1 - 0.25) = \text{MP} \times 0.75$
   SP = $(C \times 1.40) \times 0.75 = C \times 1.05$

3. We are given that the selling price is ₹2,100:
   $1.05 \times C = 2100$
   $C = \frac{2100}{1.05} = 2000$

FINAL: 2000
```

</details>

<details><summary>chain_of_thought · P2 · run 2 · ✓ correct (extracted: 2000)</summary>

**Input:**

```
A shop buys a jacket, marks the price up by 40% over its cost, and then gives a 25% discount on the marked price. The jacket sells for ₹2,100. What did the shop originally pay for the jacket (in ₹)?
```

**Raw output (unedited):**

```
To find out what the shop originally paid for the jacket, we can work through the problem step by step using algebra.

1. **Define the variables:**
   Let $C$ be the original cost price of the jacket (what the shop paid).

2. **Calculate the marked price:**
   The shop marks the price up by 40% over its cost. 
   $$\text{Marked Price} = C + 0.40C = 1.40C$$

3. **Calculate the selling price after the discount:**
   The shop gives a 25% discount on the marked price. This means the selling price is 75% of the marked price (since $100\% - 25\% = 75\%$).
   $$\text{Selling Price} = 0.75 \times \text{Marked Price}$$
   $$\text{Selling Price} = 0.75 \times 1.40C$$

4. **Multiply the decimals:**
   $$0.75 \times 1.40 = 1.05$$
   So, the selling price in terms of $C$ is:
   $$\text{Selling Price} = 1.05C$$

5. **Solve for the cost price ($C$):**
   We are given that the jacket sells for ₹2,100.
   $$1.05C = 2100$$
   $$C = \frac{2100}{1.05}$$
   $$C = 2000$$

FINAL: 2000
```

</details>

<details><summary>direct · P3 · run 1 · ✓ correct (extracted: 20)</summary>

**Input:**

```
Aman is currently twice as old as Bela. Five years ago, Aman was three times as old as Bela. How old is Aman now?
```

**Raw output (unedited):**

```
To find Aman's current age, we can set up the following equations where $A$ is Aman's age and $B$ is Bela's age:

1. $A = 2B$
2. $A - 5 = 3(B - 5)$

Substituting the first equation into the second:
$2B - 5 = 3B - 15$
$B = 10$

Since Aman is twice as old as Bela:
$A = 2(10) = 20$

FINAL: 20
```

</details>

<details><summary>chain_of_thought · P3 · run 1 · ✓ correct (extracted: 20)</summary>

**Input:**

```
Aman is currently twice as old as Bela. Five years ago, Aman was three times as old as Bela. How old is Aman now?
```

**Raw output (unedited):**

```
To find Aman's current age, we can set up a system of equations based on the information given.

Let $A$ be Aman's current age and $B$ be Bela's current age.

1. "Aman is currently twice as old as Bela":
   $$A = 2B$$

2. "Five years ago, Aman was three times as old as Bela":
   Five years ago, Aman's age was $A - 5$ and Bela's age was $B - 5$.
   $$A - 5 = 3(B - 5)$$

Now, substitute the first equation into the second equation:
$$(2B) - 5 = 3(B - 5)$$

Expand and simplify the equation:
$$2B - 5 = 3B - 15$$

Rearrange to solve for $B$:
$$15 - 5 = 3B - 2B$$
$$10 = B$$

So, Bela is currently 10 years old. 

Now, find Aman's current age using $A = 2B$:
$$A = 2 \times 10 = 20$$

FINAL: 20
```

</details>

<details><summary>direct · P3 · run 2 · ✓ correct (extracted: 20)</summary>

**Input:**

```
Aman is currently twice as old as Bela. Five years ago, Aman was three times as old as Bela. How old is Aman now?
```

**Raw output (unedited):**

```
To find Aman's current age, we can set up a system of equations based on the problem statement:

Let $A$ be Aman's current age and $B$ be Bela's current age.
1) $A = 2B$
2) $A - 5 = 3(B - 5)$

Substitute the first equation into the second:
$2B - 5 = 3B - 15$
$B = 10$

Since Aman is twice as old as Bela:
$A = 2 \times 10 = 20$

FINAL: 20
```

</details>

<details><summary>chain_of_thought · P3 · run 2 · ✓ correct (extracted: 20)</summary>

**Input:**

```
Aman is currently twice as old as Bela. Five years ago, Aman was three times as old as Bela. How old is Aman now?
```

**Raw output (unedited):**

```
To find Aman's current age, let's set up a system of equations based on the information given.

1. Let $A$ be Aman's current age.
2. Let $B$ be Bela's current age.

From the first sentence ("Aman is currently twice as old as Bela"):
$$A = 2B$$

From the second sentence ("Five years ago, Aman was three times as old as Bela"):
Five years ago, Aman's age was $A - 5$ and Bela's age was $B - 5$. 
$$A - 5 = 3(B - 5)$$

Now, substitute $A = 2B$ into the second equation:
$$2B - 5 = 3(B - 5)$$

Expand the right side:
$$2B - 5 = 3B - 15$$

Rearrange the equation to solve for $B$:
$$15 - 5 = 3B - 2B$$
$$B = 10$$

So, Bela is currently 10 years old. 

Now, find Aman's current age ($A$) using $A = 2B$:
$$A = 2 \times 10 = 20$$

FINAL: 20
```

</details>

<details><summary>direct · P4 · run 1 · ✓ correct (extracted: 4.8)</summary>

**Input:**

```
Tap A can fill an empty tank in 6 hours, tap B can fill it in 8 hours, and drain C can empty a full tank in 12 hours. If A, B and C are all opened together on an empty tank, how many hours does it take to fill the tank? Give the answer as a decimal number of hours.
```

**Raw output (unedited):**

```
To find the time it takes to fill the tank when all three taps are open, we first determine the rate of each tap per hour:
- Tap A fills $\frac{1}{6}$ of the tank per hour.
- Tap B fills $\frac{1}{8}$ of the tank per hour.
- Drain C empties $\frac{1}{12}$ of the tank per hour.

When all three are opened together, the net rate of filling the tank per hour is:
$$\text{Net rate} = \frac{1}{6} + \frac{1}{8} - \frac{1}{12}$$

Finding a common denominator (which is 24):
$$\text{Net rate} = \frac{4}{24} + \frac{3}{24} - \frac{2}{24} = \frac{5}{24}$$

Thus, the time required to fill the entire tank is the reciprocal of the net rate:
$$\text{Time} = \frac{24}{5} = 4.8 \text{ hours}$$

FINAL: 4.8
```

</details>

<details><summary>chain_of_thought · P4 · run 1 · ✓ correct (extracted: 4.8)</summary>

**Input:**

```
Tap A can fill an empty tank in 6 hours, tap B can fill it in 8 hours, and drain C can empty a full tank in 12 hours. If A, B and C are all opened together on an empty tank, how many hours does it take to fill the tank? Give the answer as a decimal number of hours.
```

**Raw output (unedited):**

```
To find the time it takes to fill the empty tank when taps A, B, and drain C are all opened together, we can calculate the net rate of work done by the taps per hour.

1. **Calculate the rate of each tap per hour:**
   - Tap A can fill the tank in 6 hours, so its rate is $\frac{1}{6}$ of the tank per hour.
   - Tap B can fill the tank in 8 hours, so its rate is $\frac{1}{8}$ of the tank per hour.
   - Drain C can empty the tank in 12 hours, so its rate of emptying is $-\frac{1}{12}$ of the tank per hour.

2. **Calculate the combined net rate per hour:**
   When all three are opened together, the net rate is:
   $$\text{Net Rate} = \frac{1}{6} + \frac{1}{8} - \frac{1}{12}$$

3. **Find a common denominator to add and subtract the fractions:**
   The least common multiple of 6, 8, and 12 is 24.
   - $\frac{1}{6} = \frac{4}{24}$
   - $\frac{1}{8} = \frac{3}{24}$
   - $\frac{1}{12} = \frac{2}{24}$

   $$\text{Net Rate} = \frac{4}{24} + \frac{3}{24} - \frac{2}{24} = \frac{4 + 3 - 2}{24} = \frac{5}{24}$$
   
   So, $\frac{5}{24}$ of the tank is filled per hour.

4. **Calculate the total time to fill the tank:**
   The time required is the reciprocal of the net rate:
   $$\text{Time} = \frac{24}{5} = 4.8 \text{ hours}$$

FINAL: 4.8
```

</details>

<details><summary>direct · P4 · run 2 · ✓ correct (extracted: 4.8)</summary>

**Input:**

```
Tap A can fill an empty tank in 6 hours, tap B can fill it in 8 hours, and drain C can empty a full tank in 12 hours. If A, B and C are all opened together on an empty tank, how many hours does it take to fill the tank? Give the answer as a decimal number of hours.
```

**Raw output (unedited):**

```
To find the time it takes to fill the tank when all three taps are opened together, we first determine the rate of each tap per hour:
- Tap A fills $\frac{1}{6}$ of the tank per hour.
- Tap B fills $\frac{1}{8}$ of the tank per hour.
- Drain C empties $\frac{1}{12}$ of the tank per hour.

The net rate when all three are opened together is:
$$\text{Net Rate} = \frac{1}{6} + \frac{1}{8} - \frac{1}{12}$$

To add and subtract these fractions, find a common denominator, which is 24:
$$\text{Net Rate} = \frac{4}{24} + \frac{3}{24} - \frac{2}{24} = \frac{5}{24}$$

Thus, the time required to fill the entire tank is the reciprocal of the net rate:
$$\text{Time} = \frac{24}{5} = 4.8 \text{ hours}$$

FINAL: 4.8
```

</details>

<details><summary>chain_of_thought · P4 · run 2 · ✓ correct (extracted: 4.8)</summary>

**Input:**

```
Tap A can fill an empty tank in 6 hours, tap B can fill it in 8 hours, and drain C can empty a full tank in 12 hours. If A, B and C are all opened together on an empty tank, how many hours does it take to fill the tank? Give the answer as a decimal number of hours.
```

**Raw output (unedited):**

```
To find the time it takes to fill the tank when all three taps are opened together, we can calculate the net rate at which the tank is filled per hour.

1. **Find the rate of each tap/drain per hour:**
   - Tap A fills the tank in 6 hours, so its rate is $\frac{1}{6}$ of the tank per hour.
   - Tap B fills the tank in 8 hours, so its rate is $\frac{1}{8}$ of the tank per hour.
   - Drain C empties the tank in 12 hours, so its rate is $-\frac{1}{12}$ of the tank per hour.

2. **Calculate the net rate when all three are open together:**
   $$\text{Net Rate} = \frac{1}{6} + \frac{1}{8} - \frac{1}{12}$$

3. **Find a common denominator to add and subtract the fractions:**
   The least common multiple of 6, 8, and 12 is 24.
   - $\frac{1}{6} = \frac{4}{24}$
   - $\frac{1}{8} = \frac{3}{24}$
   - $\frac{1}{12} = \frac{2}{24}$

   $$\text{Net Rate} = \frac{4}{24} + \frac{3}{24} - \frac{2}{24} = \frac{4 + 3 - 2}{24} = \frac{5}{24}$$

   So, $\frac{5}{24}$ of the tank is filled per hour.

4. **Calculate the total time to fill the tank:**
   The total time is the reciprocal of the net rate:
   $$\text{Time} = \frac{24}{5} = 4.8 \text{ hours}$$

FINAL: 4.8
```

</details>

<details><summary>direct · P5 · run 1 · ✓ correct (extracted: 41)</summary>

**Input:**

```
How many integers from 1 to 100 inclusive are divisible by 3 or by 5, but NOT divisible by 15?
```

**Raw output (unedited):**

```
To find the number of integers from 1 to 100 inclusive that are divisible by 3 or by 5, but NOT divisible by 15, we can use the principle of inclusion-exclusion. 

- The number of integers divisible by 3 is $\lfloor 100 / 3 \rfloor = 33$.
- The number of integers divisible by 5 is $\lfloor 100 / 5 \rfloor = 20$.
- The number of integers divisible by both 3 and 5 (i.e., divisible by 15) is $\lfloor 100 / 15 \rfloor = 6$.

The integers divisible by 3 or 5 are $33 + 20 - 6 = 47$. 
To exclude those divisible by 15, we subtract the count of multiples of 15 twice (once from the multiples of 3 and once from the multiples of 3 or 5), which leaves us with the numbers divisible by 3 or 5 minus the ones divisible by 15: $47 - 6 = 41$.

FINAL: 41
```

</details>

<details><summary>chain_of_thought · P5 · run 1 · ✓ correct (extracted: 41)</summary>

**Input:**

```
How many integers from 1 to 100 inclusive are divisible by 3 or by 5, but NOT divisible by 15?
```

**Raw output (unedited):**

```
To find the number of integers from 1 to 100 inclusive that are divisible by 3 or by 5, but NOT divisible by 15, we can break the problem down into logical steps.

**Step 1: Find the number of integers divisible by 3.**
The integers from 1 to 100 divisible by 3 form an arithmetic sequence where the first term is 3 and the last term is 99 ($3 \times 33$). 
The number of such integers is:
$$\lfloor \frac{100}{3} \rfloor = 33$$

**Step 2: Find the number of integers divisible by 5.**
The integers from 1 to 100 divisible by 5 range from 5 to 100 ($5 \times 20$).
The number of such integers is:
$$\lfloor \frac{100}{5} \rfloor = 20$$

**Step 3: Find the number of integers divisible by both 3 and 5 (i.e., divisible by 15).**
The integers divisible by both 3 and 5 must be multiples of the least common multiple of 3 and 5, which is 15. These are 15, 30, 45, 60, 75, and 90 ($15 \times 6$).
The number of such integers is:
$$\lfloor \frac{100}{15} \rfloor = 6$$

**Step 4: Find the total number of integers divisible by 3 or by 5.**
Using the Principle of Inclusion-Exclusion, the number of integers divisible by 3 or 5 is:
$$\text{Divisible by 3} + \text{Divisible by 5} - \text{Divisible by 15}$$
$$33 + 20 - 6 = 47$$

**Step 5: Exclude the integers divisible by 15.**
We need the numbers that are divisible by 3 or 5, *but NOT* divisible by 15. This means we take the total from Step 4 and subtract the numbers that are divisible by 15 (which we already added and subtracted, but now we want to exclude them completely from our "OR" condition).
Wait, let's re-read carefully: "divisible by 3 or by 5, but NOT divisible by 15".
The numbers divisible by 3 or 5 consist of:
- Numbers divisible by 3 only
- Numbers divisible by 5 only
- Numbers divisible by both 3 and 5 (i.e., divisible by 15)

We want to exclude the ones divisible by 15. Therefore, we just need the sum of numbers divisible *only* by 3 and numbers divisible *only* by 5.
- Numbers divisible only by 3 = (Divisible by 3) - (Divisible by 15) = $33 - 6 = 27$
- Numbers divisible only by 5 = (Divisible by 5) - (Divisible by 15) = $20 - 6 = 14$

Total = $27 + 14 = 41$

Alternatively, take the total divisible by 3 or 5 (47) and subtract the ones divisible by 15 (6):
$$47 - 6 = 41$$

FINAL: 41
```

</details>

<details><summary>direct · P5 · run 2 · ✓ correct (extracted: 41)</summary>

**Input:**

```
How many integers from 1 to 100 inclusive are divisible by 3 or by 5, but NOT divisible by 15?
```

**Raw output (unedited):**

```
To find the number of integers from 1 to 100 inclusive that are divisible by 3 or by 5, but NOT divisible by 15, we can use the Principle of Inclusion-Exclusion and then exclude those divisible by both 3 and 5 (i.e., multiples of 15).

- Multiples of 3: $\lfloor 100/3 \rfloor = 33$
- Multiples of 5: $\lfloor 100/5 \rfloor = 20$
- Multiples of 15 (both 3 and 5): $\lfloor 100/15 \rfloor = 6$

Integers divisible by 3 or 5: $33 + 20 - 6 = 47$.
Excluding those divisible by 15: $47 - 6 = 41$.

FINAL: 41
```

</details>

<details><summary>chain_of_thought · P5 · run 2 · ✓ correct (extracted: 41)</summary>

**Input:**

```
How many integers from 1 to 100 inclusive are divisible by 3 or by 5, but NOT divisible by 15?
```

**Raw output (unedited):**

```
To find the number of integers from 1 to 100 inclusive that are divisible by 3 or by 5, but NOT divisible by 15, we can follow these steps:

1. **Find the number of integers divisible by 3:**
   The integers are $3, 6, 9, \dots, 99$. This is an arithmetic sequence where the last term is $3 \times 33$.
   So, there are $\lfloor 100 / 3 \rfloor = 33$ integers divisible by 3.

2. **Find the number of integers divisible by 5:**
   The integers are $5, 10, 15, \dots, 100$. This is an arithmetic sequence where the last term is $5 \times 20$.
   So, there are $\lfloor 100 / 5 \rfloor = 20$ integers divisible by 5.

3. **Find the number of integers divisible by both 3 and 5 (i.e., divisible by 15):**
   The integers are $15, 30, 45, 60, 75, 90$.
   So, there are $\lfloor 100 / 15 \rfloor = 6$ integers divisible by 15.

4. **Find the number of integers divisible by 3 or 5:**
   Using the Principle of Inclusion-Exclusion, the number of integers divisible by 3 or 5 is:
   $$\text{Divisible by 3} + \text{Divisible by 5} - \text{Divisible by 15} = 33 + 20 - 6 = 47$$

5. **Exclude the integers divisible by 15:**
   We want the numbers divisible by 3 or 5 *excluding* those that are divisible by 15. 
   Since the 6 numbers divisible by 15 were included in the 47, we subtract them:
   $$47 - 6 = 41$$

FINAL: 41
```

</details>

<details><summary>direct · P6 · run 1 · ✓ correct (extracted: 9900)</summary>

**Input:**

```
Priya invests ₹10,000 at 10% interest compounded annually. At the end of year 1, right after the interest is added, she withdraws ₹2,000. How much is in the account at the end of year 2 (in ₹)?
```

**Raw output (unedited):**

```
To find the amount in the account at the end of year 2:

1. Principal at the start of year 1 = ₹10,000
2. Interest for year 1 (10% of 10,000) = ₹1,000
3. Amount at the end of year 1 before withdrawal = ₹10,000 + ₹1,000 = ₹11,000
4. Withdrawal at the end of year 1 = ₹2,000
5. New principal for year 2 = ₹11,000 - ₹2,000 = ₹9,000
6. Interest for year 2 (10% of 9,000) = ₹900
7. Amount at the end of year 2 = ₹9,000 + ₹900 = ₹9,900

FINAL: 9900
```

</details>

<details><summary>chain_of_thought · P6 · run 1 · ✓ correct (extracted: 9900)</summary>

**Input:**

```
Priya invests ₹10,000 at 10% interest compounded annually. At the end of year 1, right after the interest is added, she withdraws ₹2,000. How much is in the account at the end of year 2 (in ₹)?
```

**Raw output (unedited):**

```
To find the amount in Priya's account at the end of year 2, let's break it down step by step:

1. **Calculate the amount at the end of Year 1 (before withdrawal):**
   * Initial Principal ($P_1$) = ₹10,000
   * Interest Rate ($r$) = 10% per annum
   * Interest for Year 1 = $10,000 \times 10\% = ₹1,000$
   * Total amount at the end of Year 1 (before withdrawal) = $10,000 + 1,000 = ₹11,000$

2. **Account balance after the withdrawal at the end of Year 1:**
   * Withdrawal = ₹2,000
   * Remaining Principal for Year 2 ($P_2$) = $11,000 - 2,000 = ₹9,000$

3. **Calculate the amount at the end of Year 2:**
   * Interest for Year 2 on the remaining principal = $9,000 \times 10\% = ₹900$
   * Total amount at the end of Year 2 = $9,000 + 900 = ₹9,900$

FINAL: 9900
```

</details>

<details><summary>direct · P6 · run 2 · ✓ correct (extracted: 9900)</summary>

**Input:**

```
Priya invests ₹10,000 at 10% interest compounded annually. At the end of year 1, right after the interest is added, she withdraws ₹2,000. How much is in the account at the end of year 2 (in ₹)?
```

**Raw output (unedited):**

```
To find the amount in the account at the end of year 2:

1. **End of Year 1 (before withdrawal):** 
   Principal = ₹10,000
   Interest = 10% of ₹10,000 = ₹1,000
   Total = ₹10,000 + ₹1,000 = ₹11,000

2. **End of Year 1 (after withdrawal):** 
   Remaining Principal = ₹11,000 - ₹2,000 = ₹9,000

3. **End of Year 2:** 
   Interest for Year 2 = 10% of ₹9,000 = ₹900
   Total = ₹9,000 + ₹900 = ₹9,900

FINAL: 9900
```

</details>

<details><summary>chain_of_thought · P6 · run 2 · ✓ correct (extracted: 9900)</summary>

**Input:**

```
Priya invests ₹10,000 at 10% interest compounded annually. At the end of year 1, right after the interest is added, she withdraws ₹2,000. How much is in the account at the end of year 2 (in ₹)?
```

**Raw output (unedited):**

```
To find the amount in Priya's account at the end of year 2, let's break it down year by year:

**Year 1:**
1. **Initial Principal:** ₹10,000
2. **Interest for Year 1 (10% of ₹10,000):** 
   $$\frac{10}{100} \times 10,000 = ₹1,000$$
3. **Total amount right before withdrawal:** 
   $$10,000 + 1,000 = ₹11,000$$
4. **Withdrawal at the end of Year 1:** ₹2,000
5. **New Principal for Year 2:** 
   $$11,000 - 2,000 = ₹9,000$$

**Year 2:**
1. **Interest for Year 2 (10% of the new principal ₹9,000):** 
   $$\frac{10}{100} \times 9,000 = ₹900$$
2. **Total amount at the end of Year 2:** 
   $$9,000 + 900 = ₹9,900$$

FINAL: 9900
```

</details>

## 3. Structured output: JSON extraction

**Task:** extract `{name, date, amount, currency}` from messy text. Test inputs include a missing amount (J7, expected `null`), a distractor amount (J8), a dd/mm/yyyy date (J4) and a spelled-out date (J3).

**Test inputs and gold answers**

- **J1**: hey its priya sharma here, paid the rent yesterday — 15th Oct 2025 — total came to ₹18,500 incl. maintenance
  - gold: `{"name": "Priya Sharma", "date": "2025-10-15", "amount": 18500, "currency": "INR"}`
- **J2**: INVOICE #4471 // Bill to: Marcus O'Neil // Issued: 2025-03-02 // Amount due: $1,249.99 USD
  - gold: `{"name": "Marcus O'Neil", "date": "2025-03-02", "amount": 1249.99, "currency": "USD"}`
- **J3**: Received 2,500 euros from Jean-Luc Picard on the fourth of July, 2024. Thanks!!
  - gold: `{"name": "Jean-Luc Picard", "date": "2024-07-04", "amount": 2500, "currency": "EUR"}`
- **J4**: Dr. Anita Desai - consultation fee Rs. 800/- dated 09/11/2025 (dd/mm/yyyy)
  - gold: `{"name": "Anita Desai", "date": "2025-11-09", "amount": 800, "currency": "INR"}`
- **J5**: Thomas Idris bought a laptop on March 3, 2025 for £1,199.50 (receipt attached)
  - gold: `{"name": "Thomas Idris", "date": "2025-03-03", "amount": 1199.5, "currency": "GBP"}`
- **J6**: Ref: refund to Li Wei, 12 January 2026, amount: 75 CAD.
  - gold: `{"name": "Li Wei", "date": "2026-01-12", "amount": 75, "currency": "CAD"}`
- **J7**: Aisha Khan paid by card on 20 Feb 2025, forgot to note down the total.
  - gold: `{"name": "Aisha Khan", "date": "2025-02-20", "amount": null, "currency": null}`
- **J8**: Paid ₹500 to Ravi Kumar on 1 Dec 2025 (his bill was ₹650 but he gave a discount of ₹150).
  - gold: `{"name": "Ravi Kumar", "date": "2025-12-01", "amount": 500, "currency": "INR"}`

**Prompt variants** (`{input}` is replaced by the text). Variant 4 uses the same text as variant 3 plus the API's JSON mode (`response_mime_type=application/json` with a response schema).

**`v1_naive`**

```
Extract the name, date and amount from this text as JSON.

Text: {input}
```

**`v2_explicit_schema`**

```
Extract payment details from the text below.

Return ONLY a JSON object (no markdown, no code fences, no commentary) with exactly these keys:
{
  "name": string | null,       // full name of the person involved
  "date": string | null,       // ISO format YYYY-MM-DD
  "amount": number | null,     // plain number, no currency symbol or thousands separators
  "currency": string | null    // ISO 4217 code such as INR, USD, EUR
}

Rules: use null for any field that is not stated in the text. Do not guess. If several amounts appear, use the amount actually paid.

Text: {input}
```

**`v3_schema_plus_examples`**

```
Extract payment details from the text below.

Return ONLY a JSON object (no markdown, no code fences, no commentary) with exactly these keys:
{
  "name": string | null,       // full name of the person involved
  "date": string | null,       // ISO format YYYY-MM-DD
  "amount": number | null,     // plain number, no currency symbol or thousands separators
  "currency": string | null    // ISO 4217 code such as INR, USD, EUR
}

Rules: use null for any field that is not stated in the text. Do not guess. If several amounts appear, use the amount actually paid.

Example 1
Text: Invoice for Carla Mendes dated 2024-06-30, total 310.50 USD.
Output: {"name": "Carla Mendes", "date": "2024-06-30", "amount": 310.5, "currency": "USD"}

Example 2
Text: Sanjay paid us on 5 May 2025 but didn't say how much.
Output: {"name": "Sanjay", "date": "2025-05-05", "amount": null, "currency": null}

Text: {input}
```

**`v4_examples_plus_json_mode`** (same text as v3, plus API JSON mode with a response schema)

```
Extract payment details from the text below.

Return ONLY a JSON object (no markdown, no code fences, no commentary) with exactly these keys:
{
  "name": string | null,       // full name of the person involved
  "date": string | null,       // ISO format YYYY-MM-DD
  "amount": number | null,     // plain number, no currency symbol or thousands separators
  "currency": string | null    // ISO 4217 code such as INR, USD, EUR
}

Rules: use null for any field that is not stated in the text. Do not guess. If several amounts appear, use the amount actually paid.

Example 1
Text: Invoice for Carla Mendes dated 2024-06-30, total 310.50 USD.
Output: {"name": "Carla Mendes", "date": "2024-06-30", "amount": 310.5, "currency": "USD"}

Example 2
Text: Sanjay paid us on 5 May 2025 but didn't say how much.
Output: {"name": "Sanjay", "date": "2025-05-05", "amount": null, "currency": null}

Text: {input}
```

**Success levels.** *Strict parse* = the raw output is valid JSON exactly as returned. *Parse after cleanup* = valid after stripping markdown fences. *Schema OK* = exactly the 4 keys with the right types and `YYYY-MM-DD` date. *All values correct* = schema OK and every value equals the gold answer.

| Variant | Strict parse | Parse after cleanup | Schema OK | All values correct |
|---|---|---|---|---|
| v1_naive | 0/16 (0%) | 16/16 (100%) | 0/16 (0%) | 0/16 (0%) |
| v2_explicit_schema | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) |
| v3_schema_plus_examples | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) |
| v4_examples_plus_json_mode | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) |

**Every failure, with the reason**

- `v1_naive` · J1 · run 1: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null; date '15th Oct 2025' is not YYYY-MM-DD
- `v1_naive` · J1 · run 2: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null; date '15th Oct 2025' is not YYYY-MM-DD
- `v1_naive` · J2 · run 1: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null
- `v1_naive` · J2 · run 2: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null
- `v1_naive` · J3 · run 1: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null
- `v1_naive` · J3 · run 2: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null
- `v1_naive` · J4 · run 1: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null; date '09/11/2025' is not YYYY-MM-DD
- `v1_naive` · J4 · run 2: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null; date '09/11/2025' is not YYYY-MM-DD
- `v1_naive` · J5 · run 1: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null; date 'March 3, 2025' is not YYYY-MM-DD
- `v1_naive` · J5 · run 2: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null; date 'March 3, 2025' is not YYYY-MM-DD
- `v1_naive` · J6 · run 1: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null; date '12 January 2026' is not YYYY-MM-DD
- `v1_naive` · J6 · run 2: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null; date '12 January 2026' is not YYYY-MM-DD
- `v1_naive` · J7 · run 1: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']
- `v1_naive` · J7 · run 2: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']
- `v1_naive` · J8 · run 1: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null; date '1 Dec 2025' is not YYYY-MM-DD
- `v1_naive` · J8 · run 2: raw output is not valid JSON as returned; keys are ['amount', 'date', 'name'], expected ['amount', 'currency', 'date', 'name']; amount is not number/null; date '1 Dec 2025' is not YYYY-MM-DD

### Analysis (write this yourself)

**What changed.** Variant 1 (just "extract ... as JSON") scored 0/16 on strict parsing because every output was wrapped in a markdown code fence, and 0/16 on the schema check: amounts came back as strings with symbols (for example `"₹18,500"`), dates were not ISO (for example `"15th Oct 2025"`), and there was no `currency` key. After stripping the fences all 16 outputs parsed, so the content was mostly fine and the format was the problem. Adding an explicit schema with rules (v2) took every metric to 16/16, and this is where the whole gain came from.

**Where it did not help, and caveats.** Examples (v3) and the API's JSON mode (v4) added no measurable gain because v2 was already at 100%, so this test cannot tell the three apart. The examples did change surface style: all v3 outputs were single-line like the examples, while v2 and v4 were a mix of pretty-printed and single-line. JSON mode's real benefit is a guarantee of pure JSON, which 16 samples per variant cannot demonstrate. Two caveats about my own test: v1's schema failures are partly my doing, since its prompt never asked for `currency` or ISO dates; and the v2 rules (use `null` when a field is missing, use the amount actually paid) were written with my own tricky inputs J7 and J8 in mind, so the 100% partly reflects me anticipating those cases. My name check was also case-insensitive, so v4's `"priya sharma"` (lowercase) counted as correct.

### Complete raw outputs

<details><summary>v1_naive · J1 · run 1 · ✗ failed</summary>

**Input:**

```
hey its priya sharma here, paid the rent yesterday — 15th Oct 2025 — total came to ₹18,500 incl. maintenance
```

**Raw output (unedited):**

````
```json
{
  "name": "Priya Sharma",
  "date": "15th Oct 2025",
  "amount": "₹18,500"
}
```
````

</details>

<details><summary>v2_explicit_schema · J1 · run 1 · ✓ all correct</summary>

**Input:**

```
hey its priya sharma here, paid the rent yesterday — 15th Oct 2025 — total came to ₹18,500 incl. maintenance
```

**Raw output (unedited):**

```
{
  "name": "Priya Sharma",
  "date": "2025-10-15",
  "amount": 18500,
  "currency": "INR"
}
```

</details>

<details><summary>v3_schema_plus_examples · J1 · run 1 · ✓ all correct</summary>

**Input:**

```
hey its priya sharma here, paid the rent yesterday — 15th Oct 2025 — total came to ₹18,500 incl. maintenance
```

**Raw output (unedited):**

```
{"name": "Priya Sharma", "date": "2025-10-15", "amount": 18500, "currency": "INR"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J1 · run 1 · ✓ all correct</summary>

**Input:**

```
hey its priya sharma here, paid the rent yesterday — 15th Oct 2025 — total came to ₹18,500 incl. maintenance
```

**Raw output (unedited):**

```
{
  "name": "priya sharma",
  "date": "2025-10-15",
  "amount": 18500,
  "currency": "INR"
}
```

</details>

<details><summary>v1_naive · J1 · run 2 · ✗ failed</summary>

**Input:**

```
hey its priya sharma here, paid the rent yesterday — 15th Oct 2025 — total came to ₹18,500 incl. maintenance
```

**Raw output (unedited):**

````
```json
{
  "name": "Priya Sharma",
  "date": "15th Oct 2025",
  "amount": "₹18,500"
}
```
````

</details>

<details><summary>v2_explicit_schema · J1 · run 2 · ✓ all correct</summary>

**Input:**

```
hey its priya sharma here, paid the rent yesterday — 15th Oct 2025 — total came to ₹18,500 incl. maintenance
```

**Raw output (unedited):**

```
{"name": "Priya Sharma", "date": "2025-10-15", "amount": 18500, "currency": "INR"}
```

</details>

<details><summary>v3_schema_plus_examples · J1 · run 2 · ✓ all correct</summary>

**Input:**

```
hey its priya sharma here, paid the rent yesterday — 15th Oct 2025 — total came to ₹18,500 incl. maintenance
```

**Raw output (unedited):**

```
{"name": "Priya Sharma", "date": "2025-10-15", "amount": 18500, "currency": "INR"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J1 · run 2 · ✓ all correct</summary>

**Input:**

```
hey its priya sharma here, paid the rent yesterday — 15th Oct 2025 — total came to ₹18,500 incl. maintenance
```

**Raw output (unedited):**

```
{
  "name": "Priya Sharma",
  "date": "2025-10-15",
  "amount": 18500.0,
  "currency": "INR"
}
```

</details>

<details><summary>v1_naive · J2 · run 1 · ✗ failed</summary>

**Input:**

```
INVOICE #4471 // Bill to: Marcus O'Neil // Issued: 2025-03-02 // Amount due: $1,249.99 USD
```

**Raw output (unedited):**

````
```json
{
  "name": "Marcus O'Neil",
  "date": "2025-03-02",
  "amount": "$1,249.99 USD"
}
```
````

</details>

<details><summary>v2_explicit_schema · J2 · run 1 · ✓ all correct</summary>

**Input:**

```
INVOICE #4471 // Bill to: Marcus O'Neil // Issued: 2025-03-02 // Amount due: $1,249.99 USD
```

**Raw output (unedited):**

```
{
  "name": "Marcus O'Neil",
  "date": "2025-03-02",
  "amount": 1249.99,
  "currency": "USD"
}
```

</details>

<details><summary>v3_schema_plus_examples · J2 · run 1 · ✓ all correct</summary>

**Input:**

```
INVOICE #4471 // Bill to: Marcus O'Neil // Issued: 2025-03-02 // Amount due: $1,249.99 USD
```

**Raw output (unedited):**

```
{"name": "Marcus O'Neil", "date": "2025-03-02", "amount": 1249.99, "currency": "USD"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J2 · run 1 · ✓ all correct</summary>

**Input:**

```
INVOICE #4471 // Bill to: Marcus O'Neil // Issued: 2025-03-02 // Amount due: $1,249.99 USD
```

**Raw output (unedited):**

```
{"name": "Marcus O'Neil", "date": "2025-03-02", "amount": 1249.99, "currency": "USD"}
```

</details>

<details><summary>v1_naive · J2 · run 2 · ✗ failed</summary>

**Input:**

```
INVOICE #4471 // Bill to: Marcus O'Neil // Issued: 2025-03-02 // Amount due: $1,249.99 USD
```

**Raw output (unedited):**

````
```json
{
  "name": "Marcus O'Neil",
  "date": "2025-03-02",
  "amount": "$1,249.99 USD"
}
```
````

</details>

<details><summary>v2_explicit_schema · J2 · run 2 · ✓ all correct</summary>

**Input:**

```
INVOICE #4471 // Bill to: Marcus O'Neil // Issued: 2025-03-02 // Amount due: $1,249.99 USD
```

**Raw output (unedited):**

```
{"name": "Marcus O'Neil", "date": "2025-03-02", "amount": 1249.99, "currency": "USD"}
```

</details>

<details><summary>v3_schema_plus_examples · J2 · run 2 · ✓ all correct</summary>

**Input:**

```
INVOICE #4471 // Bill to: Marcus O'Neil // Issued: 2025-03-02 // Amount due: $1,249.99 USD
```

**Raw output (unedited):**

```
{"name": "Marcus O'Neil", "date": "2025-03-02", "amount": 1249.99, "currency": "USD"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J2 · run 2 · ✓ all correct</summary>

**Input:**

```
INVOICE #4471 // Bill to: Marcus O'Neil // Issued: 2025-03-02 // Amount due: $1,249.99 USD
```

**Raw output (unedited):**

```
{
  "name": "Marcus O'Neil",
  "date": "2025-03-02",
  "amount": 1249.99,
  "currency": "USD"
}
```

</details>

<details><summary>v1_naive · J3 · run 1 · ✗ failed</summary>

**Input:**

```
Received 2,500 euros from Jean-Luc Picard on the fourth of July, 2024. Thanks!!
```

**Raw output (unedited):**

````
```json
{
  "name": "Jean-Luc Picard",
  "date": "2024-07-04",
  "amount": "2,500 euros"
}
```
````

</details>

<details><summary>v2_explicit_schema · J3 · run 1 · ✓ all correct</summary>

**Input:**

```
Received 2,500 euros from Jean-Luc Picard on the fourth of July, 2024. Thanks!!
```

**Raw output (unedited):**

```
{
  "name": "Jean-Luc Picard",
  "date": "2024-07-04",
  "amount": 2500,
  "currency": "EUR"
}
```

</details>

<details><summary>v3_schema_plus_examples · J3 · run 1 · ✓ all correct</summary>

**Input:**

```
Received 2,500 euros from Jean-Luc Picard on the fourth of July, 2024. Thanks!!
```

**Raw output (unedited):**

```
{"name": "Jean-Luc Picard", "date": "2024-07-04", "amount": 2500.0, "currency": "EUR"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J3 · run 1 · ✓ all correct</summary>

**Input:**

```
Received 2,500 euros from Jean-Luc Picard on the fourth of July, 2024. Thanks!!
```

**Raw output (unedited):**

```
{
  "name": "Jean-Luc Picard",
  "date": "2024-07-04",
  "amount": 2500,
  "currency": "EUR"
}
```

</details>

<details><summary>v1_naive · J3 · run 2 · ✗ failed</summary>

**Input:**

```
Received 2,500 euros from Jean-Luc Picard on the fourth of July, 2024. Thanks!!
```

**Raw output (unedited):**

````
```json
{
  "name": "Jean-Luc Picard",
  "date": "2024-07-04",
  "amount": "2,500 euros"
}
```
````

</details>

<details><summary>v2_explicit_schema · J3 · run 2 · ✓ all correct</summary>

**Input:**

```
Received 2,500 euros from Jean-Luc Picard on the fourth of July, 2024. Thanks!!
```

**Raw output (unedited):**

```
{
  "name": "Jean-Luc Picard",
  "date": "2024-07-04",
  "amount": 2500,
  "currency": "EUR"
}
```

</details>

<details><summary>v3_schema_plus_examples · J3 · run 2 · ✓ all correct</summary>

**Input:**

```
Received 2,500 euros from Jean-Luc Picard on the fourth of July, 2024. Thanks!!
```

**Raw output (unedited):**

```
{"name": "Jean-Luc Picard", "date": "2024-07-04", "amount": 2500, "currency": "EUR"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J3 · run 2 · ✓ all correct</summary>

**Input:**

```
Received 2,500 euros from Jean-Luc Picard on the fourth of July, 2024. Thanks!!
```

**Raw output (unedited):**

```
{
  "name": "Jean-Luc Picard",
  "date": "2024-07-04",
  "amount": 2500,
  "currency": "EUR"
}
```

</details>

<details><summary>v1_naive · J4 · run 1 · ✗ failed</summary>

**Input:**

```
Dr. Anita Desai - consultation fee Rs. 800/- dated 09/11/2025 (dd/mm/yyyy)
```

**Raw output (unedited):**

````
```json
{
  "name": "Dr. Anita Desai",
  "date": "09/11/2025",
  "amount": "Rs. 800/-"
}
```
````

</details>

<details><summary>v2_explicit_schema · J4 · run 1 · ✓ all correct</summary>

**Input:**

```
Dr. Anita Desai - consultation fee Rs. 800/- dated 09/11/2025 (dd/mm/yyyy)
```

**Raw output (unedited):**

```
{
  "name": "Anita Desai",
  "date": "2025-11-09",
  "amount": 800,
  "currency": "INR"
}
```

</details>

<details><summary>v3_schema_plus_examples · J4 · run 1 · ✓ all correct</summary>

**Input:**

```
Dr. Anita Desai - consultation fee Rs. 800/- dated 09/11/2025 (dd/mm/yyyy)
```

**Raw output (unedited):**

```
{"name": "Anita Desai", "date": "2025-11-09", "amount": 800.0, "currency": "INR"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J4 · run 1 · ✓ all correct</summary>

**Input:**

```
Dr. Anita Desai - consultation fee Rs. 800/- dated 09/11/2025 (dd/mm/yyyy)
```

**Raw output (unedited):**

```
{"name": "Anita Desai", "date": "2025-11-09", "amount": 800.0, "currency": "INR"}
```

</details>

<details><summary>v1_naive · J4 · run 2 · ✗ failed</summary>

**Input:**

```
Dr. Anita Desai - consultation fee Rs. 800/- dated 09/11/2025 (dd/mm/yyyy)
```

**Raw output (unedited):**

````
```json
{
  "name": "Dr. Anita Desai",
  "date": "09/11/2025",
  "amount": "Rs. 800/-"
}
```
````

</details>

<details><summary>v2_explicit_schema · J4 · run 2 · ✓ all correct</summary>

**Input:**

```
Dr. Anita Desai - consultation fee Rs. 800/- dated 09/11/2025 (dd/mm/yyyy)
```

**Raw output (unedited):**

```
{"name": "Anita Desai", "date": "2025-11-09", "amount": 800, "currency": "INR"}
```

</details>

<details><summary>v3_schema_plus_examples · J4 · run 2 · ✓ all correct</summary>

**Input:**

```
Dr. Anita Desai - consultation fee Rs. 800/- dated 09/11/2025 (dd/mm/yyyy)
```

**Raw output (unedited):**

```
{"name": "Anita Desai", "date": "2025-11-09", "amount": 800, "currency": "INR"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J4 · run 2 · ✓ all correct</summary>

**Input:**

```
Dr. Anita Desai - consultation fee Rs. 800/- dated 09/11/2025 (dd/mm/yyyy)
```

**Raw output (unedited):**

```
{
  "name": "Anita Desai",
  "date": "2025-11-09",
  "amount": 800.0,
  "currency": "INR"
}
```

</details>

<details><summary>v1_naive · J5 · run 1 · ✗ failed</summary>

**Input:**

```
Thomas Idris bought a laptop on March 3, 2025 for £1,199.50 (receipt attached)
```

**Raw output (unedited):**

````
```json
{
  "name": "Thomas Idris",
  "date": "March 3, 2025",
  "amount": "£1,199.50"
}
```
````

</details>

<details><summary>v2_explicit_schema · J5 · run 1 · ✓ all correct</summary>

**Input:**

```
Thomas Idris bought a laptop on March 3, 2025 for £1,199.50 (receipt attached)
```

**Raw output (unedited):**

```
{"name": "Thomas Idris", "date": "2025-03-03", "amount": 1199.50, "currency": "GBP"}
```

</details>

<details><summary>v3_schema_plus_examples · J5 · run 1 · ✓ all correct</summary>

**Input:**

```
Thomas Idris bought a laptop on March 3, 2025 for £1,199.50 (receipt attached)
```

**Raw output (unedited):**

```
{"name": "Thomas Idris", "date": "2025-03-03", "amount": 1199.5, "currency": "GBP"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J5 · run 1 · ✓ all correct</summary>

**Input:**

```
Thomas Idris bought a laptop on March 3, 2025 for £1,199.50 (receipt attached)
```

**Raw output (unedited):**

```
{
  "name": "Thomas Idris",
  "date": "2025-03-03",
  "amount": 1199.50,
  "currency": "GBP"
}
```

</details>

<details><summary>v1_naive · J5 · run 2 · ✗ failed</summary>

**Input:**

```
Thomas Idris bought a laptop on March 3, 2025 for £1,199.50 (receipt attached)
```

**Raw output (unedited):**

````
```json
{
  "name": "Thomas Idris",
  "date": "March 3, 2025",
  "amount": "£1,199.50"
}
```
````

</details>

<details><summary>v2_explicit_schema · J5 · run 2 · ✓ all correct</summary>

**Input:**

```
Thomas Idris bought a laptop on March 3, 2025 for £1,199.50 (receipt attached)
```

**Raw output (unedited):**

```
{"name": "Thomas Idris", "date": "2025-03-03", "amount": 1199.5, "currency": "GBP"}
```

</details>

<details><summary>v3_schema_plus_examples · J5 · run 2 · ✓ all correct</summary>

**Input:**

```
Thomas Idris bought a laptop on March 3, 2025 for £1,199.50 (receipt attached)
```

**Raw output (unedited):**

```
{"name": "Thomas Idris", "date": "2025-03-03", "amount": 1199.5, "currency": "GBP"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J5 · run 2 · ✓ all correct</summary>

**Input:**

```
Thomas Idris bought a laptop on March 3, 2025 for £1,199.50 (receipt attached)
```

**Raw output (unedited):**

```
{"name": "Thomas Idris", "date": "2025-03-03", "amount": 1199.5, "currency": "GBP"}
```

</details>

<details><summary>v1_naive · J6 · run 1 · ✗ failed</summary>

**Input:**

```
Ref: refund to Li Wei, 12 January 2026, amount: 75 CAD.
```

**Raw output (unedited):**

````
```json
{
  "name": "Li Wei",
  "date": "12 January 2026",
  "amount": "75 CAD"
}
```
````

</details>

<details><summary>v2_explicit_schema · J6 · run 1 · ✓ all correct</summary>

**Input:**

```
Ref: refund to Li Wei, 12 January 2026, amount: 75 CAD.
```

**Raw output (unedited):**

```
{"name": "Li Wei", "date": "2026-01-12", "amount": 75, "currency": "CAD"}
```

</details>

<details><summary>v3_schema_plus_examples · J6 · run 1 · ✓ all correct</summary>

**Input:**

```
Ref: refund to Li Wei, 12 January 2026, amount: 75 CAD.
```

**Raw output (unedited):**

```
{"name": "Li Wei", "date": "2026-01-12", "amount": 75, "currency": "CAD"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J6 · run 1 · ✓ all correct</summary>

**Input:**

```
Ref: refund to Li Wei, 12 January 2026, amount: 75 CAD.
```

**Raw output (unedited):**

```
{
  "name": "Li Wei",
  "date": "2026-01-12",
  "amount": 75.0,
  "currency": "CAD"
}
```

</details>

<details><summary>v1_naive · J6 · run 2 · ✗ failed</summary>

**Input:**

```
Ref: refund to Li Wei, 12 January 2026, amount: 75 CAD.
```

**Raw output (unedited):**

````
```json
{
  "name": "Li Wei",
  "date": "12 January 2026",
  "amount": "75 CAD"
}
```
````

</details>

<details><summary>v2_explicit_schema · J6 · run 2 · ✓ all correct</summary>

**Input:**

```
Ref: refund to Li Wei, 12 January 2026, amount: 75 CAD.
```

**Raw output (unedited):**

```
{"name": "Li Wei", "date": "2026-01-12", "amount": 75, "currency": "CAD"}
```

</details>

<details><summary>v3_schema_plus_examples · J6 · run 2 · ✓ all correct</summary>

**Input:**

```
Ref: refund to Li Wei, 12 January 2026, amount: 75 CAD.
```

**Raw output (unedited):**

```
{"name": "Li Wei", "date": "2026-01-12", "amount": 75, "currency": "CAD"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J6 · run 2 · ✓ all correct</summary>

**Input:**

```
Ref: refund to Li Wei, 12 January 2026, amount: 75 CAD.
```

**Raw output (unedited):**

```
{"name": "Li Wei", "date": "2026-01-12", "amount": 75, "currency": "CAD"}
```

</details>

<details><summary>v1_naive · J7 · run 1 · ✗ failed</summary>

**Input:**

```
Aisha Khan paid by card on 20 Feb 2025, forgot to note down the total.
```

**Raw output (unedited):**

````
```json
{
  "name": "Aisha Khan",
  "date": "2025-02-20",
  "amount": null
}
```
````

</details>

<details><summary>v2_explicit_schema · J7 · run 1 · ✓ all correct</summary>

**Input:**

```
Aisha Khan paid by card on 20 Feb 2025, forgot to note down the total.
```

**Raw output (unedited):**

```
{
  "name": "Aisha Khan",
  "date": "2025-02-20",
  "amount": null,
  "currency": null
}
```

</details>

<details><summary>v3_schema_plus_examples · J7 · run 1 · ✓ all correct</summary>

**Input:**

```
Aisha Khan paid by card on 20 Feb 2025, forgot to note down the total.
```

**Raw output (unedited):**

```
{"name": "Aisha Khan", "date": "2025-02-20", "amount": null, "currency": null}
```

</details>

<details><summary>v4_examples_plus_json_mode · J7 · run 1 · ✓ all correct</summary>

**Input:**

```
Aisha Khan paid by card on 20 Feb 2025, forgot to note down the total.
```

**Raw output (unedited):**

```
{
  "name": "Aisha Khan",
  "date": "2025-02-20",
  "amount": null,
  "currency": null
}
```

</details>

<details><summary>v1_naive · J7 · run 2 · ✗ failed</summary>

**Input:**

```
Aisha Khan paid by card on 20 Feb 2025, forgot to note down the total.
```

**Raw output (unedited):**

````
```json
{
  "name": "Aisha Khan",
  "date": "2025-02-20",
  "amount": null
}
```
````

</details>

<details><summary>v2_explicit_schema · J7 · run 2 · ✓ all correct</summary>

**Input:**

```
Aisha Khan paid by card on 20 Feb 2025, forgot to note down the total.
```

**Raw output (unedited):**

```
{
  "name": "Aisha Khan",
  "date": "2025-02-20",
  "amount": null,
  "currency": null
}
```

</details>

<details><summary>v3_schema_plus_examples · J7 · run 2 · ✓ all correct</summary>

**Input:**

```
Aisha Khan paid by card on 20 Feb 2025, forgot to note down the total.
```

**Raw output (unedited):**

```
{"name": "Aisha Khan", "date": "2025-02-20", "amount": null, "currency": null}
```

</details>

<details><summary>v4_examples_plus_json_mode · J7 · run 2 · ✓ all correct</summary>

**Input:**

```
Aisha Khan paid by card on 20 Feb 2025, forgot to note down the total.
```

**Raw output (unedited):**

```
{"name": "Aisha Khan", "date": "2025-02-20", "amount": null, "currency": null}
```

</details>

<details><summary>v1_naive · J8 · run 1 · ✗ failed</summary>

**Input:**

```
Paid ₹500 to Ravi Kumar on 1 Dec 2025 (his bill was ₹650 but he gave a discount of ₹150).
```

**Raw output (unedited):**

````
```json
{
  "name": "Ravi Kumar",
  "date": "1 Dec 2025",
  "amount": "₹500"
}
```
````

</details>

<details><summary>v2_explicit_schema · J8 · run 1 · ✓ all correct</summary>

**Input:**

```
Paid ₹500 to Ravi Kumar on 1 Dec 2025 (his bill was ₹650 but he gave a discount of ₹150).
```

**Raw output (unedited):**

```
{
  "name": "Ravi Kumar",
  "date": "2025-12-01",
  "amount": 500,
  "currency": "INR"
}
```

</details>

<details><summary>v3_schema_plus_examples · J8 · run 1 · ✓ all correct</summary>

**Input:**

```
Paid ₹500 to Ravi Kumar on 1 Dec 2025 (his bill was ₹650 but he gave a discount of ₹150).
```

**Raw output (unedited):**

```
{"name": "Ravi Kumar", "date": "2025-12-01", "amount": 500.0, "currency": "INR"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J8 · run 1 · ✓ all correct</summary>

**Input:**

```
Paid ₹500 to Ravi Kumar on 1 Dec 2025 (his bill was ₹650 but he gave a discount of ₹150).
```

**Raw output (unedited):**

```
{"name": "Ravi Kumar", "date": "2025-12-01", "amount": 500.0, "currency": "INR"}
```

</details>

<details><summary>v1_naive · J8 · run 2 · ✗ failed</summary>

**Input:**

```
Paid ₹500 to Ravi Kumar on 1 Dec 2025 (his bill was ₹650 but he gave a discount of ₹150).
```

**Raw output (unedited):**

````
```json
{
  "name": "Ravi Kumar",
  "date": "1 Dec 2025",
  "amount": "₹500"
}
```
````

</details>

<details><summary>v2_explicit_schema · J8 · run 2 · ✓ all correct</summary>

**Input:**

```
Paid ₹500 to Ravi Kumar on 1 Dec 2025 (his bill was ₹650 but he gave a discount of ₹150).
```

**Raw output (unedited):**

```
{"name": "Ravi Kumar", "date": "2025-12-01", "amount": 500, "currency": "INR"}
```

</details>

<details><summary>v3_schema_plus_examples · J8 · run 2 · ✓ all correct</summary>

**Input:**

```
Paid ₹500 to Ravi Kumar on 1 Dec 2025 (his bill was ₹650 but he gave a discount of ₹150).
```

**Raw output (unedited):**

```
{"name": "Ravi Kumar", "date": "2025-12-01", "amount": 500, "currency": "INR"}
```

</details>

<details><summary>v4_examples_plus_json_mode · J8 · run 2 · ✓ all correct</summary>

**Input:**

```
Paid ₹500 to Ravi Kumar on 1 Dec 2025 (his bill was ₹650 but he gave a discount of ₹150).
```

**Raw output (unedited):**

```
{
  "name": "Ravi Kumar",
  "date": "2025-12-01",
  "amount": 500,
  "currency": "INR"
}
```

</details>

## 4. Overall conclusions (write this yourself)

The biggest gain came from the explicit schema in the structured-output task (0% to 100% on schema validity and on correct values). Next was few-shot prompting fixing the output format in classification (strict accuracy 10% to 100%, although real classification accuracy was already 100%). Chain-of-thought gave the least: no accuracy change on these problems at roughly double the output length. In all three tests the model (`gemini-3.5-flash-lite`, temperature 0.7, 2 runs per input) was already strong, so the techniques mainly improved the format and reliability of the output, not its underlying capability.

With more time I would use harder and more ambiguous inputs, a truly answer-only direct prompt, more runs per input, and a weaker model, so that the techniques have room to show a difference.
