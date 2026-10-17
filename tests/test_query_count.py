from sqlalchemy import event


def test_list_tasks_query_count_is_constant(client, db_session):
    engine = db_session.get_bind()
    counts = {}
    for n in (3, 10):
        for i in range(n):
            client.post("/tasks", json={"title": f"할 일 {i}", "tags": ["개인", f"태그{i}"]})

        queries = []

        def count(conn, cursor, statement, *args):
            queries.append(statement)

        event.listen(engine, "before_cursor_execute", count)
        try:
            assert client.get("/tasks").status_code == 200
        finally:
            event.remove(engine, "before_cursor_execute", count)
        counts[n] = len(queries)

    # 할 일 개수와 무관하게 tasks 1회 + tags 1회
    assert counts[3] == counts[10] == 2
