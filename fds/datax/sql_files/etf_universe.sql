--Historical Fund holdings bASed on Ticker and Start Date
DECLARE @fund_ticker AS CHAR(8), @sd DATE, @ed DATE;
SET @fund_ticker = '{etf_ticker}'; --Fund Ticker + Region, SPY-US
SET @sd = '{sd}'; --Earliest date for holdings
SET @ed = '{ed}'; --Latest date for holdings;
WITH hist
     AS (SELECT DISTINCT
                fi.factset_fund_id,
                fh.report_date,
                DATEDIFF(DAY, LAG(report_date, 1, report_date) OVER(PARTITION
                BY fi.factset_fund_id
                ORDER BY report_date), fh.report_date) AS rpt_gap,
                LEAD(report_date) OVER(PARTITION BY fi.factset_fund_id
                ORDER BY report_date) AS next_rpt
         FROM   sym_v1.sym_ticker_region AS tr
         JOIN sym_v1.sym_coverage AS cov
           ON tr.fsym_id = cov.fsym_id
         JOIN own_v5.own_ent_fund_identifiers AS fi
           ON fi.fund_identifier = cov.fsym_security_id
         JOIN own_v5.own_ent_fund_filing_hist AS fh
           ON fh.factset_fund_id = fi.factset_fund_id
         WHERE  tr.ticker_region = @fund_ticker
                AND fh.report_date BETWEEN @sd AND @ed),
     own
     AS (SELECT fd.factset_fund_id,
                fd.fsym_id,
                fd.report_date,
                fd.adj_holding,
                h.rpt_gap,
                h.next_rpt
         FROM   hist AS h
         JOIN own_v5.own_fund_detail AS fd
           ON h.factset_fund_id = fd.factset_fund_id
              AND h.report_date = fd.report_date),
     gaps
     AS (SELECT o.factset_fund_id,
                o.fsym_id,
                o.report_date,
                o.next_rpt,
                o.adj_holding,
                o.rpt_gap,
                CASE
                    WHEN DATEDIFF(DAY, LAG(report_date) OVER(PARTITION BY
                    fsym_id
                         ORDER BY report_date), report_date) <= rpt_gap
                    THEN 0
                    ELSE 1
                END AS isstart
         FROM   own AS o),
     grp
     AS (SELECT *,
                SUM(isstart) OVER(PARTITION BY fsym_id
                ORDER BY report_date ROWS UNBOUNDED PRECEDING) AS grp2
         FROM   gaps),
     univ
     AS (SELECT fsym_id,grp2,
                MIN(report_date) AS startdate,
                MAX(next_rpt) AS enddate
         FROM   grp
         GROUP BY fsym_id,
                  grp2)
     SELECT u.fsym_id AS ref_id,
            cov.fsym_primary_listing_id,
            cov.fsym_primary_equity_id,
            cd.ref_date AS date
     FROM   ref_v2.ref_calendar_dates AS cd
     JOIN univ AS u
       ON cd.ref_date >= u.startdate
          AND cd.ref_date < u.enddate
     JOIN sym_v1.sym_coverage AS cov
       ON u.fsym_id = cov.fsym_id;