--
-- PostgreSQL database dump
--

\restrict YjjIjx15SSb5POyQfjgFxdGsdiJ1wDPMgjq522GQaM2BkLeRxzyIom5x9EO0uvX

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-05-09 12:21:37

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

--
-- TOC entry 4 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- TOC entry 5035 (class 0 OID 0)
-- Dependencies: 4
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 224 (class 1259 OID 16407)
-- Name: assessments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.assessments (
    id integer NOT NULL,
    municipality_id integer,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    total_score numeric(5,2),
    answers jsonb
);


--
-- TOC entry 223 (class 1259 OID 16406)
-- Name: assessments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.assessments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5036 (class 0 OID 0)
-- Dependencies: 223
-- Name: assessments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.assessments_id_seq OWNED BY public.assessments.id;


--
-- TOC entry 220 (class 1259 OID 16389)
-- Name: municipalities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.municipalities (
    id integer NOT NULL,
    name character varying(100),
    county character varying(100),
    population integer,
    contact_email character varying(255)
);


--
-- TOC entry 219 (class 1259 OID 16388)
-- Name: municipalities_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.municipalities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5037 (class 0 OID 0)
-- Dependencies: 219
-- Name: municipalities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.municipalities_id_seq OWNED BY public.municipalities.id;


--
-- TOC entry 222 (class 1259 OID 16397)
-- Name: questions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.questions (
    id integer NOT NULL,
    category character varying(100),
    question_text text,
    weight integer,
    gap_description text,
    recommendation text
);


--
-- TOC entry 221 (class 1259 OID 16396)
-- Name: questions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5038 (class 0 OID 0)
-- Dependencies: 221
-- Name: questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.questions_id_seq OWNED BY public.questions.id;


--
-- TOC entry 4868 (class 2604 OID 16410)
-- Name: assessments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assessments ALTER COLUMN id SET DEFAULT nextval('public.assessments_id_seq'::regclass);


--
-- TOC entry 4866 (class 2604 OID 16392)
-- Name: municipalities id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipalities ALTER COLUMN id SET DEFAULT nextval('public.municipalities_id_seq'::regclass);


--
-- TOC entry 4867 (class 2604 OID 16400)
-- Name: questions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.questions ALTER COLUMN id SET DEFAULT nextval('public.questions_id_seq'::regclass);


--
-- TOC entry 5029 (class 0 OID 16407)
-- Dependencies: 224
-- Data for Name: assessments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.assessments (id, municipality_id, "timestamp", total_score, answers) FROM stdin;
1	1	2026-05-09 12:16:53.0837	50.55	[[1, 4], [2, 2], [3, 1], [4, 1], [5, 4], [6, 2], [7, 1], [8, 1], [9, 4], [10, 2], [11, 1], [12, 1], [13, 4], [14, 2], [15, 1], [16, 1], [17, 4], [18, 2], [19, 1], [20, 1], [21, 4], [22, 2], [23, 1], [24, 1], [25, 4], [26, 2], [27, 1], [28, 1], [29, 4], [30, 2], [31, 1]]
\.


--
-- TOC entry 5025 (class 0 OID 16389)
-- Dependencies: 220
-- Data for Name: municipalities; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.municipalities (id, name, county, population, contact_email) FROM stdin;
1	Warsaw	Kosciusko	15000	contact@warsaw.in.gov
2	Plymouth	Marshall	10000	contact@plymouth.in.gov
3	Wabash	Wabash	10000	contact@wabash.in.gov
4	Logansport	Cass	18000	contact@logansport.in.gov
5	Other	Unknown	0	N/A
\.


