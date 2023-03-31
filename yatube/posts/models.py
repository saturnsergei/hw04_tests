from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(unique=True, verbose_name='Путь')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title


class Post(models.Model):
    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ('-pub_date',)

    text = models.TextField(verbose_name='Текст', help_text='Текст поста')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )

    group = (models.ForeignKey(Group,
                               blank=True,
                               null=True,
                               on_delete=models.SET_NULL,
                               related_name='posts',
                               verbose_name='Сообщество',
                               help_text=('Группа, к которой '
                                          'будет относиться пост')))

    def __str__(self):
        return self.text[:15]
