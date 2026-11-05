Assignment 3
Due Sunday by 23:59 Points 45 Submitting a file upload
Assignment Name

Full-Stack Web Development for a Secure AI Application

Assignment Description

In this final assignment, you turn a trained model into a full-stack web application that people can use and that holds up when someone tries to misuse it. The front end must be built with React and the back end with FastAPI. A user provides input through the front end, the back end runs it through your model, and the result comes back to the user clearly and safely.

Treat your model as a black box that takes an input and returns a prediction. You may use your Assignment 2 model, or any model you train for your topic. This assignment does not mark your model's accuracy. It marks how well you build, connect, and protect the application around the model, so a weaker model from Assignment 2 will not cost you marks here.

Every topic in this unit is a cybersecurity problem, which means your application will receive hostile input by design. Making it secure is the focus of this assignment, and the main route to the highest marks.

As the final assignment of the unit, this project carries the largest weight. It tests whether you can build a complete web application, connect a model to it, handle errors and hostile input safely, and explain clearly how all of it works.

Weight	
45% of your total marks for the unit

Due Date

Sunday 8 November 2026, 11:59 pm (Week 13)

Submission	
Source code (ZIP), including your README and your model file
Video (MP4 or AVI), 15 minutes maximum
Meeting minutes (PDF)
Contribution form (PDF)
There is no written report. Section 3 describes each deliverable.

Late Penalties

Any submission after the due date counts as late. For the first 3 days late, no marks are deducted. From the fourth day, 5% of the available mark is deducted for each calendar day or part thereof.

Monday 9 to Wednesday 11 November, late, but no marks deducted
Thursday 12 November, 5% deducted
Friday 13 November, 10% deducted
Saturday 14 November, 15% deducted
Sunday 15 November, 20% deducted
Submissions more than 7 calendar days late are not accepted. If serious circumstances mean you need more time than this, email your tutor and Lecturer as soon as possible to request an extension.

1. Project Description
This project develops a complete machine learning solution to a real cybersecurity problem, combining project management, design and technical implementation. Your team works through three phases, planning the project in Assignment 1, building and evaluating a model in Assignment 2, and delivering it as a secure web application in this assignment.

Your topic is the one your team has worked on all semester: one of prompt injection guardrail, AI-generated content detection, phishing URL detection, and log anomaly detection.

 

2. Overview of the tasks
Sections 2.1 to 2.5 apply to every topic. Together they describe a complete, working application.

2.1 Front end (React.js)
The front end is what users and markers see first, so it must work well and look professional.

An input form that validates input before anything is sent to the back end
Results shown clearly with the model's confidence, and the result as the most prominent element on screen
Visible loading, success and error states, so the user always knows what is happening
Error pages, including a page for addresses that do not exist and a fallback page when something fails unexpectedly, so the user never sees a blank screen
At least two visualisations, each answering a different question about the results, with clear titles, labels and legends, and tooltips at minimum
A consistent visual design throughout, with one colour scheme, consistent typography and spacing, and a clear layout
A responsive layout that works on both a desktop and a phone-sized screen
Basic accessibility, with a label on every input, readable colour contrast, and every function usable by keyboard
For a topic that checks one input at a time, one visualisation can show the current result while another compares all the inputs checked in the current session. More charts do not earn more marks. Each one should help the user understand something the others do not.

2.2 Back end (FastAPI)
Request and response models defined with Pydantic
At least two HTTP methods, each used for a genuine purpose
Correct HTTP status codes, and clear error messages when input is invalid
Every error, including unexpected ones, returned in one consistent JSON format, without internal details such as stack traces
The model loaded once when the server starts, not on every request
2.3 Security hygiene
These are the minimum expected of any application in a cybersecurity unit. None of them takes much work, and an application that misses them cannot reach the higher grades.

User input is never rendered as HTML
Text inputs and file uploads have a size limit, enforced on the back end
CORS allows only your own front end, not every origin
Passwords, keys and other secrets are kept out of your source code, for example in environment variables
React escapes text for you, so the first requirement holds as long as you never bypass it, for example with dangerouslySetInnerHTML to highlight words. React 19 and later also neutralise a javascript: link written into href, but earlier versions at most print a warning, and no version protects a URL passed to window.open or assigned to window.location.

