# DTDLINK — complete English speaking script

Session 7, Group 5. Record A, B and C separately and combine them into one video.
Read the matching presenter files for screen actions and rehearsal instructions.
Timings are targets; rehearse the complete recording before export.


# Presenter A — Introduction and website demonstration


## A1 · 00:00–00:30 · Introduction

Hello, we are Session Seven, Group Five. Our project is DTDLINK, Detect The
Deception Links. It helps people inspect a suspicious link before opening it.
Our React interface connects to a FastAPI backend and a trained Random Forest.
The application analyses URL text without visiting the destination website.

## A2 · 00:30–01:35 · A real prediction and readable URL evidence

I will select “A misleading address” and analyse it. The main result shows the
model's prediction and its confidence. This estimate is not a guarantee of
real-world harm or safety.
The actual host is account-check dot example. PayPal dot com appears before
the at sign, so it is user information, not the destination hostname.

The breakdown separates the connection type, user information, hostname and
page path. “Hidden destination” explains the misleading structure and suggests
checking a trusted address. “Account-related terms” shows words such as account
and login. These are observations about the text, not the exact reasons for
the model's decision.

## A3 · 01:35–02:40 · Loading, validation and error states

During a request, the button shows “Analysing” and prevents repeated submission.
We have slowed the response for this demonstration so the loading state is visible.
An incomplete address receives a message beside the input.
Here, a deliberately interrupted request shows a service error. An unknown
route shows our not-found page. A separate controlled rendering failure reaches
the unexpected-error fallback, with a reload option. These are controlled faults
to demonstrate recovery, rather than a normal prediction.

## A4 · 02:40–03:10 · Phone layout and keyboard access

This is the phone-sized layout. The navigation collapses into a menu, and the
result remains readable. Labels and visible keyboard focus support accessibility.
Users can move through controls with Tab and submit with Enter.

## A5 · 03:10–04:15 · Two interactive visualisations

The first chart groups observed signals by attention level. I can filter the
categories and select “Hidden destination” for more detail.

Session insights answers a different question: how do the model scores compare
across checks? I can filter predictions and select a check to inspect its score
and signal count. The dashed line marks the fifty-percent decision threshold.

Only the latest twenty anonymous entries remain in memory. This comparison
excludes URLs and hostnames. Clearing the session removes these entries.

Next, we will follow a request through the actual frontend, API and model code.

# Presenter B — Follow one request through the actual code


## B1 · 04:15–04:40 · Architecture

I will explain how the parts connect. React sends one URL to FastAPI. The
backend validates it, extracts features, runs the saved model, and returns JSON.
React then displays the result. We use POST for prediction and GET for readiness
and model information, so both methods serve a practical purpose.

## B2 · 04:40–05:30 · Frontend input and request

In App dot JSX, onSubmit first validates the input. It then sets the loading
state and sends the original string in a JSON object containing the URL field.
It does not remove HTTPS or rewrite the input to improve the prediction.

In api dot JS, fetch sends the request to slash predict. The response is parsed
as JSON. Failed status codes become useful messages, and an AbortController
handles the ten-second client timeout. Finally, the loading state is cleared.

## B3 · 05:30–06:35 · Pydantic, real /docs request and errors

Frontend checks help users, but attackers can bypass the interface. In schemas
dot PY, Pydantic requires a string with a maximum of two thousand and forty-eight
characters, and our validator requires a complete HTTP or HTTPS URL.

Here in slash docs, I submit the same example directly to the API. The successful
response contains the label, dangerous probability, confidence, URL components
and observations. These values come from the backend, rather than fixed interface text.
Removing the scheme returns status four twenty-two. The error uses a consistent
JSON structure with a code, message, field details and request identifier.
Internal stack traces and filesystem paths are not returned.

## B4 · 06:35–07:40 · Startup and real model inference

In main dot PY, the lifespan function loads the model once when the server
starts. The service checks its trusted hash before loading the joblib file.

