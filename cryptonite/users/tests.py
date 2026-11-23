from io import BytesIO
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from users.forms import ProfileChangeForm, SetPasswordForm, UserCreationForm


def image_bytes(fmt='PNG', size=(32, 32)):
    with BytesIO() as output, Image.new('RGB', size) as image:
        image.save(output, format=fmt)
        return output.getvalue()


class ProfileUploadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='player',
            email='player@example.com',
        )

    def profile_form(self, **files):
        return ProfileChangeForm(
            {'username': self.user.username, 'about_me': 'Profile'},
            files,
            instance=self.user,
        )

    def test_valid_upload_is_reencoded_using_actual_format(self):
        upload = SimpleUploadedFile(
            'misleading.jpg',
            image_bytes() + b'extra bytes',
            content_type='image/jpeg',
        )
        form = self.profile_form(avatar=upload)
        self.assertTrue(form.is_valid(), form.errors)
        normalized = form.cleaned_data['avatar']
        self.assertTrue(normalized.name.endswith('.png'))
        self.assertEqual(normalized.content_type, 'image/png')
        self.assertNotIn(b'extra bytes', normalized.read())

    def test_rejects_corrupt_disallowed_and_oversized_images(self):
        cases = [
            ('avatar', b'not an image', 'invalid_image'),
            ('avatar', image_bytes('GIF'), 'invalid_image'),
            ('avatar', image_bytes()[:25], 'invalid_image'),
            ('avatar', image_bytes(size=(2049, 1)), 'image_too_large'),
            ('avatar', b'x' * (2 * 1024 * 1024 + 1), 'file_too_large'),
            ('background', image_bytes(size=(4097, 1)), 'image_too_large'),
            ('background', b'x' * (5 * 1024 * 1024 + 1), 'file_too_large'),
        ]
        for field, data, error in cases:
            with self.subTest(field=field, error=error):
                form = self.profile_form(
                    **{
                        field: SimpleUploadedFile(
                            'picture.png', data, content_type='image/png'
                        ),
                    }
                )
                self.assertFalse(form.is_valid())
                self.assertEqual(form.errors.as_data()[field][0].code, error)

    def test_signup_validates_avatar(self):
        form = UserCreationForm(
            {
                'username': 'another_player',
                'email': 'another@example.com',
                'password1': 'some-strong-password!14',
                'password2': 'some-strong-password!14',
            },
            {'avatar': SimpleUploadedFile('avatar.png', b'invalid')},
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['avatar'][0].code, 'invalid_image'
        )

    def test_profile_edit_saves_normalized_file(self):
        self.client.force_login(self.user)
        with TemporaryDirectory() as media, self.settings(MEDIA_ROOT=media):
            response = self.client.post(
                reverse('users:profile_edit'),
                {
                    'username': self.user.username,
                    'about_me': 'New bio',
                    'avatar': SimpleUploadedFile(
                        'avatar.png', image_bytes('JPEG')
                    ),
                },
            )
            self.assertEqual(response.status_code, 302)
            self.user.refresh_from_db()
            self.assertEqual(self.user.about_me, 'New bio')
            self.assertTrue(self.user.avatar.name.endswith('.jpg'))
            with self.user.avatar.open() as avatar:
                self.assertEqual(avatar.read(2), b'\xff\xd8')

    def test_stale_password_form_does_not_overwrite_wallet(self):
        get_user_model().objects.filter(pk=self.user.pk).update(
            money=80, xp=100
        )
        password = 'new-long-random-password!2026'
        form = SetPasswordForm(
            self.user,
            {'new_password1': password, 'new_password2': password},
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(password))
        self.assertEqual((self.user.money, self.user.xp), (80, 100))
