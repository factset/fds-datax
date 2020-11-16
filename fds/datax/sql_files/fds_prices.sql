
SET NOCOUNT ON;
DECLARE @sd DATE= '{sd}';
DECLARE @ed DATE= '{ed}';
IF OBJECT_ID('tempdb..#listofIDS') IS NOT NULL
    DROP TABLE #listofIDS;
CREATE TABLE #listofIDS
(
    id NVARCHAR(50),
    PRIMARY KEY(id)
);
{insert_statements}
WITH
    prices
    AS
    (
        SELECT cov.fsym_id,
            cal.ref_date AS p_date,
            cal.day_of_week,
            p.currency,
            p.p_price,
            CASE
                       WHEN p.p_date = cal.ref_date
                       THEN p.p_price_open
                       ELSE 0
                   END AS p_price_open,
            CASE
                       WHEN p.p_date = cal.ref_date
                       THEN p.p_price_high
                       ELSE 0
                   END AS p_price_high,
            CASE
                       WHEN p.p_date = cal.ref_date
                       THEN p.p_price_low
                       ELSE 0
                   END AS p_price_low,
            CASE
                       WHEN p.p_date = cal.ref_date
                       THEN p.p_volume
                       ELSE 0
                   END AS p_volume
        FROM ref_v2.ref_calendar_dates AS cal
         CROSS JOIN fp_v2.fp_sec_coverage AS cov
            -- Limit to last trade date
            JOIN
            (
             SELECT fsym_id,
                MAX(p_date) AS last_trade_date,
                MIN(p_date) AS first_trade_date
            FROM fp_v2.fp_basic_prices AS fp2
            GROUP BY fsym_id
         ) AS fp_max
            ON fp_max.fsym_id = cov.fsym_id
                AND cal.ref_date <= fp_max.last_trade_date
                AND cal.ref_date >= fp_max.first_trade_date
            --Convert to 7 Day calendar
            LEFT JOIN fp_v2.fp_basic_prices AS p
            ON fp_max.fsym_id = p.fsym_id
                AND p.p_date =
         (
             SELECT MAX(p_date)
                FROM fp_v2.fp_basic_prices AS fp2
                WHERE  fp2.fsym_id = p.fsym_id
                    AND fp2.p_date <= cal.ref_date
         )
        WHERE cal.ref_date >= @sd
            AND cal.ref_date <= @ed
            AND cov.fsym_id IN
         (
             SELECT id
            FROM #listofIDS
         )
    ),
    splits
    AS
    (
        SELECT fsym_id,
            EXP(SUM(LOG(p_split_factor)) OVER(PARTITION BY fsym_id
                ORDER BY p_split_date DESC)) AS cum_split_factor,
            p_split_date,
            ISNULL(LAG(p_split_date, 1) OVER(PARTITION BY fsym_id
                ORDER BY p_split_date), '1900-01-01') AS p_split_end_date,
            p_split_factor
        FROM fp_v2.fp_basic_splits AS s
        WHERE  s.fsym_id IN
         (
             SELECT id
        FROM #listofIDS
         )
    ),
    spin
    AS
    (
        SELECT div.fsym_id,
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
            FROM fp_v2.fp_basic_dividends AS div
            WHERE  div.p_divs_s_pd = 1
                AND div.fsym_id IN
             (
                 SELECT id
                FROM #listofIDS
             )
            GROUP BY div.fsym_id,
                      div.p_divs_exdate
         ) AS div
            JOIN fp_v2.fp_basic_prices AS p
            ON p.fsym_id = div.fsym_id
                AND p.p_date =
         (
             SELECT MAX(p_date)
                FROM fp_v2.fp_basic_prices AS p2
                WHERE  p2.fsym_id = p.fsym_id
                    AND p2.p_date < div.p_divs_exdate
         )
    ),
    adjdates
    AS
    (
        SELECT ISNULL(sl.fsym_id, sp.fsym_id) AS fsym_id,
            ISNULL(p_split_date, p_divs_exdate) AS p_date
        FROM splits AS sl
            FULL OUTER JOIN spin AS sp
            ON sp.fsym_id = sl.fsym_id
                AND sp.p_divs_exdate = sl.p_split_date
    ),
    adjfactors
    AS
    (
        SELECT ad.p_date,
            ad.fsym_id,
            ISNULL(LAG(ad.p_date) OVER(PARTITION BY ad.fsym_id
                ORDER BY ad.p_date ASC), '1900-01-01') AS p_end_date,
            CONVERT(FLOAT, sp.cum_spin_factor) AS cum_spin_factor,
            CONVERT(FLOAT, ss.cum_split_factor) AS cum_split_factor
        FROM adjdates AS ad
            LEFT JOIN spin AS sp
            ON sp.fsym_id = ad.fsym_id
                AND ad.p_date > sp.p_divs_exdate_end_date
                AND ad.p_date <= sp.p_divs_exdate
            LEFT JOIN splits AS ss
            ON ss.fsym_id = ad.fsym_id
                AND ad.p_date > ss.p_split_end_date
                AND ad.p_date <= ss.p_split_date
    ),
    shares_out
    AS
    (
        SELECT shs_out.fsym_id,
            shs_out.p_date,
            ISNULL(LEAD(shs_out.p_date) OVER(PARTITION BY shs_out.
                   fsym_id
                   ORDER BY shs_out.p_date), '3001-01-01') AS
                   p_shs_out_end_date,
            shs_out.p_com_shs_out
        FROM
            (
                                                                                             SELECT s.fsym_id,
                    cov.p_first_date AS p_date,
                    s.p_com_shs_out
                FROM fp_v2.fp_sec_coverage AS cov
                    JOIN fp_v2.fp_basic_shares_current AS s
                    ON cov.fsym_id = s.fsym_id
                WHERE   cov.fsym_id NOT IN
             (
                 SELECT DISTINCT
                        FSYM_ID
                    FROM fp_v2.fp_basic_shares_hist
             )
                    AND p_com_shs_out <> 0
                    AND cov.fsym_id IN
             (
                 SELECT id
                    FROM #listofIDS
             )
            UNION
                SELECT sh.fsym_id,
                    sh.p_date,
                    sh.p_com_shs_out
                FROM fp_v2.fp_basic_shares_hist AS sh
                WHERE  sh.fsym_id IN
             (
                 SELECT id
                FROM #listofIDS
             )
         ) AS shs_out
    )
