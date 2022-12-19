from mastodon import Mastodon


Mastodon.create_app(
    "audiotarky_app",
    api_base_url="https://mas.to",
    to_file="pytooter_clientcred.secret",
)
