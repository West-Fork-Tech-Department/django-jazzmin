import json
from unittest.mock import MagicMock, NonCallableMock

import pytest
from django.contrib.admin.models import CHANGE, LogEntry
from jazzmin.templatetags import jazzmin


@pytest.mark.django_db
def test_app_is_installed(settings):
    """
    Returns True if an app is under INSTALLED_APPS, False otherwise
    """
    app = "test_app"

    assert jazzmin.app_is_installed(app) is False

    settings.INSTALLED_APPS.append(app)

    assert jazzmin.app_is_installed(app) is True


@pytest.mark.django_db
def test_action_message_to_list(admin_user):
    """
    We can generate a list of messages from a log entry object
    """
    message = [
        {"changed": {"fields": ["Owner", "Text", "Pub date", "Active"]}},
        {"added": {"name": "choice", "object": "More random choices"}},
        {"deleted": {"name": "choice", "object": "Person serious choose tea"}},
    ]
    log_entry = LogEntry.objects.create(user=admin_user, action_flag=CHANGE, change_message=json.dumps(message))
    assert jazzmin.action_message_to_list(log_entry) == [
        {"msg": "Changed Owner, Text, Pub date and Active.", "icon": "edit", "colour": "blue"},
        {"msg": "Added choice “More random choices”.", "icon": "plus-circle", "colour": "success"},
        {"msg": "Deleted “Person serious choose tea”.", "icon": "trash", "colour": "danger"},
    ]


def test_style_bold_first_word():
    """
    Adds <strong> HTML element wrapping first word given a sentence
    """
    message = "The bomb has been planted"

    assert jazzmin.style_bold_first_word(message) == "<strong>The</strong> bomb has been planted"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "case,test_input,field,expected,log",
    [
        (1, MagicMock(avatar="image.jpg"), "avatar", "image.jpg", None),
        (2, MagicMock(avatar="image.jpg"), lambda u: u.avatar, "image.jpg", None),
        (3, MagicMock(avatar=MagicMock(url="image.jpg")), "avatar", "image.jpg", None),
        # Properly set file field but empty (no image uploaded)
        (
            4,
            MagicMock(avatar=MagicMock(__bool__=lambda x: False)),
            "avatar",
            "/static/vendor/adminlte/img/user2-160x160.jpg",
            None,
        ),
        # No avatar field set
        (
            5,
            MagicMock(
                avatar="image.jpg",
            ),
            None,
            "/static/vendor/adminlte/img/user2-160x160.jpg",
            None,
        ),
        # No proper avatar field set
        (
            6,
            MagicMock(avatar=NonCallableMock(spec_set=["__bool__"], __bool__=lambda x: True)),
            "avatar",
            "/static/vendor/adminlte/img/user2-160x160.jpg",
            "Avatar field must be",
        ),
    ],
)
def test_get_user_avatar(case, test_input, field, expected, log, custom_jazzmin_settings, caplog):
    """
    We can specify the name of a charfield or imagefield on our user model, or a callable that receives our user
    """
    custom_jazzmin_settings["user_avatar"] = field
    assert jazzmin.get_user_avatar(test_input) == expected
    print(caplog.text)
    if log:
        assert log in caplog.text
    else:
        assert not caplog.text
