CREATE TABLE domain (
   domain_id    NUMERIC       NOT NULL,
   domain_name  VARCHAR(1000) NOT NULL,
   reg_time     DATE    NOT NULL,
   unreg_time   DATE,
   CONSTRAINT domain_pk PRIMARY KEY (domain_id)
);