2.4 Running the application
The whole application starts from your README on a clean machine
Dependency versions are pinned, so the application runs the same way for the marker as it does for you
2.5 Requirements for your topic
You decide what your application takes as input, whether that is text, a URL, an image, audio, a log file, or a combination, so that it suits the model you are deploying. What your topic decides is what the application must show at minimum.

Topic

The application shows at minimum

Prompt injection guardrail

Whether the input is allowed or blocked, with confidence

AI-generated content detection

Whether the content is AI-generated or human-made, with confidence

Phishing URL detection

Whether the input is phishing or legitimate, with confidence

Log anomaly detection

Each session with an anomaly score, an overall summary, and a detail view for any session the user selects

2.6 Threat model
Before you defend your application, decide what you are defending it against. Write a short threat model that answers three questions.

Who would want to attack your application?
What are they trying to achieve?
What can they actually do to it?
Your answers decide which defences matter most, and you should use them to justify the choices you make in section 2.7. Half a page in your README is enough, and you should summarise it in your video before demonstrating your defences.

Each topic suggests a natural starting point.

Topic

A likely attacker, and what they want

Phishing URL detection

A phisher who wants their link to pass as legitimate

Prompt injection guardrail

An attacker who wants an injection to get past the guardrail

AI-generated content detection

Someone who wants AI-generated content to be judged human-made

Log anomaly detection

An intruder who wants their activity hidden among normal logs, using log lines that may themselves carry malicious content

2.7 Innovation. Security defences

Innovation in this assignment means defending your application against the attacks your threat model identifies, and proving each defence works by attacking your own application.

One principle runs through all of this. Front-end checks are for usability. Back-end checks are for security. Attackers do not use your interface, so several of the attacks below can only be demonstrated by sending requests directly, with a tool such as curl or Postman.

Not every risk applies to every application. An application whose back end never makes outbound requests cannot suffer SSRF, and one without a database cannot suffer SQL injection. Part of your threat model is working out which risks your design actually exposes, and saying briefly why the others do not apply.

Each risk below has a level, which sets the most a defence against it can earn. A Basic defence can earn up to 2 marks, an Intermediate one up to 3, and an Advanced one up to 4. Levels reflect how much work a defence takes to build and demonstrate, not how serious the risk is.

Risk

Level

When it applies to your application

How to prove you have stopped it

Unsafe model loading

Basic

Whenever you load a model with joblib or pickle, both of which can execute code hidden in the file. It matters most when the model file comes from a download script or from someone else

Check the model file's hash when the server starts, and refuse to load it if the hash does not match

Command injection

Basic

Whenever your back end runs a system command, such as the whois tool. Pasting the input into a shell command lets input such as example.com; ls run commands of the attacker's choosing

Submit a crafted input with curl and show the extra command never runs, because the input is validated and passed as a list of arguments, never through a shell

Missing rate limiting

Basic

Every application. FastAPI sets no limit, so anyone can flood the API or probe how the model makes its decisions

Send rapid requests and show the limit is enforced

SQL injection

Intermediate

Once you store data in a database, such as a history of past checks. Building a query by pasting the input into the SQL text lets input such as ' OR '1'='1 change what the query does

Submit a crafted input with curl, show it is stored and returned as plain data, and show that every query passes input as a parameter or through an ORM such as SQLAlchemy

Unsafe file upload

Intermediate

Whenever you accept files. FastAPI does not limit upload size for you, and saving a file under the user's own filename lets ../ write outside the upload folder. A size limit alone is already required by section 2.3, so this defence must go further

Send an oversized file, a crafted filename, and a file whose contents do not match its type with curl, and show all three are rejected

Misconfiguration and vulnerable dependencies

Intermediate

Every application. Security headers are not set by default, debug features are easy to leave on, and any library can carry a known vulnerability

Run pip-audit and npm audit, scan the running application with OWASP ZAP, then fix or justify each finding

Denial of service

Advanced

Every application, because running a model costs far more than sending a request. Slow inference inside an async def endpoint makes every other user wait until it finishes, and a small crafted input can cost far more than it looks, such as text that makes a regular expression backtrack, or a 118 KB image that takes 300 MB of memory once decoded

