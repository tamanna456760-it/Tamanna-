# User Profile and Settings Persistence

Owner: HM INSAN ALI

The persistence layer stores a private profile/settings record for each user
in the `user_settings` SQL table. The existing `users` table stores the
account name and email.

Supported metadata:
- Profile name and email (email is normalized to lowercase and unique).
- Preferred response language: `auto`, `en`, `bn`, `hi`, or `ar`.
- Usage context/pattern (up to 500 characters).
- Custom instructions (up to 4,000 characters).
- JSON preferences for user customization.

Example:

```python
profile = db.get_user_settings(user_id=authenticated_user_id)
db.update_user_settings(
    user_id=authenticated_user_id,
    language="bn",
    usage_pattern="Study and software development",
    custom_instructions="Answer in Bangla and include practical examples.",
    preferences={"tone": "concise"},
)
```

Always obtain `user_id` from a verified server-side login session. Never accept
it as authoritative from request JSON or a browser form. The chat assistant
adds the user's language and custom instructions to its prompt, while treating
profile metadata as lower-priority context that cannot override system or
safety instructions.

The settings model is created by SQLAlchemy `create_all` without changing
existing user table columns. Profile/settings API endpoints and a frontend
settings screen must still be connected by the application layer. Protect
profile email changes with the application's normal email verification flow.
