---
type: Page
title: 3. AG2 Multi-Agent Core Development Tasks
description: null
icon: null
createdAt: '2025-07-15T15:52:43.733Z'
creationDate: 2025-07-15 10:52
modificationDate: 2025-07-15 10:53
tags: []
coverImage: null
---

### 3. AG2 Multi-Agent Core Development Tasks

This phase focuses on developing the individual AI agents and orchestrating their collaboration within the AG2 framework to automate marketing workflows.

**3.1. AG2 Framework & Core Agent Setup**

- **Task 3.1.1: Initialize AG2 Project Structure:**

    - Set up the `ag2-core/` directory with necessary Python files and subdirectories (e.g., `agents/`, `tools/`, `workflows/`, `configs/`).

    - Add `autogen` (or `ag2` if that's the specific community fork you're using) and `python-dotenv` to `ag2-core/requirements.txt`.

- **Task 3.1.2: Basic AG2 Agent Configuration:**

    - Create a central configuration file or method for `llm_config` that points all agents to the `Portkey AI Gateway` (`LLM_GATEWAY_URL` environment variable).

    - Implement initial basic `ConversableAgent` instances for each planned agent role (Listing, Content, UserProxy, Social Media, Notification) with placeholder system messages.

- **Task 3.1.3: Shared Database Tool Integration:**

    - Integrate the SQLAlchemy database access functions (from Task 2.3.5) into a shared `tools/database_tools.py` module within the `ag2-core` project.

    - Ensure agents can register and use these tools for database interactions.

**3.2. Listing Agent Development**

- **Task 3.2.1: Implement Web Scraping Logic (FR-1.1.1):**

    - Write Python code using `Playwright` (or `requests`/`BeautifulSoup` if sufficient for `holidaybuilders.com`) within the `Listing Agent` to navigate and extract data from Holiday Builders listing pages.

    - Focus on extracting Address, Images, Description, and Key Features (beds, baths, sqft, community amenities, builder incentives).

- **Task 3.2.2: Data Structuring & Normalization (FR-1.1.2):**

    - Develop logic to parse the scraped HTML and structure the extracted data into a clean, consistent format (e.g., Python dictionary matching the `rltr_mktg_listings` table schema).

- **Task 3.2.3: New Listing Detection & Storage (FR-1.1.3):**

    - Implement logic to compare newly scraped listings against existing ones in the `rltr_mktg_listings` table (using `source_id` or address for unique identification).

    - Store only new or significantly updated listings in the database using the database tools.

- **Task 3.2.4: Trigger Content Agent:**

    - After successfully processing a new/updated listing, the `Listing Agent` SHALL send a message to the `Content Agent`, signaling that content needs to be generated for the new `listing_id`.

**3.3. Content Agent Development**

- **Task 3.3.1: Content Generation Logic (FR-1.2.1, FR-1.2.2):**

    - Enable the `Content Agent` to receive a `listing_id` and retrieve full listing details from the database using its tools.

    - Craft initial LLM prompts (via `Portkey`) to generate social media post elements (headline, body, CTA, hashtags, emojis) and basic flyer text elements (headline, property details, summary, agent contact info).

    - Implement parsing of LLM output to ensure it fits the `generated_text` JSONB structure.

- **Task 3.3.2: Langflow Workflow Integration:**

    - Develop a Python client/tool within the `Content Agent` to make API calls to the `Langflow Workflow Engine` (once Langflow is running and exposes endpoints).

    - Initial integration would be for processing raw text into a templated format for flyers or for further optimization.

- **Task 3.3.3: Initiate Approval Flow (FR-2.2.4):**

    - After generating content, the `Content Agent` SHALL save the draft `content_piece` to the database with `status='draft'`.

    - It then sends a message to the `UserProxyAgent`, explicitly requesting approval for the new `content_piece_id`.

