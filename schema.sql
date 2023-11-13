
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    fullname TEXT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    isadmin INTEGER DEFAULT 0,
    created TIMESTAMP NOT NULL DEFAULT 
    CURRENT_TIMESTAMP
);

-- Create the 'level' table if it doesn't exist
CREATE TABLE IF NOT EXISTS level (
    level_id INTEGER PRIMARY KEY,
    level_name VARCHAR(255) NOT NULL
);

-- Insert levels from level 1 to level 4 if the table exists
-- INSERT INTO level (level_name) VALUES
--     ('Level 1'),
--     ('Level 2'),
--     ('Level 3'),
--     ('Level 4'),
--     ('Level 5');

-- Create the 'category' table if it doesn't exist
CREATE TABLE IF NOT EXISTS category (
    category_id INTEGER PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL
);

-- Insert top 5 medical imaging technique names into the 'category' table
-- INSERT INTO category (category_name)
-- VALUES
--     ('Radiography'),
--     ('Computed Tomography (CT)'),
--     ('Magnetic Resonance Imaging (MRI)'),
--     ('Ultrasound'),
--     ('Mammography');

-- Create the 'tutorials' table if it doesn't exist
CREATE TABLE IF NOT EXISTS tutorials (
    tutorial_id INTEGER PRIMARY KEY,
    logo VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    details TEXT,
    content_type VARCHAR(50),
    level_id INT,
    category_id INT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY,
    question TEXT NOT NULL,
    option1 VARCHAR(255) NULL,
    option2 VARCHAR(255) NULL,
    option3 VARCHAR(255) NULL,
    option4 VARCHAR(255) NULL,
    answer VARCHAR(255) NULL,
    level VARCHAR(255) NULL,
    category VARCHAR(255) NULL,
    created_by VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_answers (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    question_id INTEGER,
    user_answer VARCHAR(255),
    quiz_id VARCHAR(255),
    mark_count INTEGER
);

CREATE TABLE IF NOT EXISTS quiz_list (
    id INTEGER PRIMARY KEY,
    quiz_id VARCHAR(255),
    user_id INTEGER,
    total_mark INTEGER,
    category VARCHAR(255),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
