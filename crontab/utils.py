import json
import logging
import os
import tempfile


def list_by_osquery():
    """
    List all crontab tasks by osquery.
    """
    pass
    # check if osquery is installed
    if os.system("which osquery") == 0:
        return []

    # use popen to get crontab tasks
    osquery_cmd = "osqueryi --json \"select * from crontab where path like '%root';\""
    osquery_result = os.popen(osquery_cmd).read()
    task_list = []
    try:
        osquery_result = json.loads(osquery_result)
        for i in osquery_result:
            if i["event"]:
                task = f'{i["event"]}    {i["command"]}'
            else:
                task = f'{i["minute"]} {i["hour"]} {i["day_of_month"]} {i["month"]} {i["day_of_week"]}    {i["command"]}'

            task_list.append(task)

    except Exception as e:
        logging.error(f"failed to parse osquery result: {e}")
        return []
    return task_list


class CronTab:
    def __init__(self) -> None:
        self.crontab_file = tempfile.NamedTemporaryFile().name
        self.data = self.list()
        os.system(f"touch {self.crontab_file}")

    def list(self):
        data = list_by_osquery()

        if data:
            return data
        else:
            raise Exception("failed to get crontab list")

    def add(
        self,
        schedule_expressions: str,
        cmd: str,
    ) -> None:
        cron = f"{schedule_expressions.strip()}    {cmd.strip()}"
        if cron not in self.data:
            self.data.append(cron)

    def remove(
        self,
        schedule_expressions: str,
        cmd: str,
    ) -> None:
        cron = f"{schedule_expressions.strip()}    {cmd.strip()}"
        if cron in self.data:
            self.data.remove(cron)

    def save(self) -> None:
        """
        It will save the crontab to the system.
        """

        crontab_context = "\n".join(self.data) + "\n"

        with open(self.crontab_file, "w") as f:
            f.write(crontab_context)

        os.system("crontab {}".format(self.crontab_file))

    def __del__(self):
        os.system(f"rm {self.crontab_file}")


if __name__ == "__main__":
    cron = CronTab()
    cron.add("* * * * *", "echo 1")
    cron.save()

    cron.remove("* * * * *", "echo 1")
    cron.add("* * * * *", "echo `date` >> /root/crontab.log")
    cron.remove("* * * * *", "echo `date` >> /root/crontab.log")
    cron.add("* * * * *", "echo `date` >> /root/crontab.log")
    cron.save()
