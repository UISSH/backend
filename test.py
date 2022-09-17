class CustomList(list):
    def __getattribute__(self, item):
        methods = ['append', 'clear', 'copy', 'extend', 'insert', 'pop', 'remove']
        if item not in methods:
            return super(CustomList, self).__getattribute__(item)

        method = super(CustomList, self).__getattribute__(item)

        def length_change(*args, **kwargs):
            data = method(*args, **kwargs)
            # 改造下面一行代码就能实现通知了
            print(f"len:{len(self)}")
            return data

        return length_change


if __name__ == '__main__':
    a = CustomList()
    a.append(1)
    a.append(1)
    a.append(1)
    a.append(1)
    a.pop()
    """
    len:1
    len:2
    len:3
    len:4
    len:3
    """
