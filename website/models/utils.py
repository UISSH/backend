FullNginxConfig = str
SectionNginxConfig = str


def update_nginx_server_name(full_nginx_config_data: str, domain: str, sub_domain: str = None) -> FullNginxConfig:
    """
    @param full_nginx_config_data: str
    @param domain: str
    @param sub_domain: str
    @return: Modified full_nginx_config_data.
    """
    line_list: list[str] = full_nginx_config_data.split("\n")
    server_name = '*'
    for line in line_list:
        line = line.strip()
        if line.startswith("server_name"):
            server_name = line
            break
    if sub_domain is None or len(sub_domain) < 3:
        setting_server_name = f'server_name {domain};'
    else:
        setting_server_name = f'server_name {domain} {sub_domain};'

    if server_name != '*':
        full_nginx_config_data = full_nginx_config_data.replace(server_name, setting_server_name)
    return full_nginx_config_data


def disable_section(full_nginx_config_data: str, section_name: str) -> FullNginxConfig:
    """
    @param full_nginx_config_data: str
    @param section_name: str
    @return: Modified full_nginx_config_data.
    """

    def add_comment(line):
        char_list = list(line)
        if line == ' ' or line == '#':
            return line

        _insert_position = -1
        for index, item in enumerate(char_list):

            break_list = ['#', '\n', '\r']
            if item == ' ':
                continue
            if item in break_list:
                break
            _insert_position = index
            break

        if _insert_position < 0:
            return line

        char_list[_insert_position - 1] = ' #**#'
        return "".join(char_list)

    split = f'########{section_name.upper()}########'
    _data = full_nginx_config_data.split(split)
    section_data = _data[1].split('\n')

    new_data = []
    for line in section_data:
        new_data.append(add_comment(line))
    new_data = "\n".join(new_data)
    _data[1] = new_data
    return split.join(_data)


def enable_section(full_nginx_config_data, section_name) -> FullNginxConfig:
    """
     @param full_nginx_config_data: str
     @param section_name: str
     @return: Modified full_nginx_config_data.
     """
    split = f'########{section_name.upper()}########'
    data = full_nginx_config_data.split(split)
    data[1] = data[1].replace('#**#', '')
    return split.join(data)


def insert_section(full_nginx_config_data, section_data, section_name: str) -> FullNginxConfig:
    """
     @param full_nginx_config_data: str
     @param section_data: str
     @param section_name: str
     @return: Modified full_nginx_config_data.
    """

    section_name = f'########{section_name.upper()}########'
    _data = full_nginx_config_data.split(section_name)
    _data[1] = f'{section_data}'
    return section_name.join(_data)


def get_section(full_nginx_config_data: str, section_name: str) -> SectionNginxConfig:
    """

    @param full_nginx_config_data:str
    @param section_name:str
    @return: a part of full nginx config.
    """

    section_name = f'########{section_name.upper()}########'
    _data = full_nginx_config_data.split(section_name)[1]
    return _data
