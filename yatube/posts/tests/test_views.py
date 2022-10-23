from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group, User

User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        cls.post = Post.objects.create(
            id='2',
            author=User.objects.create_user(username='Sazan1',
                                            email='test@ya.ru',
                                            password='test_pass'),
            text='Тестовая запись',
            group=Group.objects.create(
                title='Тестовый заголовой',
                slug='test_slug'
            ))

    def setUp(self):
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:group_lists', kwargs={'slug': 'test_slug'}),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': 'StasBasov'}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': '2'}
            ),
            'posts/post_create.html': reverse('posts:post_create'),
        }
        # Проверяем, что при обращении к name вызывается соответствующий шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author0 = first_object.author.username
        self.assertEqual(post_text_0, 'Тестовая запись')
        self.assertEqual(post_group_0, 'Тестовый заголовой')
        self.assertEqual(post_author0, 'Sazan1')

    def test_index_show_correct_context(self):
        """Список постов в шаблоне index равен ожидаемому контексту."""
        response = self.guest_client.get(reverse('posts:index'))
        first_pages = list(Post.objects.all()[:10])
        self.assertEqual(list(response.context['page_obj']), first_pages)

    def test_group_list_show_correct_context(self):
        """Список постов в шаблоне group_list равен ожидаемому контексту."""
        response = self.guest_client.get(
            reverse('posts:group_lists', kwargs={'slug': 'test_slug'})
        )
        first_pages = list(Post.objects.filter(group=self.post.group.id)[:10])
        self.assertEqual(list(response.context['page_obj']), first_pages)

    def test_profile_show_correct_context(self):
        """Список постов в шаблоне profile равен ожидаемому контексту."""
        response = self.guest_client.get(
            reverse('posts:profile', args=(self.post.author,))
        )
        first_pages = list(Post.objects.filter(author=self.post.author)[:10])
        self.assertEqual(list(response.context['page_obj']), first_pages)

    def test_post_detail_show_correct_context(self):
        """Один пост, отфильтрованный по id"""
        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={'post_id': self.post.id})
        )
        first_object = response.context.get('post')
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author0 = first_object.author.username
        self.assertEqual(post_text_0, 'Тестовая запись')
        self.assertEqual(post_group_0, 'Тестовый заголовой')
        self.assertEqual(post_author0, 'Sazan1')

    # def test_post_edit_show_correct_context(self):
    #     """Форма редактирования поста, отфильтрованного по id"""
    #     response = self.authorized_client.get(
    #         reverse('posts:post_edit', args=(self.post.id,))
    #     )
    #     form_fields = {
    #         'text': forms.fields.CharField,
    #         'group': forms.models.ModelChoiceField,
    #     }
    #     for value, expected in form_fields.items():
    #         form_field = response.context['form'].fields[value]
    #         self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context(self):
        """Форма создания поста работает исправно"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            form_field = response.context.get('post').fields.get(value)
            self.assertIsInstance(form_field, expected)

    def test_group_in_pages(self):
        """Проверяем созднание поста на нужных страницах"""
        post = Post.objects.create(
            text='Тестовый текст проверка как добавился',
            author=self.user,
            group=self.post.group)
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_lists',
                    kwargs={'slug': f'{post.group.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index, 'поста нет на главной')
        self.assertIn(post, group, 'поста нет в профиле')
        self.assertIn(post, profile, 'поста нет в группе')
