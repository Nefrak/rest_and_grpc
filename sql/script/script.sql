DROP TABLE IF EXISTS domain, domain_flag;
/*DROP TYPE IF EXISTS VALID_FLAGS;*/

CREATE TYPE VALID_FLAGS AS ENUM ('EXPIRED', 'OUTZONE', 'DELETE_CANDIDATE');

/*--Functions--*/
CREATE OR REPLACE FUNCTION check_domain_registration(d_name varchar(1000), r_time timestamp) 
  RETURNS boolean AS
$$
DECLARE
  i timestamp;
BEGIN
  SELECT MAX(domain_unreg_time) INTO i FROM domain WHERE domain_name = d_name;
  IF (i <= r_time or i IS NULL) THEN
    RETURN true;
  END IF;

  RETURN false;  
END
$$ LANGUAGE plpgsql;

/*little debetable, since it can be also done with exceptions (it just wont update value)*/
CREATE OR REPLACE FUNCTION check_flag_update()
  RETURNS trigger AS
$BODY$
    BEGIN
        NEW.df_id := OLD.df_id;
        NEW.df_domain_id := OLD.df_domain_id;
        NEW.df_valid_flag := OLD.df_valid_flag;
        NEW.df_reg_time := OLD.df_reg_time;
        
        IF OLD.df_unreg_time <> 'infinity' OR NEW.df_unreg_time < CURRENT_TIMESTAMP THEN
            NEW.df_unreg_time := OLD.df_unreg_time;
        END IF;
        RETURN NEW;
    END;
$BODY$
  LANGUAGE plpgsql;

/*--Tables--*/
CREATE TABLE domain (
   domain_id INT GENERATED ALWAYS AS IDENTITY,
   domain_name VARCHAR(1000),
   domain_reg_time TIMESTAMP NOT NULL,
   domain_unreg_time TIMESTAMP NOT NULL,
   PRIMARY KEY(domain_id)
);

CREATE TABLE domain_flag (
   df_id INT GENERATED ALWAYS AS IDENTITY,
   df_domain_id INT NOT NULL,
   df_valid_flag VALID_FLAGS,
   df_reg_time TIMESTAMP NOT NULL,
   df_unreg_time TIMESTAMP DEFAULT 'infinity' NOT NULL,
   PRIMARY KEY(df_id),
   CONSTRAINT reference_domain FOREIGN KEY(df_domain_id) REFERENCES domain(domain_id)
);

/*--Triggers and constraints--*/
CREATE TRIGGER prevent_update BEFORE UPDATE ON domain_flag FOR EACH ROW EXECUTE PROCEDURE check_flag_update();

ALTER TABLE domain ADD CONSTRAINT no_overlap CHECK (check_domain_registration(domain_name, domain_reg_time));

/*Commented block with test values*/
/*INSERT INTO domain (domain_name, domain_reg_time, domain_unreg_time) 
VALUES('https://www.seznam.cz/', '2021-02-14 11:22:33.000', '2021-02-15 11:22:33.000');
INSERT INTO domain (domain_name, domain_reg_time, domain_unreg_time) 
VALUES('https://www.seznam.cz/', '2021-02-15 11:22:33.000', '2025-02-15 11:22:33.000');
INSERT INTO domain (domain_name, domain_reg_time, domain_unreg_time) 
VALUES('https://www.youtube.com/', '2021-02-15 10:22:33.000', '2021-02-15 11:22:33.000');
INSERT INTO domain (domain_name, domain_reg_time, domain_unreg_time) 
VALUES('https://www.some.cz/', '2021-02-15 11:22:33.000', '2025-02-15 11:22:33.000');
INSERT INTO domain_flag (df_domain_id, df_valid_flag, df_reg_time, df_unreg_time) 
VALUES(2, 'EXPIRED', '2021-02-14 11:22:33.000', '2021-02-15 11:22:33.000');
INSERT INTO domain_flag (df_domain_id, df_valid_flag, df_reg_time) 
VALUES(2, 'EXPIRED', '2021-02-16 11:22:33.000');
INSERT INTO domain_flag (df_domain_id, df_valid_flag, df_reg_time) 
VALUES(3, 'OUTZONE', '2021-02-16 11:22:33.000');
INSERT INTO domain_flag (df_domain_id, df_valid_flag, df_reg_time) 
VALUES(4, 'DELETE_CANDIDATE', '2021-02-16 11:22:33.000');
INSERT INTO domain_flag (df_domain_id, df_valid_flag, df_reg_time) 
VALUES(4, 'EXPIRED', '2025-02-16 11:22:33.000');
INSERT INTO domain_flag (df_domain_id, df_valid_flag, df_reg_time, df_unreg_time) 
VALUES(4, 'EXPIRED', '2019-02-16 11:22:33.000', '2020-02-16 11:22:33.000');

UPDATE domain_flag SET df_unreg_time = '2023-02-16 11:22:33.000' WHERE df_id = 2;
UPDATE domain_flag SET df_unreg_time = '2024-02-16 11:22:33.000' WHERE df_id = 2;*/

/*--Selects--*/
SELECT domain_name FROM domain LEFT OUTER JOIN domain_flag ON domain_id = df_domain_id
WHERE domain_reg_time < CURRENT_TIMESTAMP AND domain_unreg_time > CURRENT_TIMESTAMP 
AND (df_valid_flag IS NULL OR df_valid_flag <> 'EXPIRED' 
OR (df_valid_flag = 'EXPIRED' AND df_reg_time > CURRENT_TIMESTAMP AND df_unreg_time < CURRENT_TIMESTAMP));

SELECT domain_name FROM domain LEFT OUTER JOIN domain_flag ON domain_id = df_domain_id
WHERE (df_valid_flag = 'EXPIRED' OR df_valid_flag = 'OUTZONE') AND df_unreg_time < CURRENT_TIMESTAMP;