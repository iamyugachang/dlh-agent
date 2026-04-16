import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the scripts directory to path so we can import trino_query
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import trino_query

def test_dry_run(capsys):
    """Test that --dry-run outputs the SQL without executing."""
    test_query = "SELECT * FROM test"
    with patch('sys.argv', ['trino_query.py', test_query, '--dry-run']):
        trino_query.main()
    
    captured = capsys.readouterr()
    assert "DRY RUN" in captured.out
    assert test_query in captured.out

@patch('trino.dbapi.connect')
def test_successful_query(mock_connect, capsys):
    """Test a successful query execution and formatting."""
    # Mock connection and cursor
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    
    # Mock results
    mock_cur.description = [('id',), ('name',)]
    mock_cur.fetchall.return_value = [(1, 'Alice'), (2, 'Bob')]
    
    test_query = "SELECT id, name FROM users"
    with patch('sys.argv', ['trino_query.py', test_query]):
        trino_query.main()
    
    captured = capsys.readouterr()
    assert "id" in captured.out
    assert "name" in captured.out
    assert "Alice" in captured.out
    assert "Bob" in captured.out

@patch('trino.dbapi.connect')
def test_trino_error(mock_connect, capsys):
    """Test handling of TrinoQueryError."""
    from trino.exceptions import TrinoQueryError
    
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    
    # Simulate a Trino error
    error_msg = "Table 'users' does not exist"
    mock_cur.execute.side_effect = TrinoQueryError({"message": error_msg, "errorName": "TABLE_NOT_FOUND", "queryId": "123"})
    
    test_query = "SELECT * FROM users"
    with patch('sys.argv', ['trino_query.py', test_query]):
        with pytest.raises(SystemExit) as e:
            trino_query.main()
    
    assert e.value.code == 1
    captured = capsys.readouterr()
    assert f"TRINO ERROR: {error_msg}" in captured.err
    assert "ERROR TYPE: TABLE_NOT_FOUND" in captured.err
