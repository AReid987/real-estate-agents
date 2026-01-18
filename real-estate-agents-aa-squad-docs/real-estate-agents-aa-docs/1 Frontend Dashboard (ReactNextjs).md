---
type: Page
title: 1. Frontend Dashboard (React/Next.js)
description: null
icon: null
createdAt: '2025-07-15T09:10:25.075Z'
creationDate: 2025-07-15 04:10
modificationDate: 2025-07-15 04:10
tags: []
coverImage: null
---

### 1. Frontend Dashboard (React/Next.js)

The Frontend Dashboard serves as Chris's primary interface with the system. It's the visual manifestation of the Human-in-the-Loop approval process and the central hub for his marketing overview.

- **Core Responsibilities:**

    - **Content Review & Approval (FR-2.1.1, FR-2.1.2, FR-2.1.3, FR-2.2.1 to FR-2.2.7):** Displays a dedicated "Content Approvals" section.

        - Shows a clear list of content drafts (social media posts, flyer text) awaiting review, including status badges.

        - Provides interactive previews of the generated content (text, associated images).

        - Enables actions: "Approve & Post," "Reject (Discard)," "Request Revisions" (with text feedback), and "Send to Marketing Department for Approval."

        - Provides an interface for Chris to manually "Record Marketing Department Response."

    - **Listing Management (FR-1.1.4):** Displays ingested listings and allows Chris to initiate content creation for a specific listing. Includes a simple manual listing input form for fallback.

    - **Notification Display (FR-4.1.1, FR-4.2.1 to FR-4.2.9):** Shows in-app alerts and notifications about content status, posting success/failure, new listings, and reminders related to Marketing Department approval.

    - **Settings & Preferences (FR-4.1.2):** Provides a basic UI for Chris to toggle on/off specific notification types.

    - **Content Marketing Calendar (Future):** While not explicitly an MVP FR, the UI will be designed to accommodate a future "content marketing calendar" to visualize scheduled posts.

    - **Agent Details Configuration:** Allows Chris to input and update his contact details (phone, email, agent name) used by the `Content Agent`.

- **Interaction:** Communicates primarily with the `API Gateway Layer` via RESTful API calls for data retrieval and action submission. May potentially use WebSockets (or long polling for MVP) for real-time notifications pushed from the `Notification Agent`.

### 2. API Gateway Layer

The API Gateway acts as the secure, unified entry point for all external interactions with our backend services (AG2 Core, Langflow). Its role is crucial for routing, authentication, and simplifying frontend-to-backend communication.

- **Core Responsibilities:**

    - **Request Routing:** Directs incoming requests from the `Frontend Dashboard` to the appropriate internal service (`ag2-core`, `langflow`).

    - **Authentication & Authorization:** Handles user login for the `Frontend Dashboard` and ensures that only authorized requests reach the backend services. (Initial MVP: Simple token-based auth).

    - **Unified API Endpoint:** Presents a single, consistent API interface to the `Frontend Dashboard`, abstracting away the complexity of multiple backend microservices.

    - **Specific Endpoints (MVP Examples):**

        - `POST /api/listings/initiate-content`: Triggers content creation for a specific listing (routes to `ag2-core`).

        - `GET /api/content/pending-approvals`: Retrieves a list of content drafts for Chris's review (routes to `ag2-core` for query or directly to DB).

        - `POST /api/content/{id}/action`: Submits Chris's approval action (approve, reject, revise, send to marketing, record marketing response) (routes to `ag2-core` which interacts with `UserProxyAgent`).

        - `GET /api/notifications`: Retrieves Chris's notification history.

        - `POST /api/settings/notifications`: Updates Chris's notification preferences.

    - **Notification Push (via Frontend Bridge):** While not directly integrating an LLM, the API Gateway will be responsible for relaying notifications (e.g., from the `Notification Agent`) to the `Frontend Dashboard` for display.

- **Interaction:** Serves as the intermediary between the `Frontend Dashboard` and the `AG2 Multi-Agent Core` (and potentially `Langflow` directly for certain operations if needed, though AG2 often orchestrates Langflow).

