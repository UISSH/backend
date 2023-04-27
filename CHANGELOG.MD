# 2023/04/05

## Update

### New features

- django app
  - Add 'iptables' django app
  - Add 'crontab' app

- website application
  - Add flarum application.

- other
  - Add execute command api
  - Add get website default config api

### Changes

application interface:

- change `localStorage` to `dbStorage` for application config, and mark `localStorage` as deprecated.

wordpress application:

- update version to 6.2 from 6.0.1

### Website application interface

- Add `toggle_ssl(self, toggle: bool) -> OperatingRes` method.
  - It is called when the user switches the ssl state of the website.
- Add `update_domain(self, old_domain: str, new_domain: str) -> OperatingRes` method.
  - This method is called when the website domain name (excluding subdomains) is updated.
- Add `get_boot_status`, `get_run_status`, `get_requried_ports`, `get_requried_databases` methods.


## Breaking

- Update `read(*args, **kwargs)-> ApplicationWebServerConfig` abstract method.
- rename 'api/OperatingRes' to 'api/Operating' and 'Operating.query' method to 'get' from 'post'.
