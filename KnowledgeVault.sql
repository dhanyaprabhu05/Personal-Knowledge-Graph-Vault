DROP DATABASE IF EXISTS KnowledgeVault1; 
CREATE DATABASE KnowledgeVault1;
USE KnowledgeVault1;

-- -------------------------
-- 1) Core tables
-- -------------------------
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    role VARCHAR(50)
) ENGINE=InnoDB;

CREATE TABLE Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    concept_count INT DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE Concepts (
    entity_id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50),
    title VARCHAR(150),
    created_on DATE,
    category_id INT,
    user_id INT,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Notes references entity_id (matches app.py usage)
CREATE TABLE Notes (
    note_id INT AUTO_INCREMENT PRIMARY KEY,
    entity_id INT,
    body TEXT,
    created_on DATE,
    FOREIGN KEY (entity_id) REFERENCES Concepts(entity_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tasks references entity_id
CREATE TABLE Tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    entity_id INT,
    description TEXT,
    due_on DATE,
    status VARCHAR(20),
    remind_on DATE,
    FOREIGN KEY (entity_id) REFERENCES Concepts(entity_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tags (generic)
CREATE TABLE Tags (
    tag_id INT AUTO_INCREMENT PRIMARY KEY,
    tag VARCHAR(100),
    role VARCHAR(50)
) ENGINE=InnoDB;

-- Junction table for tags
CREATE TABLE Concept_Tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity_id INT,
    tag_id INT,
    FOREIGN KEY (entity_id) REFERENCES Concepts(entity_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES Tags(tag_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Attachments with entity_id FK
CREATE TABLE Attachments (
    attachment_id INT AUTO_INCREMENT PRIMARY KEY,
    entity_id INT,
    file_path VARCHAR(255),
    file_type VARCHAR(50),
    FOREIGN KEY (entity_id) REFERENCES Concepts(entity_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Collaborators uses column concept_id (matches your app inserts)
CREATE TABLE Collaborators (
    collab_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    concept_id INT,
    role VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES Concepts(entity_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Links linking concepts
CREATE TABLE Links (
    link_id INT AUTO_INCREMENT PRIMARY KEY,
    src_concept_id INT,
    dst_concept_id INT,
    relation_type VARCHAR(100),
    FOREIGN KEY (src_concept_id) REFERENCES Concepts(entity_id) ON DELETE CASCADE,
    FOREIGN KEY (dst_concept_id) REFERENCES Concepts(entity_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Small trigger-log table so GUI can show trigger activity
CREATE TABLE Trigger_Log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    log_table VARCHAR(64),
    log_action VARCHAR(64),
    log_info VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


USE KnowledgeVault1;
-- 2) Sample data (so GUI has something)
INSERT INTO Users (name, role) VALUES
('Alice','Student'), ('Dhanya','Student'), ('Ananya','Researcher'), ('Ravi','Professor');

INSERT INTO Categories (name, description) VALUES
('Research Topics','Papers and ideas'), ('Projects','Course projects');

INSERT INTO Concepts (type, title, created_on, category_id, user_id) VALUES
('Idea','Federated Learning','2025-09-10', 1, 1),
('Paper','Membership inference attacks','2025-09-12', 1, 2),
('Project','Anonymization of Medical Data','2025-09-15', 2, 3);

INSERT INTO Notes (entity_id, body, created_on) VALUES
(1, 'Initial idea notes for Federated Learning', '2025-09-11');

INSERT INTO Tasks (entity_id, description, due_on, status, remind_on) VALUES
(1, 'Write FL report', '2025-09-20', 'Pending', '2025-09-18'),
(2, 'Reproduce MIA experiment', '2025-09-25', 'Pending', '2025-09-20');

INSERT INTO Tags (tag, role) VALUES
('AI','Primary'), ('Privacy','Topic'), ('Security','Topic');

INSERT INTO Concept_Tags (entity_id, tag_id) VALUES
(1,1),(2,2);

INSERT INTO Attachments (entity_id, file_path, file_type) VALUES
(1,'/files/fl_notes.pdf','application/pdf');

INSERT INTO Collaborators (user_id, concept_id, role) VALUES
(1,1,'Owner'), (2,2,'Contributor');

INSERT INTO Links (src_concept_id, dst_concept_id, relation_type) VALUES
(2,1,'related to');

-- 3) Triggers (3 triggers)
/* Trigger list:
   trg_after_task_update  -> logs updates; if status becomes Completed, auto-create a Note and log it
   trg_after_concept_insert -> increments category concept_count and logs
   trg_after_concept_delete -> decrements category concept_count and logs
*/

DROP TRIGGER IF EXISTS trg_after_task_update;
DELIMITER $$
CREATE TRIGGER trg_after_task_update
AFTER UPDATE ON Tasks
FOR EACH ROW
BEGIN
    -- log every task update
    INSERT INTO Trigger_Log (log_table, log_action, log_info)
    VALUES ('Tasks', CONCAT('UPDATE status=', NEW.status), CONCAT('task_id=', NEW.task_id));

    -- if moved to Completed, create a note (automation) and log it
    IF NEW.status = 'Completed' AND OLD.status <> 'Completed' THEN
        INSERT INTO Notes (entity_id, body, created_on)
        VALUES (NEW.entity_id,
                CONCAT('Task \"', NEW.description, '\" completed on ', DATE_FORMAT(CURDATE(), '%Y-%m-%d')),
                CURDATE());
        INSERT INTO Trigger_Log (log_table, log_action, log_info)
        VALUES ('Notes', 'AUTO_INSERT_FROM_TASK', CONCAT('task_id=', NEW.task_id, ';entity_id=', NEW.entity_id));
    END IF;
END $$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_after_concept_insert;
DELIMITER $$
CREATE TRIGGER trg_after_concept_insert
AFTER INSERT ON Concepts
FOR EACH ROW
BEGIN
    IF NEW.category_id IS NOT NULL THEN
        UPDATE Categories SET concept_count = IFNULL(concept_count,0) + 1 WHERE category_id = NEW.category_id;
        INSERT INTO Trigger_Log (log_table, log_action, log_info)
        VALUES ('Categories','INCREMENT_CONCEPT_COUNT', CONCAT('category_id=', NEW.category_id));
    END IF;
END $$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_after_concept_delete;
DELIMITER $$
CREATE TRIGGER trg_after_concept_delete
AFTER DELETE ON Concepts
FOR EACH ROW
BEGIN
    IF OLD.category_id IS NOT NULL THEN
        UPDATE Categories SET concept_count = GREATEST(IFNULL(concept_count,0)-1,0) WHERE category_id = OLD.category_id;
        INSERT INTO Trigger_Log (log_table, log_action, log_info)
        VALUES ('Categories','DECREMENT_CONCEPT_COUNT', CONCAT('category_id=', OLD.category_id));
    END IF;
END $$
DELIMITER ;

-- 4) Stored Procedures / Function / View
/* Procedures:
   - GetConceptDetails(entity_id) : returns notes, tasks, tags for a concept (multiple result sets)
   - GetLinkedConcepts(entity_id) : returns outgoing links
   - MarkTaskCompleted(task_id) : marks a task completed (will fire task trigger)
   - Function: DaysRemaining(task_id) -> int
   - View: Concept_Summary (counts) for GUI summary
*/

DROP PROCEDURE IF EXISTS GetConceptDetails;
DELIMITER $$
CREATE PROCEDURE GetConceptDetails(IN in_entity_id INT)
BEGIN
    SELECT note_id, body, created_on FROM Notes WHERE entity_id = in_entity_id ORDER BY created_on DESC;
    SELECT task_id, description, due_on, status, remind_on FROM Tasks WHERE entity_id = in_entity_id ORDER BY due_on DESC;
    SELECT t.tag_id, t.tag, t.role
    FROM Concept_Tags ct
    JOIN Tags t ON ct.tag_id = t.tag_id
    WHERE ct.entity_id = in_entity_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS GetLinkedConcepts;
DELIMITER $$
CREATE PROCEDURE GetLinkedConcepts(IN in_entity_id INT)
BEGIN
    SELECT l.link_id, c2.entity_id AS related_entity_id, c2.title AS related_title, l.relation_type
    FROM Links l
    JOIN Concepts c2 ON l.dst_concept_id = c2.entity_id
    WHERE l.src_concept_id = in_entity_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS MarkTaskCompleted;
DELIMITER $$
CREATE PROCEDURE MarkTaskCompleted(IN in_task_id INT)
BEGIN
    UPDATE Tasks SET status = 'Completed' WHERE task_id = in_task_id;
    -- trigger will auto-create note + log
END $$
DELIMITER ;

USE KnowledgeVault1;
DROP PROCEDURE IF EXISTS CountNotesPerConcept;
DELIMITER $$
CREATE PROCEDURE CountNotesPerConcept()
BEGIN
    SELECT 
        c.entity_id,
        c.title,
        COUNT(n.note_id) AS note_count
    FROM Concepts c
    LEFT JOIN Notes n ON c.entity_id = n.entity_id
    GROUP BY c.entity_id, c.title
    ORDER BY note_count DESC;
END $$
DELIMITER ;

DROP FUNCTION IF EXISTS DaysRemaining;
DELIMITER $$
CREATE FUNCTION DaysRemaining(in_task_id INT) RETURNS INT DETERMINISTIC
BEGIN
    DECLARE days_left INT;
    SELECT DATEDIFF(due_on, CURDATE()) INTO days_left FROM Tasks WHERE task_id = in_task_id;
    RETURN days_left;
END $$
DELIMITER ;

-- View summarizing concept counts for GUI
CREATE OR REPLACE VIEW Concept_Summary AS
SELECT
  c.entity_id,
  c.title,
  c.type,
  c.created_on,
  cat.name AS category,
  u.name AS owner,
  COALESCE(n.note_count,0) AS notes_count,
  COALESCE(t.task_count,0) AS tasks_count
FROM Concepts c
LEFT JOIN Categories cat ON c.category_id = cat.category_id
LEFT JOIN Users u ON c.user_id = u.user_id
LEFT JOIN ( SELECT entity_id, COUNT(*) AS note_count FROM Notes GROUP BY entity_id ) n ON c.entity_id = n.entity_id
LEFT JOIN ( SELECT entity_id, COUNT(*) AS task_count FROM Tasks GROUP BY entity_id ) t ON c.entity_id = t.entity_id;

-- 5) Example queries you can hook to GUI (join / nested / aggregate)

-- 1) JOIN query (notes + tasks for a concept)
-- Example to show in GUI: notes with matching tasks (left join)
SELECT n.note_id, n.entity_id, n.body, t.task_id, t.description, t.status
FROM Notes n
LEFT JOIN Tasks t ON n.entity_id = t.entity_id
WHERE n.entity_id = 1;

-- 2) Nested query: concepts having more notes than average
SELECT entity_id, title, notes_count FROM (
    SELECT c.entity_id, c.title, COUNT(n.note_id) AS notes_count
    FROM Concepts c LEFT JOIN Notes n ON c.entity_id = n.entity_id
    GROUP BY c.entity_id
) AS sub
WHERE notes_count > (SELECT AVG(note_count) FROM (SELECT COUNT(*) AS note_count FROM Notes GROUP BY entity_id) AS tmp);

-- 3) Aggregate query: number of notes per concept
SELECT c.entity_id, c.title, COUNT(n.note_id) AS notes_count
FROM Concepts c LEFT JOIN Notes n ON c.entity_id = n.entity_id
GROUP BY c.entity_id, c.title
ORDER BY notes_count DESC;

-- 6) Quick test/demo steps (run in this order to show triggers/procedures)
-- 1) Show triggers
SHOW TRIGGERS;

-- 2) Show content
SELECT * FROM Concepts;
SELECT * FROM Notes;
SELECT * FROM Tasks;
SELECT * FROM Trigger_Log ORDER BY created_at DESC LIMIT 10;

-- 3) Demonstrate trigger: reset task 1 to Pending and mark Completed
UPDATE Tasks SET status = 'Pending' WHERE task_id = 1;
UPDATE Tasks SET status = 'Completed' WHERE task_id = 1;

-- 4) Check results: a new note should be auto-created and trigger_log updated
SELECT * FROM Notes WHERE entity_id = 1 ORDER BY created_on DESC;
SELECT * FROM Trigger_Log ORDER BY created_at DESC LIMIT 10;

-- 5) Call stored procedure (GetConceptDetails)
CALL GetConceptDetails(1);

-- 6) Call MarkTaskCompleted (which fires trigger)
CALL MarkTaskCompleted(2);
SELECT * FROM Notes WHERE entity_id = 2 ORDER BY created_on DESC;

-- 7) Test DaysRemaining function
SELECT task_id, description, DaysRemaining(task_id) AS days_left FROM Tasks;

-- 8) Show view
SELECT * FROM Concept_Summary;
