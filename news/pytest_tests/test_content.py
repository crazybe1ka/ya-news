import pytest
from pytest_lazy_fixtures import lf

from django.urls import reverse
from django.conf import settings


def get_object_list(client):
    """Вспомогательная функция для получения object_list."""
    home_url = reverse('news:home')
    response = client.get(home_url)
    return response.context['object_list']


@pytest.mark.django_db
def test_news_count(client, create_news):
    """Проверяет количество новостей на главной странице."""
    object_list = get_object_list(client)
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, create_news):
    """Проверяет, что свежие новости отображаются в начале списка."""
    object_list = get_object_list(client)
    all_dates = [news_item.date for news_item in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, create_comments, news):
    """Проверяет хронологию отображения комментариев к новости."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps, reverse=True)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'test_client, should_have_form',
    [
        (lf('client'), False),
        (lf('author_client'), True),
    ]
)
def test_form_presence_for_clients(news, should_have_form, test_client):
    """Проверяет доступность отображения формы
    для авторизованных и анонимных пользователей.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = test_client.get(url)
    if should_have_form:
        assert 'form' in response.context
    else:
        assert 'form' not in response.context
