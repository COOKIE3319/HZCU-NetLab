# Decompiled from netlab.exe (Python 3.8, PyInstaller 5.0.1)
import os, sys, wget, pandas as pd
from ssh_cmd import MySSH
from http_cmd import getHTMLText
from onekey import GetOneKey
from ping_cmd import ping
import socket, time, random, zipfile, base64, datetime

DEBUG = False
port_http = {
    '0': 9096, '1': 8970, '2': 9263, '3': 8368, '4': 9418,
    '5': 9517, '6': 9632, '7': 8761, '8': 8414, '9': 8076
}
hostName = "10.66.56.8"
port_tcp = lambda x: 6230 + (int(x[5]) + int(x[7])) % 10
port_udp = lambda x: 6570 + (int(x[5]) + int(x[7])) % 10
cmd = [
    'ping_fun(hostName, af)',
    'get_html_fun(xh_in)',
    'tcp_fun(hostName, xh_in, af)',
    'udp_fun(hostName, xh_in, af)',
    'ssh_cmd(hostName, af)'
]


def ping_fun(hostName, tmp_df):
    try:
        print("Start Net Test....")
        con = tmp_df["ping_dat"].values[0]
        if DEBUG == True:
            print("Send Data: {}".format(con))
        ping(hostName, con)
        print("正在执行Ping测试，请等待......")
        time.sleep(2)
        print("完成Ping测试！")
    except:
        print("Ping测试失败")


def get_html_fun(n):
    try:
        port = port_http["%s" % ((int(n[4:6]) + int(n[6:8])) % 10)]
        fn = f'{dic["fname"]}'
        url = "http://{}:{}/{}".format(hostName, port, fn)
        resp = getHTMLText(url)
        print("正在打开网页并爬取数据，请等待......")
        time.sleep(2)
        s = resp[resp.find("<body>") + 7:resp.find("</body>")].replace("\\n", "")
        s = base64.decodebytes(eval(s)).decode()
        if DEBUG == True:
            print("Send Data: {}".format(s))
        if n in s:
            print("成功爬取文件！！")
        else:
            print("爬取文件错误!!")
        print("完成网页爬取!")
    except:
        print("网页爬取失败")


def tcp_fun(hst, n, tmp_df):
    try:
        port = port_tcp(n)
        address = (hst, port)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(address)
        print("SERVER CONNECT SUCCESS")
        content = tmp_df["tcp_dat"].values[0]
        if DEBUG == True:
            print("Send Data: {}".format(content))
        client.send(bytes(content, encoding="utf-8"))
        content = client.recv(1024)
        rcvdat = content.decode("utf-8")
        if DEBUG == True:
            print("Rcv Data: {}".format(rcvdat))
        if content.decode() in rcvdat:
            print("Received TCP Data， Success！")
        else:
            print("Received TCP Data， ERROR！")
        time.sleep(0.5)
        client.close()
        print("使用Socket执行TCP通讯，发送并接收数据，请等待......")
        time.sleep(2)
        print("完成TCP通讯!")
    except:
        print("TCP通讯失败")


def udp_fun(hst, n, tmp_df):
    try:
        port = port_udp(n)
        address = (hst, port)
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        content = tmp_df["udp_dat"].values[0]
        if DEBUG == True:
            print("Send Data: {}".format(content))
        client.sendto(bytes(content, encoding="utf-8"), address)
        content, addr = client.recvfrom(1024)
        rcvdat = content.decode("utf-8")
        if DEBUG == True:
            print("Rcv Data: {}".format(rcvdat))
        if content.decode() in rcvdat:
            print("Received UDP Data， Success！")
        else:
            print("Received UDP Data， ERROR！")
        time.sleep(0.5)
        client.close()
        print("执行UDP通讯，发送并接收数据，请等待......")
        time.sleep(2)
        print("完成UDP通讯!")
    except:
        print("UDP通讯失败")


def ssh_cmd(hst, tmp_df):
    try:
        port = 22
        username = "S%s" % tmp_df["xh"].values[0]
        passstr = tmp_df["ps"].values[0]
        xh = tmp_df["xh"].values[0]
        password = "N%s%s" % (passstr, xh[6:8])
        my_ssh = MySSH(hst, port)
        print("正在登录服务器，执行指令，请等待......")
        my_ssh.connect(username, password)
        cmd = "uptime;who am i"
        my_ssh.exec_cmd(cmd)
        my_ssh.close()
        time.sleep(2)
        print("完成SSH登录!")
    except:
        print("登录失败")


