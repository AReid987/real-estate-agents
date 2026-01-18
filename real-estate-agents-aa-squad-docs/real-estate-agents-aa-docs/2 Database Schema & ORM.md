---
type: Page
title: 2. Database Schema & ORM
description: null
icon: null
createdAt: '2025-07-15T15:49:47.249Z'
creationDate: 2025-07-15 10:49
modificationDate: 2025-07-15 10:50
tags: []
coverImage: null
---

### 2. Database Schema & ORM

The PostgreSQL database will serve as the central persistent data store. Here are the core entities and their essential fields required to support the MVP functionalities:

**2.1.** `users` **Table**

- **Purpose:** Stores user authentication and basic profile information for accessing the Frontend Dashboard.

- **Essential Fields:**

    - `id` (UUID, Primary Key)

    - `email` (VARCHAR, UNIQUE, NOT NULL)

    - `password_hash` (VARCHAR, NOT NULL) - *For direct logins, though OAuth might abstract this*

    - `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

    - `last_login_at` (TIMESTAMP)

    - `is_active` (BOOLEAN, DEFAULT TRUE)

    - `agent_id` (UUID, FOREIGN KEY to `agents.id`, UNIQUE) - *Links user login to a specific real estate agent profile*

**2.2.** `agents` **Table**

- **Purpose:** Stores specific details for each real estate agent using the system (e.g., Chris's profile), independent of their login credentials.

- **Essential Fields:**

    - `id` (UUID, Primary Key)

    - `name` (VARCHAR, NOT NULL) - *Agent's full name*

    - `phone` (VARCHAR)

    - `email` (VARCHAR, UNIQUE, NOT NULL) - *Agent's primary contact email*

    - `company` (VARCHAR)

    - `profile_image_url` (TEXT)

    - `notification_preferences` (JSONB) - *Stores toggles for notifications (FR-4.1.2)*

    - `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

    - `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

**2.3.** `social_media_accounts` **Table**

- **Purpose:** Stores securely encrypted credentials/tokens for connected social media platforms.

- **Essential Fields:**

    - `id` (UUID, Primary Key)

    - `agent_id` (UUID, FOREIGN KEY to `agents.id`, NOT NULL)

    - `platform` (VARCHAR, NOT NULL) - *e.g., 'facebook', 'instagram'*

    - `account_id` (VARCHAR, NOT NULL) - *Platform-specific ID (e.g., Facebook Page ID)*

    - `access_token_encrypted` (TEXT, NOT NULL) - *Encrypted OAuth token*

    - `token_expires_at` (TIMESTAMP)

    - `refresh_token_encrypted` (TEXT) - *If platform supports refresh tokens*

    - `is_active` (BOOLEAN, DEFAULT TRUE)

    - `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

    - `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

**2.4.** `listings` **Table**

- **Purpose:** Stores structured data for properties scraped from `holidaybuilders.com`.

- **Essential Fields:**

    - `id` (UUID, Primary Key)

    - `source_id` (VARCHAR, UNIQUE, NOT NULL) - *Unique ID from holidaybuilders.com, if available*

    - `address` (VARCHAR, NOT NULL) - *Full street address*

    - `city` (VARCHAR, NOT NULL)

    - `state` (VARCHAR, NOT NULL)

    - `zip_code` (VARCHAR, NOT NULL)

    - `price` (NUMERIC)

    - `beds` (INTEGER)

    - `baths` (NUMERIC)

    - `sqft` (INTEGER)

    - `description` (TEXT) - *Raw scraped description*

    - `key_features` (TEXT[]) - *Array of key features identified (e.g., "clubhouse", "pool access")*

    - `image_urls` (TEXT[]) - *Array of URLs for property images*

    - `status` (VARCHAR, DEFAULT 'active') - *e.g., 'active', 'sold', 'off_market'*

    - `scraped_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

    - `last_updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

**2.5.** `content_pieces` **Table**

- **Purpose:** Stores all AI-generated marketing content drafts and their final approved versions.

- **Essential Fields:**

    - `id` (UUID, Primary Key)

    - `listing_id` (UUID, FOREIGN KEY to `listings.id`, NOT NULL)

    - `agent_id` (UUID, FOREIGN KEY to `agents.id`, NOT NULL) - *Agent who "owns" this content*

    - `content_type` (VARCHAR, NOT NULL) - *e.g., 'social_media_post', 'flyer_text'*

    - `generated_text` (JSONB, NOT NULL) - *Stores generated headline, body, hashtags, etc. (FR-1.2.1, FR-1.2.2)*

    - `associated_image_urls` (TEXT[]) - *URLs of images to be used with this content*

    - `status` (VARCHAR, NOT NULL) - *e.g., 'draft', 'pending_approval_agent', 'pending_external_marketing_approval', 'approved_for_posting', 'rejected', 'pending_ai_revision', 'posted_successfully', 'posting_failed'*

    - `feedback` (TEXT) - *Most recent feedback for revision*

    - `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

    - `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

    - `last_approved_at` (TIMESTAMP)

**2.6.** `post_schedule` **Table**

- **Purpose:** Manages the scheduling of approved social media posts.

- **Essential Fields:**

    - `id` (UUID, Primary Key)

    - `content_piece_id` (UUID, FOREIGN KEY to `content_pieces.id`, NOT NULL)

    - `social_media_account_id` (UUID, FOREIGN KEY to `social_media_accounts.id`, NOT NULL)

    - `scheduled_at` (TIMESTAMP, NOT NULL) - *When the post should go live*

    - `posted_at` (TIMESTAMP) - *Actual time posted*

    - `status` (VARCHAR, NOT NULL) - *e.g., 'pending', 'sent', 'success', 'failed'*

    - `platform_post_id` (VARCHAR) - *ID returned by social media API after successful post*

    - `error_message` (TEXT) - *If posting failed*

    - `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

    - `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

**2.7.** `notifications` **Table**

- **Purpose:** Stores a log of all system notifications sent to agents, allowing for in-app display and tracking.

- **Essential Fields:**

    - `id` (UUID, Primary Key)

    - `agent_id` (UUID, FOREIGN KEY to `agents.id`, NOT NULL)

    - `notification_type` (VARCHAR, NOT NULL) - *e.g., 'content_awaiting_approval', 'post_success', 'listing_ingested'*

    - `message` (TEXT, NOT NULL)

    - `related_entity_id` (UUID) - *e.g.,* `content_piece_id`*,* `listing_id`

    - `is_read` (BOOLEAN, DEFAULT FALSE)

    - `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

