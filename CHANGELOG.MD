# 2022/10/16

- Add flarum application.

## Application

- Add `toggle_ssl(self, toggle: bool) -> OperatingRes` method.
  - It is called when the user switches the ssl state of the website.
- Add `update_domain(self, old_domain: str, new_domain: str) -> OperatingRes` method.
  - The website's main domain name is called when it is updated. 

## Breaking

- Update `read(*args, **kwargs)-> ApplicationWebServerConfig` abstract method.