--
-- TOC entry 5027 (class 0 OID 16397)
-- Dependencies: 222
-- Data for Name: questions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.questions (id, category, question_text, weight, gap_description, recommendation) FROM stdin;
1	Asset Management	Does your municipality maintain an up-to-date inventory of all hardware devices connected to your network?	2	No hardware asset inventory in place	Create a spreadsheet listing every device connected to city systems. Include make, model, serial number, and location. Review quarterly.
2	Asset Management	Does your municipality maintain an inventory of all software applications installed on city-owned devices?	2	No software asset inventory in place	Document all software on city devices including version numbers and license expiration dates. Flag any end-of-life software for high-priority replacement.
3	Asset Management	Has your municipality identified which systems handle sensitive data (resident PII, financial records, law enforcement data)?	3	Sensitive data locations not documented	Walk through each department and list every system that stores resident PII, financial records, or law enforcement information. Required for Indiana data breach notification compliance.
4	Governance	Does your municipality have a written cybersecurity policy reviewed or updated in the last two years?	3	No written cybersecurity policy exists	Draft a one- to two-page policy covering acceptable use, password requirements, and incident reporting. Have the city council formally adopt it. CISA offers free templates at cisa.gov.
5	Governance	Is there a designated person (staff or vendor) responsible for cybersecurity decisions in your municipality?	2	No designated cybersecurity responsible person	Assign one person as the go-to for cybersecurity decisions. Can be the IT coordinator, city administrator, or a contracted IT vendor. Document their name and share with all staff.
6	Governance	Has the city council formally approved a cybersecurity budget or allocated resources for cybersecurity improvements?	2	No cybersecurity budget allocated	Present council with a minimal cybersecurity budget proposal. Even $2,000-$5,000/year covers critical tools. Frame it as risk management, not IT spending.
7	Risk Assessment	Has your municipality conducted a formal cybersecurity risk assessment in the last three years?	3	No formal cybersecurity risk assessment conducted	Apply to Indiana Cybertrack for a free seven-week assessment by Purdue University. Contact Indiana IDHS at 800-800-3578.
8	Risk Assessment	Does your municipality have a process to evaluate cybersecurity risks from third-party vendors and service providers?	2	Third-party vendor risk not managed	Review IT vendor contracts and add a clause requiring 72-hour breach notification. IN-ISAC offers free sample contract language.
9	Access Control	Are unique user accounts required for every employee who accesses city systems? (No shared accounts)	3	Shared accounts in use - individual credentials not enforced	Create individual accounts for every staff member. Remove shared accounts like admin or office. This is the foundational prerequisite for all other access controls.
10	Access Control	Is Multi-Factor Authentication (MFA) enabled for email and remote access to city systems?	3	Multi-Factor Authentication not enabled	Enable MFA for Microsoft 365 or Google Workspace (free at account level), VPN, and remote desktop. Most effective control against ransomware. See cisa.gov/mfa for step-by-step guidance.
11	Access Control	Are employee accounts disabled or removed promptly when staff leave the municipality?	2	No formal account offboarding process	Add account deactivation to your HR offboarding checklist. Accounts should be disabled within 24 hours and deleted within 30 days of departure.
12	Access Control	Do employees only have access to the systems and data they need to perform their job?	2	Excessive access privileges granted to staff	Review what systems each employee can access and remove access unrelated to their role. Ensure no standard employee has local administrator rights.
13	Awareness and Training	Do all city employees receive cybersecurity awareness training at least once per year?	3	No annual cybersecurity awareness training program	CISA offers a free training catalog at cisa.gov/cybersecurity-training-exercises. Assign phishing awareness and password hygiene modules. Document completion annually.
14	Awareness and Training	Are employees trained to recognize and report phishing emails?	2	Employees not trained to identify phishing attempts	Deploy CISA free phishing awareness training. Establish a reporting mechanism such as a dedicated phishing@yourcity.gov address. Phishing is the #1 ransomware entry point in local government.
15	Data Security	Are backups of critical city data performed regularly (at least weekly) and stored separately from primary systems?	3	Inadequate or missing data backup process	Set up automated backups following the 3-2-1 rule: 3 copies, 2 different media, 1 offsite or cloud. Backups on the same network are destroyed in ransomware attacks. Cloud backup costs $5-$50/month for most small municipalities.
16	Data Security	Are backup restorations tested at least once per year to confirm data can be recovered?	3	Backups never tested for successful restoration	Schedule an annual restore test: pick a non-critical system and verify full recovery. Document the result and time required. An untested backup provides no guarantee of recovery.
17	Data Security	Is sensitive data encrypted when stored on laptops, USB drives, or portable devices?	2	Sensitive data on portable devices not encrypted	Enable BitLocker (Windows) or FileVault (Mac) on all city laptops - both built in and free. Ensures compliance with Indiana Data Breach Notification Law (IC 24-4.9).
18	Information Protection	Are operating systems and software on city devices kept up to date with security patches?	3	Patch management process is lacking or absent	Enable automatic updates on all devices. Designate the second Tuesday of each month for patching servers. Cross-reference CISA Known Exploited Vulnerabilities at cisa.gov/known-exploited-vulnerabilities-catalog.
19	Information Protection	Does your municipality use antivirus or endpoint protection software on all city-owned devices?	2	Antivirus or endpoint protection not deployed on all devices	MS-ISAC provides free CrowdStrike Falcon EDR to local governments. Apply at cisecurity.org/ms-isac. At minimum ensure Windows Defender is active and updated on all Windows devices.
20	Information Protection	Is there a firewall protecting the boundary between your city network and the internet?	2	No firewall protecting city network perimeter	At minimum enable the built-in firewall on your ISP router. For better protection deploy a managed firewall through an IT vendor. Enroll in free CISA CyHy scanning at cisa.gov/cyber-hygiene-services.
21	Information Protection	Is guest Wi-Fi separated from the internal city network?	2	Public Wi-Fi not isolated from internal city network	Configure a separate SSID for guest Wi-Fi isolated from city systems via VLAN. Typically a free configuration change on existing equipment.
22	Continuous Monitoring	Does your municipality have a way to detect unauthorized access or unusual activity on city systems?	3	No detection capability for unauthorized access or unusual activity	Enable Windows Security Event logging on servers and workstations. Enroll in free CISA CyHy scanning. Enable MS-ISAC free Malicious Domain Blocking (MDBR). Three steps, no cost.
23	Continuous Monitoring	Are security logs reviewed on a regular basis (at least monthly)?	2	Security logs not reviewed regularly	Designate your IT contact to review Windows Event Logs and firewall logs monthly. Focus on failed logins, account lockouts, and unusual outbound connections.
24	Continuous Monitoring	Has your municipality enrolled in CISA free Cyber Hygiene (CyHy) vulnerability scanning service?	2	Not enrolled in free CISA vulnerability scanning	Enroll at cisa.gov/cyber-hygiene-services. CISA scans your public-facing systems weekly and emails a report. Enrollment takes 15 minutes and is free for all Indiana municipalities.
25	Response Planning	Does your municipality have a written Incident Response Plan describing what to do in the event of a cyberattack?	3	No written Incident Response Plan exists	Use the free CISA IRP template to create a one- to two-page plan. Print and store offline - ransomware blocks access to digital-only files. Contact Indiana IDHS at 800-800-3578 for assistance.
26	Response Planning	Has your municipality conducted a tabletop exercise to practice responding to a cyber incident in the last two years?	2	No tabletop exercise or cyber incident drill conducted	Contact CISA Region 5 (312-353-7272) or IN-ISAC for a free facilitated tabletop exercise. CISA also offers ready-to-run packages at cisa.gov that can be completed in two hours.
27	Communications	Does your municipality know who to contact at the state and federal level in the event of a cyberattack?	2	Emergency cybersecurity contacts not identified or documented	Create a printed contact card: Indiana IDHS (800-800-3578), MS-ISAC (866-787-4722), CISA Region 5 (312-353-7272), FBI IC3 (ic3.gov). Post physically - digital records are inaccessible during ransomware attacks.
28	Communications	Does your municipality have cyber liability insurance coverage?	2	No cyber liability insurance in place	Contact your municipal insurance carrier about adding a cyber liability rider. Premiums for small municipalities range $1,500-$5,000/year and cover ransomware, recovery costs, and legal fees.
29	Recovery Planning	Does your municipality have a Continuity of Operations Plan (COOP) or Disaster Recovery Plan that addresses cyber incidents?	3	No Continuity of Operations Plan for cyber incidents	Use the free FEMA COOP template to document how essential services continue when IT is unavailable. Cover manual fallback procedures for water, utilities, 911 dispatch, and payroll.
30	Recovery Planning	Have Recovery Time Objectives (RTOs) been defined for critical city systems?	2	Recovery Time Objectives not defined for critical systems	Document maximum acceptable downtime per system. Examples: 911 dispatch = 0 hours, financial system = 24 hours, email = 4 hours. RTOs drive recovery prioritization and backup strategy.
31	Improvements	After a security incident or near-miss, does your municipality conduct a post-incident review to identify lessons learned?	2	No post-incident review process in place	After any incident - even a clicked phishing link - document what happened, how it was detected, and what should change. A simple one-page summary is sufficient. This is how organizations improve over time.
\.


