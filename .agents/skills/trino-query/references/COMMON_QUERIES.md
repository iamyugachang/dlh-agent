# Common Trino Query Patterns

Use these patterns to synthesize high-quality SQL for the Data Lakehouse.

## 1. Iceberg Discovery
```sql
-- List tables and their types
SELECT table_name, table_type 
FROM iceberg.information_schema.tables 
WHERE table_schema = 'public';

-- Inspect partitions (Iceberg specific)
SELECT * FROM "catalog"."schema"."table$partitions";
```

## 2. Cross-Catalog Joins (Postgres + Iceberg)
```sql
-- Join operational Postgres data with historical Iceberg data
SELECT o.order_id, o.customer_id, h.event_time, h.total_amount
FROM postgres.public.orders o
JOIN iceberg.analytics.historical_events h ON o.order_id = h.order_id
WHERE o.status = 'COMPLETED'
LIMIT 100;
```

## 3. Time Series Analysis
```sql
-- Aggregating by date
SELECT date_trunc('day', event_time) as day, count(*) as count
FROM iceberg.analytics.events
GROUP BY 1
ORDER BY 1 DESC;
```

## 4. Troubleshooting
- **Keywords**: Always wrap identifiers in double quotes if they match SQL keywords: `SELECT "user", "order" FROM ...`
- **Casting**: Use explicit casts for types: `CAST(total AS decimal(18,2))`
