import logging


def __init__():
    from .. import config

    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        data = config("SENTRY_SDK_DNS")
        if data != "null":
            print("load sentry_sdk...")
            sentry_sdk.init(
                dsn=data,
                integrations=[DjangoIntegration()],
                traces_sample_rate=1.0,
                # If you wish to associate users to errors (assuming you are using
                # django.contrib.auth) you may enable sending PII data.
                send_default_pii=True,
            )

    except Exception as e:
        logging.debug(f"load sentry sdk error: {e}")
