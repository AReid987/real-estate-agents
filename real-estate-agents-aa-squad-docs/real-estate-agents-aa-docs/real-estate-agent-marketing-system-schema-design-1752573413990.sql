--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3 (PGlite 0.2.0)
-- Dumped by pg_dump version 16.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = off;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET escape_string_warning = off;
SET row_security = off;

--
-- Name: meta; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA meta;


ALTER SCHEMA meta OWNER TO postgres;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: embeddings; Type: TABLE; Schema: meta; Owner: postgres
--

CREATE TABLE meta.embeddings (
    id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    content text NOT NULL,
    embedding public.vector(384) NOT NULL
);


ALTER TABLE meta.embeddings OWNER TO postgres;

--
-- Name: embeddings_id_seq; Type: SEQUENCE; Schema: meta; Owner: postgres
--

ALTER TABLE meta.embeddings ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME meta.embeddings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: migrations; Type: TABLE; Schema: meta; Owner: postgres
--

CREATE TABLE meta.migrations (
    version text NOT NULL,
    name text,
    applied_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE meta.migrations OWNER TO postgres;

--
-- Name: rltr_mktg_agents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rltr_mktg_agents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    phone text,
    email text NOT NULL,
    company text,
    profile_image_url text,
    notification_preferences jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.rltr_mktg_agents OWNER TO postgres;

--
-- Name: rltr_mktg_approval_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rltr_mktg_approval_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    content_piece_id uuid,
    agent_id uuid,
    action_type text,
    "timestamp" timestamp with time zone DEFAULT now(),
    feedback text,
    CONSTRAINT approval_logs_action_type_check CHECK ((action_type = ANY (ARRAY['approved'::text, 'rejected'::text, 'requested_revisions'::text, 'sent_to_marketing'::text, 'recorded_marketing_approval'::text])))
);


ALTER TABLE public.rltr_mktg_approval_logs OWNER TO postgres;

--
-- Name: rltr_mktg_content_pieces; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rltr_mktg_content_pieces (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    listing_id uuid,
    agent_id uuid,
    content_type text,
    generated_text jsonb,
    associated_image_urls text[],
    status text,
    feedback text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    last_approved_at timestamp with time zone,
    CONSTRAINT content_pieces_content_type_check CHECK ((content_type = ANY (ARRAY['social_media_post'::text, 'flyer_text'::text]))),
    CONSTRAINT content_pieces_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'pending_approval_agent'::text, 'pending_external_marketing_approval'::text, 'approved_for_posting'::text, 'rejected'::text, 'pending_ai_revision'::text, 'posted_successfully'::text, 'posting_failed'::text])))
);


ALTER TABLE public.rltr_mktg_content_pieces OWNER TO postgres;

--
-- Name: rltr_mktg_listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rltr_mktg_listings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_id text NOT NULL,
    address jsonb NOT NULL,
    price numeric,
    beds integer,
    baths integer,
    sqft integer,
    description text,
    key_features text[],
    image_urls text[],
    status text,
    scraped_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT listings_status_check CHECK ((status = ANY (ARRAY['active'::text, 'sold'::text])))
);


ALTER TABLE public.rltr_mktg_listings OWNER TO postgres;

--
-- Name: rltr_mktg_notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rltr_mktg_notifications (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agent_id uuid,
    notification_type text NOT NULL,
    message_text text NOT NULL,
    related_entity_id uuid,
    is_read boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.rltr_mktg_notifications OWNER TO postgres;

--
-- Name: rltr_mktg_post_schedule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rltr_mktg_post_schedule (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    content_piece_id uuid,
    social_media_account_id uuid,
    scheduled_at timestamp with time zone NOT NULL,
    posted_at timestamp with time zone,
    status text,
    platform_post_id text,
    error_message text,
    CONSTRAINT post_schedule_status_check CHECK ((status = ANY (ARRAY['pending'::text, 'sent'::text, 'success'::text, 'failed'::text])))
);


ALTER TABLE public.rltr_mktg_post_schedule OWNER TO postgres;

--
-- Name: rltr_mktg_social_media_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rltr_mktg_social_media_accounts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agent_id uuid,
    platform text NOT NULL,
    platform_account_id text NOT NULL,
    encrypted_access_token text NOT NULL,
    token_expiration timestamp with time zone,
    encrypted_refresh_token text,
    active boolean DEFAULT true
);


ALTER TABLE public.rltr_mktg_social_media_accounts OWNER TO postgres;

--
-- Name: rltr_mktg_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rltr_mktg_users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email text NOT NULL,
    password_hash text,
    created_at timestamp with time zone DEFAULT now(),
    last_login timestamp with time zone,
    agent_id uuid
);


