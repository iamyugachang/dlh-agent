import sys
import os
import argparse
import trino
from tabulate import tabulate
from dotenv import load_dotenv

def main():
    # Load environment variables from the .env file located directly next to this script
    # This is critical for portable skills that might be installed in deep subdirectories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Look for .env in the parent directory of 'scripts/' which is 'trino-query/'
    env_path = os.path.join(script_dir, '..', '.env')
    load_dotenv(env_path)

    parser = argparse.ArgumentParser(description="Modern Trino SQL Execution Tool for AI Agents")
    parser.add_argument("query", help="The Trino SQL string to execute")
    parser.add_argument("--dry-run", action="store_true", help="Print the SQL query without executing it")
    parser.add_argument("--format", default="pipe", choices=["pipe", "plain", "grid", "html"], help="Output table format (default: pipe)")
    args = parser.parse_args()

    if args.dry_run:
        print("--- DRY RUN: SQL QUERY ---")
        print(args.query)
        print("--------------------------")
        return

    # Read credentials and connection info from environment variables
    host = os.environ.get("TRINO_HOST", "localhost")
    port = int(os.environ.get("TRINO_PORT", 8080))
    user = os.environ.get("TRINO_USER", "admin")
    password = os.environ.get("TRINO_PASSWORD", "")
    catalog = os.environ.get("TRINO_CATALOG", "")
    schema = os.environ.get("TRINO_SCHEMA", "")

    auth = None
    if password:
        # Use BasicAuthentication if a password is provided
        from trino.auth import BasicAuthentication
        auth = BasicAuthentication(user, password)
        http_scheme = "https" # usually auth requires https
    else:
        http_scheme = os.environ.get("TRINO_HTTP_SCHEME", "http")

    conn_args = {
        "host": host,
        "port": port,
        "user": user,
        "http_scheme": http_scheme,
    }
    
    if auth:
        conn_args["auth"] = auth
    if catalog:
        conn_args["catalog"] = catalog
    if schema:
        conn_args["schema"] = schema

    try:
        # Connect to Trino
        conn = trino.dbapi.connect(**conn_args)
        cur = conn.cursor()
        
        # Execute the query passed from the CLI
        cur.execute(args.query)
        rows = cur.fetchall()
        
        # Display the result
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            print(tabulate(rows, headers=columns, tablefmt=args.format))
        else:
            print("Query executed successfully. No rows returned.")
            
    except trino.exceptions.TrinoQueryError as e:
        print(f"TRINO ERROR: {e.message}", file=sys.stderr)
        if e.error_name:
            print(f"ERROR TYPE: {e.error_name}", file=sys.stderr)
        if e.query_id:
            print(f"QUERY ID: {e.query_id}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"SYSTEM ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