Send one deliberately expensive request and show that other requests are still answered promptly, then send many at once and show the application rejects the excess with a 503 error instead of freezing

Server-side request forgery (SSRF)

Advanced

Only if your back end makes a request based on the input, such as fetching a page, looking up a domain, or downloading an image from a link

Submit inputs that point at internal addresses, such as 127.0.0.1 or a link that redirects there, and show from your back-end logs that no such request is made

Broken access control

Advanced

Only once you add user accounts. User B may then fetch user A's records by requesting them directly

Logged in as user B, request one of user A's record IDs with curl, and show the request is refused

A distributed denial-of-service attack, where many machines flood your network at once, is stopped upstream by a hosting provider or a content delivery network rather than by application code, and it cannot be tested fairly on a single laptop. What your back end can and should defend against is a request that costs it far more to handle than it costs an attacker to send.

Each topic has a natural place to start. SQL injection suits prompt injection, because every input is itself an attack string and is easily stored in a history of past checks. SSRF and command injection suit phishing, where lookups such as WHOIS are tempting to add. File upload suits any application that accepts files, such as log files, images or audio. Rate limiting suits AI-generated content detection, where people may probe the detector repeatedly. Denial of service suits any application whose inference is slow, such as one using a deep learning model or parsing large log files. Denial of service and misconfiguration apply to every application, so every topic has a route to full marks.

Choose up to two defences, from risks your application actually has, and name them in your README. Only those two are marked, so building more earns nothing extra. Your two defences together are capped at 8 marks, so full marks for this section need one Advanced defence together with an Intermediate or Advanced one. You may choose two Advanced defences, but the total is still capped at 8 marks.

Each defence is marked on its quality, up to the value of its level. The highest marks go to a defence that stops the attack and its obvious variations, is shown in your video with the attack succeeding without the defence and failing with it, is justified by your threat model, and has its cost explained. A defence that an obvious variation can get past, or that is shown working without the attack, earns less. A defence that does not appear in the video earns nothing.

If you choose both rate limiting and denial of service, each must rely on a different mechanism. A justified innovation of your own can take the place of one of the two, and your tutor will decide its level by the same standard. Security is still the recommended direction.

2.8 Advanced security
This part goes beyond typical undergraduate work and is aimed at groups who want the highest marks. These attacks exploit the fact that a trained model sits behind an API, however accurate the model is. Choose one, name it in your README, and do it properly. Only one is marked.

Side channels. A side channel leaks information through something other than the response itself, such as how long the response takes or how large it is. An application can therefore give its answer away even when the visible response reveals nothing.

Attack

What it looks like in this application

What to measure

Timing side channel in the decision

Every response looks the same, but some take longer, for example because blocked requests do extra work, so an attacker can infer the outcome from timing alone

The response-time distribution for each outcome, before and after you make response times uniform

Cache timing side channel

If you cache results to speed up repeated inputs, a cached answer returns far faster, so anyone can tell whether another user has already checked a given input. In our test, a cached answer took about 2 ms and a new one about 17 ms, with no overlap at all

Response times for inputs other users have submitted against new inputs, before and after you scope the cache to each user or remove the difference

Response size side channel

Responses that differ in size by outcome reveal the outcome even to someone who cannot read them. HTTPS hides the content of a response but not its length. In our test, an allowed response was 21 bytes and a blocked one 118 bytes

The response size for each outcome, before and after you return the same fields at the same size for every outcome

Login timing side channel

Only once you add user accounts. If the password check runs only for usernames that exist, a failed login reveals which usernames are real. In our test, a real username took about 490 ms to reject and an unknown one under 2 ms

Response times for real and unknown usernames, before and after you always run the password check, against a dummy hash when the username does not exist

Some side channels are created by defences elsewhere in this specification. A cache that protects you against denial of service is exactly what creates the cache timing side channel, so if you add one, check whether it leaks.

Attacks on the model through its API.

Attack

What it looks like in this application

What to measure

Membership inference

The model's confidence reveals whether a particular example was in its training data

Attack accuracy compared with the 50% of random guessing, before and after your defence

Model extraction

Repeated queries let an attacker train a copy of your model

How closely the copy agrees with your model as the number of queries grows, with and without your defence

Detection evasion

