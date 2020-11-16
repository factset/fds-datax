 SET NOCOUNT ON;
IF OBJECT_ID('tempdb..#listofIDS') IS NOT NULL
    DROP TABLE #listofIDS;
CREATE TABLE #listofIDS(id NVARCHAR(50), PRIMARY KEY(id));
{insert_statements}
WITH   splits
     AS (SELECT fsym_id,
                EXP(SUM(LOG(p_split_factor)) OVER(PARTITION BY fsym_id
                ORDER BY p_split_date DESC)) AS cum_split_factor,
                p_split_date,
                ISNULL(LAG(p_split_date, 1) OVER(PARTITION BY fsym_id
                ORDER BY p_split_date), '1900-01-01') AS p_split_end_date,
                p_split_factor
         FROM   fp_v2.fp_basic_splits AS s
         WHERE  s.fsym_id IN
         (
             SELECT id
             FROM   #listofIDS
         )),
     spin
     AS (SELECT    div.fsym_id,
                   div.p_divs_exdate,
                   ISNULL(LAG(p_divs_exdate, 1) OVER(PARTITION BY div.fsym_id
                   ORDER BY p_divs_exdate), '1900-01-01') AS
                   p_divs_exdate_end_date,
                   EXP(SUM(LOG(CASE
                                   WHEN p_price - p_divs_pd <= 0
                                   THEN 1
                                   ELSE(p_price - p_divs_pd) / p_price
                               END)) OVER(PARTITION BY div.fsym_id
                   ORDER BY div.p_divs_exdate DESC)) AS cum_spin_factor
         FROM
         (
             SELECT div.fsym_id,
                    div.p_divs_exdate,
                    SUM(div.p_divs_pd) AS p_divs_pd
             FROM   fp_v2.fp_basic_dividends AS div
             WHERE  div.p_divs_s_pd = 1
                    AND div.fsym_id IN
             (
                 SELECT id
                 FROM   #listofIDS
             )
             GROUP BY div.fsym_id,
                      div.p_divs_exdate
         ) AS div
         JOIN fp_v2.fp_basic_prices AS p
           ON p.fsym_id = div.fsym_id
              AND p.p_date =
         (
             SELECT MAX(p_date)
             FROM   fp_v2.fp_basic_prices AS p2
             WHERE  p2.fsym_id = p.fsym_id
                    AND p2.p_date < div.p_divs_exdate
         )),
     adjdates
     AS (SELECT ISNULL(sl.fsym_id, sp.fsym_id) AS fsym_id,
                ISNULL(p_split_date, p_divs_exdate) AS p_date
         FROM   splits AS sl
         FULL OUTER JOIN spin AS sp
           ON sp.fsym_id = sl.fsym_id
              AND sp.p_divs_exdate = sl.p_split_date),
     adjfactors
     AS (SELECT ad.p_date,
                ad.fsym_id,
                ISNULL(LAG(ad.p_date) OVER(PARTITION BY ad.fsym_id
                ORDER BY ad.p_date ASC), '1900-01-01') AS p_end_date,
                CONVERT(FLOAT, sp.cum_spin_factor) AS cum_spin_factor,
                CONVERT(FLOAT, ss.cum_split_factor) AS cum_split_factor
         FROM   adjdates AS ad
         LEFT JOIN spin AS sp
           ON sp.fsym_id = ad.fsym_id
              AND ad.p_date > sp.p_divs_exdate_end_date
              AND ad.p_date <= sp.p_divs_exdate
         LEFT JOIN splits AS ss
           ON ss.fsym_id = ad.fsym_id
              AND ad.p_date > ss.p_split_end_date
              AND ad.p_date <= ss.p_split_date)
     SELECT fsym_id,
            p_date AS price_date,
            p_end_date AS price_end_date,
            cum_spin_factor,
            cum_split_factor
     FROM   adjfactors
     ORDER BY p_date;