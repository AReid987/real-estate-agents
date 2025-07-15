--
-- Real Estate Agent Marketing System Database Schema
-- Enhanced for Production Use
--

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;

-- Create meta schema for system metadata
CREATE SCHEMA IF NOT EXISTS meta;

SET default_tablespace = '';
SET default_table_access_method = heap;

-- Meta tables for system management
CREATE TABLE meta.embeddings (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    content text NOT NULL,
    embedding public.vector(384) NOT NULL
);

CREATE TABLE meta.migrations (
    version text PRIMARY KEY,
    name text,
    applied_at timestamp with time zone DEFAULT now() NOT NULL
);

-- Core business tables
CREATE TABLE public.rltr_mktg_agents (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    name text NOT NULL,
    phone text,
    email text NOT NULL UNIQUE,
    company text,
    profile_image_url text,
    notification_preferences jsonb DEFAULT '{"email": true, "sms": false, "push": true}'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

CREATE TABLE public.rltr_mktg_users (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    email text NOT NULL UNIQUE,
    password_hash text,
    created_at timestamp with time zone DEFAULT now(),
    last_login timestamp with time zone,
    agent_id uuid REFERENCES public.rltr_mktg_agents(id) ON DELETE CASCADE
);

CREATE TABLE public.rltr_mktg_listings (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    source_id text NOT NULL UNIQUE,
    address jsonb NOT NULL,
    price numeric,
    beds integer,
    baths integer,
    sqft integer,
    description text,
    key_features text[],
    image_urls text[],
    status text DEFAULT 'active',
    scraped_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT listings_status_check CHECK (status IN ('active', 'sold', 'pending', 'off_market'))
);

CREATE TABLE public.rltr_mktg_social_media_accounts (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_id uuid REFERENCES public.rltr_mktg_agents(id) ON DELETE CASCADE,
    platform text NOT NULL,
    platform_account_id text NOT NULL,
    encrypted_access_token text NOT NULL,
    token_expiration timestamp with time zone,
    encrypted_refresh_token text,
    active boolean DEFAULT true,
    UNIQUE(agent_id, platform, platform_account_id)
);

CREATE TABLE public.rltr_mktg_content_pieces (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    listing_id uuid REFERENCES public.rltr_mktg_listings(id) ON DELETE CASCADE,
    agent_id uuid REFERENCES public.rltr_mktg_agents(id) ON DELETE CASCADE,
    content_type text NOT NULL,
    generated_text jsonb,
    associated_image_urls text[],
    status text DEFAULT 'draft',
    feedback text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    last_approved_at timestamp with time zone,
    CONSTRAINT content_pieces_content_type_check CHECK (content_type IN ('social_media_post', 'flyer_text', 'email_campaign', 'property_description')),
    CONSTRAINT content_pieces_status_check CHECK (status IN ('draft', 'pending_approval_agent', 'pending_external_marketing_approval', 'approved_for_posting', 'rejected', 'pending_ai_revision', 'posted_successfully', 'posting_failed'))
);

CREATE TABLE public.rltr_mktg_post_schedule (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    content_piece_id uuid REFERENCES public.rltr_mktg_content_pieces(id) ON DELETE CASCADE,
    social_media_account_id uuid REFERENCES public.rltr_mktg_social_media_accounts(id) ON DELETE CASCADE,
    scheduled_at timestamp with time zone NOT NULL,
    posted_at timestamp with time zone,
    status text DEFAULT 'pending',
    platform_post_id text,
    error_message text,
    CONSTRAINT post_schedule_status_check CHECK (status IN ('pending', 'sent', 'success', 'failed', 'cancelled'))
);

CREATE TABLE public.rltr_mktg_approval_logs (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    content_piece_id uuid REFERENCES public.rltr_mktg_content_pieces(id) ON DELETE CASCADE,
    agent_id uuid REFERENCES public.rltr_mktg_agents(id) ON DELETE CASCADE,
    action_type text NOT NULL,
    timestamp timestamp with time zone DEFAULT now(),
    feedback text,
    CONSTRAINT approval_logs_action_type_check CHECK (action_type IN ('approved', 'rejected', 'requested_revisions', 'sent_to_marketing', 'recorded_marketing_approval'))
);

CREATE TABLE public.rltr_mktg_notifications (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_id uuid REFERENCES public.rltr_mktg_agents(id) ON DELETE CASCADE,
    notification_type text NOT NULL,
    message_text text NOT NULL,
    related_entity_id uuid,
    is_read boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now()
);

-- Performance indexes
CREATE INDEX idx_listings_status ON public.rltr_mktg_listings(status);
CREATE INDEX idx_listings_updated_at ON public.rltr_mktg_listings(updated_at);
CREATE INDEX idx_content_pieces_status ON public.rltr_mktg_content_pieces(status);
CREATE INDEX idx_content_pieces_agent_id ON public.rltr_mktg_content_pieces(agent_id);
CREATE INDEX idx_post_schedule_scheduled_at ON public.rltr_mktg_post_schedule(scheduled_at);
CREATE INDEX idx_notifications_agent_unread ON public.rltr_mktg_notifications(agent_id, is_read);
CREATE INDEX idx_approval_logs_content_piece ON public.rltr_mktg_approval_logs(content_piece_id);

-- Vector search index for embeddings
CREATE INDEX embeddings_embedding_idx ON meta.embeddings USING hnsw (embedding vector_cosine_ops);

-- Insert initial migration record
INSERT INTO meta.migrations (version, name) VALUES ('202407160001', 'initial_schema');

-- Create a trigger to update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON public.rltr_mktg_agents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_listings_updated_at BEFORE UPDATE ON public.rltr_mktg_listings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_pieces_updated_at BEFORE UPDATE ON public.rltr_mktg_content_pieces 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
