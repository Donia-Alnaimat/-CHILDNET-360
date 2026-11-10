\# CHILDNET 360

\### AI-Powered Multi-Agent Intelligence for Child Online Safety and Telecommunications Policy



\*\*An evidence-grounded AI system for child digital safety, telecommunications policy analysis, privacy protection, and human-centered risk escalation.\*\*



\---



\## 1. Project Overview



CHILDNET 360 is a multi-agent AI prototype developed for the \*\*ITU AI for Good Lab Hackathon\*\*.



The project explores how artificial intelligence, telecommunications policy, and child protection principles can work together to support safer digital environments for children.



Instead of relying on a single chatbot, CHILDNET 360 combines four specialized agents with semantic retrieval from a policy knowledge base.



The system demonstrates how a child's initial request for help can evolve into a higher-risk situation requiring coordinated assessment, privacy safeguards, and authorized human intervention.



\*\*Core principle: Protect the child without unnecessarily exposing the child's sensitive information.\*\*



\## 2. The Problem



Children experiencing online threats may struggle to explain what happened or provide complete information.



At the same time, organizations handling these situations must balance several responsibilities:



\- Recognizing and escalating child safety risks.

\- Understanding telecommunications responsibilities.

\- Protecting sensitive personal information.

\- Applying relevant legal and policy guidance.

\- Maintaining transparency and human oversight.



CHILDNET 360 explores these challenges through a coordinated AI-assisted workflow.



\## 3. Our Solution



The prototype combines:



\*\*Four specialized AI agents\*\*



Each agent addresses a different aspect of the situation.



\*\*Evidence-grounded policy intelligence\*\*



The system retrieves relevant passages from a structured knowledge base before generating policy analysis.



\*\*Progressive risk scenarios\*\*



The demonstration shows how decisions change as new information becomes available.



\*\*Human-centered safeguards\*\*



Sensitive requests and higher-risk situations are flagged for authorized human review.



\*\*Explainable outputs\*\*



The system returns decisions, agent results, retrieved evidence, and source information.



\## 4. Multi-Agent Architecture



\### Child Safety Agent



Evaluates child safety signals and contributes to risk escalation decisions.



\### Telecom Safety Agent



Examines telecommunications-related aspects of the simulated incident.



\### Privacy Agent



Supports privacy-aware handling of sensitive information and access requests.



\### Policy Agent



Retrieves and analyzes relevant regulatory and policy evidence.



\### Coordinator



The coordinator orchestrates the agents according to the scenario stage and produces a structured decision.



Not every agent is invoked at every stage. Agent participation depends on the event being processed.



\## 5. AI and Knowledge Base



CHILDNET 360 uses the following technologies:



| Component | Technology |

|---|---|

| Programming language | Python |

| API framework | FastAPI |

| Embedding model | `intfloat/multilingual-e5-small` |

| Full embedding backend | PyTorch and SentenceTransformers |

| Optimized embedding backend | ONNX Runtime INT8 |

| Vector search | FAISS |

| Generative policy analysis | Gemini API |

| Frontend | HTML, CSS, JavaScript |

| Data exchange | JSON |



\### Knowledge Base



The indexed knowledge base contains \*\*2,080 text chunks\*\*.



It supports semantic retrieval of relevant policy passages and includes metadata such as:



\- Document name

\- Page number

\- Jurisdiction

\- Authority

\- Document type

\- Source URL, where available

\- Article or section, where available



The retrieval system supports jurisdiction-aware filtering for UAE federal, Dubai, and international reference materials.



\### Retrieval-Augmented Generation



The policy assistant follows this workflow:



\*\*User Question → E5 Embeddings → FAISS Retrieval → Policy Evidence → Gemini Analysis → Source-Referenced Response\*\*



Gemini is instructed to distinguish binding legal materials from international guidance and identify uncertainty where evidence is insufficient.



AI-generated legal interpretations require independent human verification.



\## 6. Progressive Child Safety Scenario



The demonstration contains four stages.



| Stage | Scenario | System Response |

|---|---|---|

| 1 | A child requests help | `RECEIVED` |

| 2 | The child reports a threat involving an image | `ESCALATED` |

| 3 | An external party requests the original image | `DATA\_REQUEST\_UNDER\_REVIEW` |

| 4 | Unauthorized access to case information is attempted | `ACCESS\_DENIED\_PENDING\_REVIEW` |



The workflow demonstrates that:



\- An initial request can be accepted without a complete account of the incident.

\- New information can trigger escalation.

\- Original sensitive images are not automatically collected.

\- Unauthorized access does not result in disclosure.

\- Higher-risk events require human review.



\*\*These scenarios are simulations, not live child protection operations.\*\*



\## 7. Installation



\### Step 1 — Clone the repository



Clone the repository using GitHub, then open a terminal in the project directory.



\### Step 2 — Create a Python environment



A dedicated Python environment is recommended.



\### Step 3 — Install dependencies



```bash

python -m pip install -r requirements.txt

```



The full embedding backend uses PyTorch and SentenceTransformers.



