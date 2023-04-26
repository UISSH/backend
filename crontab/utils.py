import os
import tempfile


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
        crontab_file = tempfile.NamedTemporaryFile().name
        os.system("crontab -l > {}".format(crontab_file))
        with open(crontab_file) as f:
            data = f.read().strip()
            if data:
                data = data.split("\n")
            else:
                data = []
            return data

    def add(self, cron: str) -> None:
        if cron in self.crontab_context:
            return
        else:
            self.crontab_context += "{}\n".format(cron)

    def remove(self, cron: str, strict=True) -> None:
        if strict:
            if cron in self.crontab_context:
                self.crontab_context = self.crontab_context.replace(cron, "")
        else:
            _cron_list = self.crontab_context.split("\n")
            new_crontab = []
            for item in _cron_list:
                if cron in item:
                    continue
                new_crontab.append(item)
            self.crontab_context = "\n".join(new_crontab) + "\n"

    def save(self) -> None:
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
    cron.add("*/5 * * * * /path/to/command")
    cron.save()
    print(cron.list())
    cron.remove("*/5 * * * * /path/to/command")
    cron.save()
    print(cron.list())