**2.8.** `approval_logs` **Table**

- **Purpose:** Provides an audit trail for all content approval actions.

- **Essential Fields:**

    - `id` (UUID, Primary Key)

    - `content_piece_id` (UUID, FOREIGN KEY to `content_pieces.id`, NOT NULL)

    - `agent_id` (UUID, FOREIGN KEY to `agents.id`, NOT NULL) - *Agent who took the action*

    - `action_type` (VARCHAR, NOT NULL) - *e.g., 'approved', 'rejected', 'requested_revisions', 'sent_to_marketing', 'recorded_marketing_approval'*

    - `timestamp` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

    - `feedback` (TEXT) - *Details of the feedback provided*

---

Now, here's the prompt you can use for the Supabase `database.build` agent. It distills our requirements and the schema above into a concise format for an LLM-based agent.

---

### Prompt for Supabase `database.build` Agent

```text
Please generate a PostgreSQL schema (CREATE TABLE statements with appropriate constraints, indexes, and relationships) for a "Real Estate Agent Marketing System". The system aims to automate content generation and social media posting for real estate agents. Consider the following entities and their relationships. Focus on a Minimal Viable Product (MVP) but ensure it's extensible.
**Core Entities & Their Relationships:**
1.  **Users:** Standard user authentication for a web application. Each user will be linked to one real estate agent profile.
2.  **Agents:** Represents individual real estate agents using the system. Stores their contact details, notification preferences, and links to their connected social media accounts. An agent can have multiple social media accounts and multiple listings/content pieces.
3.  **Listings:** Property data primarily scraped from external websites (like holidaybuilders.com). An agent can be associated with multiple listings. Listings will have basic property details, images, and descriptions.
4.  **Content Pieces:** AI-generated marketing content (social media posts, flyer text) for specific listings. Each piece of content belongs to one agent and one listing. It will track its approval status and associated feedback.
5.  **Social Media Accounts:** Stores authentication tokens and details for an agent's connected Facebook and Instagram accounts. One agent can connect multiple accounts.
6.  **Post Schedule:** Manages the scheduling and tracking of content posted to social media accounts. Links a content piece to a social media account at a specific time.
7.  **Notifications:** Stores a log of system notifications sent to agents (e.g., approval requests, posting success/failure). Links to a specific agent and a related entity (listing or content).
8.  **Approval Logs:** An audit trail for all content approval actions, tracking who did what, when, and any feedback provided. Links to a content piece and the agent who performed the action.
**Key Data Points for Each Entity (Minimum MVP):**
* **User:** ID, Email, Password Hash (or placeholder for OAuth), Created/Last Login timestamps, Agent ID (FK).
* **Agent:** ID, Name, Phone, Agent Email, Company, Profile Image URL, Notification Preferences (JSONB), Created/Updated timestamps.
* **Social Media Account:** ID, Agent ID (FK), Platform (e.g., 'facebook', 'instagram'), Platform Account ID, Encrypted Access Token, Token Expiration, Encrypted Refresh Token, Active status.
* **Listing:** ID, Source ID (unique ID from external website), Address (street, city, state, zip), Price, Beds, Baths, SqFt, Description, Array of Key Features, Array of Image URLs, Status (active/sold), Scraped/Updated timestamps.
* **Content Piece:** ID, Listing ID (FK), Agent ID (FK), Content Type ('social_media_post', 'flyer_text'), Generated Text (JSONB for structured elements), Array of Associated Image URLs, Status (draft, pending_approval_agent, pending_external_marketing_approval, approved_for_posting, rejected, pending_ai_revision, posted_successfully, posting_failed), Feedback text, Created/Updated timestamps, Last Approved timestamp.
* **Post Schedule:** ID, Content Piece ID (FK), Social Media Account ID (FK), Scheduled At, Posted At, Status ('pending', 'sent', 'success', 'failed'), Platform Post ID, Error Message.
* **Notification:** ID, Agent ID (FK), Notification Type, Message Text, Related Entity ID (FK to listing/content), Is Read status, Created At.
* **Approval Log:** ID, Content Piece ID (FK), Agent ID (FK), Action Type ('approved', 'rejected', 'requested_revisions', 'sent_to_marketing', 'recorded_marketing_approval'), Timestamp, Feedback.
**Constraints & Considerations:**
* Use UUIDs for primary keys.
* Implement appropriate NOT NULL constraints.
* Consider UNIQUE constraints for obvious fields (e.g., `user.email`, `listing.source_id`).
* Establish Foreign Key relationships where clearly defined.
* Ensure `TEXT[]` or `JSONB` are used for arrays/structured data where appropriate.
* Prioritize simplicity for MVP while allowing for future expansion.
```

