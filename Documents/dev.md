|Version| md5 |json|
| :--: | :--: | :--: |
|2 bytes|  32bytes | N bytes|


请求

	{
		"method":"get",
		"url":"http://baidu.com",
		"headers":{
			"cookie":"NMB",
		},
		"data":"base64ed",
		"content":"base64ed",
		"requestid":"hash",
		"proxies":{
			"http":"",
			"https":""
		}	
	}

返回

	{
		"method":"return",
		"requestid":"hash",
		"state":200,
		"url":"http://baidu.com",
		"headers":{
			"cookie":"NMB",
		},
		"content":"base64ed"
	}


胶水拓展库
| 请求 | web |解析程序|数据库连接器|
| :--: | :--: | :--: |:--:|
|固定|  可选 | 自行编写|可选|

数据库信息

	{
		"serverid":"hash",
		"type":0, #0:分发器解析器 1:抓取器
		"last_activate_time":1510000000, #timestamp
		"cpu":{
			"cores_num":1,
			"useage":0.05
		},
		"memory":{
			"max":1024 * 1024 * 1024, #1GB
			"useage": 400 * 1024 * 1024
		},
		"network":{
			"max_10_minutes": 1024 * 1024 * 1024, #1GB
			"min_10_minutes": 1024 * 1024 * 1024, #1GB
			"average_10_minutes": 1024 * 1024 * 1024 #1GB
		},
		"requests":{
			"current_requests_num":100,
			"average_delay":2000, #ms
			"requests_per_s":1000
		},
		"core":{
			"gevents_num":100,
			"queue_length":100
		}
	}

TCP传输 Python实现

	from Crypto.Cipher import AES
	import struct
	from hashlib import md5
	
	class CryptoTCP:
	    def __init__(self, key = b"0" * 16, iv = b"0" * 16, version = 1):
	        self.key = key
	        self.iv = iv
	        self.version = version
	
	    def Encrypt(self, data=""):
	        cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
	        pack = struct.Struct("h32s")
	        pack = pack.pack(self.version, md5(data.encode()).hexdigest().encode())
	        pack += cipher.encrypt(data.encode())
	        return pack
	
	    def Decrypt(self, data):
	        cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
	        unpack = struct.Struct("h32s")
	        unpack = unpack.unpack(data[:34])
	        version = unpack[0]
	        md5 = unpack[1].decode()
	        data = cipher.decrypt(data[34:])
	        return {
	            "version": version,
	            "md5": md5,
	            "data": data.decode()
	        }
	
	if __name__ == "__main__":
	    ct = CryptoTCP()
	    enc = ct.Encrypt("MDZZ")
	    print(enc)
	    print(ct.Decrypt(enc))