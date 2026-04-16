---
name: trino-query
description: Advanced Trino SQL agent for answering data questions via natural language.
---

# Trino Query Agent

Expert at querying Data Lakehouses (Iceberg, Postgres, MinIO) via Trino. Follows a reasoning loop to ensure SQL accuracy and schema consistency.

## Primary Workflow: The Reason-Evaluate Loop

When a user asks about data, follow these steps strictly:

1.  **Schema Discovery**: If you are unsure of the catalog, schema, or table structure, DO NOT guess. Use:
    ```bash
    bash trino-query/scripts/run.sh "SHOW CATALOGS"
    bash trino-query/scripts/run.sh "SHOW SCHEMAS IN <catalog>"
    bash trino-query/scripts/run.sh "SHOW TABLES IN <catalog>.<schema>"
    bash trino-query/scripts/run.sh "DESCRIBE <catalog>.<schema>.<table>"
    ```
2.  **Synthesis**: Draft an optimized Trino SQL query. Prefer Iceberg for historical data and Postgres for operational data.
3.  **Execution**: Run the query.
    ```bash
    bash trino-query/scripts/run.sh "<YOUR_TRINO_SQL_QUERY>"
    ```
4.  **Error Diagnosis & Recovery**: If the command returns a `TRINO ERROR`:
    -   **Column/Table Not Found**: Re-run discovery (Step 1) to verify the schema.
    -   **Syntax Error**: Check Trino documentation for proper SQL dialect (e.g., escaping keywords with double quotes).
    -   **Timeout**: Simplify the query (add `LIMIT` or filter by date/partition).
5.  **Summarization**: Present the results in a readable format. If the result is a table, preserve the markdown format.

## Advanced Usage

-   **Dry Run**: To verify your SQL without executing it (e.g., for complex joins), use `--dry-run`.
-   **Reference Material**: Check `trino-query/references/` for common query patterns if you encounter complex analytical requests.

## Implementation Details

-   **Installation Path**: The script is located at `trino-query/scripts/trino_query.py` and invoked via `trino-query/scripts/run.sh`.
-   **Dependencies**: Handled automatically by `run.sh` which creates a virtual environment on the first run.
