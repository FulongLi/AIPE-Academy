# AI Tutor Prompts

These prompts are designed for learners using Codex, Claude, ChatGPT, or another AI assistant as a study partner.

They work best when the learner gives the AI:

- the repository link or local folder
- the current stage
- the topic file
- their background level
- what they tried already

## Start a Stage

```text
You are my power electronics tutor. I am studying Stage [number/name] in Spirit Connect Academy.

My current background is: [describe honestly].

Please first explain the big picture of this stage, then give me a 7-day study plan. Use simple language, but do not hide the engineering truth. Ask me questions before assuming I understand.
```

## Explain a Topic

```text
Explain [topic] to me as a beginner in power electronics.

Use this order:
1. intuition
2. real-world purpose
3. minimum math
4. example
5. common mistakes
6. one self-check question

If I misunderstand something, correct me directly and kindly.
```

## Turn Theory Into Simulation

```text
Help me turn [topic/converter] into a simulation.

Use [LTspice/ngspice/Python/MATLAB-style code].

Give me:
1. the model or circuit
2. parameter values
3. what to plot
4. what waveform shape I should expect
5. three experiments where I change one parameter at a time
```

## Check My Understanding

```text
Interview me about [topic].

Ask one question at a time. Start easy, then increase the difficulty. Do not give me the answer immediately. If my answer is vague, ask a follow-up. At the end, summarize what I understand and what I should review.
```

## Debug a Calculation

```text
Here is my calculation for [topic]:

[paste calculation]

Please check units, assumptions, equations, and engineering reasonableness. Explain every correction clearly.
```

## Review a Design

```text
Review my power electronics design idea as a cautious engineering mentor.

Application:
Input:
Output:
Power:
Switching frequency:
Topology:
Components:
Control method:
Protection:
Layout notes:

Please identify risks in safety, device stress, thermal design, control stability, EMI, layout, and testing.
```

## Build a Learning Note

```text
Turn my messy notes into a clear learning note for Spirit Connect Academy.

Use this structure:
1. concept
2. intuition
3. key equations
4. example
5. simulation idea
6. common mistakes
7. questions I still have

Keep the wording original and beginner-friendly.
```

