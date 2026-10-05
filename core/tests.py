from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import ChatGroup, ChatMessage, GroupMembership


class AccountAndChatTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="adnan",
            password="Unique-Horse-47-Cloud!",
            first_name="Adnan",
        )
        self.group = ChatGroup.objects.create(
            name="Frontend learners",
            description="Learn HTML, CSS, and JavaScript together.",
            created_by=self.owner,
        )

    def test_home_page_includes_branding(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "devpulse-logo")
        self.assertContains(response, "devpulse-favicon")

    def test_signin_creates_and_logs_in_new_account(self):
        response = self.client.post(
            reverse("signin"),
            {
                "username": "newstudent",
                "first_name": "New",
                "last_name": "Student",
                "email": "student@example.com",
                "password1": "Bright-Forest-82-Planet!",
                "password2": "Bright-Forest-82-Planet!",
            },
        )
        self.assertRedirects(response, reverse("chat_list"))
        self.assertTrue(User.objects.filter(username="newstudent").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_signin_rejects_empty_required_fields(self):
        response = self.client.post(reverse("signin"), {})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="").exists())
        self.assertContains(response, "This field is required.")

    def test_login_authenticates_existing_account(self):
        response = self.client.post(
            reverse("login"),
            {"username": "adnan", "password": "Unique-Horse-47-Cloud!"},
        )
        self.assertRedirects(response, reverse("chat_list"))

    def test_group_creation_adds_creator_as_member(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("create_group"),
            {"name": "Python learners", "description": "Practice Python together."},
        )
        group = ChatGroup.objects.get(name="Python learners")
        self.assertRedirects(response, reverse("chat_detail", args=[group.pk]))
        self.assertTrue(GroupMembership.objects.filter(group=group, user=self.owner).exists())

    def test_anonymous_users_cannot_create_groups(self):
        response = self.client.get(reverse("create_group"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('create_group')}",
        )

    def test_chat_list_searches_group_names_and_descriptions(self):
        response = self.client.get(reverse("chat_list"), {"q": "javascript"})
        self.assertContains(response, self.group.name)
        self.assertNotContains(response, "No groups found.")

        response = self.client.get(reverse("chat_list"), {"q": "no matching group"})
        self.assertContains(response, "No groups found.")

    def test_only_followers_can_read_or_send_group_messages(self):
        other_user = User.objects.create_user(
            username="learner2",
            password="Unique-River-37-Mountain!",
        )
        ChatMessage.objects.create(group=self.group, author=self.owner, body="Welcome!")
        self.client.force_login(other_user)

        response = self.client.get(reverse("chat_detail", args=[self.group.pk]))
        self.assertNotContains(response, "Welcome!")

        self.client.post(reverse("toggle_follow", args=[self.group.pk]), {"next": "/"})
        response = self.client.post(
            reverse("chat_detail", args=[self.group.pk]),
            {"body": "Hello everyone!"},
        )
        self.assertRedirects(response, reverse("chat_detail", args=[self.group.pk]))
        self.assertTrue(
            ChatMessage.objects.filter(group=self.group, author=other_user, body="Hello everyone!").exists()
        )

    def test_empty_message_is_not_saved(self):
        GroupMembership.objects.create(group=self.group, user=self.owner)
        self.client.force_login(self.owner)
        response = self.client.post(reverse("chat_detail", args=[self.group.pk]), {"body": "   "})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ChatMessage.objects.filter(group=self.group).exists())

    def test_profile_shows_groups_the_person_follows(self):
        GroupMembership.objects.create(group=self.group, user=self.owner)
        response = self.client.get(reverse("profile", args=[self.owner.username]))
        self.assertContains(response, "Frontend learners")

    def test_follow_redirect_rejects_external_url(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("toggle_follow", args=[self.group.pk]),
            {"next": "https://example.com/"},
        )
        self.assertRedirects(response, reverse("chat_list"))
