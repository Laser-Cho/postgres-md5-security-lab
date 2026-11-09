-- ========================================================
-- 01-init-dummy-data.sql
-- MD5 Authentication & Dummy Data Initialization
-- ========================================================

-- Ensure password encryption is set to md5 for newly created roles
SET password_encryption = 'md5';

-- 1. Create Application Users with MD5 passwords
CREATE USER app_user WITH PASSWORD 'Company2026!';
CREATE USER auditor WITH PASSWORD 'SecurityAudit123';

-- 2. Create Confidential Data Tables
CREATE TABLE IF NOT EXISTS company_confidential (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    secret_code VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    classified_level VARCHAR(20) NOT NULL
);

INSERT INTO company_confidential (category, secret_code, description, classified_level) VALUES
('R&D', 'PROJ-QUANTUM-9921', 'Next-Gen AI Autonomous Trading Core Engine Specs', 'TOP SECRET'),
('Finance', 'CORP-BANK-ACCOUNTS', 'Offshore Escrow & Reserve Account Routing Numbers', 'CONFIDENTIAL'),
('HR', 'EXEC-SALARY-TABLE-2026', 'Executive Board Compensation and Bonus Multipliers', 'SECRET'),
('Security', 'VPN-GATEWAY-MASTER-KEY', 'Global Edge VPN Fallback Pre-Shared Key', 'TOP SECRET');

-- 3. Create Employee Records
CREATE TABLE IF NOT EXISTS employee_records (
    emp_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    salary INT NOT NULL
);

INSERT INTO employee_records (name, department, email, salary) VALUES
('홍길동', '보안팀', 'gildong.hong@company.internal', 75000000),
('김철수', '인프라팀', 'cheolsoo.kim@company.internal', 82000000),
('이영희', 'DB운영팀', 'younghee.lee@company.internal', 91000000),
('박대표', '경영지원', 'ceo@company.internal', 250000000);

-- 4. Grant Permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO auditor;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
