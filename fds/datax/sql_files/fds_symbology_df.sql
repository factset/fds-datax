SET NOCOUNT ON;
IF OBJECT_ID('tempdb..#listofIDS') IS NOT NULL
    DROP TABLE #listofIDS;
CREATE TABLE #listofIDS(id NVARCHAR(50), PRIMARY KEY(id));
{insert_statements}
SELECT market_id AS ref_id,
       a.fsym_id,
       cov.proper_name,
       se.factset_entity_id,
       se.start_date AS entity_start_date,
	   se.end_date AS entity_end_date
FROM   #listofIDS AS ids
JOIN
(
    SELECT fsym_id,
           cusip AS market_id,
           start_date,
           end_date
    FROM     sym_v1.sym_cusip_hist
    UNION
    SELECT fsym_id,
           isin AS market_id,
           start_date,
           end_date
    FROM     sym_v1.sym_isin_hist
    UNION
    SELECT fsym_id,
           sedol AS market_id,
           start_date,
           end_date
    FROM     sym_v1.sym_sedol_hist
) AS a
  ON a.market_id = ids.id
JOIN sym_v1.sym_coverage AS cov
  ON cov.fsym_id = a.fsym_id
JOIN sym_v1.sym_coverage AS cov2
  ON cov2.fsym_id = cov.fsym_security_id
JOIN ff_v3.ff_sec_entity_hist AS se
  ON se.fsym_id = cov.fsym_security_id;
