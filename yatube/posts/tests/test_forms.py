from posts.models import Post, Group, User
from django.test import Client, TestCase

from django.urls import reverse
from http import HTTPStatus


class PostCreateFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='Byblik')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое поле'
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Нестовый Текст',
            group=self.group,
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {'text': 'Тестовый текст', 'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        posts = Post.objects.all().filter(text='Тестовый текст').filter(
            group=self.group.id).order_by('-id')[:1]
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(posts.exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        """Валидная форма меняет запись"""
        post_count = Post.objects.count()
        form_data = {'text': 'Изменяем текст', 'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        posts = Post.objects.all().filter(text='Изменяем текст').filter(
            group=self.group.id).order_by('-id')[:1]
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(posts.exists())
        error_1 = 'Пользователь не может изменить текст поста'
        self.assertNotEqual(self.post.text, form_data['text'], error_1)
        error_2 = 'Пользователь не может изменить группу'
        self.assertNotEqual(self.post.group, form_data['group'], error_2)
        self.assertEqual(response.status_code, HTTPStatus.OK)
