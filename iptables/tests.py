from pprint import pprint


def test_list():
    text = """ufw status 
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere                  
80/tcp                     ALLOW       Anywhere                  
443/tcp                    ALLOW       Anywhere                  
8080/tcp                   ALLOW       Anywhere                  
80/tcp                     ALLOW       192.168.1.100             
80                         ALLOW       192.168.1.100             
80/udp                     ALLOW       192.168.1.100             
127.0.0.1 80/udp           ALLOW       192.168.1.100             
192.168.2.200 123:133/udp  ALLOW       192.168.1.100 123:133/udp 
22/tcp (v6)                ALLOW       Anywhere (v6)             
80/tcp (v6)                ALLOW       Anywhere (v6)             
443/tcp (v6)               ALLOW       Anywhere (v6)             
8080/tcp (v6)              ALLOW       Anywhere (v6)"""

    lines = text.splitlines()
    first = lines[3].find('To')
    second = lines[3].find('Action')
    third = lines[3].find('From')

    area = []
    for (index, line) in enumerate(lines[5:]):
        To = line[first:second]
        Action = line[second:third]
        From = line[third:]
        data = {
            "ID": index+1,
            "to": To.strip(),
            "action": Action.strip(),
            "from": From.strip(),
        }

        area.append(data)
    pprint(area, indent=2)


test_list()
