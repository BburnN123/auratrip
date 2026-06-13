# Architecture Overview

This document serves as a critical, living template designed to equip agents with a rapid and comprehensive understanding of the Auratrip codebase's architecture, enabling efficient navigation and effective contribution from day one. Update this document as the codebase evolves.

## 1. Project Structure

This section provides a high-level overview of the project's directory and file structure, categorised by architectural layer or major functional area.

```
[Project Root]/
├── backend/                    # Server-side code, APIs, and agent swarm
│   ├── src/
│   │   ├── api/                # FastAPI endpoints and controllers
│   │   ├── agents/             # Kimi K2.6 agent swarm implementations
│   │   │   ├── scout_agent.py      # Bright Data scraping orchestration
│   │   │   ├── weather_agent.py    # Weather extraction & validation
│   │   │   ├── planner_agent.py    # Itinerary generation & optimization
│   │   │   └── visual_agent.py     # SenseNova U1 image/PPT generation
│   │   ├── client/             # Business logic and service implementations
│   │   │   ├── brightdata_client.py
│   │   │   ├── daytona_client.py
│   │   │   ├── nosana_client.py
│   │   │   ├── sensenova_client.py
│   │   │   ├── terminal3_client.py
│   │   │   ├── tokenrouter_client.py
│   │   │   └── videodb_client.py
│   │   ├── models/             # Database models/schemas
│   │   │   ├── trip.py
│   │   │   ├── itinerary.py
│   │   │   ├── scraped_post.py
│   │   │   └── user.py
│   │   ├── services/           # Core business services
│   │   │   ├── scraping_service.py
│   │   │   ├── weather_service.py
│   │   │   ├── planning_service.py
│   │   │   └── generation_service.py
│   │   └── utils/              # Backend utility functions
│   ├── config/                 # Backend configuration files
│   │   ├── settings.py
│   │   └── agent_config.yaml
│   ├── tests/                  # Backend unit and integration tests
│   └── Dockerfile              # Backend deployment container
├── frontend/                   # Client-side code for the trip planner UI
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── ItineraryCard.tsx
│   │   │   ├── WeatherWidget.tsx
│   │   │   ├── ScrapedPostFeed.tsx
│   │   │   └── MapView.tsx
│   │   ├── pages/              # Application pages/views
│   │   │   ├── Home.tsx
│   │   │   ├── TripPlanner.tsx
│   │   │   └── ItineraryView.tsx
│   │   ├── assets/             # Images, fonts, static assets
│   │   ├── services/           # Frontend API interaction layer
│   │   │   └── api.ts
│   │   └── store/              # State management (Zustand)
│   ├── public/                 # Publicly accessible assets
│   ├── tests/                  # Frontend unit and E2E tests
│   └── package.json
├── common/                     # Shared code, types, utilities
│   ├── types/                  # Shared TypeScript/interface definitions
│   │   ├── trip.ts
│   │   ├── itinerary.ts
│   │   ├── agent.ts
│   │   └── api.ts
│   └── utils/                  # General utility functions
│       ├── validators.ts
│       └── formatters.ts
├── docs/                       # Project documentation
│   ├── API.md
│   ├── SETUP.md
│   └── HACKATHON.md
├── scripts/                    # Automation scripts
│   ├── deploy.sh
│   ├── seed_data.py
│   └── scrape_bootstrap.py
├── .github/                    # GitHub Actions CI/CD
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── .gitignore
├── README.md
└── ARCHITECTURE.md             # This document
```

## 2. High-Level System Diagram

The following diagram illustrates the major components and data flow of the Auratrip system:

```
[User] <--> [Frontend Application] <--> [TokenRouter API Gateway]
                                              |
                    +---------------------------+---------------------------+
                    |                           |                           |
                    ▼                           ▼                           ▼
            [Kimi K2.6 Agent Swarm]    [Daytona Sandboxes]      [VideoDB]
                    |                           |                           |
        +-----------+-----------+       [Bright Data] <--> [Scraped Content]
        |           |           |             |                           |
        ▼           ▼           ▼             ▼                           ▼
   [Scout]    [Weather]   [Planner]  [Nosana GPU Cluster]      [Indexed Videos]
   Agent      Agent       Agent              |                           |
        |           |           |             ▼                           ▼
        +-----------+-----------+      [SenseNova U1] <------------[Searchable Context]
                    |                  (Image Gen / PPT)
                    ▼
            [Terminal 3 TEE]
            (Identity / Attestation)
                    |
                    ▼
            [PostgreSQL + Redis]
```

