from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.forms import PostForm
from posts.models import Post, Group

User = get_user_model()


class PostFormTests(TestCase):

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
        cls.form = PostForm(instance=PostFormTests.post)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_post_create_success(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': PostFormTests.group.pk,
            'author': self.user
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'HasNoName'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст поста',
                group=PostFormTests.group.pk,
                author=self.user
            ).exists()
        )

    def test_post_edit_success(self):
        """Валидная форма изменяет запись в Post."""
        form_data = {
            'text': 'Новый текст поста',
            'group': PostFormTests.group.pk,
        }
        post_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            PostFormTests.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_details', kwargs={'post_id': PostFormTests.post.pk}))
        self.assertEqual(Post.objects.count(), post_count)
        post = Post.objects.get(pk=PostFormTests.post.pk)
        self.assertEqual(form_data['text'], post.text)
        self.assertEqual(form_data['group'], post.group.pk)
        self.assertEqual(PostFormTests.user, post.author)
