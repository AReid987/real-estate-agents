---
type: Page
title: 'Real Estate Marketing Agents: Backlog'
description: null
icon: null
createdAt: '2025-07-15T16:32:30.945Z'
creationDate: 2025-07-15 11:32
modificationDate: 2025-07-15 11:33
tags: []
coverImage: null
---

## Real Estate Agent Marketing System - Preliminary Product Backlog (MVP)

This backlog is prioritized from top to bottom, with the highest priority items at the top. Items within a phase can often be worked on in parallel by different components of the system (e.g., Frontend and Backend tasks for the same feature).

### Phase 1: Foundation & Core Data Flow (Focus: Getting the skeleton working)

**Goal:** Establish the development environment, version control, basic CI/CD, and the core data ingestion loop from `Holidaybuilders.com` into our database.

1. **Core Infrastructure Setup (Tasks 1.1 - 1.7):**

    - **Repo & Monorepo Setup:** GitHub repo, `docker-compose.yml` (Task 1.1).

    - **Containerization:** Basic `Dockerfile`s, local `docker compose up` verification (Task 1.2).

    - **Version Control & Code Quality:** `cz-git`, `Commitlint`, `lint-staged`, initial linters (`ESLint`, `Pylint`, `Prettier`, `Biome.js`), `husky` (Task 1.3).

    - **Testing Frameworks:** `pytest`, `Jest` setup (Task 1.4.1).

    - **CI/CD Setup (GitHub Actions):** Basic linting & testing workflows (Tasks 1.5.1, 1.5.2).

    - **Env Vars & Secrets Management:** `.env.example`, GitHub Secrets (Task 1.6).

    - **Frontend Deployment:** Vercel project setup (Task 1.7).

2. **Database Schema & ORM Setup (Tasks 2.1 - 2.3.5):**

    - Finalize `rltr_mktg` schema in PostgreSQL.

    - Install SQLAlchemy and define models.

    - Set up database connection and session management.

    - Implement initial Alembic migrations.

    - Develop basic CRUD operations for `rltr_mktg_listings` and `rltr_mktg_agents`.

3. **AG2: Listing Agent Core Development (Tasks 3.2.1 - 3.2.4):**

    - Implement web scraping logic for `holidaybuilders.com`.

    - Develop data structuring, normalization, and new listing detection.

    - Store listings in the database (`rltr_mktg_listings`).

    - Trigger `Content Agent` for new listings.

4. **AG2: Content Agent - Initial LLM Integration:**

    - Basic setup of `Content Agent` (`ag2-core/agents/content_agent.py`).

    - Integrate LLM calls via `Portkey AI Gateway` for simple text generation (e.g., initial draft of social media post text, *without* Langflow integration yet).

    - Save generated content to `rltr_mktg_content_pieces` with `status='draft'`.

### Phase 2: First User Interaction & Core AI Value (Focus: Chris's initial "aha!" moment)

**Goal:** Enable Chris to see generated content and take basic approval actions.

1. **API Gateway: Core Endpoints (Tasks 5.2.1 - 5.2.3):**

    - Implement API endpoints for User Authentication (`/api/auth/register`, `/api/auth/login`).

    - Implement endpoint for `GET /api/listings` and `POST /api/listings/manual-upload`.

    - Implement endpoint for `POST /api/content/create-for-listing`.

2. **Frontend Dashboard: Core Views (Tasks 6.2, 6.3, 6.4):**

    - Develop Login and Registration pages.

    - Build the main Dashboard Overview.

    - Create the Listings Management View with "Initiate Content Creation" action and Manual Listing Upload form.

3. **AG2: UserProxyAgent & Initial Approval Flow (Tasks 3.4.1 - 3.4.2):**

    - Set up `UserProxyAgent` to receive content from `Content Agent`.

    - Implement initial logic for processing "Approve" and "Reject" actions from the Frontend.

    - Update `rltr_mktg_content_pieces` status based on actions.

4. **API Gateway: Content Approval Endpoints (Task 5.2.4 - Initial):**

    - Implement `GET /api/content/pending-approvals` to retrieve content for review.

    - Implement `POST /api/content/{content_id}/action` for `approve_and_post`, `reject_discard`, and `request_revisions` actions.

5. **Frontend Dashboard: Content Approval View (Tasks 6.5.1 - 6.5.3 - Initial):**

    - Develop the "Pending Content List" UI.

    - Implement Content Preview Modal/Detail Page.

    - Add "Approve & Post," "Reject (Discard)," "Request Revisions" buttons and feedback input.

### Phase 3: Distribution & Notifications (Focus: Content reaches audience, Chris stays informed)

**Goal:** Enable automated social media posting and comprehensive notifications for Chris.

1. **External Integrations: Social Media APIs (Tasks 7.1, 7.2):**

    - Develop Facebook Graph API and Instagram Graph API clients.

    - Implement secure token handling.

2. **API Gateway: Social Media Account Endpoints (Task 5.2.6):**

    - Implement `GET /api/social-accounts`, `POST /api/social-accounts/connect-facebook`, `POST /api/social-accounts/connect-instagram`.

3. **Frontend Dashboard: Settings - Social Accounts (Task 6.7.3):**

    - Develop the UI for connecting and managing social media accounts.

4. **AG2: Social Media Agent Development (Tasks 3.5.1 - 3.5.4):**

    - Implement posting logic to Facebook and Instagram.

    - Add basic scheduling and error handling.

    - Update `rltr_mktg_post_schedule` table.

5. **External Integrations: Email Service Provider (Task 7.3):**

    - Choose ESP and develop email client.

    - Define basic email templates.

6. **AG2: Notification Agent Development (Tasks 3.6.1 - 3.6.3):**

    - Implement notification triggering and delivery (in-app, email).

    - Log notifications to `rltr_mktg_notifications`.

7. **API Gateway: Notification Endpoints (Task 5.2.5):**

    - Implement `GET /api/notifications`, `PUT /api/notifications/{id}/read`, `PUT /api/agent/me/notification-preferences`.

8. **Frontend Dashboard: Notifications & Settings (Tasks 6.6, 6.7.2):**

    - Develop Notifications View.

    - Implement Notification Preferences UI.

### Phase 4: Refinement & Advanced MVP (Focus: Polish, specific workflows, and readiness for pilot)

**Goal:** Complete the MVP features, including the Marketing Department workflow and advanced content generation.

1. **AG2: Content Agent - Langflow Integration (Tasks 4.1 - 4.3):**

    - Design Langflow workflows for "Flyer Text Generation" and "Social Media Post Optimization."

    - Integrate Langflow API client calls into `Content Agent` for these workflows.

2. **AG2: UserProxyAgent - Marketing Department Flow (Refined Task 3.4.2/3.4.3):**

    - Complete logic for "Send to Marketing Department" and "Record Marketing Department Response" actions.

    - Ensure proper status updates and notifications (FR-2.2.4, FR-2.2.5, FR-4.2.7, FR-4.2.8, FR-4.2.9).

3. **Frontend Dashboard: Content Approval View (Complete Task 6.5.3):**

    - Finalize "Send to Marketing Department" and "Record Marketing Department Response" UI.

4. **Testing & QA:**

    - Implement End-to-End tests (`Playwright`).

    - Ensure comprehensive unit and integration test coverage.

    - Perform manual QA for core user flows.

5. **Documentation:**

    - Update READMEs for each service.

    - Document API endpoints for internal use.

