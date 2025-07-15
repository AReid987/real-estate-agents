---
type: Page
title: 'Real Estate Agents: Sprint 1'
description: null
icon: null
createdAt: '2025-07-15T16:34:47.115Z'
creationDate: 2025-07-15 11:34
modificationDate: 2025-07-15 11:35
tags: []
coverImage: null
---

**Sprint 1 Goal:** Establish core development environment, version control, initial code quality automation, and foundational database setup.

**Proposed Tasks for Sprint 1 (Estimated: 1-2 Weeks)**

From **Phase 1: Foundation & Core Data Flow** of our Product Backlog:

- **1.1. Repository & Project Structure Setup:**

    - **Task 1.1.1: Initialize GitHub Monorepo.**

        - *Deliverable:* Empty GitHub repository with root `.gitignore` and monorepo directory structure (`frontend/`, `ag2-core/`, `api-gateway/`, `langflow-workflows/`, `dagger/`, `configs/`, `integrations/`, `tools/`, `database/`).

    - **Task 1.1.2: Establish Initial** `docker-compose.yml`**.**

        - *Deliverable:* `docker-compose.yml` file with all core services (`ag2-core`, `langflow`, `api-gateway`, `postgres`, `redis`, `portkey`, `frontend`) defined, including basic network and volume configurations.

- **1.2. Containerization & Local Development Setup:**

    - **Task 1.2.1: Dockerfile Creation (Initial).**

        - *Deliverable:* Basic `Dockerfile`s for `ag2-core` (Python), `api-gateway` (Python), and a configured frontend build for Next.js.

    - **Task 1.2.2: Local Development Environment Verification.**

        - *Deliverable:* All services (`ag2-core`, `api-gateway`, `langflow`, `postgres`, `redis`, `portkey`, `frontend`) successfully start and run locally via `docker compose up --build`, showing no immediate errors. Basic connectivity (e.g., `frontend` service reachable) confirmed.

- **1.3. Version Control & Code Quality Automation (Pre-Commit/CI):**

    - **Task 1.3.1: Commit Management Setup.**

        - *Deliverable:* `commitizen`, `cz-git` configured for AI/emoji options, `Commitlint` set up, `husky` hook for `commit-msg` in root.

    - **Task 1.3.2: Code Formatting & Linting Setup (Initial).**

        - *Deliverable:* `lint-staged` configured, `Prettier` (JS/Python), `ESLint v9` (JS), `Biome.js` (JS), `Pylint` (Python) installed and configured. `husky` hook for `pre-commit` to run linters.

- **1.6. Environment Variables & Secrets Management:**

    - **Task 1.6.1: Define** `.env.example`**.**

        - *Deliverable:* A template `.env.example` file at monorepo root listing all required environment variables for local development.

    - **Task 1.6.2: Configure GitHub Secrets (Basic).**

        - *Deliverable:* GitHub repository secrets set up for initial LLM API keys (`OPENAI_API_KEY`) and any other sensitive credentials required for local `docker compose` startup and basic CI tests (e.g., Portkey key if separate).

- **2.3. ORM Setup & Initial Models (SQLAlchemy):**

    - **Task 2.3.1: Install SQLAlchemy.**

        - *Deliverable:* `SQLAlchemy` and `asyncpg` added to `requirements.txt` for `ag2-core` and `api-gateway`.

    - **Task 2.3.2: Define SQLAlchemy Models (Core).**

        - *Deliverable:* Python SQLAlchemy ORM models created for `rltr_mktg_users`, `rltr_mktg_agents`, `rltr_mktg_listings`, and `rltr_mktg_content_pieces` in `database/models.py`.

    - **Task 2.3.3: Database Connection & Session Management.**

        - *Deliverable:* Module (`database/session.py`) to manage async PostgreSQL connection and SQLAlchemy sessions.

    - **Task 2.3.4: Initial Migrations Setup (Alembic).**

        - *Deliverable:* Alembic initialized, and a first migration script generated that creates the tables for the models defined in Task 2.3.2.

This sprint focuses heavily on getting the plumbing in place, ensuring your development environment is robust and automated from day one. By the end of this sprint, you'll have a solid foundation for all future development.