if __name__ == "__main__":
    try:
        t = datetime.datetime.now().strftime("%m-%d %H:%M")
        print("{}".format("*").center(60, "*"))
        print("{}".format(t).center(60, "-"))
        print("{}".format("      1、请确保你使用校园有线网络, ** 使用校园有线网络 **"))
        print("{}".format("      2、开启Wireshark软件，选择正确网卡, 进入数据捕获！"))
        print("{}".format("*").center(60, "*"))
        print("")
        GetOneKey()
        xh_in = input("Input XH(请输入8位学号):")
        ps_in = input("Input Password(请输入4位密码):")
        ps_in = "%s" % ps_in
        print("\\n正在读取网络通讯配置文件.......")
        url = "http://{}:8180/info.zip".format(hostName)
        filenames = "tmp_part"
        if os.path.exists(filenames):
            os.remove(filenames)
        print("Downloading ")
        try:
            wget.download(url, out=filenames)
        except:
            print("\nCan't Connect to Host!!")
            if os.path.exists(filenames):
                os.remove(filenames)
            sys.exit(0)
        print("\nDownload Success!!")
        try:
            zf = zipfile.ZipFile(filenames)
            filenamed = "config.xlsx"
            zf.extract(filenamed, pwd=b'NetLAB06102025')
            zf.close()
        except:
            print("\n解压密码错误t!!")
            zf.close()
            if os.path.exists(filenamed):
                os.remove(filenamed)
            sys.exit(0)
        df = pd.read_excel(filenamed)
        if os.path.exists(filenamed):
            os.remove(filenamed)
        if os.path.exists(filenames):
            os.remove(filenames)
        df["xh"] = df["xh"].astype(str)
        df["ps"] = df["ps"].astype(str)
        tmp = df[df["xh"] == xh_in]
        af = pd.DataFrame()
        dic = dict()
        if len(tmp) != 1:
            print("Load Config Error!!")
            print("不存在这样的学号!!\n")
            sys.exit(0)
        else:
            print("Load Config Success!!")
        password = tmp["ps"].values[0]
        dic["xh"] = xh_in
        dic["ps"] = password
        if ps_in.strip() != password.strip():
            print("密码错误，请检查后再试！！！")
            sys.exit(0)
        dic["ps"] = tmp["ps"].values[0]
        dic["fname"] = tmp["fname"].values[0]
        dic["ping_dat"] = base64.decodebytes(eval(tmp["ping_dat"].values[0])).decode()
        dic["html_port"] = int(tmp["html_port"].values[0])
        dic["html_dat"] = base64.decodebytes(eval(tmp["html_dat"].values[0])).decode()
        dic["tcp_port"] = int(tmp["tcp_port"].values[0])
        dic["udp_port"] = int(tmp["udp_port"].values[0])
        dic["tcp_dat"] = base64.decodebytes(eval(tmp["tcp_dat"].values[0])).decode()
        dic["udp_dat"] = base64.decodebytes(eval(tmp["udp_dat"].values[0])).decode()
        af = pd.DataFrame([dic])
        if os.path.exists(filenamed):
            os.remove(filenamed)
        if os.path.exists(filenames):
            os.remove(filenames)
        print("\n请 %s同学 检查并准备测试。\n" % tmp["name"].values[0])
        GetOneKey()
        print("")
        print("{}".format(" ***准备Telnet通信*** ").center(60, "<"))
        print("请开启新的窗口，准备登录Telnet服务器，IP：{}, Port：8023".format(hostName))
        print("！！！连接Telnet后，60秒内无对话，将自动退出！！！，退出：exit")
        print("{}".format(" 请注意 ").center(60, "*"))
        print("{}".format(" 请注意! 请注意 ").center(60, "*"))
        print("{}".format("完成Telnet操作后，关闭窗口，返回NetLab测试窗口").center(60, ">"))
        GetOneKey()
        print("")
        for cmd_rnd in random.sample(cmd, 5):
            print("")
            print(cmd_rnd)
            eval(cmd_rnd)
            GetOneKey()
        else:
            print("")
            print("\n{}".format("已完成网络通讯"))
            print("{}".format("请停止WireShark数据捕获，并保存数据到文件"))
            print("{}".format("后续请使用保存数据分析"))
            print("{}".format("撰写数据分析过程及结果的实验报告，上传至学在城院平台"))
            print("{}".format('打开网页"10.66.56.8:5000", 填写分析结果并保存'))
            print("{}".format("数据通讯已完成，请进入数据分析阶段"))
            print("{}\n".format("** 祝你好运 **"))
    except:
        print("程序运行错误，请检查确认后再运行！")
        print("按任意键结束程序")
        GetOneKey()
        print("")