The original multilingual E5 model may need to be downloaded during its first initialization. An internet connection may therefore be required.



\### Step 4 — Configure Gemini



Set the environment variable:



`GEMINI\_API\_KEY`



On Windows Command Prompt:



```bat

set "GEMINI\_API\_KEY=YOUR\_API\_KEY"

```



On macOS or Linux:



```bash

export GEMINI\_API\_KEY="YOUR\_API\_KEY"

```



Replace `YOUR\_API\_KEY` with your own credential.



\*\*Never commit API keys or other secrets to GitHub.\*\*



\### Step 5 — Start the API



From the project root:



```bash

python -m uvicorn evaluation.api:app --host 127.0.0.1 --port 8000

```



Open the application locally at:



`http://127.0.0.1:8000/`



Interactive API documentation:



`http://127.0.0.1:8000/docs`



\## 8. Embedding Backends



\### Full E5 Backend



The default backend uses the original multilingual E5 model through SentenceTransformers.



To select it explicitly on Windows:



```bat

set "CHILDNET\_EMBEDDING\_BACKEND=full"

```



\### ONNX INT8 Backend



An optimized ONNX INT8 version is also included as two repository parts.



On Windows Command Prompt, reconstruct the model:



```bat

copy /b e5\_onnx\\model\_int8.onnx.part01+e5\_onnx\\model\_int8.onnx.part02 e5\_onnx\\model\_int8.onnx

```



Then select the ONNX backend:



```bat

set "CHILDNET\_EMBEDDING\_BACKEND=onnx"

```



Both backends use the FAISS vector index.



The default full backend does not require reconstructing the ONNX file.



\## 9. API Endpoints



| Endpoint | Method | Purpose |

|---|---|---|

| `/health` | GET | Service health check |

| `/progressive-scenario` | GET | Run the four-stage simulation |

| `/policy-intelligence` | GET | Retrieve jurisdiction-specific policy evidence |

| `/agent-chat` | POST | Generate evidence-grounded policy analysis |

| `/api/help` | POST | Process a simulated child help request |

| `/docs` | GET | Interactive API documentation |



\### Example: Policy Assistant



Request:



```json

{

&#x20; "message": "What obligations do UAE internet service providers have regarding child online safety?",

&#x20; "top\_k": 3

}

```



Send the request to:



`POST /agent-chat`



The response includes an answer, retrieved sources, and the response mode.



Possible modes include:



\- `GEMINI\_RAG`: Gemini generated an answer using retrieved evidence.

\- `EVIDENCE\_ONLY`: Gemini was unavailable, and the API returned the available policy evidence without generating a legal analysis.

\- `NO\_EVIDENCE`: No relevant evidence was retrieved.



\## 10. Transparency and Human Oversight



CHILDNET 360 is designed as a research and demonstration prototype.



Its current workflow includes:



\- Source-referenced policy retrieval.

\- Structured agent outputs.

\- Human-review indicators.

\- Simulated access restrictions.

\- Scenario history.

\- Audit-log generation in the demonstration workflow.



The system does not autonomously contact emergency services, investigate real individuals, enforce regulations, or authorize access to sensitive child information.



Policy gap observations are exploratory and should not be treated as confirmed legal deficiencies.



\## 11. Limitations



The current prototype has important limitations:



1\. The progressive scenarios are predefined demonstrations.

2\. Retrieved passages require verification against their original documents.

3\. Similarity scores measure semantic relevance, not legal correctness.

4\. Gemini responses may contain errors despite evidence-grounding instructions.

5\. API availability depends partly on external services.

6\. Human-review flags do not constitute a live case-management or emergency-response system.



Further work would include expert evaluation, expanded policy coverage, stronger access controls, automated citation validation, and systematic testing across diverse scenarios.



\## 12. Project Structure



```text

CHILDNET\_360/

|

|-- agents/

|   |-- child\_safety\_agent.py

|   |-- telecom\_agent.py

|   |-- privacy\_agent.py

|   |-- policy\_agent.py

|

|-- knowledge\_base/

|   |-- kb\_engine.py

|   |-- knowledge\_base.py

|   |-- processed/

|       |-- childnet\_faiss.index

|       |-- knowledge\_chunks.json

|       |-- document\_metadata.json

|

|-- e5\_onnx/

|   |-- model\_int8.onnx.part01

|   |-- model\_int8.onnx.part02

|   |-- tokenizer.json

|

|-- evaluation/

|   |-- api.py

|   |-- demo\_system.py

|   |-- main.py

|

|-- simulation/

|-- vector\_store/

|-- web/

|   |-- index.html

|   |-- style.css

|   |-- app.js

|

|-- requirements.txt

|-- README.md

```



\## 13. Vision



\*\*A safer digital world begins when a child's request for help is heard, understood, and handled responsibly.\*\*



CHILDNET 360 explores how AI agents, telecommunications policy intelligence, and privacy-conscious decision support can contribute to that goal.



\---



\*\*CHILDNET 360 | ITU AI for Good Lab Hackathon | 2026\*\*



\*Research prototype — Not a substitute for professional child protection, legal, or emergency services.\*

