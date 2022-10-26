# 2022/10/16

- Add flarum application.

## Application

- Add `toggle_ssl(self, toggle: bool) -> OperatingRes` method.
  - It is called when the user switches the ssl state of the website.
- Add `update_domain(self, old_domain: str, new_domain: str) -> OperatingRes` method.
  - This method is called when the website domain name (excluding subdomains) is updated.

## Breaking

- Update `read(*args, **kwargs)-> ApplicationWebServerConfig` abstract method.