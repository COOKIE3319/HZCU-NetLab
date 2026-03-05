# Decompiled from ping_cmd.pyc (Python 3.8)
import time
import struct
import socket
import select


def chesksum(data):
    n = len(data)
    m = n % 2
    sum = 0
    for i in range(0, n - m, 2):
        sum += data[i] + (data[i + 1] << 8)
    if m:
        sum += data[-1]
    sum = (sum >> 16) + (sum & 65535)
    sum += sum >> 16
    answer = ~sum & 65535
    answer = answer >> 8 | (answer << 8 & 65280)
    return answer


def request_ping(data_type, data_code, data_checksum, data_ID, data_Sequence, payload_body):
    icmp_packet = struct.pack('>BBHHH32s', data_type, data_code, data_checksum, data_ID, data_Sequence, payload_body)
    icmp_chesksum = chesksum(icmp_packet)
    icmp_packet = struct.pack('>BBHHH32s', data_type, data_code, icmp_chesksum, data_ID, data_Sequence, payload_body)
    return icmp_packet


def raw_socket(dst_addr, icmp_packet):
    '''连接套接字,并将数据发送到套接字'''
    rawsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
    send_request_ping_time = time.time()
    rawsocket.sendto(icmp_packet, (dst_addr, 80))
    return (send_request_ping_time, rawsocket, dst_addr)


def reply_ping(send_request_ping_time, rawsocket, data_Sequence, timeout=2):
    while True:
        started_select = time.time()
        what_ready = select.select([rawsocket], [], [], timeout)
        wait_for_time = time.time() - started_select
        if what_ready[0] == []:
            return -1
        time_received = time.time()
        received_packet, addr = rawsocket.recvfrom(1024)
        icmpHeader = received_packet[20:28]
        type, code, checksum, packet_id, sequence = struct.unpack('>BBHHH', icmpHeader)
        if type == 0 and sequence == data_Sequence:
            return time_received - send_request_ping_time
        timeout = timeout - wait_for_time
        if timeout <= 0:
            return -1


def dealtime(dst_addr, sumtime, shorttime, longtime, accept, i, time):
    sumtime += time
    print(sumtime)
    if i == 4:
        print('{0}的Ping统计信息：'.format(dst_addr))
        print('数据包：已发送={0},接收={1}，丢失={2}（{3}%丢失），\n往返行程的估计时间（以毫秒为单位）：\n\t最短={4}ms，最长={5}ms，平均={6}ms'.format(
            i + 1, accept, i + 1 - accept, ((i + 1 - accept) / (i + 1)) * 100, shorttime, longtime, sumtime))


def ping(host, con):
    send, accept, lost = 0, 0, 0
    sumtime, shorttime, longtime, avgtime = 0, 1000, 0, 0
    data_type = 8
    data_code = 0
    data_checksum = 0
    data_ID = 0
    data_Sequence = 1
    payload_body = bytes(con, 'utf-8')
    dst_addr = socket.gethostbyname(host)
    print('正在 Ping {0} [{1}] 具有 {2} 字节的数据:'.format(host, dst_addr, len(payload_body)))
    for i in range(0, 4):
        send = i + 1
        icmp_packet = request_ping(data_type, data_code, data_checksum, data_ID, data_Sequence + i, payload_body)
        send_request_ping_time, rawsocket, addr = raw_socket(dst_addr, icmp_packet)
        times = reply_ping(send_request_ping_time, rawsocket, data_Sequence + i)
        if times > 0:
            print('来自 {0} 的回复: 字节={1} 时间={2}ms'.format(addr, len(payload_body), int(times * 1000)))
            accept += 1
            return_time = int(times * 1000)
            sumtime += return_time
            if return_time > longtime:
                longtime = return_time
            if return_time < shorttime:
                shorttime = return_time
            time.sleep(0.7)
        else:
            lost += 1
            print('请求超时。')
        if send == 4:
            print('{0}的Ping统计信息:'.format(dst_addr))
            print('\t数据包：已发送={0},接收={1}，丢失={2}（{3}%丢失），\n往返行程的估计时间（以毫秒为单位）：\n\t最短={4}ms，最长={5}ms，平均={6}ms'.format(
                i + 1, accept, i + 1 - accept, ((i + 1 - accept) / (i + 1)) * 100, shorttime, longtime, sumtime / send))
