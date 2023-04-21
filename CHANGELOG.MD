# 2023/04/05

## Update

### New features

- Add flarum application.
- Add 'iptables' django app
- Add execute command api
- Add get website default config api

### Changes

application interface:

- change `localStorage` to `dbStorage` for application config, and mark `localStorage` as deprecated.

wordpress application:

- update version to 6.2 from 6.0.1

### Application interface

- Add `toggle_ssl(self, toggle: bool) -> OperatingRes` method.
  - It is called when the user switches the ssl state of the website.
- Add `update_domain(self, old_domain: str, new_domain: str) -> OperatingRes` method.
  - This method is called when the website domain name (excluding subdomains) is updated.

## Breaking

- Update `read(*args, **kwargs)-> ApplicationWebServerConfig` abstract method.
- rename 'api/OperatingRes' to 'api/Operating' and 'Operating.query' method to 'get' from 'post'.
