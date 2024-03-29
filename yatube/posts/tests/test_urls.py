from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from posts.models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        # Создаем экземпляр клиента
        guest_client = Client()
        # Делаем запрос к главной странице и проверяем статус
        response = guest_client.get('/')
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)


class PostsURLTest(TestCase):

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
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTest.user)

    def test_home_url_exists_at_desired_location(self):
        """Главная страница доступна любому пользователю."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desired_location(self):
        """Страница группы доступна любому пользователю."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exists_at_desired_location(self):
        """Страница профиля доступна любому пользователю."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'HasNoName'}))
        self.assertEqual(response.status_code, 200)

    def test_post_url_exists_at_desired_location(self):
        """Страница поста доступна любому пользователю."""
        response = self.guest_client.get(
            reverse('posts:post_details',
                    kwargs={'post_id': PostsURLTest.post.pk}))
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location_author(self):
        """Страница редактирования поста доступна только автору."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            PostsURLTest.post.pk}))
        self.assertEqual(response.status_code, 200)

        second_user = User.objects.create_user(username='secondUser')
        second_client = Client()
        second_client.force_login(second_user)
        response_second = second_client.get(
            reverse('posts:post_edit', kwargs={'post_id':
                    PostsURLTest.post.pk}))
        self.assertEqual(response_second.status_code, 302)

    def test_post_create_url_exists_at_desired_location_authorized(self):
        """Страница создания поста доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        """Несуществующая страница поста недоступна."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': 'HasNoName'}),
            'posts/post_detail.html': reverse(
                'posts:post_details',
                kwargs={'post_id': PostsURLTest.post.pk}),
            'posts/create_post.html': reverse('posts:post_create'),
        }

        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_edit_not_author_uses_correct_template(self):
        """URL-адрес для не автора поста использует
        соответствующий шаблон."""
        second_user = User.objects.create_user(username='Second')
        second_client = Client()
        second_client.force_login(second_user)

        response = second_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostsURLTest.post.pk}), follow=True)
        self.assertTemplateUsed(response, 'posts/post_detail.html')

    def test_guest_uses_correct_template(self):
        """URL-адрес для анонимного пользователя использует
        соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:post_create'): 'users/login.html',
            reverse('posts:post_edit', kwargs={
                'post_id': PostsURLTest.post.pk}): 'users/login.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertTemplateUsed(response, template)
