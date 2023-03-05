import serial
from flask import Flask, request,jsonify

app = Flask(__name__)
# 定义串口通信参数
ser = serial.Serial()
ser.port = '38400'  # 指定串口号
ser.baudrate = 9600  # 波特率
ser.bytesize = serial.EIGHTBITS  # 数据位
ser.stopbits = serial.STOPBITS_ONE  # 停止位
ser.parity = serial.PARITY_NONE  # 校验位
ser.timeout = 1  # 超时时间
# 连接串口
try:
    ser.open()
    print("串口连接成功")
except Exception as e:
    print("串口连接失败")
    print(e)
    exit()

# 初始化指令
init_cmd = b'\xAA\x01\x0D\x49\x74\x31\x36\x30\x30\x30\x2C\x31\x30\x30\x2C\x30\x85'

#1. 定义初始化指令
@app.route('/init', methods=['GET'])

def init():
    # 发送初始化指令

    ser.write(init_cmd)

    # 接收返回值
    response = ser.read(5)#5个字节

    # 解析返回值
    if response[0] == 0x55 and response[1] == 0x01 and response[2] == 0x02:
        status = "Success"
    else:
        status = "Failed"

    # 返回结果
    return jsonify({'status': status})


# 定义控制指令
cmd_take = b'\x01'  # 取枪头
cmd_absorb_liquid = b'\xAA\x01\x0E\x49\x61\x31\x30\x30\x30\x30\x2C\x32\x30\x30\x2C\x31\x30\x9F'  # 吸液
cmd_expel_liquid = b'\x44\x61\x31\x30\x30\x30\x2C\x35\x30\x30\x2C\x32\x30\x30\x2C\x31\x30\x30\x5F'  # 吐液
cmd_mix_liquid = b'\x04'  # 混合均匀
cmd_detect_liquid_level = b'\xAA\x01\x08\x4C\x64\x31\x2C\x35\x30\x30\x30\x85'  # 读取液面检测结果


# 处理各项命令

#2. 定义吸液指令
@app.route('/absorb_liquid')
def absorb_liquid():
    # 发送初始化指令
    ser.write(cmd_absorb_liquid)

    # 接收返回值
    response = ser.read(5)#5个字节

    # 解析返回值
    if response[0] == 0x55 and response[1] == 0x01 and response[2] == 0x02:
        status = "Success"
    else:
        status = "Failed"
    # 返回结果
    return jsonify({'status': status})



#3. 定义液面检测指令
@app.route('/detect_liquid_level')
def detect_liquid_level():
    # 发送初始化指令
    ser.write(cmd_detect_liquid_level)

    # 接收返回值
    response = ser.read(5)#5个字节

    # 解析返回值
    if response[0] == 0x55 and response[1] == 0x01 and response[2] == 0x02:
        status = "Success"
    else:
        status = "Failed"

    # 返回结果
    return jsonify({'status': status})


#4. 定义吸液指令
@app.route('/absorb_liquid')
def absorb_liquid():
    # 发送初始化指令
    ser.write(cmd_absorb_liquid)

    # 接收返回值
    response = ser.read(5)#5个字节

    # 解析返回值
    if response[0] == 0x55 and response[1] == 0x01 and response[2] == 0x02:
        status = "Success"
    else:
        status = "Failed"
    # 返回结果
    return jsonify({'status': status})

#5. 定义吐液指令
@app.route('/expel_liquid')
def expel_liquid():
    # 发送初始化指令
    ser.write(cmd_expel_liquid)

    # 接收返回值
    response = ser.read(5)#5个字节

    # 解析返回值
    if response[0] == 0x55 and response[1] == 0x01 and response[2] == 0x02:
        status = "Success"
    else:
        status = "Failed"
    # 返回结果
    return jsonify({'status': status})

#6. 查询当前状态指令
@app.route('/get_status')
def get_status():
    command = 'AA01013FEB'
    ser.write(bytes.fromhex(command))
    response = ser.readline().hex()#以行为单位/将接受到的数据转换为16进制的字符串
    if response.startswith('5501'):
        status = int(response[4:6], 16)
        return jsonify({'status': status})
    else:
        return jsonify({'status': -1})

#7. 丢弃枪头指令
# 发送指令并校验返回结果
def send_cmd(cmd):
    ser.write(cmd) # 发送指令
    response = ser.read(5) # 读取响应
    if response == b'\x55\x01\x02\x00\x58':
        return True # 操作成功
    else:
        return False # 操作失败

# 定义去掉tip头指令
def drop_cmd(speed, status):
    cmd_str = 'Dt{}, {}'.format(speed, status)
    cmd_bytes = bytearray(cmd_str.encode())
    checksum = sum(cmd_bytes) & 0xFF    #计算一个命令的校验和
    return b'\xAA\x01\x12' + cmd_bytes + bytearray([checksum])

# 使用去头指令丢弃枪头
def drop(speed, status):
    cmd = drop_cmd(speed, status)
    return send_cmd(cmd)


#8. 混合均匀
#相对距离向上移动
def up(distance, speed_run,speed_stop):
    cmd_str = 'Up{}, {}'.format(distance, speed_run,speed_stop)
    cmd_bytes = bytearray(cmd_str.encode())
    checksum = sum(cmd_bytes) & 0xFF    #计算一个命令的校验和
    return b'\xAA\x01\x12' + cmd_bytes + bytearray([checksum])
#相对距离向下移动
def down(distance, speed_run,speed_stop,dis_back):
    cmd_str = 'Dp{}, {},{},{}'.format(distance, speed_run,speed_stop,dis_back)
    cmd_bytes = bytearray(cmd_str.encode())
    checksum = sum(cmd_bytes) & 0xFF    #计算一个命令的校验和
    return b'\xAA\x01\x12' + cmd_bytes + bytearray([checksum])

#移动
def mix_liquid(distance, speed_run,speed_stop):
        up_cmd = up(distance, speed_run,speed_stop)
        down_cmd = down(distance, speed_run,speed_stop,dis_back)
        # 接收返回值
        response = ser.read(5)#5个字节

        # 解析返回值
        if response[0] == 0x55 and response[1] == 0x01 and response[2] == 0x02:
            status = "Success"
        else:
            status = "Failed"
        # 返回结果
        return jsonify({'status': status})


if __name__ == '__main__':
        app.run(debug=True)  # 运行Flask应用程序