ALTER TABLE public.rltr_mktg_users OWNER TO postgres;

--
-- Data for Name: embeddings; Type: TABLE DATA; Schema: meta; Owner: postgres
--



--
-- Data for Name: migrations; Type: TABLE DATA; Schema: meta; Owner: postgres
--

INSERT INTO meta.migrations VALUES ('202407160001', 'embeddings', '2025-07-15 06:08:27.759+00');


--
-- Data for Name: rltr_mktg_agents; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: rltr_mktg_approval_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: rltr_mktg_content_pieces; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: rltr_mktg_listings; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: rltr_mktg_notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: rltr_mktg_post_schedule; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: rltr_mktg_social_media_accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Data for Name: rltr_mktg_users; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- Name: embeddings_id_seq; Type: SEQUENCE SET; Schema: meta; Owner: postgres
--

SELECT pg_catalog.setval('meta.embeddings_id_seq', 1, false);


--
-- Name: embeddings embeddings_pkey; Type: CONSTRAINT; Schema: meta; Owner: postgres
--

ALTER TABLE ONLY meta.embeddings
    ADD CONSTRAINT embeddings_pkey PRIMARY KEY (id);


--
-- Name: migrations migrations_pkey; Type: CONSTRAINT; Schema: meta; Owner: postgres
--

ALTER TABLE ONLY meta.migrations
    ADD CONSTRAINT migrations_pkey PRIMARY KEY (version);


--
-- Name: rltr_mktg_agents agents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_agents
    ADD CONSTRAINT agents_pkey PRIMARY KEY (id);


--
-- Name: rltr_mktg_approval_logs approval_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_approval_logs
    ADD CONSTRAINT approval_logs_pkey PRIMARY KEY (id);


--
-- Name: rltr_mktg_content_pieces content_pieces_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_content_pieces
    ADD CONSTRAINT content_pieces_pkey PRIMARY KEY (id);


--
-- Name: rltr_mktg_listings listings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_listings
    ADD CONSTRAINT listings_pkey PRIMARY KEY (id);


--
-- Name: rltr_mktg_listings listings_source_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_listings
    ADD CONSTRAINT listings_source_id_key UNIQUE (source_id);


--
-- Name: rltr_mktg_notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: rltr_mktg_post_schedule post_schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_post_schedule
    ADD CONSTRAINT post_schedule_pkey PRIMARY KEY (id);


--
-- Name: rltr_mktg_social_media_accounts social_media_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_social_media_accounts
    ADD CONSTRAINT social_media_accounts_pkey PRIMARY KEY (id);


--
-- Name: rltr_mktg_users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: rltr_mktg_users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: rltr_mktg_approval_logs approval_logs_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_approval_logs
    ADD CONSTRAINT approval_logs_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.rltr_mktg_agents(id);


--
-- Name: rltr_mktg_approval_logs approval_logs_content_piece_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_approval_logs
    ADD CONSTRAINT approval_logs_content_piece_id_fkey FOREIGN KEY (content_piece_id) REFERENCES public.rltr_mktg_content_pieces(id);


--
-- Name: rltr_mktg_content_pieces content_pieces_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_content_pieces
    ADD CONSTRAINT content_pieces_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.rltr_mktg_agents(id);


--
-- Name: rltr_mktg_content_pieces content_pieces_listing_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_content_pieces
    ADD CONSTRAINT content_pieces_listing_id_fkey FOREIGN KEY (listing_id) REFERENCES public.rltr_mktg_listings(id);


--
-- Name: rltr_mktg_notifications notifications_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_notifications
    ADD CONSTRAINT notifications_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.rltr_mktg_agents(id);


--
-- Name: rltr_mktg_post_schedule post_schedule_content_piece_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_post_schedule
    ADD CONSTRAINT post_schedule_content_piece_id_fkey FOREIGN KEY (content_piece_id) REFERENCES public.rltr_mktg_content_pieces(id);


--
-- Name: rltr_mktg_post_schedule post_schedule_social_media_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_post_schedule
    ADD CONSTRAINT post_schedule_social_media_account_id_fkey FOREIGN KEY (social_media_account_id) REFERENCES public.rltr_mktg_social_media_accounts(id);


--
-- Name: rltr_mktg_social_media_accounts social_media_accounts_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_social_media_accounts
    ADD CONSTRAINT social_media_accounts_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.rltr_mktg_agents(id);


--
-- Name: rltr_mktg_users users_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rltr_mktg_users
    ADD CONSTRAINT users_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.rltr_mktg_agents(id);


--
-- PostgreSQL database dump complete
--