The prediction service calls the saved URL pipeline. Features from URLs applies
the unchanged Assignment Two extractor and builds a table in the required
feature order. The classifier then calls predict proba.

This is a Random Forest using thirty-six numeric features, including URL length,
user information and hostname structure. We preserve the training-time feature
logic instead of introducing different preprocessing at prediction time.

## B5 · 07:40–08:45 · Meaning of the response and design choices

Class zero is benign. Class one combines phishing, malware and defacement,
so the application does not claim to identify a particular attack type.

At a dangerous probability of at least zero point five, the label is “Potentially
dangerous”. Below that threshold, it is “Likely legitimate”. Confidence is the
probability of the predicted class: either p or one minus p.

Result dot JSX displays these returned values. URLAnalysis displays the address
and observations as escaped React text, without making the destination clickable.
The observations are a separate explanation layer, not learned feature contributions.

We chose local text analysis to avoid fetching untrusted destinations and sending
submitted links to outside services. Next, we will demonstrate the application's
security controls and their limitations.

# Presenter C — Security, reproducibility and limitations


## C1 · 08:45–09:30 · Threat model and baseline controls

An attacker can bypass React, submit hostile input and send concurrent requests
to mislead the model or exhaust the service.

We enforce backend input and body limits, text-only rendering, exact CORS and
security headers. CORS is not authentication.

Without a database or outbound website requests, the prediction path does not
expose SQL injection or server-side request forgery. Our selected defences address
availability and configuration risks.

## C2 · 09:30–11:35 · Defence one: application-level denial of service

First, application-level denial of service. Our test-only baseline runs synchronous
inference inside an asynchronous endpoint. This blocks the event loop, delaying
unrelated requests.

The script compares that baseline with the production application factory using
thirty-two concurrent predictions, repeated ten times, while measuring health
request completion.
Compare the baseline and defended health timings in the output. The defended
case rejects excess work with status five oh three instead of accepting an
unbounded workload. The health endpoint remains available.
In main dot PY, a bounded thread pool moves inference away from the event loop.
The default capacity is two jobs. The endpoint checks capacity before scheduling
work, and returns five oh three with a retry header when it is full.

Slots remain occupied until the actual work finishes, even if the client cancels.

The separate slow-request case deliberately repeats inference thirty times to
create controlled load. It is not a discovered URL exploit. These in-process
measurements demonstrate scheduling, not protection against a distributed network attack.

The trade-off is limited throughput: legitimate users may need to retry while
all prediction slots are occupied.

## C3 · 11:35–12:55 · Defence two: configuration and dependencies

Our second defence addresses misconfiguration and vulnerable dependencies.
These saved audit results are from November fifth.

ZAP identified an overly permissive inline-style policy. We tightened the content
security policy, using self-hosted styles and a development nonce. The bounded
scan after that fix recorded no high, medium or low alerts, with informational
observations still documented.

The dependency audit also identified issues in the environment's pip version.
We upgraded it in the isolated Assignment Three environment. The saved pip and
npm audits then reported no known findings. A clean scan is not proof of complete security.
This request rejects an unapproved Origin. We test only our own local application.
These controls require dependency reviews and a policy permitting only necessary resources.

## C4 · 12:55–13:25 · Running the application and acknowledging assistance

The README covers installation, pinned dependencies, startup, architecture and
references. The included model needs no retraining. Our AI statement discloses
assistance with implementation, testing and documentation.

## C5 · 13:25–14:15 · Honest limitations and next steps

Finally, the model still produces false positives and is sensitive to URL
formatting. Its confidence is uncalibrated, and it cannot distinguish the three
dangerous subtypes or inspect current website content.

Separate Assignment Three experiments improved some validation metrics but did
not meet all acceptance criteria, so the primary application retains the original
model. We do not claim a completed advanced security study under section two point eight.

Next steps include better-sourced data, independent evaluation and broader
deployment testing. DTDLINK provides evidence to support cautious decisions,
rather than a guarantee of safety. Thank you.
