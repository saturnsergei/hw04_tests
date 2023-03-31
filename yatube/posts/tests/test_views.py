from django import forms
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from posts.models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Группа',
            slug='test-slug',
            description='Описание'
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'HasNoName'}): 'posts/profile.html',
            reverse('posts:post_details',
                    kwargs={'post_id':
                            PostPagesTests.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            PostPagesTests.post.pk}): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон главной страницы сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        post_group_0 = first_object.group

        self.assertEqual(post_text_0, 'Текст поста')
        self.assertEqual(post_pub_date_0, PostPagesTests.post.pub_date)
        self.assertEqual(post_author_0, PostPagesTests.user)
        self.assertEqual(post_group_0, PostPagesTests.group)

    def test_group_page_show_correct_context(self):
        """Шаблон страницы группы сформирован с правильным контекстом и
        содержит пост с группой"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        post_group_0 = first_object.group

        self.assertEqual(post_text_0, 'Текст поста')
        self.assertEqual(post_pub_date_0, PostPagesTests.post.pub_date)
        self.assertEqual(post_author_0, PostPagesTests.user)
        self.assertEqual(post_group_0, PostPagesTests.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон страницы группы сформирован с правильным контекстом и
        содержит пост указанного пользователя"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'HasNoName'}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        post_group_0 = first_object.group

        self.assertEqual(post_text_0, 'Текст поста')
        self.assertEqual(post_pub_date_0, PostPagesTests.post.pub_date)
        self.assertEqual(post_author_0, PostPagesTests.user)
        self.assertEqual(post_group_0, PostPagesTests.group)

    def test_post_detail_show_correct_context(self):
        """Шаблон страницы поста сформирован с правильным контекстом"""
        response = (self.authorized_client.
                    get(reverse('posts:post_details',
                        kwargs={'post_id':
                                PostPagesTests.post.pk})))
        self.assertEqual(response.context.get('post').text, 'Текст поста')
        self.assertEqual(response.context.get('post').pub_date,
                         PostPagesTests.post.pub_date)
        self.assertEqual(response.context.get('post').author,
                         PostPagesTests.user)
        self.assertEqual(response.context.get('post').group,
                         PostPagesTests.group)

    def test_paginator(self):
        """Пагинатор показывает правильное количество постов"""
        pages_names = {
            'index': reverse('posts:index'),
            'group': reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            'profile': reverse('posts:profile',
                               kwargs={'username': 'HasNoName'})
        }

        for i in range(1, 13):
            Post.objects.create(
                text='Текст поста',
                author=PostPagesTests.user,
                group=PostPagesTests.group
            )

        for page, reverse_name in pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response_first_page = self.client.get(reverse_name)
                self.assertEqual(len(
                    response_first_page.context['page_obj']), 10)

                response_second_page = self.client.get(
                    reverse_name + '?page=2')
                self.assertEqual(len(
                    response_second_page.context['page_obj']), 3)

    def test_create_page_show_correct_context(self):
        """Форма создания сформирована с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        """Форма редактирования сформирована с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostPagesTests.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_doesnt_exists_at_undesired_group(self):
        """Пост не попал в группу, для которой не был предназначен"""
        Group.objects.create(
            title='Вторая группа',
            slug='second-slug',
            description='Описание'
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'second-slug'}))
        self.assertEqual(len(response.context['page_obj']), 0)
