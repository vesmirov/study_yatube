from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.base import ContentFile
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from tempfile import TemporaryDirectory
from io import BytesIO
from PIL import Image

from .models import User, Post, Group, Comment, Follow

test_data = {
    'username': 'test_user',
    'email': 'test_user@yatube.com',
    'password': 'test3321',
    'text': 'Test.',
    'edited': 'Edited text.',
}


class TestPost(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_unlogged = Client()

        self.group = Group.objects.create(title='Test', slug='test')
        self.user = User.objects.create_user(
            username=test_data['username'],
            email=test_data['email'],
            password=test_data['password'],
        )
        self.client.force_login(self.user)

    def post_urls_check(self, post):
        urls = [
            reverse('index'),
            reverse('profile', kwargs={'username': post.author.username}),
            reverse(
                'post',
                kwargs={'username': post.author.username, 'post_id': post.id}
            ),
        ]

        for url in urls:
            resp = self.client.get(url)
            cache.clear()
            self.assertContains(resp, post.text)
            self.assertContains(resp, post.author.username)

    def test_auth_publish(self):
        response = self.client.post(
            reverse('new_post'),
            data={'text': test_data['text'], 'group': self.group.id},
            follow=True
        )
        posts = Post.objects.all()

        self.assertEqual(
            response.status_code,
            200,
            msg='Не удается опубликовать пост авторизованному пользователю.'
        )
        self.assertEqual(posts.count(), 1)
        self.assertEqual(posts[0].text, test_data['text'])
        self.assertEqual(posts[0].author, self.user)

    def test_unlogged_publish(self):
        response = self.client_unlogged.post(
            reverse('new_post'),
            data={'text': test_data['text'], 'group': self.group.id},
        )
        posts = Post.objects.all()

        self.assertEqual(
            response.status_code,
            302,
            msg='Неавторизованный посетитель может добавить запись.'
        )
        self.assertEqual(posts.count(), 0)

    def test_post_show(self):
        post = Post.objects.create(
            text=test_data['text'],
            author=self.user,
            group=self.group
        )

        self.post_urls_check(post)

    def test_post_edit(self):
        cache.clear()
        post = Post.objects.create(
            text=test_data['text'],
            author=self.user,
            group=self.group
        )

        response = self.client.post(
            reverse(
                'post_edit',
                kwargs={'username': self.user.username, 'post_id': post.id}
            ),
            {'text': test_data['edited'], 'group': post.group.id},
            follow=True
        )
        post = Post.objects.get(text=test_data['edited'])
        self.post_urls_check(post)

    def test_unlogged_post_edit(self):
        post = Post.objects.create(
            text=test_data['text'],
            author=self.user,
            group=self.group
        )
        response = self.client_unlogged.post(
            reverse(
                'post_edit',
                kwargs={'username': self.user.username, 'post_id': post.id}
            ),
            {'text': test_data['edited']},
            follow=True
        )

        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertEqual(
            post.text,
            test_data['text'],
            msg='Неавторизованный может отредактировать пост.'
        )


class TestPages(TestCase):
    def setUp(self):
        self.client = Client()

    def test_404(self):
        response = self.client.get('/404/')
        self.assertEqual(response.status_code, 404)


class TestImages(TestCase):
    def setUp(self):
        self.client = Client()
        self.group = Group.objects.create(title='Test', slug='test')
        self.user = User.objects.create_user(
            username=test_data['username'],
            email=test_data['email'],
            password=test_data['password'],
        )
        self.client.force_login(self.user)

    def test_image_on_post_page(self):
        self.post = Post.objects.create(text=test_data['text'], author=self.user)
        with TemporaryDirectory() as temp_directory:
            with override_settings(MEDIA_ROOT=temp_directory):
                byte_image = BytesIO()
                im = Image.new("RGB", size=(500, 500), color=(255, 0, 0, 0))
                im.save(byte_image, format='jpeg')
                byte_image.seek(0)

                params = {'username': self.user.username, 'post_id': self.post.id}
                data = {'text': 'post with image', 'image': ContentFile(byte_image.read(), name='test.jpeg')}
                response = self.client.post(reverse('post_edit', kwargs=params), data=data, follow=True)

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, '<img')

    def test_image_on_all_urls(self):
        cache.clear()
        with TemporaryDirectory() as temp_directory:
            with override_settings(MEDIA_ROOT=temp_directory):
                byte_image = BytesIO()
                im = Image.new("RGB", size=(500, 500), color=(255, 0, 0, 0))
                im.save(byte_image, format='jpeg')
                byte_image.seek(0)

                post = Post.objects.create(
                    text=test_data['text'],
                    author=self.user,
                    group=self.group,
                    image=ContentFile(byte_image.read(), name='test.jpeg')
                )
                urls = [
                    reverse('index'),
                    reverse('profile', kwargs={'username': post.author.username}),
                    reverse('group', kwargs={'slug': post.group.slug}),
                ]
                for url in urls:
                    response = self.client.get(url)
                    self.assertContains(response, '<img', html=False)
                    self.assertEqual(response.context['page'][0].image, post.image)

    def test_upload_format(self):
        img_bytes = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        image = SimpleUploadedFile(
            'small.txt', img_bytes,
            content_type='text/plain'
        )
        post_data = {
            'text': 'test post',
            'group': self.group.id,
            'image': image
        }
        error_text = "Формат файлов 'txt' не поддерживается. Поддерживаемые форматы файлов: '" \
                     "bmp, dib, gif, tif, tiff, jfif, jpe, jpg, jpeg, pbm, pgm, ppm, pnm, png, apng, " \
                     "blp, bufr, cur, pcx, dcx, dds, ps, eps, fit, fits, fli, flc, ftc, ftu, gbr, grib, " \
                     "h5, hdf, jp2, j2k, jpc, jpf, jpx, j2c, icns, ico, im, iim, mpg, mpeg, mpo, msp, " \
                     "palm, pcd, pdf, pxr, psd, bw, rgb, rgba, sgi, ras, tga, icb, vda, vst, webp, wmf, " \
                     "emf, xbm, xpm'."

        response = self.client.post(reverse('new_post'), data=post_data)
        self.assertFormError(response, form='form', field='image', errors=error_text)


