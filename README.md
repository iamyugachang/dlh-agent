# Lakehouse Data Exploration with Trino (Modern 2025 Edition)

This project provides a Trino-based environment for exploring data across different catalogs (e.g., Iceberg and Postgres) using natural language. It is built as a **Modern AI Skill** following 2024-2025 agentic engineering standards.

## 🚀 Natural Language Querying (No SQL Required)

The core power of this project is the **Trino Query Skill**. Integrated directly into the Gemini CLI or Claude Code, it follows a **Reason-Evaluate Loop** to handle complex data tasks:

1.  **Autonomous Schema Discovery**: The agent discovers catalogs, schemas, and table structures before guessing a query.
2.  **Surgical SQL Synthesis**: Optimized Trino SQL generated via Claude 3.5/3.7 Sonnet.
3.  **Advanced Error Recovery**: Built-in logic to diagnose and recover from SQL syntax errors or schema drift.
4.  **Dry-Run Verification**: Support for `--dry-run` to validate logic without executing.

---

## 🛠 Skill Architecture

Following modern AI tool standards, the skill is structured for modularity and safety:

- **`SKILL.md`**: The metadata and "brain" of the agent, defining the reason-evaluate loop.
- **`scripts/trino_query.py`**: The robust execution engine with advanced error reporting and absolute pathing.
- **`references/`**: Domain-specific knowledge base (Iceberg patterns, cross-catalog joins).
- **`tests/`**: Automated validation using `pytest` to ensure connection and formatting stability.

---

## 🛠 Why a "Skill" instead of an "MCP Server"?

-   **Context Efficiency**: This skill is activated *only* when needed, keeping your context window lean.
-   **No-Wait Execution**: Direct script execution via terminal is 10-32x more token-efficient than complex MCP schema exchanges.
-   **Surgical Portability**: Drop the `trino-query` folder into any `.agents/skills/` directory and it works immediately.

---

## 🏗 Infrastructure
- **Iceberg:** Stored in S3/MinIO via Hive Metastore.
- **Postgres:** Relational database for operational data.
- **Trino:** The unified query engine bridging both worlds.

## 💻 Installation
To easily embed this skill into any agent project:

1.  **Clone/Copy** this repository.
2.  **Run Install**:
    ```bash
    ./install.sh /path/to/your/agent/workspace
    ```
3.  **Setup Credentials**:
    -   Copy `trino-query/.env.example` to `trino-query/.env`
    -   Update `TRINO_HOST`, `USER`, and `PASSWORD`.
4.  **Install Dependencies**:
    ```bash
    pip install -r trino-query/requirements.txt
    ```

## 🛠 Development & Testing
Run the automated test suite to verify your environment:
```bash
pytest trino-query/tests/
```
