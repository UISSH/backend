import json
import subprocess
from dataclasses import dataclass

from base.utils.format import format_os_query_result


@dataclass
class OSQueryResult:
    out: str
    err: str


def os_query_json(sql) -> OSQueryResult:
    res = subprocess.Popen(['osqueryi', '--json', sql],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)

    out, err = res.communicate()

    err = ''
    if out:
        out = json.loads(format_os_query_result(out.decode()))
    else:
        out = []
    if err:
        err = out.decode()

    return OSQueryResult(out=out, err=err)