class TestCache(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username=test_data['username'],
            email=test_data['email'],
            password=test_data['password'],
        )
        self.client.force_login(self.user)

    def test_cache_main(self):
        response = self.client.post(
            reverse('new_post'),
            data={'text': test_data['text']},
            follow=True
        )
        post = Post.objects.first()
        self.assertContains(response, test_data['text'])
        post.delete()
        response = self.client.get(reverse('index'))
        self.assertContains(response, test_data['text'])


class TestFollow(TestCase):
    def setUp(self):
        usernames = ['user1', 'user2', 'user3']
        emails = [
            'user1@yatube.com',
            'user2@yatube.com',
            'user3@yatube.com',
        ]
        self.users = []
        for x in range(3):
            self.users.append(
                User.objects.create_user(
                    username=usernames[x],
                    email=emails[x],
                    password=test_data['password']
                )
            )
        self.client = Client()
        self.client_unlogged = Client()
        self.client.force_login(self.users[0])

    def test_follow(self):
        cache.clear()
        self.client.get(
            reverse('profile_follow', kwargs={'username': self.users[1]})
        )
        self.assertEqual(
            self.users[0].follower.values_list('author').count(),
            1
        )

    def test_unfollow(self):
        cache.clear()
        Follow.objects.create(user=self.users[0], author=self.users[1])
        self.client.get(
            reverse('profile_unfollow', kwargs={'username': self.users[1]})
        )
        self.assertEqual(
            self.users[0].follower.values_list('author').count(),
            0
        )

    def test_follow_author_post_show(self):
        cache.clear()
        Post.objects.create(
            author=self.users[2],
            text=test_data['text'],
        )
        response = self.client.get(
            reverse('profile_follow', kwargs={'username': self.users[2]}),
            follow=True
        )

        self.assertEqual(len(response.context['paginator'].object_list), 1)
        self.assertEqual(
            response.context['paginator'].object_list[0].author,
            self.users[2]
        )

        self.client.force_login(self.users[1])
        response = self.client.get(reverse('follow_index'))
        self.assertEqual(len(response.context['paginator'].object_list), 0)

    def test_auth_user_comment(self):
        post = Post.objects.create(
            author=self.users[2],
            text=test_data['text'],
        )

        self.client.post(reverse('add_comment', kwargs={
            'username': self.users[2].username, 'post_id': post.id}),
                         data={'text': test_data['text']},
                         follow=True)
        self.assertEqual(post.comments.count(), 1)

    def test_unauth_user_comment(self):
        post = Post.objects.create(
            author=self.users[2],
            text=test_data['text'],
        )

        self.client_unlogged.post(reverse('add_comment', kwargs={
            'username': self.users[2].username, 'post_id': post.id}),
                                  data={'text': test_data['text']},
                                  follow=True)
        self.assertEqual(post.comments.count(), 0)
