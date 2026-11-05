# Presenter A — Introduction and website demonstration

**Final-video timeline:** 00:00–04:15. The group will choose the presenter. Read only the English blockquotes aloud; all other text gives recording instructions. Timings are targets and must be checked during rehearsal. Use the primary app at http://127.0.0.1:5173/.

## A1 · 00:00–00:30 · Introduction

**Screen:** Open Check URL with no result displayed. A short project title is enough; no long slide introduction is needed.

> Hello, we are Session Seven, Group Five. Our project is DTDLINK, Detect The
> Deception Links. It helps people inspect a suspicious link before opening it.
> Our React interface connects to a FastAPI backend and a trained Random Forest.
> The application analyses URL text without visiting the destination website.

## A2 · 00:30–01:35 · A real prediction and readable URL evidence

**Actions, in order:**
1. Click **A misleading address**, then **Analyse link**. The example button fills the input but does not submit it.
2. Point to the returned label and confidence. The input is `https://paypal.com@account-check.example/login`. The browser check on 6 November displayed Potentially dangerous and 97.3% confidence. The narration avoids quoting that number.
3. Scroll to **THIS LINK POINTS TO**. Expand **Understand the parts of this URL**.
4. Point to **Hidden destination** and **Account-related terms** under **READ THE SIGNS** as you explain them. Do not open the submitted destination.

> I will select “A misleading address” and analyse it. The main result shows the
> model's prediction and its confidence. This estimate is not a guarantee of
> real-world harm or safety.
> The actual host is account-check dot example. PayPal dot com appears before
> the at sign, so it is user information, not the destination hostname.
>
> The breakdown separates the connection type, user information, hostname and
> page path. “Hidden destination” explains the misleading structure and suggests
> checking a trusted address. “Account-related terms” shows words such as account
> and login. These are observations about the text, not the exact reasons for
> the model's decision.

## A3 · 01:35–02:40 · Loading, validation and error states

**Prepare these controlled-state clips before recording:** Delay a request so loading stays visible; interrupt a request to show the service error; use the existing malformed-response test for the rendering fallback. See the bundle README for rehearsal commands. Restore normal connectivity before the next real prediction; do not modify the model.

**Actions, in order:** Show **Analysing…** and **Reading the signs in your link…**. Submit `example.com/` to show **Start the URL with http:// or https://.** Then show the interrupted-request clip, the `/unknown-page` route, and the separate rendering fallback. Match each spoken sentence to its corresponding screen. Controlled error responses are test fixtures, not model predictions.

> During a request, the button shows “Analysing” and prevents repeated submission.
> We have slowed the response for this demonstration so the loading state is visible.
> An incomplete address receives a message beside the input.
> Here, a deliberately interrupted request shows a service error. An unknown
> route shows our not-found page. A separate controlled rendering failure reaches
> the unexpected-error fallback, with a reload option. These are controlled faults
> to demonstrate recovery, rather than a normal prediction.

## A4 · 02:40–03:10 · Phone layout and keyboard access

**Actions:** Use a phone-sized viewport of approximately 375×812. Open and close the navigation menu, show the input and a result, and use Tab to show focus and Enter to submit. Describe this as a phone-sized viewport, not a physical-device test. Return to desktop size before the chart scene.

> This is the phone-sized layout. The navigation collapses into a menu, and the
> result remains readable. Labels and visible keyboard focus support accessibility.
> Users can move through controls with Tab and submit with Enter.

## A5 · 03:10–04:15 · Two interactive visualisations

**Prepare:** In the same normal browser tab, run the misleading and simple examples, then run the misleading example again so its signals are available. These inputs are not independently verified safety labels. Do not reload before showing Session insights.

**Actions, in order:**
1. In **What deserves a closer look?**, change **Show signals** to **High attention**, then select **Hidden destination**.
2. Open **Session insights**, select a **Check #** button, and demonstrate **Filter checks**. If there are no legitimate predictions, show the empty state for that filter, then return to **All results**.
3. Point to the dashed threshold line and anonymous check details.
4. Click **Clear session** only after finishing the chart demonstration.

> The first chart groups observed signals by attention level. I can filter the
> categories and select “Hidden destination” for more detail.
>
> Session insights answers a different question: how do the model scores compare
> across checks? I can filter predictions and select a check to inspect its score
> and signal count. The dashed line marks the fifty-percent decision threshold.
>
> Only the latest twenty anonymous entries remain in memory. This comparison
> excludes URLs and hostnames. Clearing the session removes these entries.
>
> Next, we will follow a request through the actual frontend, API and model code.

## Understand before recording

- Confidence belongs to the predicted class; it does not measure real-world safety.
- The hostname after the at sign determines the host. Familiar text before it does not verify the destination.
- The charts show different things: pattern counts by attention level and model scores across checks.
- Loading, interrupted requests and rendering failures are controlled demonstrations. Record the matching state before using its narration. Do not present a fixture or test screenshot as a real model prediction.

**Pronunciation:** URL = “you are ell”; API = “A P I”; @ = “at sign”. Point to long URLs instead of reading every character.
