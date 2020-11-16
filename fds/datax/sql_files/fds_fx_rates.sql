SELECT fx.iso_currency as currency,fx.date AS price_date
       ,fx.exch_rate_usd,fx.exch_rate_per_usd
  FROM ref_v2.fx_rates_usd AS fx
 WHERE fx.date BETWEEN '{sd}' AND '{ed}' --formatted for pyodbc params
   AND fx.iso_currency IN ({ids})
 UNION
--add USD placeholder
SELECT distinct 'USD' as currency,date
       ,1 as exch_rate_usd,1 as exch_rate_per_usd
  FROM ref_v2.fx_rates_usd AS usd
 WHERE usd.date BETWEEN '{sd}' AND '{ed}' --formatted for pyodbc params