- **Task 3.3.4: Handle Revision Feedback (FR-2.2.3):**

    - The `Content Agent` SHALL be able to receive specific feedback messages from the `UserProxyAgent` (following a "Request Revisions" action from Chris).

    - Implement logic to incorporate this feedback into subsequent LLM calls to generate a revised content draft.

**3.4. UserProxyAgent Development (for Chris's Approval)**

- **Task 3.4.1: Frontend Interaction Bridge:**

    - Configure the `UserProxyAgent`'s `human_input_mode` to `NEVER` but set up a mechanism (e.g., an internal callback triggered by the `API Gateway`) to receive Chris's explicit approval actions from the Frontend.

- **Task 3.4.2: Process Approval Actions (FR-2.2.1 to FR-2.2.7):**

    - Implement logic to process messages/payloads received from the `API Gateway` representing Chris's actions: "Approve & Post," "Reject (Discard)," "Request Revisions," "Send to Marketing Department," "Record Marketing Department Response."

    - Update the `content_piece` status in the database accordingly using database tools.

- **Task 3.4.3: Direct Workflow Orchestration:**

    - Based on Chris's action:

        - "Approve & Post" -> Send message to `Social Media Agent` with `content_piece_id`.

        - "Reject (Discard)" / "Request Revisions" -> Send message with feedback to `Content Agent`.

        - "Send to Marketing Department" -> Trigger `Notification Agent` to inform Chris (FR-4.2.7).

        - "Record Marketing Department Response" -> Based on the recorded response (approved/rejected), either trigger `Social Media Agent` or `Content Agent` (for further revisions based on Marketing Dept feedback).

- **Task 3.4.4: Notification Agent Triggering:**

    - Ensure the `UserProxyAgent` triggers appropriate notifications via the `Notification Agent` for all Chris's actions (FR-4.2.2, FR-4.2.3, FR-4.2.7, FR-4.2.8, FR-4.2.9).

**3.5. Social Media Agent Development**

- **Task 3.5.1: Social Media API Client Integration:**

    - Develop Python clients for interacting with Facebook Graph API and Instagram Basic Display API (leveraging libraries like `facebook-sdk`, `instagram-private-api` as discussed previously).

    - Ensure secure handling of encrypted access tokens retrieved from the database.

- **Task 3.5.2: Posting Logic (FR-3.2.1 to FR-3.2.4):**

    - Enable the `Social Media Agent` to receive `content_piece_id` and `social_media_account_id` (and optionally `scheduled_at` time) from the `UserProxyAgent` or a scheduler.

    - Retrieve content details and associated social media account credentials from the database.

    - Implement platform-specific posting methods for Facebook and Instagram.

- **Task 3.5.3: Post Scheduling:**

    - Integrate with Redis or a simple internal scheduler for posts that are scheduled for a future time (FR-3.2.4).

- **Task 3.5.4: Error Handling & Logging (FR-3.3.1, FR-3.3.2):**

    - Implement try-except blocks for API calls.

    - Implement basic retry logic for transient errors.

    - Log all post success/failure events to the database and notify the `Notification Agent`.

**3.6. Notification Agent Development**

- **Task 3.6.1: Notification Service Integration:**

    - Develop a tool/client to interface with an external Email Service Provider (e.g., SendGrid) for email notifications.

    - Develop an internal mechanism (e.g., publishing to a Redis Pub/Sub channel or directly calling an API Gateway endpoint) for in-app notifications to the Frontend.

- **Task 3.6.2: Notification Triggering & Delivery (FR-4.2.1 to FR-4.2.9):**

    - Enable the `Notification Agent` to receive messages from other agents (e.g., Listing, Content, UserProxy, Social Media).

    - Based on message type and Chris's preferences (from `rltr_mktg_agents.notification_preferences`), format and send notifications via the appropriate channels.

- **Task 3.6.3: Notification History Logging (FR-2.7):**

    - Log all sent notifications (type, message, related entity, status) to the `rltr_mktg_notifications` table.

