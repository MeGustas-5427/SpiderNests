class Packer:
    def pack(self, arr):
        """
        Pack dict to two-dimension
        :param arr: dict
        :return: packed dict
        """
        temp = {}
        if isinstance(arr, list):
            for i in range(len(arr)):
                temp[i] = arr[i]
            next = temp
            return self.pack(next)
        elif isinstance(arr, dict):
            a = {}
            for i in arr.keys():
                deep = self.pack(arr[i])
                if isinstance(deep, dict):
                    for j in deep.keys():
                        temp = str(i) + "::" + str(j)
                        a[temp] = deep[j]
                else:
                    temp = str(i)
                    a[temp] = deep
            return a
        return arr

    def unpack(self, plain):
        """
        Unpack Packed-redis-data
        :param plain: packed dict
        :return: unpacked value
        """
        arr = {}
        for i in plain.keys():
            s = i.split("::")
            if len(s) != 0 and s != ['']:
                if s[0] not in arr.keys():
                    arr[s[0]] = {}
            else:
                return plain['']
        for i in arr.keys():
            temp = {}
            for j in plain.keys():
                s = j.split("::")
                if len(s) != 0 and s[0] == i:
                    temp["::".join(s[1:])] = plain[j]
            arr[i] = self.unpack(temp)
        return arr