**Data Flow Summary:**
1. User submits a destination (e.g., "Bangkok") via the Frontend.
2. Request routes through TokenRouter to the optimal AI model.
3. Kimi K2.6 Orchestrator spawns specialized agents in Daytona sandboxes.
4. Scout Agent triggers Bright Data to scrape Instagram/TikTok in real-time.
5. Raw scraped content (videos, images, captions) is ingested into VideoDB for indexing and clip extraction.
6. Weather Agent parses posts for weather signals, validated by external APIs.
7. Nosana GPUs analyze scraped images for visual weather cues (crowd levels, sky conditions).
8. Planner Agent synthesizes all data into a dynamic, hour-by-hour itinerary.
9. Visual Agent invokes SenseNova U1 to generate itinerary visuals and PowerPoint exports.
10. Terminal 3 TEE cryptographically attests the itinerary's authenticity.
11. Final response is cached by TokenRouter and returned to the user.

## 3. Core Components

### 3.1. Frontend

**Name:** Auratrip Web Application

**Description:** The primary user interface for the Auratrip trip planner. Users input destinations and travel dates, view real-time generated itineraries, browse scraped social media evidence supporting recommendations, download generated PowerPoint itineraries, and interact with a chat-based agent interface for iterative trip refinement.

**Technologies:** React 18, TypeScript, Tailwind CSS, Mapbox GL JS, Zustand (state management)

**Deployment:** Vercel (frontend static hosting)

### 3.2. Backend Services

#### 3.2.1. API Gateway & Orchestration Service

**Name:** TokenRouter Gateway

**Description:** The unified entry point for all client requests. Implements intelligent model routing, smart caching, and fallback logic. Determines whether a request requires Kimi K2.6 (complex reasoning), SenseNova U1 (multimodal generation), or cached responses. Manages rate limiting and request aggregation.

**Technologies:** Python (FastAPI), TokenRouter SDK, Redis (cache layer)

**Deployment:** Daytona sandbox (containerized), exposed via HTTPS

#### 3.2.2. Agent Swarm Service

**Name:** Kimi K2.6 Agent Swarm

**Description:** The core intelligence layer. A coordinator agent dispatches tasks to four specialized sub-agents (Scout, Weather, Planner, Visual) that collaborate within a shared context window using Kimi's native agent swarm execution. Agents communicate via structured JSON tool calls and persist state in Daytona volumes.

**Technologies:** Python, Kimi K2.6 API (with context caching), Pydantic (schema validation)

**Deployment:** Daytona sandboxes (isolated, stateful containers per user session)

#### 3.2.3. Scraping Service

**Name:** Bright Data Scraping Engine

**Description:** Handles all web scraping operations. Encapsulates Bright Data's Scraping Browser API into reusable "skills" for Instagram and TikTok. Manages proxy rotation, rate limiting, anti-detection measures, and data extraction pipelines. Runs inside Daytona sandboxes for isolation.

**Technologies:** Python, Bright Data SDK, Playwright, BeautifulSoup

**Deployment:** Daytona sandbox (isolated scraper containers)

#### 3.2.4. Video Infrastructure Service

**Name:** VideoDB Integration Layer

**Description:** Manages ingestion, transcription, indexing, and retrieval of scraped video content. Converts Instagram Reels and TikTok videos into searchable context. Enables agents to query video content (e.g., "find clips of Grand Palace from today") and triggers real-time alerts when new relevant content is posted.

**Technologies:** Python, VideoDB SDK, FFmpeg (transcoding)

**Deployment:** VideoDB cloud (managed), with client integration in Daytona sandboxes

#### 3.2.5. GPU Compute Service

**Name:** Nosana GPU Compute Orchestrator

**Description:** Submits heavy AI workloads to Nosana's decentralized GPU cluster. Primary tasks include vision analysis of scraped images (weather detection, crowd estimation, text recognition on signs/menus) and hosting custom local models for batch inference when external APIs are rate-limited.