---

### 2. Database Schema & ORM (Continued)

Now that we've chosen SQLAlchemy, let's define the immediate development tasks for setting up the ORM and creating basic data interaction capabilities:

**2.3. ORM Setup & Initial Models (SQLAlchemy)**

- **Task 2.3.1: Install SQLAlchemy:**

    - Add `SQLAlchemy` to the `requirements.txt` for `ag2-core` and `api-gateway` services.

    - Consider `psycopg2` or `asyncpg` as the PostgreSQL driver. `asyncpg` is preferred for async contexts common in modern Python services.

- **Task 2.3.2: Define SQLAlchemy Models:**

    - Translate the SQL schema we just received into SQLAlchemy ORM models (Python classes). Each table (`rltr_mktg_agents`, `rltr_mktg_listings`, `rltr_mktg_content_pieces`, etc.) will have a corresponding SQLAlchemy model.

    - Place these models in a shared `database/models.py` module that both `ag2-core` and `api-gateway` can import.

    - Ensure relationships (e.g., `agents` to `listings`, `listings` to `content_pieces`) are correctly defined using SQLAlchemy's relationship capabilities.

- **Task 2.3.3: Database Connection & Session Management:**

    - Implement a module (e.g., `database/session.py`) for establishing a connection to the PostgreSQL database and managing SQLAlchemy sessions.

    - Ensure it supports asynchronous operations (`asyncio`) if we're using `asyncpg` or `SQLAlchemy`'s async capabilities, which is highly recommended for performance in an API/agent context.

    - Configure database URL using environment variables (`DATABASE_URL`).

- **Task 2.3.4: Initial Migrations Setup (Alembic):**

    - Set up `Alembic` for database migrations. This is crucial for managing schema changes as the project evolves.

    - Generate the first migration script based on our current schema.

    - Write a script/command to apply migrations.

- **Task 2.3.5: Basic CRUD Operations:**

    - Develop initial utility functions or repository classes for basic Create, Read, Update, and Delete (CRUD) operations for key entities: `agents`, `users`, `listings`, and `content_pieces`.

    - These functions will demonstrate how `ag2-core` agents and the `api-gateway` can interact with the database using the SQLAlchemy models.

