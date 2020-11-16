        	SET NOCOUNT ON;
IF OBJECT_ID('tempdb..#listofIDS') IS NOT NULL
    DROP TABLE #listofIDS;
CREATE TABLE #listofIDS(id NVARCHAR(50), PRIMARY KEY(id));
{insert_statements}
SELECT cov.fsym_id AS ref_id, 
       cov.proper_name, 
       se.factset_entity_id, 
       se.start_date AS entity_start_date,
	   se.end_date AS entity_end_date
FROM   #listofIDS AS ids
JOIN sym_v1.sym_coverage AS cov
  ON cov.fsym_id = ids.id
JOIN sym_v1.sym_coverage AS cov2
  ON cov2.fsym_id = cov.fsym_security_id
JOIN own_v5.own_sec_entity_hist AS se
  ON se.fsym_id = cov.fsym_security_id