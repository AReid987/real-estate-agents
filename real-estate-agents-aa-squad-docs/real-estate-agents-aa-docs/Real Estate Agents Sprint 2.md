---
type: Page
title: 'Real Estate: Agents Sprint 2'
description: null
icon: null
createdAt: '2025-07-15T18:32:52.201Z'
creationDate: 2025-07-15 13:32
modificationDate: 2025-07-15 13:33
tags: []
coverImage: null
---

## Sprint 2 Plan

**Sprint 2 Goal:** Enable agents to log in, view listings, initiate AI content generation, and perform initial content approval/rejection via the Frontend Dashboard.

**Duration:** [Suggest 1-2 Weeks, similar to Sprint 1]

**Selected Tasks from Product Backlog:**

1. **API Gateway: User Authentication & Profile (Tasks 5.2.1):**

    - Implement `POST /api/auth/register` endpoint.

    - Implement `POST /api/auth/login` endpoint.

    - Implement `GET /api/agent/me` and `PUT /api/agent/me` endpoints.

2. **Frontend Dashboard: Authentication & Profile Views (Tasks 6.2.1, 6.2.2, 6.2.3, 6.7.1):**

    - Develop Login and Registration pages.

    - Implement protected routes and authentication flow.

    - Build a basic Agent Profile editing UI.

3. **API Gateway: Listing Data Retrieval & Manual Upload (Tasks 5.2.2):**

    - Implement `GET /api/listings` and `GET /api/listings/{listing_id}` endpoints.

    - Implement `POST /api/listings/manual-upload` endpoint.

4. **Frontend Dashboard: Listings Management View (Tasks 6.4.1, 6.4.3):**

    - Develop the Listings List Display UI.

    - Build the Manual Listing Upload Form.

5. **AG2: Content Agent - Core Generation & Handoff (Refinement of Sprint 1's Task 3.3.1 & 3.3.3):**

    - Ensure `Content Agent` reliably generates social media post text and basic flyer text using LLMs via Portkey.

    - Ensure `Content Agent` saves the generated content to `rltr_mktg_content_pieces` with `status='draft'`.

    - Ensure `Content Agent` correctly sends a message to the `UserProxyAgent` to initiate the approval flow for the `content_piece_id`.

6. **AG2: UserProxyAgent - Initial Approval Processing (Tasks 3.4.1, 3.4.2):**

    - Configure `UserProxyAgent` to receive content approval requests from `Content Agent`.

    - Implement logic to process messages from the `API Gateway` for "Approve & Post" and "Reject (Discard)" actions (FR-2.2.1, FR-2.2.2).

    - Update `rltr_mktg_content_pieces` status in the database based on these actions.

7. **API Gateway: Content Approval & Action Endpoints (Initial) (Task 5.2.4):**

    - Implement `GET /api/content/pending-approvals` endpoint.

    - Implement `POST /api/content/{content_id}/action` for `approve_and_post`, `reject_discard`, and `request_revisions` actions. This endpoint will communicate with the `UserProxyAgent`.

8. **Frontend Dashboard: Content Approval View (Initial) (Tasks 6.5.1, 6.5.2, 6.5.3 - initial buttons):**

    - Develop the "Pending Content List" UI component.

    - Build the Content Preview Modal/Detail Page.

    - Implement "Approve & Post," "Reject (Discard)," and "Request Revisions" buttons with a basic text input for feedback.

9. **Frontend Dashboard: "Initiate Content Creation" Action (Task 6.4.2):**

    - Add the UI button/action next to listings to call `POST /api/content/create-for-listing`.

**Definition of Done for Sprint 2:**

- **User Authentication:** Chris can successfully register and log in to the system.

- **Listing Visibility:** Chris can view a list of available listings and manually upload a new listing.

- **Content Generation Trigger:** Chris can select a listing and initiate the generation of marketing content.

- **Content Approval Flow (Core):** Chris can view AI-generated content drafts and perform "Approve & Post" and "Reject (Discard)" actions through the UI, which correctly updates content status in the database.

- **Code Quality:** All new code passes configured linters and formatters.

- **Tests:** Unit tests are written for new backend logic and passing. Basic frontend component tests exist.

