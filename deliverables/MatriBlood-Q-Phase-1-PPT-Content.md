# MatriBlood Q - Phase 1 PPT Content

Presentation limit: 3 minutes  
Recommended slide count: 6 slides  
Tone: clear, specific, technical enough for judges, but not overloaded

---

## Slide 1 - Title

### Title
MatriBlood Q

### Subtitle
Voice-first quantum optimization for obstetric emergency blood procurement

### On-slide bullets
- For maternity emergencies where every minute matters
- Converts spoken clinical requests into procurement plans
- Uses Qiskit to optimize source, product, and courier choices

### Speaker notes
MatriBlood Q is a voice-first procurement copilot for maternity emergencies such as postpartum hemorrhage. The goal is not to diagnose or prescribe treatment. The goal is to help a clinician quickly assemble the blood products and emergency medicines they have already requested, across tied-up blood banks and pharmacies.

### Timing
20 seconds

---

## Slide 2 - Problem Statement

### Title
The problem is not only blood availability; it is emergency procurement orchestration.

### On-slide bullets
- Maternity emergencies need a complete kit, not partial stock visibility
- A single nearby blood bank may not have all requested products
- Platelets and blood components can expire, creating shortage and wastage at the same time
- During emergencies, teams still rely on calls, manual checks, and nearest-source decisions

### Key example
Postpartum hemorrhage case:
- Need 2 O-negative PRBC
- Need 2 FFP
- Need 1 platelet unit
- Need tranexamic acid and oxytocin
- Target: within 30 minutes

### Speaker notes
In an emergency, seeing that some stock exists is not enough. The clinician needs the complete kit to arrive quickly. The nearest source may only have part of the request. Another source may have platelets expiring soon. A pharmacy may have the required medicine. So the real problem is deciding the best combination of sources and couriers under time, inventory, compatibility, and expiry constraints.

### Timing
35 seconds

---

## Slide 3 - Proposed Approach

### Title
MatriBlood Q turns a spoken emergency request into an optimized procurement action plan.

### On-slide flow
1. Voice request  
   Clinician speaks into Elato ESP32 device

2. Transcript  
   Elato Deno WebSocket server stores transcript in Supabase

3. Structured parsing  
   TokenRouter extracts requested products, blood group, units, urgency, and target time

4. Quantum optimization  
   Python + Qiskit chooses the best source-product-courier combination

5. Action plan  
   Dashboard and voice response return a prioritized procurement plan

### Example input
"Postpartum hemorrhage emergency. Patient unstable. Need 2 O-negative PRBC, 2 FFP, 1 platelet, TXA, and oxytocin within 30 minutes."

### Example output
"Request 1 PRBC and 2 FFP from Blood Bank A, 1 PRBC and 1 platelet from Blood Bank B, and oxytocin from Pharmacy D. Complete kit ETA: 24 minutes."

### Speaker notes
The workflow starts from voice because clinicians may not have time to type during an emergency. The LLM is only used to structure the request. The actual procurement decision is made by the Qiskit optimization model. This keeps the system safer and more explainable.

### Timing
40 seconds

---

## Slide 4 - How Quantum Computing Is Involved

### Title
The quantum component is the decision engine, not a decoration.

### On-slide bullets
We model procurement as a constrained binary optimization problem.

Decision variables:
- take_PRBC_from_bank_A = 0 or 1
- take_platelet_from_bank_B = 0 or 1
- take_oxytocin_from_pharmacy_D = 0 or 1
- send_courier_2_to_bank_B = 0 or 1

Objective:
- Minimize complete-kit arrival time
- Minimize missing critical items
- Minimize incompatible or impossible allocations
- Reduce avoidable expiry waste

Constraints:
- Do not exceed available stock
- Respect simplified blood compatibility rules
- Respect expiry windows
- Respect courier capacity
- Meet the emergency time target where possible

### Safe quantum claim
We formulate the problem as a QUBO/Ising-style optimization model and solve it with a Qiskit hybrid quantum-classical workflow.

### Do not claim
We are not claiming quantum speedup.

### Speaker notes
Quantum computing fits because this is a combinatorial optimization problem. There are many possible combinations of blood banks, products, pharmacies, and couriers. Qiskit lets us encode those choices as binary variables and search for the best plan under constraints. For the demo, we can compare the Qiskit result against a greedy nearest-source baseline.

### Timing
45 seconds

---

## Slide 5 - Tech Stack and Hardware Components

### Title
The stack is feasible for Phase 2 because every layer has a clear job.

### On-slide table

| Layer | Tool | Role |
|---|---|---|
| Voice hardware | Elato ESP32 | Captures spoken emergency request |
| Firmware setup | PlatformIO | Flashes and configures device |
| Voice transport | Elato Deno WebSocket server | Moves audio/transcript between device and backend |
| Database | Remote Supabase | Stores transcripts, cases, inventory, optimization runs, actions |
| LLM parsing | TokenRouter | Converts messy transcript into structured JSON |
| Optimization | Python + Qiskit | Solves procurement allocation problem |
| Dashboard | Next.js + TypeScript | Shows inventory, case, baseline, optimized plan |
| Optional TTS | ElevenLabs / Elato response path | Speaks the final action plan |