**Technologies:** Python, Nosana CLI, Docker, PyTorch, Transformers

**Deployment:** Nosana decentralized network (job submission from Daytona sandboxes)

#### 3.2.6. Multimodal Generation Service

**Name:** SenseNova U1 Integration Service

**Description:** Handles all multimodal content generation. Invokes SenseNova U1 for high-fidelity image generation (itinerary cards, mood boards) and leverages SenseNova U1 Skills for automated PowerPoint creation and Excel budget analysis. Provides an abstraction layer so the Planner Agent can request assets without managing model details.

**Technologies:** Python, SenseNova U1 API, SenseNova Skills SDK

**Deployment:** Daytona sandbox (generation worker containers)

#### 3.2.7. Identity & Security Service

**Name:** Terminal 3 Agent Identity Service

**Description:** Equips all Auratrip agents with verifiable decentralized identities (DIDs). Manages TEE-secured secret storage (API keys, OAuth tokens). Cryptographically attests itinerary outputs to prove they were generated by authenticated agents and not tampered with. Enables secure autonomous transactions (e.g., booking reservations) on behalf of users.

**Technologies:** Python, Terminal 3 ADK SDK, TEE attestation libraries

**Deployment:** Terminal 3 Network (TEE-secured hardware nodes)

## 4. Data Stores

### 4.1. Primary Application Database

**Name:** Auratrip Main Database

**Type:** PostgreSQL 15

**Status:** Not yet implemented in the current codebase. The minimal API uses in-memory placeholders, so no Postgres instance is required for the MVP.

**Purpose:** Stores user accounts, trip metadata, generated itineraries, agent execution logs, and scraped post references. Serves as the system of record for all persistent application data.

**Key Schemas/Collections:**
- `users` — User profiles, preferences, auth credentials
- `trips` — Trip requests (destination, dates, status)
- `itineraries` — Generated day-by-day plans with activity details
- `scraped_posts` — Metadata and content references for social media posts
- `agent_runs` — Execution logs from the agent swarm
- `weather_snapshots` — Extracted weather data with confidence scores

### 4.2. Cache & Session Store

**Name:** Redis Cluster

**Type:** Redis 7 (with persistence)

**Status:** Not yet implemented in the current codebase.

**Purpose:** Caches frequently accessed itineraries, TokenRouter smart-cache entries, user session states, and real-time agent coordination locks. Enables sub-second response times for repeat queries.

**Key Data Structures:**
- Itinerary cache (TTL: 1 hour for live data)
- TokenRouter model routing decisions
- Agent swarm shared context snapshots
- Rate-limiting counters for external APIs

### 4.3. Video Data Infrastructure

**Name:** VideoDB

**Type:** Managed video data infrastructure (VideoDB cloud)

**Purpose:** Stores raw scraped video content, extracted frames, audio transcriptions, and vector embeddings for semantic video search. Acts as the video-specific data layer for the agent swarm.

**Key Collections:**
- `raw_streams` — Original Instagram/TikTok video files
- `clips` — Extracted scene segments with metadata
- `transcriptions` — Audio-to-text outputs
- `embeddings` — Vector representations for semantic search

## 5. External Integrations / APIs

### 5.1. Bright Data

**Purpose:** Large-scale, reliable web scraping from Instagram and TikTok. Provides real-time social media data including posts, captions, geotags, images, and videos.

**Integration Method:** Bright Data Scraping Browser API (REST + Python SDK)

**Key Features Used:**
- Proxy rotation and anti-detection
- Custom scraping "skills" for Instagram/TikTok
- Rate-limited, compliant data extraction

### 5.2. Kimi AI (K2.6 API)

**Purpose:** Core reasoning engine for the agent swarm. Handles complex itinerary planning, natural language understanding of scraped content, code execution, and native agent swarm orchestration.

**Integration Method:** REST API (OpenAI-compatible) with official Python SDK

**Key Features Used:**
- Kimi K2.6 model for reasoning and planning
- Context caching for multi-turn agent conversations
- Native agent swarm execution
- Function/tool calling for agent inter-communication

### 5.3. Daytona

**Purpose:** Provides fast, isolated, stateful sandboxes for running scrapers, AI agents, and code execution safely. Each user trip gets an isolated compute environment.

**Integration Method:** Daytona SDK (Python/TypeScript)

