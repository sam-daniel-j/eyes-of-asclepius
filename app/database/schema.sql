-- pg_dump -U postgres -d eyes_of_asclepius -s > schema.sql(use this to extract the schema from the database, without data)
-- PostgreSQL database dump
--

\restrict fRlnH1x6u4MVZbz4gNaz1nvx9jcOTd1X3SwNg0JQOmOKodIemKTbJ9rHUN1FeAO

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: access_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.access_logs (
    id integer NOT NULL,
    user_id integer,
    patient_id integer,
    action character varying(40) NOT NULL,
    justification text,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT access_logs_action_check CHECK (((action)::text = ANY ((ARRAY['LOGIN'::character varying, 'VIEW_RECORD'::character varying, 'CREATE_RECORD'::character varying, 'EMERGENCY_ACCESS'::character varying, 'REFERRAL_GRANTED'::character varying, 'REFERRAL_ACCESS'::character varying, 'REFERRAL_EXPIRED'::character varying])::text[])))
);


ALTER TABLE public.access_logs OWNER TO postgres;

--
-- Name: access_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.access_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.access_logs_id_seq OWNER TO postgres;

--
-- Name: access_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.access_logs_id_seq OWNED BY public.access_logs.id;


--
-- Name: doctor_patient_map; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.doctor_patient_map (
    id integer NOT NULL,
    doctor_id integer NOT NULL,
    patient_id integer NOT NULL,
    assigned_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.doctor_patient_map OWNER TO postgres;

--
-- Name: doctor_patient_map_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.doctor_patient_map_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.doctor_patient_map_id_seq OWNER TO postgres;

--
-- Name: doctor_patient_map_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.doctor_patient_map_id_seq OWNED BY public.doctor_patient_map.id;


--
-- Name: doctor_referrals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.doctor_referrals (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    from_doctor_id integer NOT NULL,
    to_doctor_id integer NOT NULL,
    reason text NOT NULL,
    access_expires_at timestamp without time zone,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    record_id integer,
    encrypted_aes_key text
);


ALTER TABLE public.doctor_referrals OWNER TO postgres;

--
-- Name: doctor_referrals_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.doctor_referrals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.doctor_referrals_id_seq OWNER TO postgres;

--
-- Name: doctor_referrals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.doctor_referrals_id_seq OWNED BY public.doctor_referrals.id;


--
-- Name: medical_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.medical_records (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    created_by_doctor_id integer NOT NULL,
    encrypted_data text NOT NULL,
    iv text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.medical_records OWNER TO postgres;

--
-- Name: medical_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.medical_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.medical_records_id_seq OWNER TO postgres;

--
-- Name: medical_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.medical_records_id_seq OWNED BY public.medical_records.id;


--
-- Name: record_keys; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.record_keys (
    id integer NOT NULL,
    record_id integer NOT NULL,
    user_id integer NOT NULL,
    encrypted_aes_key text NOT NULL,
    granted_via character varying(30) NOT NULL,
    expires_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT record_keys_granted_via_check CHECK (((granted_via)::text = ANY ((ARRAY['OWNER'::character varying, 'EMERGENCY'::character varying, 'REFERRAL'::character varying])::text[])))
);


ALTER TABLE public.record_keys OWNER TO postgres;

--
-- Name: record_keys_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.record_keys_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.record_keys_id_seq OWNER TO postgres;

--
-- Name: record_keys_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.record_keys_id_seq OWNED BY public.record_keys.id;


--
-- Name: user_id_counters; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_id_counters (
    role character varying(3) NOT NULL,
    year integer NOT NULL,
    last_value integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.user_id_counters OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password_hash text NOT NULL,
    role character varying(20) NOT NULL,
    specialization character varying(100),
    rsa_public_key text NOT NULL,
    rsa_private_key_encrypted text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    private_key_salt text,
    public_id character varying(20),
    CONSTRAINT users_role_check CHECK (((role)::text = ANY ((ARRAY['admin'::character varying, 'doctor'::character varying, 'patient'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: access_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_logs ALTER COLUMN id SET DEFAULT nextval('public.access_logs_id_seq'::regclass);


--
-- Name: doctor_patient_map id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_patient_map ALTER COLUMN id SET DEFAULT nextval('public.doctor_patient_map_id_seq'::regclass);


--
-- Name: doctor_referrals id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_referrals ALTER COLUMN id SET DEFAULT nextval('public.doctor_referrals_id_seq'::regclass);


--
-- Name: medical_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medical_records ALTER COLUMN id SET DEFAULT nextval('public.medical_records_id_seq'::regclass);


--
-- Name: record_keys id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.record_keys ALTER COLUMN id SET DEFAULT nextval('public.record_keys_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: access_logs access_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_logs
    ADD CONSTRAINT access_logs_pkey PRIMARY KEY (id);


--
-- Name: doctor_patient_map doctor_patient_map_doctor_id_patient_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_patient_map
    ADD CONSTRAINT doctor_patient_map_doctor_id_patient_id_key UNIQUE (doctor_id, patient_id);


--
-- Name: doctor_patient_map doctor_patient_map_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_patient_map
    ADD CONSTRAINT doctor_patient_map_pkey PRIMARY KEY (id);


--
-- Name: doctor_referrals doctor_referrals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_referrals
    ADD CONSTRAINT doctor_referrals_pkey PRIMARY KEY (id);


--
-- Name: medical_records medical_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medical_records
    ADD CONSTRAINT medical_records_pkey PRIMARY KEY (id);


--
-- Name: record_keys record_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.record_keys
    ADD CONSTRAINT record_keys_pkey PRIMARY KEY (id);


--
-- Name: user_id_counters user_id_counters_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_id_counters
    ADD CONSTRAINT user_id_counters_pkey PRIMARY KEY (role, year);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_public_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_public_id_key UNIQUE (public_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_doctor_patient_doctor; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_doctor_patient_doctor ON public.doctor_patient_map USING btree (doctor_id);


--
-- Name: idx_doctor_patient_patient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_doctor_patient_patient ON public.doctor_patient_map USING btree (patient_id);


--
-- Name: idx_records_doctor; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_records_doctor ON public.medical_records USING btree (created_by_doctor_id);


--
-- Name: idx_records_patient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_records_patient ON public.medical_records USING btree (patient_id);


--
-- Name: idx_users_public_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_public_id ON public.users USING btree (public_id);


--
-- Name: access_logs access_logs_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_logs
    ADD CONSTRAINT access_logs_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.users(id);


--
-- Name: access_logs access_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_logs
    ADD CONSTRAINT access_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: doctor_patient_map doctor_patient_map_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_patient_map
    ADD CONSTRAINT doctor_patient_map_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: doctor_patient_map doctor_patient_map_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_patient_map
    ADD CONSTRAINT doctor_patient_map_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: doctor_referrals doctor_referrals_from_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_referrals
    ADD CONSTRAINT doctor_referrals_from_doctor_id_fkey FOREIGN KEY (from_doctor_id) REFERENCES public.users(id);


--
-- Name: doctor_referrals doctor_referrals_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_referrals
    ADD CONSTRAINT doctor_referrals_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: doctor_referrals doctor_referrals_to_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_referrals
    ADD CONSTRAINT doctor_referrals_to_doctor_id_fkey FOREIGN KEY (to_doctor_id) REFERENCES public.users(id);


--
-- Name: medical_records medical_records_created_by_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medical_records
    ADD CONSTRAINT medical_records_created_by_doctor_id_fkey FOREIGN KEY (created_by_doctor_id) REFERENCES public.users(id);


--
-- Name: medical_records medical_records_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medical_records
    ADD CONSTRAINT medical_records_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: record_keys record_keys_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.record_keys
    ADD CONSTRAINT record_keys_record_id_fkey FOREIGN KEY (record_id) REFERENCES public.medical_records(id) ON DELETE CASCADE;


--
-- Name: record_keys record_keys_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.record_keys
    ADD CONSTRAINT record_keys_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict fRlnH1x6u4MVZbz4gNaz1nvx9jcOTd1X3SwNg0JQOmOKodIemKTbJ9rHUN1FeAO