SELECT p.fsym_id,
    p.p_date AS price_date,
    p.currency,
    shs.p_com_shs_out AS unadj_shares_outstanding,
    CONVERT(FLOAT, shs.p_com_shs_out / ISNULL(cum_split_factor, 1)) AS
            split_adj_shares_outstanding,
    shs.p_com_shs_out * p.p_price AS market_value,
    p.p_volume AS unadj_volume,
    p.p_volume / ISNULL(cum_split_factor, 1) AS split_adj_volume,
    p.p_price AS unadj_price_close,
    p.p_price_high AS unadj_price_high,
    p.p_price_low AS unadj_price_low,
    p.p_price_open AS unadj_price_open,
    CONVERT(FLOAT, p.p_price * ISNULL(cum_split_factor, 1)) AS
            split_adj_price_close,
    CONVERT(FLOAT, p.p_price_high * ISNULL(cum_split_factor, 1)) AS
            split_adj_price_high,
    CONVERT(FLOAT, p.p_price_low * ISNULL(cum_split_factor, 1)) AS
            split_adj_price_low,
    CONVERT(FLOAT, p.p_price_open * ISNULL(cum_split_factor, 1)) AS
            split_adj_price_open,
    CONVERT(FLOAT, p.p_price * ISNULL(cum_split_factor, 1) * ISNULL(
            cum_spin_factor, 1)) AS split_spin_adj_price_close,
    CONVERT(FLOAT, p.p_price_high * ISNULL(cum_split_factor, 1) *
            ISNULL(cum_spin_factor, 1)) AS split_spin_adj_price_high,
    CONVERT(FLOAT, p.p_price_low * ISNULL(cum_split_factor, 1) *
            ISNULL(cum_spin_factor, 1)) AS split_spin_adj_price_low,
    CONVERT(FLOAT, p.p_price_open * ISNULL(cum_split_factor, 1) *
            ISNULL(cum_spin_factor, 1)) AS split_spin_adj_price_open,
    tr.one_day_pct AS one_day_total_return,
    ISNULL(cum_split_factor, 1) AS cum_split_factor,
    ISNULL(cum_spin_factor, 1) AS cum_spin_factor,
    CASE
                WHEN DATEADD(D, -1, a.p_date) = p.p_date
                THEN 1
                ELSE 0
            END AS adj_factor_flag
FROM prices AS p
    JOIN fp_v2.fp_total_returns_daily AS tr
    ON tr.fsym_id = p.fsym_id
        AND tr.p_date = p.p_date
    LEFT JOIN shares_out AS shs
    ON shs.fsym_id = p.fsym_id
        AND p.p_date < shs.p_shs_out_end_date
        AND p.p_date >= shs.p_date
    LEFT JOIN adjfactors AS a
    ON a.fsym_id = p.fsym_id
        AND p.p_date < a.p_date
        AND p.p_date >= a.p_end_date;