**Key Features Used:**
- On-demand sandbox creation per user session
- Stateful volume persistence across requests
- Secure code execution isolation
- Pre-configured environments with all stack dependencies

### 5.4. Nosana

**Purpose:** Decentralized GPU compute for vision analysis, image generation, and hosting custom local AI models affordably.

**Integration Method:** Nosana CLI + Docker container submission

**Key Features Used:**
- GPU job submission for batch image analysis
- Custom model hosting (vision transformers)
- Cost-effective compute for hackathon-scale workloads

### 5.5. SenseNova U1

**Purpose:** End-to-end multimodal AI for generating itinerary visuals, mood boards, PowerPoint presentations, and Excel budget analyses.

**Integration Method:** REST API (SenseNova U1) + Skills SDK

**Key Features Used:**
- Text-to-image generation (itinerary cards, destination visuals)
- SenseNova U1 Skills: PowerPoint automation
- SenseNova U1 Skills: Excel analysis and budget breakdowns

### 5.6. Terminal 3 (Agent Dev Kit)

**Purpose:** Verifiable agent identity, TEE-secured secret management, and cryptographic attestation of generated outputs.

**Integration Method:** Terminal 3 ADK SDK (Python)

**Key Features Used:**
- Decentralized Identifiers (DIDs) for each agent
- TEE-secured storage of API keys and user OAuth tokens
- Cryptographic signing of itinerary outputs
- Hardware-secured autonomous transaction execution

### 5.7. TokenRouter

**Purpose:** Unified AI model routing platform. Routes requests to the optimal model based on task complexity, cost, and latency requirements.

**Integration Method:** TokenRouter SDK (Python)

**Key Features Used:**
- Smart caching to reduce redundant API calls
- Intelligent model selection (Kimi K2.6 vs. SenseNova U1 vs. fallback)
- Performance optimization (faster, cheaper, better routing)

### 5.8. VideoDB

**Purpose:** Data infrastructure for video content. Turns scraped camera feeds, social videos, and recordings into searchable context for agents.

**Integration Method:** VideoDB API (REST + Python SDK)

**Key Features Used:**
- Video ingestion and indexing
- Semantic search across video content
- Real-time alerts on new content matching criteria
- Clip extraction and frame analysis workflows

### 5.9. Weather Validation APIs

**Status:** Not yet implemented in the current codebase.

**Purpose:** Cross-reference weather signals extracted from social media with official meteorological data to validate accuracy.

**Integration Method:** REST API (OpenWeatherMap / WeatherAPI)

## 6. Deployment & Infrastructure

**Cloud Provider:** Cloud-agnostic, primarily leveraging Daytona-managed infrastructure and managed services (VideoDB, Terminal 3 Network, Nosana Network)

**Key Services Used:**
- **Daytona:** Primary compute platform for all backend services and agent sandboxes
- **Vercel:** Frontend static site hosting and serverless functions
- **PostgreSQL:** Managed database (can be Neon, Supabase, or RDS)
- **Redis:** Managed cache (Upstash or Redis Cloud)
- **VideoDB:** Managed video data infrastructure
- **Nosana:** Decentralized GPU compute network
- **Terminal 3 Network:** TEE-secured hardware nodes for identity and security

**CI/CD Pipeline:** GitHub Actions
- **CI:** Linting (ESLint, Ruff), type checking, unit tests (Pytest, Jest)
- **CD:** Automated deployment to Daytona sandboxes, Vercel frontend deployment

**Monitoring & Logging:**
- **Backend:** Structured logging (Python `structlog`), Daytona sandbox logs
- **Agents:** Agent execution tracing via Kimi API dashboard
- **External APIs:** TokenRouter usage analytics, Bright Data scraping metrics
- **Alerting:** Custom health checks for agent swarm and scraping pipelines

## 7. Security Considerations

**Authentication:**
- User authentication via JWT (JSON Web Tokens) with short expiry
- Refresh token rotation for session management
- Optional OAuth2 integration (Google, Apple) for streamlined signup

**Authorization:**
- Role-Based Access Control (RBAC): `user`, `admin`, `agent`
- Agents authenticated via Terminal 3 DIDs with capability-based permissions
- API endpoints protected by scope-based access controls