--
-- TOC entry 5039 (class 0 OID 0)
-- Dependencies: 223
-- Name: assessments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.assessments_id_seq', 1, true);


--
-- TOC entry 5040 (class 0 OID 0)
-- Dependencies: 219
-- Name: municipalities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.municipalities_id_seq', 1, false);


--
-- TOC entry 5041 (class 0 OID 0)
-- Dependencies: 221
-- Name: questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.questions_id_seq', 31, true);


--
-- TOC entry 4875 (class 2606 OID 16416)
-- Name: assessments assessments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_pkey PRIMARY KEY (id);


--
-- TOC entry 4871 (class 2606 OID 16395)
-- Name: municipalities municipalities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipalities
    ADD CONSTRAINT municipalities_pkey PRIMARY KEY (id);


--
-- TOC entry 4873 (class 2606 OID 16405)
-- Name: questions questions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (id);


--
-- TOC entry 4876 (class 2606 OID 16417)
-- Name: assessments assessments_municipality_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_municipality_id_fkey FOREIGN KEY (municipality_id) REFERENCES public.municipalities(id);


-- Completed on 2026-05-09 12:21:38

--
-- PostgreSQL database dump complete
--

\unrestrict YjjIjx15SSb5POyQfjgFxdGsdiJ1wDPMgjq522GQaM2BkLeRxzyIom5x9EO0uvX

