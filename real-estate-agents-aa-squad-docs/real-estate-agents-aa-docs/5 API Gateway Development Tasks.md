---
type: Page
title: 5. API Gateway Development Tasks
description: null
icon: null
createdAt: '2025-07-15T16:06:33.686Z'
creationDate: 2025-07-15 11:06
modificationDate: 2025-07-15 11:06
tags: []
coverImage: null
---

### 5. API Gateway Development Tasks

This phase involves building the `API Gateway Layer` that acts as the central communication hub between the `Frontend Dashboard` and our various backend services, routing requests and enforcing security.

**5.1. API Gateway Framework Setup**

- **Task 5.1.1: Initialize API Gateway Project:**

    - Set up a Python project in `api-gateway/` (e.g., using FastAPI, which is excellent for this purpose).

    - Add `fastapi`, `uvicorn`, `requests` (for inter-service calls), and `python-dotenv` to `api-gateway/requirements.txt`.

- **Task 5.1.2: Basic Configuration & Security:**

    - Implement CORS (Cross-Origin Resource Sharing) middleware to allow the `Frontend` to connect.

    - Set up basic logging.

**5.2. Define & Implement API Endpoints (MVP)**

- **Task 5.2.1: User Authentication & Profile Management:**

    - `POST /api/auth/register`:

        - **Request:** `{ "email": "...", "password": "...", "agent_name": "...", "phone": "..." }`

        - **Response:** `{ "user_id": "...", "agent_id": "...", "token": "..." }`

        - **Purpose:** Allows new real estate agents to create an account and their associated agent profile (`rltr_mktg_users`, `rltr_mktg_agents`).

    - `POST /api/auth/login`:

        - **Request:** `{ "email": "...", "password": "..." }`

        - **Response:** `{ "user_id": "...", "agent_id": "...", "token": "..." }`

        - **Purpose:** Authenticates a user and returns an access token for subsequent requests.

    - `GET /api/agent/me`:

        - **Request:** (Auth token in header)

        - **Response:** `{ "id": "...", "name": "...", "email": "...", "phone": "...", "notification_preferences": {...} }`

        - **Purpose:** Retrieves the authenticated agent's profile details.

    - `PUT /api/agent/me`:

        - **Request:** `{ "name": "...", "phone": "...", "email": "..." }` (Partial updates)

        - **Response:** Updated agent profile.

        - **Purpose:** Allows Chris to update his own agent profile details (FR-1.1.1 - Agent Details).

- **Task 5.2.2: Listing Data Retrieval:**

    - `GET /api/listings`:

        - **Request:** (Auth token in header, optional query params for filtering)

        - **Response:** `[ { "id": "...", "address": "...", "price": "...", "image_urls": [], ... }, ... ]`

        - **Purpose:** Retrieves a list of all listings associated with the authenticated agent or all available listings (`rltr_mktg_listings`).

    - `GET /api/listings/{listing_id}`:

        - **Request:** (Auth token in header)

        - **Response:** `{ "id": "...", "address": "...", "price": "...", "image_urls": [], ... }`

        - **Purpose:** Retrieves details for a specific listing.

    - `POST /api/listings/manual-upload`:

        - **Request:** `{ "address": "...", "description": "...", "image_urls": [], "key_features": [], ... }`

        - **Response:** `{ "listing_id": "...", "status": "processing" }`

        - **Purpose:** Supports manual listing input as an MVP fallback (FR-1.1.4).

- **Task 5.2.3: Content Creation Trigger:**

    - `POST /api/content/create-for-listing`:

        - **Request:** `{ "listing_id": "...", "content_types": ["social_media_post", "flyer_text"] }`

        - **Response:** `{ "task_id": "...", "status": "initiated" }`

        - **Purpose:** Triggers the `AG2 Multi-Agent Core` (specifically the `Content Agent` via the `UserProxyAgent` or a direct AG2 endpoint) to generate marketing content for a given listing.

- **Task 5.2.4: Content Approval Actions & Retrieval:**

    - `GET /api/content/pending-approvals`:

        - **Request:** (Auth token in header)

        - **Response:** `[ { "id": "...", "type": "...", "generated_text": {}, "associated_listing": {}, "status": "pending_approval_agent", ... }, ... ]`

        - **Purpose:** Retrieves all content pieces awaiting the agent's approval (FR-2.1.1).

    - `POST /api/content/{content_id}/action`:

        - **Request:** `{ "action": "approve_and_post" | "reject_discard" | "request_revisions" | "send_to_marketing" | "record_marketing_response", "feedback": "..." }`

        - **Response:** `{ "content_id": "...", "new_status": "..." }`

        - **Purpose:** Allows Chris to submit his decision on a content piece (FR-2.2.1 to FR-2.2.5). This endpoint will forward the action to the `UserProxyAgent` in AG2.

- **Task 5.2.5: Notification Management:**

    - `GET /api/notifications`:

        - **Request:** (Auth token in header, optional query params for `is_read`)

        - **Response:** `[ { "id": "...", "type": "...", "message": "...", "is_read": false, "created_at": "...", "related_entity_id": "..." }, ... ]`

        - **Purpose:** Retrieves all unread or read notifications for the agent (FR-4.1.1).

    - `PUT /api/notifications/{notification_id}/read`:

        - **Request:** (Auth token in header)

        - **Response:** `{ "notification_id": "...", "status": "marked_as_read" }`

        - **Purpose:** Marks a specific notification as read.

    - `PUT /api/agent/me/notification-preferences`:

        - **Request:** `{ "preferences": { "notification_type_a": true, "notification_type_b": false } }`

        - **Response:** `{ "success": true }`

        - **Purpose:** Updates Chris's notification preferences (`rltr_mktg_agents.notification_preferences`) (FR-4.1.2).

- **Task 5.2.6: Social Media Account Management:**

    - `GET /api/social-accounts`:

        - **Request:** (Auth token in header)

        - **Response:** `[ { "id": "...", "platform": "facebook", "platform_account_id": "...", "is_active": true }, ... ]`

        - **Purpose:** Retrieves a list of connected social media accounts for the agent (`rltr_mktg_social_media_accounts`).

    - `POST /api/social-accounts/connect-facebook`:

        - **Request:** `{ "auth_code": "..." }` (or similar for OAuth flow)

        - **Response:** `{ "success": true, "account_id": "..." }`

        - **Purpose:** Initiates or completes the OAuth flow to connect a Facebook Business Page (FR-3.1.1). (The actual OAuth redirect handling would likely be handled by the Frontend, which then sends the code to this endpoint).

    - `POST /api/social-accounts/connect-instagram`:

        - **Request:** `{ "auth_code": "..." }` (similar to Facebook)

        - **Response:** `{ "success": true, "account_id": "..." }`

        - **Purpose:** Initiates or completes the OAuth flow to connect an Instagram Business Account (FR-3.1.2).

