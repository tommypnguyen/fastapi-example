import pytest
from app import schemas
from tests.conftest import authorized_client


def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts")
    data = res.json()
    res_posts = [schemas.PostResponse(**post["Post"]) for post in data]
    assert len(res_posts) == len(test_posts)
    assert res.status_code == 200


def test_unauthorized_user_get_all_posts(client, test_posts):
    res = client.get("/posts")
    assert res.status_code == 401


def test_unauthorized_user_get_post(client, test_posts):
    res = client.get("/posts/{}".format(test_posts[0]["id"]))
    assert res.status_code == 401


def test_get_one_post_not_exist(authorized_client, test_posts):
    res = authorized_client.get("/posts/8888")
    assert res.status_code == 404


def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get("/posts/{}".format(test_posts[0]["id"]))
    data = res.json()
    new_post = schemas.PostResponse(**data["Post"])
    assert res.status_code == 200
    assert new_post.title == test_posts[0]["title"]


@pytest.mark.parametrize(
    "title, content",
    [("Test post", "test post content"), ("Test post 2", "Test post content 2")],
)
def test_create_post(authorized_client, test_user, title, content):
    res = authorized_client.post("/posts/", json={"title": title, "content": content})
    new_post = res.json()
    assert res.status_code == 201
    assert new_post["title"] == title
    assert new_post["content"] == content


def test_unauthorized_user_delete_post(client, test_user, test_posts):
    res = client.delete("/posts/{}".format(test_posts[0]["id"]))
    assert res.status_code == 401


def test_delete_post(authorized_client, test_user, test_posts):
    res = authorized_client.delete("/posts/{}".format(test_posts[0]["id"]))
    assert res.status_code == 204


def test_delete_post_non_exist(authorized_client, test_user, test_posts):
    res = authorized_client.delete("/posts/{}".format(8888))
    assert res.status_code == 404


def test_delete_other_user_post(authorized_client, test_user, test_user2, test_posts):
    res = authorized_client.delete("/posts/2")
    assert res.status_code == 403


def test_update_post(authorized_client, test_user, test_posts):
    data = {
        "title": "update title",
        "content": "update content",
        "id": test_posts[0]["id"],
    }
    res = authorized_client.put("/posts/{}".format(test_posts[0]["id"]), json=data)
    updated_post = schemas.PostResponse(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data["title"]


def test_update_other_user_post(authorized_client, test_user, test_user2, test_posts):
    data = {
        "title": "update title",
        "content": "update content",
        "id": test_posts[1]["id"],
    }
    res = authorized_client.put("/posts/{}".format(test_posts[1]["id"]), json=data)
    assert res.status_code == 403


def test_unauthorized_user_update_post(client, test_user, test_posts):
    data = {
        "title": "update title",
        "content": "update content",
        "id": test_posts[1]["id"],
    }
    res = client.put("/posts/{}".format(test_posts[0]["id"]), json=data)
    assert res.status_code == 401


def test_update_post_non_exist(authorized_client, test_user, test_posts):
    data = {
        "title": "update title",
        "content": "update content",
        "id": test_posts[1]["id"],
    }
    res = authorized_client.put("/posts/4242", json=data)
    assert res.status_code == 404