### Speaker notes
The architecture is intentionally modular. Elato handles the hardware voice loop. Supabase is the shared state layer. TokenRouter structures the text. Python and Qiskit make the procurement decision. Next.js gives judges and operators a clear dashboard. If any live service fails during the demo, we can use fallback transcript, fallback parsed JSON, and a classical solver fallback.

### Timing
35 seconds

---

## Slide 6 - USP and Phase 2 Feasibility

### Title
USP: a narrow, real, quantum-centered workflow that can actually be built.

### On-slide USP bullets
- Specific problem: obstetric emergency kit procurement, not generic hospital optimization
- Hardware-first: real Elato voice device, not just a web form
- Quantum-centered: Qiskit owns the allocation decision
- Science-grounded: constraints can be curated from PubMed/OpenFDA-style sources
- Demoable: compares greedy baseline vs optimized complete-kit plan

### Phase 2 build plan
0-2 hours:
- Seed demo inventory and emergency case
- Build basic dashboard

2-4 hours:
- Add transcript parser and greedy baseline

4-7 hours:
- Implement Qiskit optimizer and comparison result

7-9 hours:
- Connect Elato voice transcript path

9-10 hours:
- Polish dashboard, add fallbacks, prepare final demo

### Final pitch line
MatriBlood Q helps maternity teams assemble the right emergency kit faster by turning voice into a quantum-optimized procurement plan.

### Speaker notes
The strongest part of this idea is focus. We are not trying to build a full hospital platform. We are solving one urgent procurement decision end-to-end. The Phase 2 demo can show a greedy nearest-source strategy failing to assemble the full kit, while Qiskit combines multiple sources and couriers to complete it within the target time.

### Timing
35 seconds

---

# 3-Minute Speaking Script

Hi, our project is called MatriBlood Q. It is a voice-first quantum optimization system for obstetric emergency blood procurement.

The problem we are solving is very specific. In maternity emergencies like postpartum hemorrhage, clinicians often need a complete emergency kit quickly: PRBC, FFP, platelets, and medicines like tranexamic acid or oxytocin. Existing systems may show blood stock availability, but they do not automatically decide the fastest feasible procurement plan across tied-up blood banks, pharmacies, couriers, expiry windows, and compatibility constraints.

Our approach starts with voice. A clinician speaks into an Elato ESP32 device: "Postpartum hemorrhage emergency, unstable patient, need 2 O-negative PRBC, 2 FFP, 1 platelet, TXA, and oxytocin within 30 minutes." The transcript is stored in Supabase. TokenRouter converts the messy transcript into structured JSON. Then Python and Qiskit solve the procurement allocation problem. The dashboard shows the action plan, and the device can speak back the result.

The quantum component is central. We model procurement choices as binary variables: take PRBC from Bank A or not, take platelets from Bank B or not, send courier 2 to Bank B or not. The objective is to minimize complete-kit arrival time, missing critical items, impossible allocations, and expiry waste. The constraints include available stock, simplified compatibility, expiry windows, courier capacity, and target time.

We are not claiming quantum speedup. Our safe claim is that this is a QUBO or Ising-style constrained optimization problem solved through a Qiskit hybrid quantum-classical workflow. The demo will compare this against a greedy nearest-source baseline.

The tech stack is feasible. We use Elato ESP32 with PlatformIO for hardware, the Elato Deno WebSocket server for voice transport, remote Supabase for shared data, TokenRouter for parsing, Python FastAPI with Qiskit for optimization, and a Next.js TypeScript dashboard.

The unique point is that this is not generic hospital optimization. It is a narrow, high-stakes workflow: complete obstetric emergency kit procurement from voice. In Phase 2, we can build a demo where the nearest blood bank gives only a partial kit, but Qiskit combines multiple sources to deliver the full kit within the target time.

MatriBlood Q helps maternity teams assemble the right emergency kit faster by turning voice into a quantum-optimized procurement plan.

---

# Optional Backup Slide Content

Use this only if you want a 7th slide.

## Slide 7 - Demo Scenario

### Title
Demo scenario: nearest-source fails, Qiskit completes the kit.

### Baseline
Blood Bank A is 8 minutes away:
- 1 O-negative PRBC
- 2 FFP
- No platelets
- No oxytocin

Result:
- Fast but incomplete
- Missing platelet and medicine

### Optimized plan
Qiskit combines:
- Blood Bank A: 1 PRBC + 2 FFP
- Blood Bank B: 1 PRBC + 1 platelet
- Pharmacy D: oxytocin

Result:
- Complete kit ETA: around 24 minutes
- Missing critical items: 0

### Speaker note
This is the clearest demo moment. It shows why optimization matters. The nearest source is not enough. The optimizer has to choose the best combination across multiple sources.