Small changes, such as swapping letters for look-alike Unicode characters, change what the model sees without changing what a person sees

The evasion success rate, before and after you normalise input before it reaches the model

Four conditions apply to this part.

Measure before and after. Implement the attack, measure it, add your defence, and measure again. A claim without numbers earns no marks, because the obvious defence does not always work. Hiding the model's confidence and returning only a label, for example, does far less to stop model extraction than you might expect.
Secure the basics first. This part only counts once your application meets the security hygiene requirements in section 2.3.
Explain what the defence costs. Uniform response times slow the application down, hiding confidence gives the user less information, and a cache scoped to each user saves less work. Say what you gave up and why it was worth it.
Attack only your own application, on your own machine.
Suggested reading
OWASP Top 10Links to an external site., the standard list of the most critical web application security risks
Bortz, A. and Boneh, D. (2007) 'Exposing private information by timing web applicationsLinks to an external site.', in Proceedings of the 16th International Conference on World Wide Web. ACM, pp. 621–628.
Chen, S., Wang, R., Wang, X. and Zhang, K. (2010) 'Side-channel leaks in web applications: a reality today, a challenge tomorrowLinks to an external site.', in 2010 IEEE Symposium on Security and Privacy. IEEE, pp. 191–206.
Shokri, R., Stronati, M., Song, C. and Shmatikov, V. (2017) 'Membership inference attacks against machine learning modelsLinks to an external site.', in 2017 IEEE Symposium on Security and Privacy. IEEE, pp. 3–18.
Tramèr, F., Zhang, F., Juels, A., Reiter, M.K. and Ristenpart, T. (2016) 'Stealing machine learning models via prediction APIsLinks to an external site.', in Proceedings of the 25th USENIX Security Symposium. USENIX Association, pp. 601–618.
 

3 Deliverables
There is no written report. Everything a report would have covered now lives in your README, your API documentation, and your video.

Source code (ZIP). Front end and back end in separate folders. Include your model file, or a download script if it is too large to upload. Leave out node_modules.
README. Setup and run instructions, an architecture diagram, your pinned dependency versions, your threat model, references in Harvard style, a statement of how you used generative AI, and the defences and advanced attack you want marked.
API documentation. Use the /docs page that FastAPI generates for you. Make sure every endpoint has a description and an example request and response.
Video, 15 minutes maximum. See section 3.1.
Meeting minutes (PDF). At least one meeting each week since your team formed. You can use the attached meeting minutes as they are or as a reference to create your own. Meeting Minutes Example.docx
Contribution form (PDF). Download and complete Group Assessment Contribution Form.docx. You can download the form Group Assessment Contribution Form.docxDownload Group Assessment Contribution Form.docx
3.1 Video presentation
Your video is the main way your work is assessed, so plan it as carefully as the application itself. You decide how to structure it and how long to spend on each part, within the 15-minute maximum. Whatever structure you choose, the video must clearly explain the following.

Who the application is for, and what problem it solves
The full workflow from input to result, demonstrated live, including invalid input, error pages, and the phone-sized layout
How the parts of your code connect, following one request from the front end through your API and model and back, shown in your actual code and in /docs
How the key parts are implemented, walking through the code itself rather than only slides, and explaining in your own words what it does and why you wrote it that way
The key design decisions you made, and why you made them
Your threat model, how the application handles malicious input, and for any attack or defence you built, how the attack works and how your code stops it, demonstrated by attacking your own application
What does not work yet, and what you would do next
Anything you want marked must appear in the video, because markers assess your work mainly from it.

The video is also marked in its own right, for how well you show that you understand your own work and why it is built the way it is. If you cannot explain part of your application, you lose marks here even if that part works. A missing feature loses marks only under the application criteria, not here as well.

Your team decides who presents. Not every member has to appear in the video.
If your file exceeds the Canvas upload limit, upload it to YouTube as an unlisted video, submit the link in a text file named group-name-video-link.txt, and keep the link active until marking is complete.
If the video cannot be opened at the time of marking, most components of this assignment will receive zero. Check that it plays before you submit.
 

4. Submission
Submit through the Assignment 3 Submission link on Canvas by Sunday 8 November 2026, 11:59 pm (Week 13). No hard copy is required. Only one member of each group submits, and that member submits all the files.