### 3. AG2 Multi-Agent Core

This is the brain of the system, where the intelligent agents collaborate to automate marketing workflows.

- **Core Responsibilities:**

    - **Listing Agent:**

        - **Scraping (FR-1.1.1):** Periodically scrapes `holidaybuilders.com` for new and updated listing data.

        - **Data Structuring & Validation (FR-1.1.2):** Parses raw HTML into structured, normalized property data.

        - **New Listing Detection (FR-1.1.3):** Identifies genuinely new listings or significant updates.

        - **Handoff:** Passes structured listing data to the `Content Agent` to trigger content creation, and persists it to the `PostgreSQL Database`.

    - **Content Agent:**

        - **Content Generation (FR-1.2.1, FR-1.2.2):** Receives structured listing data from the `Listing Agent` (or via manual trigger).

        - Utilizes the `Portkey AI Gateway` to interact with LLMs for generating social media post elements and basic flyer text.

        - **Langflow Integration:** Calls `Langflow` via its API (or a dedicated SDK) to process the generated text content through visual workflows, especially for preparing it for flyer templates.

        - **Initiates Approval Flow:** After generating content, it sends the content draft to the `UserProxyAgent` to initiate Chris's approval process (FR-2.2.4).

        - **Revision Handling (FR-2.2.3):** Receives feedback from the `UserProxyAgent` (Chris's revisions) and attempts to regenerate content based on that feedback.

    - **UserProxyAgent (for Chris's Approval):**

        - **Human-in-the-Loop Interface:** Acts as the programmatic interface for Chris's actions on the `Frontend Dashboard`.

        - Receives content drafts from the `Content Agent`.

        - Receives Chris's approval actions (Approve, Reject, Request Revisions, Send to Marketing, Record Marketing Response) via the `API Gateway`.

        - **Workflow Logic:** Based on Chris's input, it directs the flow:

            - "Approve & Post" -> instructs `Social Media Agent`.

            - "Reject" / "Request Revisions" -> instructs `Content Agent`.

            - "Send to Marketing Department" -> instructs `Notification Agent` to notify Chris.

            - "Record Marketing Department Response" -> updates content status and may instruct `Social Media Agent` or `Content Agent` based on response.

        - **Database Updates:** Updates content status in the `PostgreSQL Database` based on Chris's actions.

    - **Social Media Agent:**

        - **Posting (FR-3.2.1, FR-3.2.2, FR-3.2.3, FR-3.2.4):** Receives "Approved for Posting" content from the `UserProxyAgent` (or a scheduler).

        - Interacts with `Facebook Graph API` and `Instagram Basic Display API` to publish posts.

        - **Error Handling (FR-3.3.1, FR-3.3.2):** Manages retries and logs posting failures, notifying the `Notification Agent`.

    - **Notification Agent:**

        - **Triggered Alerts (FR-4.2.1 to FR-4.2.9):** Receives messages from other AG2 agents (e.g., `Listing Agent` for new listings, `UserProxyAgent` for approval status, `Social Media Agent` for post success/failure).

        - **Channel Delivery (FR-4.1.1):** Sends notifications to Chris via configured channels (in-app display via API Gateway/Frontend, Email Service Provider).

        - **Preference Enforcement (FR-4.1.2):** Checks Chris's notification preferences before sending.

- **Interaction:** Agents communicate primarily via message passing within AG2. They use "tools" to interact with the `PostgreSQL Database`, `Redis`, `Portkey AI Gateway`, `Langflow`, and external `Social Media APIs`.

### 4. Langflow Workflow Engine

Langflow provides a visual, configurable layer, primarily used by the `Content Agent` for more structured content generation, especially related to templates.

- **Core Responsibilities:**

    - **Visual Workflow Design:** Provides a UI for defining specific content generation workflows (e.g., "Generate Flyer Content," "Optimize Social Post for Instagram") as API endpoints.

    - **Content Processing:** Receives raw text/data from the `Content Agent`. It can then apply structured LLM calls, template filling, and data transformations defined in its visual flows.

    - **Exposing API Endpoints:** Exposes its workflows as accessible API endpoints that `AG2` agents (specifically the `Content Agent`) can call.

- **Interaction:** The `Content Agent` makes API calls to `Langflow` endpoints. `Langflow` itself will make LLM calls via the `Portkey AI Gateway`.

### 5. PostgreSQL Database

PostgreSQL serves as the primary persistent data store for all structured information within the system.

- **Core Responsibilities:**

    - **User & Agent Management:** Stores `users` (Chris's login, preferences) and `real_estate_agents` (Chris's profile, contact details, associated builder info).

    - **Listing Data (FR-1.1.2):** Stores all extracted `listings` data from `holidaybuilders.com` in a structured, normalized format. This is our initial "Knowledge Graph" for property information.

    - **Content Management:** Stores `content_pieces` (all generated social media posts, flyer texts) including their `status` (draft, pending_approval, approved_for_posting, rejected, etc.), `feedback`, `associated_listing_id`, and `agent_id`.

    - **Social Media Account Connections:** Securely stores encrypted social media API tokens/credentials (`social_media_accounts`) linked to agents.

    - **Notification History:** Stores a log of `notifications` sent to agents.

    - **Approval Logs:** Stores `approval_events` detailing who approved/rejected what, when, and with what feedback.

- **Interaction:** AG2 agents (via Python DB client or ORM) interact directly with the database for all persistent data storage and retrieval.

### 6. Redis

Redis provides fast, in-memory data storage and messaging capabilities, ideal for transient data, caching, and task queues.

- **Core Responsibilities:**

    - **Agent State/Short-Term Memory:** Can be used for short-term, ephemeral state of active AG2 conversations or agent scratchpads.

    - **Task Queues:** Manages asynchronous, long-running tasks for agents:

        - `Listing Agent` scraping queue (e.g., URLs to scrape).

        - `Social Media Agent` posting queue (e.g., approved posts waiting for a scheduled time, or to be retried).

    - **Caching:** Caches frequently accessed, non-critical data (e.g., agent profiles for quick lookup by agents, or recently processed listing IDs for deduplication).

    - **Pub/Sub (for real-time notifications):** Can act as a message broker for `Notification Agent` to publish real-time events that the `API Gateway` (if integrated with WebSockets) can subscribe to and push to the `Frontend`.

- **Interaction:** AG2 agents interact with Redis for queuing, caching, and managing transient state.

### 7. Portkey AI Gateway

Portkey serves as the intelligent, centralized proxy for all LLM interactions, enhancing control, cost-efficiency, and reliability.

- **Core Responsibilities:**

    - **Unified LLM API (FR-5.6.2):** Presents a single, OpenAI-compatible API endpoint (`LLM_GATEWAY_URL`) for all LLM calls from both `AG2` agents and `Langflow`. This addresses the "Not Diamond" concept by abstracting the actual LLM provider.

    - **API Key Management (NFR-5.3.3):** Securely stores and manages API keys for various underlying LLM providers (e.g., OpenAI, Gemini), preventing direct exposure in application code.

    - **Cost Optimization (NFR-5.6.2):** Implements caching for identical LLM requests to reduce redundant calls and associated costs.

    - **Reliability & Fallbacks (NFR-5.4.3):** Can be configured to automatically retry failed LLM requests or route to alternative LLM providers in case of outages (post-MVP, for MVP basic retry/fallback built into AG2 might suffice if Portkey's advanced features aren't fully configured).

    - **Observability:** Provides centralized logging and monitoring of all LLM requests, responses, and token usage, essential for NFR-5.4.2 and NFR-5.6.2.

    - **Prompt Management:** Can store prompt templates and partials, ensuring consistency and allowing for easier iteration on prompts without code changes.

- **Interaction:** `AG2` agents (specifically `Content Agent`) and `Langflow` workflows are configured to send their LLM requests to the `Portkey AI Gateway` endpoint. `Portkey` then forwards these requests to the actual LLM providers.

