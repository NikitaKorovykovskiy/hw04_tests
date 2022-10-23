from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            id='2',
            author=User.objects.create_user(username='Sazan1',
                                            email='test@ya.ru',
                                            password='test_pass'),
            text='Тестовая запись',)

        cls.group = Group.objects.create(
            title='Тестовый заголовой',
            slug='test_slug'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Sazan')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_slug/',
            'posts/profile.html': '/profile/Sazan/',
            'posts/post_detail.html': '/posts/2/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        """Запрос к несуществующей странице."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_uses_correct_template(self):
        """Страница /create/ использует шаблон
        правильный шаблон и права доступа"""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_posts_post_id_edit_url_exists_at_author(self):
        """Страница /posts/post_id/edit/ доступна только автору."""
        self.authorized_client.force_login(TaskURLTests.post.author)
        response = self.authorized_client.get('/posts/2/edit/')
        self.assertTemplateUsed(response, 'posts/post_create.html')