File naming. Name every file with your group name, for example session-xx-group-1-A3-video.mp4. Marks may be deducted if naming and file requirements are not followed. Submissions by email are not accepted.

Deliverable

Format

Source code

One ZIP file, with front end and back end in separate folders, and the README in Markdown or PDF. Include your model file in the back-end folder, or a download script if it is too large to upload.

Video

MP4 or AVI, 15 minutes maximum, or an unlisted YouTube link in group-name-video-link.txt

Meeting minutes

PDF

Contribution form

PDF

 

5. Marking Criteria
The full rubric is provided separately. The table below shows how the grade levels relate to the requirements in this specification. This table is guidance only. Completing the parts listed for a level does not guarantee that grade. At every level, marks reward the reasoning behind your choices, not the number of features you build.

Pass to Credit

An application that works end to end, meets the security hygiene requirements, shows results clearly and runs from its README

Distinction

All of the above done well, with robust error handling, a clean API and codebase, a polished and consistent interface with interactive visualisations, and a video that explains your own code clearly, plus at least one defence from section 2.7

High Distinction

Two defences from section 2.7 done well, either two Intermediate defences or an Advanced defence with any other, each justified by your threat model, demonstrated by attacking your application, and well explained

Top of High Distinction

Advanced security work from section 2.8, measured before and after

Top of High Distinction

Advanced security work from section 2.8, measured before and after

 