**Data Encryption:**
- **In Transit:** TLS 1.3 for all API communications
- **At Rest:** AES-256 encryption for PostgreSQL volumes (managed by provider)
- **Secrets:** All API keys (Bright Data, Kimi, etc.) stored in Terminal 3 TEE — never exposed to application code in plaintext

**Key Security Tools/Practices:**
- **Terminal 3 TEE:** Hardware-secured execution for secret management and agent attestation
- **Daytona Isolation:** Each user session runs in an isolated sandbox preventing cross-contamination
- **Input Sanitization:** Strict validation of user inputs (destinations, dates) before scraping
- **Rate Limiting:** Per-user and per-IP rate limits on scraping and generation endpoints
- **Data Compliance:** Scraping respects robots.txt and platform Terms of Service; no PII storage from social media

## 8. Development & Testing Environment

**Local Setup Instructions:**
1. Clone repository and install dependencies (`pnpm install` in frontend, `poetry install` in backend)
2. Copy `.env.example` to `.env` and fill in API keys (use Terminal 3 for secure local secret injection)
3. Start local Daytona sandbox: `daytona create --config dev.yaml`
4. Run database migrations: `alembic upgrade head`
5. Start frontend dev server: `pnpm dev` (runs on `localhost:3000`)
6. Start backend: `uvicorn src.api.main:app --reload` (runs on `localhost:8000`)

**Testing Frameworks:**
- **Backend:** Pytest (unit + integration), pytest-asyncio for agent tests, pytest-mock for external API mocking
- **Frontend:** Jest (unit), React Testing Library (component), Playwright (E2E)
- **Agents:** Custom agent evaluation framework using Kimi API test mode

**Code Quality Tools:**
- **Python:** Ruff (linting + formatting), MyPy (type checking), Pydantic (runtime validation)
- **TypeScript:** ESLint, Prettier, tsc (strict mode)
- **Pre-commit:** Hooks for linting, formatting, and secret scanning (detect-secrets)

## 9. Future Considerations / Roadmap

- **Migrate to microservices:** Decompose the monolithic FastAPI backend into independent services (Scraping Service, Planning Service, Generation Service) communicating via message queues.
- **Event-driven architecture:** Implement Kafka or Redis Streams for real-time agent communication and scraped content streaming.
- **Multi-destination trips:** Extend Planner Agent to handle multi-city itineraries with transit optimization.
- **Collaborative planning:** Real-time collaborative itinerary editing using WebSockets and CRDTs.
- **Mobile application:** Native iOS/Android apps using React Native with offline itinerary caching.
- **Booking integration:** Expand Terminal 3 autonomous transactions to support hotel and activity bookings via partner APIs.
- **Feedback loop:** Implement user feedback on itineraries to fine-tune Planner Agent preferences via reinforcement learning.

## 10. Project Identification

**Project Name:** Auratrip

**Repository URL:** [To be determined / Hackathon submission]

**Primary Contact/Team:** Auratrip Hackathon Team

**Date of Last Update:** 2026-06-13

## 11. Glossary / Acronyms

| Acronym/Term | Definition |
|-------------|------------|
| **ADK** | Agent Dev Kit (Terminal 3) |
| **Bright Data** | Web data platform providing scraping infrastructure |
| **Daytona** | Open-source platform for isolated, stateful development sandboxes |
| **DID** | Decentralized Identifier (used by Terminal 3 for agent identity) |
| **GPU** | Graphics Processing Unit (compute resource via Nosana) |
| **IG** | Instagram (social media platform scraped by Bright Data) |
| **Kimi K2.6** | Moonshot AI's large language model with agent swarm capabilities |
| **Nosana** | Decentralized GPU compute network |
| **PPT** | PowerPoint presentation (generated via SenseNova U1 Skills) |
| **RAG** | Retrieval-Augmented Generation (pattern used with VideoDB search) |
| **SenseNova U1** | SenseTime's open-source native multimodal AI model |
| **TEE** | Trusted Execution Environment (hardware security via Terminal 3) |
| **TikTok** | TikTok (social media platform scraped by Bright Data) |
| **TokenRouter** | Unified AI model routing and caching platform |
| **TT** | TikTok (abbreviation) |
| **VideoDB** | Data infrastructure for video, built for machines and agents |
