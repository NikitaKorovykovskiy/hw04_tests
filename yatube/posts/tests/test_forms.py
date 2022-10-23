from posts.models import Post, Group, User
from django.test import Client, TestCase

from django.urls import reverse


class PostCreateFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='Byblik')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {'text': 'Тестовый текст'}
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст'
            ).exists()
        )
        self.assertEqual(response.status_code, 200)

    def test_post_edit(self):
        """Валидная форма меняет запись"""
        self.post = Post.objects.create(
            author=self.user,
            text='Нестовый Текст'
        )
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_dlug',
            description='Тестовое поле'
        )
        post_count = Post.objects.count()
        form_data = {'text': 'Изменяем текст', 'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text='Изменяем текст'
            ).exists()
        )
        self.assertEqual(response.status_code, 200)