Important notes
Generative AI. You must not use generative AI tools to generate the content of this assignment. You may use them for learning, generating ideas, and debugging. You are responsible for understanding, writing, and being able to explain all core logic in your application, and copying whole functions or components without understanding them counts as plagiarism. Describe all use of generative AI in your README.
Ethical testing. All security testing in this assignment is limited to your own application, running on your own machine. Never test any system you do not own, including another group's application.
Academic integrity. Acknowledge every source you use, and cite any idea or code taken from elsewhere in your README using Harvard style. Do not post any part of your work or reasoning publicly, including on Canvas discussions.
Late or changed videos. Changing the video after the due date, including replacing a YouTube upload, counts as a late submission. After Sunday, 15 November 2026, 11:59 pm, the video must not be changed at all.
Rubric
COS30049 Assignment 3 Rubric
COS30049 Assignment 3 Rubric
Criteria	Ratings	Pts
This criterion is linked to a learning outcomeVideo 1) How the parts connect
3 to >2.0 Pts
-
Follows one real request from the front end through the API and the model and back, in the actual code and in /docs. Explains what is sent and returned at each step, and where validation and errors are handled. A viewer could redraw the data flow from the video.
2 to >1.0 Pts
-
Follows a request through the actual code, but skips a step, or explains only partly what is sent and returned between the parts.
1 to >0.0 Pts
-
Describes the architecture with a diagram or slides, or names files and functions, without following a request through the code.
0 Pts
-
Not covered, or only states that the parts are connected.
3 pts
This criterion is linked to a learning outcomeVideo 2) Implementation and design decisions
3 to >2.0 Pts
-
Walks through the key parts of the code and explains, in the team's own words, what each part does and why it was written that way. Key design decisions are explained, including the alternatives considered and the reason for the choice.
2 to >1.0 Pts
-
Walks through the key code and explains what it does, but the reasons are thin, or design decisions are stated rather than justified.
1 to >0.0 Pts
-
Only says what was built, for example, 'we added validation', without explaining how it works, or reads code aloud without explaining it.
0 Pts
-
Not covered.
3 pts
This criterion is linked to a learning outcomeVideo 3) Security understanding
3 to >2.0 Pts
-
Summarises the threat model and how it shaped the team's choices, and explains how the application handles malicious input. For each attack or defence built, explains how the attack works and which part of the code stops it, and demonstrates it. A team with no defence from section 2.7 can reach this rating by explaining its threat model and how its security hygiene measures handle malicious input.
2 to >1.0 Pts
-
Covers the threat model and demonstrates the defences, but the explanation of how an attack works, or why the code stops it, is partial.
1 to >0.0 Pts
-
Mentions security features or shows a demonstration, without explaining how it works.
0 Pts
-
Security is not covered.
3 pts
This criterion is linked to a learning outcomeVideo 4) Clarity and framing
1 Pts
-
Well structured and paced, with readable screens and clear audio. Explains who the application is for and what problem it solves, and says honestly what does not work yet and what would come next.
0.5 Pts
-
Understandable, but hard to follow in places, or misses the framing or the limitations.
0 Pts
-
Hard to follow throughout.
1 pts
This criterion is linked to a learning outcomeFront end 1) Input, results and error states
3 to >2.0 Pts
-
All four of these are in place and polished. (1) Input is validated before it is sent, with clear messages beside the field. (2) The result and its confidence are the most prominent elements on screen and easy to understand. (3) Loading, success, and error states are all visible. (4) A page for addresses that do not exist and a fallback page for unexpected failures mean the user never sees a blank screen.
2 to >1.0 Pts
-
Three of the four are in place and work well, or all four are present, but some are rough, for example, unclear validation messages or a result that is hard to read.
1 to >0.0 Pts
-
Input and result work, but two or more of the input validation, visible states, and error pages are missing.
0 Pts
-
The front end does not get a result from the back end.
3 pts
This criterion is linked to a learning outcomeFront end 2) Visualisations
2 Pts
-
At least two visualisations, each answering a different question about the results, clearly titled and labelled, with interactivity that genuinely helps the user explore the results, such as filtering, zooming, or selecting an item to see its details. The marker judges whether the interactivity genuinely helps.
1.5 Pts
-
Two interactive visualisations, but the interactivity is basic, for example, tooltips only, or one chart is a weak choice for its data, or titles, labels, or legends are incomplete.
1 Pts
-
Two visualisations, but static, or both answering the same question.
0.5 Pts
-
One visualisation.
0 Pts
-
No visualisation.
2 pts
This criterion is linked to a learning outcomeFront end 3) Design, responsiveness and accessibility
5 to >4.0 Pts
-
The interface looks deliberately designed and is easy to use, with a consistent colour scheme, typography and spacing, and a clear visual hierarchy that draws the eye to the input and the result. It works as well on a phone-sized screen as on a desktop. Accessibility has clearly been considered, with a label on every input, readable contrast, and every function usable by keyboard. Meeting each requirement in section 2.1 is expected at this level but does not by itself earn it. The interface must also be polished throughout.
4 to >3.0 Pts
-
Meets the design, layout, and accessibility requirements of section 2.1 with care, but is less refined; for example, some pages are less polished than others, or there are small layout or accessibility issues on a phone.
3 to >2.0 Pts
-
Consistent and usable, but plain, or with one clear weakness, for example, a layout that breaks in places on a phone, or labels, contrast, or keyboard access neglected.
2 to >1.0 Pts
-
Usable, but with several weaknesses, for example, mostly default styling, a layout that only works on a desktop, and little attention to accessibility.
1 to >0.0 Pts
-
Cluttered or inconsistent, and hard to use on a phone or a desktop.
0 Pts
-
Unusable on any screen.
5 pts
This criterion is linked to a learning outcomeBack end 1) API design and documentation
3 to >2.0 Pts
-
All four of these are in place. (1) Request and response models are defined with Pydantic, with constraints that match the input. (2) At least two HTTP methods are used, each for a genuine purpose. (3) Status codes are correct, including for errors. (4) /docs describes every endpoint, with an example request and response.
2 to >1.0 Pts
-
Three of the four are in place; for example, errors are still returned with status 200, or /docs has no descriptions or examples.
1 to >0.0 Pts
-
The API works, but two or more are missing, for example, no Pydantic models and a second method that exists only to meet the requirement.
0 Pts
-
The API does not work.
3 pts
This criterion is linked to a learning outcomeBack end 2) Error handling
2 Pts
-
Invalid input receives a clear message with the right status code. Every error, including unexpected ones such as a failing model call, is returned in the same JSON format, without stack traces or other internal details.
1.5 Pts
-
As above, but one kind of error falls outside the shared format.
1 Pts
-
Common invalid inputs are handled, but unexpected errors fall through to a default response or a stack trace.
0.5 Pts
-
Some invalid inputs are caught, but the messages are unclear and the formats are inconsistent.
0 Pts
-
Errors crash the server or expose internal details.
2 pts
This criterion is linked to a learning outcomeBack end 3) Model integration
2 Pts
-
The model is loaded once when the server starts. Input is processed at prediction time the same way as in training, so the model receives the features it expects. Predictions are returned reliably for any valid input.
1.5 Pts
-
Works reliably, with one weakness, for example the model is reloaded on every request.
1 Pts
-
Predictions work for typical input, but processing differs from training, or some valid inputs fail.
0.5 Pts
-
Predictions work only for the few inputs shown in the video.
0 Pts
-
The model is not connected, or predictions are fixed or faked
2 pts
This criterion is linked to a learning outcomeSource code 1) Runs from the README
2 to >1.5 Pts
-
Following the README alone on a clean machine starts both the front end and the back end, with no fixes needed. Dependency versions are pinned.
1.5 to >1.0 Pts
-
Runs from the README with no fixes, but dependency versions are not pinned.
1 to >0.0 Pts
-
Runs after small fixes a marker can make in a few minutes, such as installing a missing package or correcting a path.
0 Pts
-
Cannot be run with reasonable effort.
2 pts
This criterion is linked to a learning outcomeSource code 2) Code quality and README
2 Pts
-
The code is organised into clear modules, with names and comments that explain non-obvious logic and no dead code. The README covers everything Section 3 asks for, including the architecture diagram, threat model, Harvard references, generative AI statement, and the defences to be marked.
1.5 Pts
-
Both are good, with minor gaps, for example, a few unclear functions or one README item missing.
1 Pts
-
One of the two is good, and the other is weak, for example, clean code but a README missing several required items.
0.5 Pts
-
Both are weak, for example, code that is hard to navigate, with comments that only restate it, and an incomplete README.
0 Pts
-
Disorganised code and no usable README.
2 pts
This criterion is linked to a learning outcomeSecurity 1) Hygiene requirements
2 Pts
-
All four requirements in section 2.3 are met on the back end and set sensibly. User input is never rendered as HTML, size limits suit each input, CORS lists the front end's exact origin, and no secret appears anywhere in the repository.
1.5 Pts
-
All four are met, but one is set loosely, for example, a size limit far larger than the input needs.
1 Pts
-
Three of the four are met, or one is enforced only in the front end.
0.5 Pts
-
Two or fewer are met, for example, CORS allows every origin, and a secret is committed to the repository.
0 Pts
-
None are met.
2 pts
This criterion is linked to a learning outcomeSecurity 2) Threat model
1 Pts
-
Answers the three questions specifically for this application, identifies which risks in section 2.7 the design actually exposes, and says briefly why the others do not apply.
0.5 Pts
-
Present but generic, for example, a list of attacks that could apply to any web application.
0 Pts
-
Missing.
1 pts
This criterion is linked to a learning outcomeInnovation 1) Security defences, section 2.7
7 to >5.0 Pts
-
The two defences add up to 7 or more, for example, a robust Advanced defence with a robust Intermediate one, or two robust Advanced defences.
5 to >3.0 Pts
-
For example, two robust Intermediate defences, or a robust Advanced defence with a Basic one that an obvious variation gets past.
3 to >1.0 Pts
-
For example, two robust Basic defences, or a robust Intermediate defence with a Basic one that an obvious variation gets past.
1 to >0.0 Pts
-
For example, one robust Basic defence on its own, or two Intermediate defences shown working without the attack.
0 Pts
-
No defence appears in the video, or none works.
7 pts
This criterion is linked to a learning outcomeInnovation 2) Advanced security, section 2.8
4 to >3.0 Pts
-
The attack is implemented, and its success is measured with enough repetitions to be convincing, for example, as distributions rather than single runs. The defence is implemented, and the same measurement is repeated, showing how far the attack's success falls. Results are interpreted honestly, including when an obvious defence turns out not to work, and the cost of the defence is measured or clearly explained.
3 to >2.0 Pts
-
The attack and the defence are both measured convincingly, but the interpretation of the cost is thin.
2 to >1.0 Pts
-
The attack and the defence are both measured, but the measurement is thin, for example, a few runs or no baseline.
1 to >0 Pts
-
The attack is implemented and measured convincingly, but the defence is missing, is not measured again, or does not reduce the attack's success.
4 pts
Total points: 45