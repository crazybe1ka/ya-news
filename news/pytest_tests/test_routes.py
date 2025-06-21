import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name, news):
    """
    Проверяет доступность страниц для анонимного пользователя.
    Обрабатывает особый случай 'news:detail',
    для которого требуется передать pk новости.
    """
    if name == 'news:detail':
        url = reverse(name, kwargs={'pk': news.pk})
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    """
    Проверяет доступность страниц редактирования
    и удаления комментария для пользователя-автора и не автора.
    """
    url = reverse(name, kwargs={'pk': comment.pk})
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirects(client, name, comment):
    """
    Проверяет перенаправление анонимного пользователя
    со страниц редактирования и удаления комментария
    на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, kwargs={'pk': comment.pk})
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
