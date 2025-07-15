---
type: Page
title: 6. Frontend Dashboard Development Tasks
description: null
icon: null
createdAt: '2025-07-15T16:11:41.216Z'
creationDate: 2025-07-15 11:11
modificationDate: 2025-07-15 11:12
tags: []
coverImage: null
---

### 6. Frontend Dashboard Development Tasks

This phase focuses on building the user interface that allows real estate agents to interact with the system, review content, manage settings, and receive notifications.

**6.1. Core Frontend Setup**

- **Task 6.1.1: Initialize Next.js Project:**

    - Set up a new Next.js project in the `frontend/` directory.

    - Configure basic routing, layout, and styling (e.g., Tailwind CSS, Material-UI, or a custom design system).

- **Task 6.1.2: API Integration Layer:**

    - Create a client-side API module (`utils/api.js` or similar) to handle all interactions with the `API Gateway Layer`.

    - Implement authentication token management (storage, attaching to requests).

- **Task 6.1.3: Global State Management:**

    - Set up a lightweight state management solution (e.g., React Context API, Zustand, or Redux Toolkit) for managing user authentication status, notifications, and other global data.

**6.2. Authentication & User Management Views**

- **Task 6.2.1: Login Page:**

    - UI: Email and password input fields, login button.

    - Functionality: Calls `POST /api/auth/login` and handles token storage. Displays error messages for failed login.

- **Task 6.2.2: Registration Page:**

    - UI: Fields for email, password, agent name, phone, and registration button.

    - Functionality: Calls `POST /api/auth/register` to create a new user and agent profile.

- **Task 6.2.3: Protected Routes & Authentication Flow:**

    - Implement client-side routing protection to ensure users are authenticated before accessing core system features.

    - Manage redirection to login page for unauthenticated users.

**6.3. Main Dashboard / Home Page**

- **Task 6.3.1: Dashboard Overview:**

    - UI: A concise summary view for Chris, showing:

        - Count of "Content Awaiting Approval" (linking to Content Approval View).

        - Recent successful posts with quick links (linking to live posts).

        - Summary of recent notifications.

        - Quick links to other main sections (Listings, Settings).

    - Functionality: Fetches counts and summaries from relevant API Gateway endpoints.

**6.4. Listings Management View**

- **Task 6.4.1: Listings List Display:**

    - UI: Table or card view displaying all `rltr_mktg_listings` associated with the agent.

    - Fields displayed: Address, Price, Beds, Baths, SqFt, a primary image thumbnail.

    - Functionality: Calls `GET /api/listings`.

- **Task 6.4.2: "Initiate Content Creation" Action:**

    - UI: A button or action next to each listing (or a multi-select action) to trigger content generation.

    - Functionality: Calls `POST /api/content/create-for-listing` for selected listings.

- **Task 6.4.3: Manual Listing Upload Form (FR-1.1.4):**

    - UI: A form to input essential listing details (address, description, image URLs, key features).

    - Functionality: Calls `POST /api/listings/manual-upload`.

**6.5. Content Approval View (Core MVP View)**

- **Task 6.5.1: Pending Content List (FR-2.1.1):**

    - UI: A dedicated section (e.g., "Pending Approvals") displaying a clear list of content drafts.

    - Visual Cues: Use status badges or clear grouping for "Pending Agent Approval" and "Awaiting External Marketing Approval."

- **Task 6.5.2: Content Preview Modal/Detail Page (FR-2.1.2, FR-2.1.3):**

    - UI: When a content item is selected, a detailed view or modal appears showing:

        - Full generated text for social media post (headline, body, hashtags, emojis) with placeholder for image.

        - Structured text for flyer content.

        - Associated listing details (address, primary image).

        - Last feedback received (if any).

    - Functionality: Fetches content details using appropriate API calls.

- **Task 6.5.3: Action Buttons & Feedback Input (FR-2.2.1 to FR-2.2.6):**

    - UI: Prominent buttons for: "Approve & Post," "Reject (Discard)," "Request Revisions," "Send to Marketing Department."

    - Text Input: A rich text area for providing `feedback` for "Reject" and "Request Revisions" actions.

    - **"Record Marketing Department Response" Interface (FR-2.2.5):** A specific UI element that appears when content is in "Awaiting External Marketing Approval" status, allowing Chris to select "Approved by Marketing," "Rejected by Marketing," or "Feedback Provided by Marketing" and input text.

    - Functionality: Calls `POST /api/content/{content_id}/action` with the relevant action type and feedback.

**6.6. Notifications View**

- **Task 6.6.1: Notifications List Display (FR-4.1.1, FR-4.2.1 to FR-4.2.9):**

    - UI: A chronological list of all notifications for the agent (in-app alerts, post success/failure, approval reminders, listing ingested alerts, marketing department interactions).

    - Visuals: Clearly distinguish read/unread notifications. Include links to relevant content/posts where applicable (FR-4.3.2).

    - Functionality: Calls `GET /api/notifications` and `PUT /api/notifications/{id}/read`.

**6.7. Settings & Profile View**

- **Task 6.7.1: Agent Profile Editing:**

    - UI: Form fields to edit agent `name`, `phone`, `email`.

    - Functionality: Calls `PUT /api/agent/me`.

- **Task 6.7.2: Notification Preferences (FR-4.1.2):**

    - UI: Toggle switches or checkboxes for each specific `notification_type` (e.g., "Notify on Content Approval," "Notify on Post Success," "Notify on Listing Ingested").

    - Functionality: Calls `PUT /api/agent/me/notification-preferences`.

- **Task 6.7.3: Social Media Account Connection:**

    - UI: Display list of connected social media accounts (Facebook, Instagram) (FR-5.2.6 - GET).

    - UI: Buttons to "Connect Facebook" and "Connect Instagram" which initiate the OAuth flow.

    - Functionality: Handles redirects for OAuth and calls `POST /api/social-accounts/connect-facebook` / `connect-instagram` with the authorization code.

