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
    logging.debug(f"osquery result: {osquery_result}")
    task_list = []
    try:
        osquery_result = json.loads(osquery_result)
        for i in osquery_result:
            if i["event"]:
                task = f'{i["event"]}    {i["command"]}'
            else:
                task = f'{i["minute"]} {i["hour"]} {i["day_of_month"]} {i["month"]} {i["day_of_week"]}    {i["command"]}'

            print(task)
            task_list.append(task)

    except Exception as e:
        logging.error(f"failed to parse osquery result: {e}")
        return []
    return task_list


class CronTab:
    def __init__(self) -> None:
        self.crontab_file = tempfile.NamedTemporaryFile().name
        self.__init__crontab()

    def __init__crontab(self) -> None:
        os.system("crontab -l > {}".format(self.crontab_file))
        with open(self.crontab_file) as f:
            self.crontab_context = f.read()
            self._crontab_context = self.crontab_context

    def list(self):
        data = list_by_osquery()

        if data:
            return data

        crontab_file = tempfile.NamedTemporaryFile().name
        os.system("crontab -l > {}".format(crontab_file))
        with open(crontab_file) as f:
            data = f.read().strip()
            if data:
                data = data.split("\n")
            else:
                data = []
            return data

    def add(
        self,
        schedule_expressions: str,
        cmd: str,
    ) -> None:
        cron = f"{schedule_expressions.strip()}    {cmd.strip()}"

        # Format existing crontab
        item_list = self.crontab_context.split("\n")
        for i in item_list:
            if schedule_expressions.strip() in i and cmd.strip() in i:
                self.crontab_context = self.crontab_context.replace(i, cron)

        if cron in self.crontab_context:
            return
        else:
            self.crontab_context += "{}\n".format(cron)

    def remove(
        self,
        schedule_expressions: str,
        cmd: str,
    ) -> None:
        cron = f"{schedule_expressions.strip()}    {cmd.strip()}"
        if cron in self.crontab_context:
            self.crontab_context = self.crontab_context.replace(cron, "")

    def save(self) -> None:
        """
        It will save the crontab to the system.
        """
        self.crontab_context = self.crontab_context.replace("\n\n", "\n")

        with open(self.crontab_file, "w") as f:
            f.write(self.crontab_context)
            self._crontab_context = self.crontab_context
        os.system("crontab {}".format(self.crontab_file))

    def __del__(self):
        if self.crontab_context != self._crontab_context:
            print(
                "Warning: You have modified the crontab, but it is not saved in the system."
            )
        os.remove(self.crontab_file)


if __name__ == "__main__":
    cron = CronTab()
    cron.add("* * * * *", "echo 1")
    cron.save()
    print(cron.list())
    cron.remove("* * * * *", "echo 1")
    cron.add("* * * * *", "echo `date` >> /root/crontab.log")
    cron.remove("*/10 * * * *", "echo `date` >> /root/crontab.log")
    cron.save()
    print(cron.list())
