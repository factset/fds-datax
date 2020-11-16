 SET NOCOUNT ON;
IF OBJECT_ID('tempdb..#listofIDS') IS NOT NULL
    DROP TABLE #listofIDS;
CREATE TABLE #listofIDS(id NVARCHAR(50), PRIMARY KEY(id));
{insert_statements}
SELECT ig.factset_entity_id,
       ent.entity_proper_name,
       cm.country_desc AS country,
       rm.region_desc AS region,
       rs.l1_id AS rbics_l1_id ,
       rs.l1_name AS rbics_l1,
       rs.l2_id AS rbics_l2_id,
       rs.l2_name AS rbics_l2,
       rs.l3_id AS rbics_l3_id,
       rs.l3_name AS rbics_l3,
       rs.l4_id AS rbics_l4_id,
       rs.l4_name AS rbics_l4
FROM   #listofIDS AS id
JOIN rbics_v1.rbics_ent_indgrp_curr AS ig
  ON id.id = ig.factset_entity_id
JOIN rbics_v1.rbics_structure_curr AS rs
  ON rs.l4_id = ig.l4_id
JOIN sym_v1.sym_entity AS ent
  ON ent.factset_entity_id = ig.factset_entity_id
JOIN ref_v2.country_map AS cm
  ON cm.iso_country = ent.iso_country
JOIN ref_v2.region_map AS rm
  ON rm.region_code = cm.region_code;