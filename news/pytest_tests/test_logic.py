import pytest
from pytest_lazy_fixtures import lf
from http import HTTPStatus

from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
@pytest.mark.parametrize(
    'test_client, can_create_comment',
    [
        (lf('client'), False),
        (lf('author_client'), True),
    ]
)
def test_user_can_create_comment(test_client, can_create_comment, news):
    """Проверяет доступность отправки комментария
    для авторизованных и анонимных пользователей.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    form_data = {'text': 'Текст комментария'}
    test_client.post(url, data=form_data, follow=True)
    comments_count = Comment.objects.count()
    if can_create_comment:
        assert comments_count == 1
    else:
        assert comments_count == 0


def test_user_cant_use_bad_words(author_client, news):
    """Проверяет невозможность отправки комментария со стоп-словами."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    form = response.context['form']
    assert not form.is_valid()
    assert form.errors['text'] == [WARNING]
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.parametrize(
    'test_client, expected_status',
    [
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK),
    ]
)
def test_user_can_edit_comment(test_client, comment, expected_status):
    """Проверяет доступность редактирования комментария
    для пользователя-автора и не автора.
    """
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = test_client.get(url)
    assert response.status_code == expected_status
