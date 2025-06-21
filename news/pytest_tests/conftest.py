import pytest
from datetime import datetime, timedelta

from django.test.client import Client
from django.conf import settings

from news.models import Comment, News

COUNT_COMMENTS = 2


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news
    )
    return comment


# @pytest.fixture
# def form_data():
#     return {
#         'title': 'Новый заголовок',
#         'text': 'Новый текст'
#     }


@pytest.fixture(scope='function')
def create_news():
    today = datetime.today().replace(second=0, microsecond=0)
    news_list = [
        News.objects.create(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return news_list


@pytest.fixture(scope='function')
def create_comments(news, author):
    today = datetime.today().replace(second=0, microsecond=0)
    comment_list = [
        Comment.objects.create(
            text='Текст комментария',
            author=author,
            news=news,
            created=today - timedelta(days=index)
        )
        for index in range(COUNT_COMMENTS)
    ]
    return comment_list
