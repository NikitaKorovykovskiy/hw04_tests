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
            text='Текс исходный',
            group=self.group,
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {'text': 'Новый текст', 'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        posts = Post.objects.order_by('id').last()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(posts.text, form_data['text'])
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_post_edit(self):
        """Валидная форма меняет запись и группу"""
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group
        )
        old_text = self.post
        self.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test_group',
            description='Описание'
        )
        post_count = Post.objects.count()
        form_data = {'text': 'Изменяем текст', 'group': self.group2.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_text.id}),
            data=form_data,
            follow=True,
        )
        posts = Post.objects.filter(text='Изменяем текст').get()
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(Post.objects.count(), post_count)
        # self.assertTrue(posts.exists())
        self.assertEqual(posts.text, form_data['text'])
        self.assertEqual(posts.group.id, form_data['group'])
        self.assertEqual(response.status_code, HTTPStatus.OK)
