active_users = set()


def register_user(user_id):
    active_users.add(user_id)


def get_active_users():
    return list(active_users)
