
def create_sample_task(client, **overrides):
    payload = {
        "title": "Test Task",
        "description": "A task for automated testing",
        "priority": "High",
        "status": "Todo",
        "due_date": "2026-10-30T18:00:00",
    }
    payload.update(overrides)

    return client.post("/tasks", json=payload)


def test_create_task(client):
    response = create_sample_task(client)

    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"
    assert response.json()["priority"] == "High"


def test_list_tasks(client):
    create_sample_task(client)

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert len(response.json()["items"]) == 1


def test_get_task(client):
    created = create_sample_task(client).json()

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_missing_task(client):
    response = client.get("/tasks/9999")

    assert response.status_code == 404


def test_update_task(client):
    created = create_sample_task(client).json()

    response = client.put(
        f"/tasks/{created['id']}",
        json={"title": "Updated Task"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"


def test_delete_task(client):
    created = create_sample_task(client).json()

    response = client.delete(f"/tasks/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_filter_by_priority(client):
    create_sample_task(client, priority="High")
    create_sample_task(client, title="Low Task", priority="Low")

    response = client.get("/tasks?priority=High")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["priority"] == "High"


def test_filter_by_status(client):
    create_sample_task(client, status="Todo")
    create_sample_task(
        client,
        title="Active Task",
        status="In Progress",
    )

    response = client.get("/tasks?status=Todo")

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_pagination(client):
    for number in range(3):
        create_sample_task(client, title=f"Task {number}")

    response = client.get("/tasks?page=1&limit=2")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 2
    assert response.json()["total"] == 3
    assert response.json()["total_pages"] == 2


def test_invalid_priority(client):
    response = create_sample_task(client, priority="Urgent")

    assert response.status_code == 422


def test_invalid_status_transition(client):
    created = create_sample_task(client, status="Todo").json()

    response = client.put(
        f"/tasks/{created['id']}",
        json={"status": "Done"},
    )

    assert response.status_code == 400


def test_valid_status_transition(client):
    created = create_sample_task(client, status="Todo").json()

    response = client.put(
        f"/tasks/{created['id']}",
        json={"status": "In Progress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"


def test_invalid_pagination(client):
    response = client.get("/tasks?page=0")

    assert response.status_code == 422


def test_sort_by_due_date_ascending(client):
    create_sample_task(
        client,
        title="Later Task",
        due_date="2026-11-10T10:00:00",
    )
    create_sample_task(
        client,
        title="Earlier Task",
        due_date="2026-10-25T10:00:00",
    )

    response = client.get(
        "/tasks?sort_by=due_date&order=asc"
    )

    assert response.status_code == 200
    items = response.json()["items"]
    assert items[0]["title"] == "Earlier Task"
    assert items[1]["title"] == "Later Task"


def test_invalid_sort_field(client):
    response = client.get("/tasks?sort_by=title")

    assert response.status_code == 422


def test_invalid_sort_order(client):
    response = client.get("/tasks?order=random")

    assert response.status_code == 422


def test_invalid_limit(client):
    response = client.get("/tasks?limit=101")

    assert response.status_code == 422


def test_cannot_move_done_task_back_to_todo(client):
    created = create_sample_task(
        client,
        status="In Progress",
    ).json()

    completed = client.put(
        f"/tasks/{created['id']}",
        json={"status": "Done"},
    )
    assert completed.status_code == 200

    response = client.put(
        f"/tasks/{created['id']}",
        json={"status": "Todo"},
    )

    assert response.status_code == 400
