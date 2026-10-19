import frida
import sys
import os
import json

# 配置目标 App 包名和 JS 脚本路径
PACKAGE_NAME = "com.gof.global"  # 替换为你的目标包名
JS_FILE = "hook4.js"
OUTPUT_FILE = "libnesec_decrypted4.so"
JSON_FILE = "address_alignment_map.json"

chunks_dict = {}
base_addr = 0
total_size = 0

def on_message(message, data):
    global chunks_dict, base_addr, total_size
    
    # 正确处理 js 端发来的 console.log
    if message['type'] == 'log':
        print(message['payload'])
        
    elif message['type'] == 'send':
        payload = message['payload']
        
        # 1. 接收文件块
        if payload.get('type') == 'dump_chunk':
            addr = int(payload['addr'], 16)
            chunks_dict[addr] = data
            print(f"\r[+] 接收数据块: {hex(addr)} ({payload['size']} bytes)", end="")
            
        # 2. 文件块发送完毕，拼接并保存 SO
        elif payload.get('type') == 'dump_complete':
            base_addr = int(payload['base'], 16)
            total_size = payload['totalSize']
            dumped_size = payload['dumpedSize']
            
            print(f"\n[+] 传输完成！模块基址: {hex(base_addr)}, 总大小: {total_size}, 实际读取: {dumped_size}")
            print("[*] 开始拼接文件...")
            
            with open(OUTPUT_FILE, "wb") as f:
                current_addr = base_addr
                end_addr = base_addr + total_size
                
                while current_addr < end_addr:
                    if current_addr in chunks_dict:
                        chunk_data = chunks_dict[current_addr]
                        f.write(chunk_data)
                        current_addr += len(chunk_data)
                    else:
                        # 缺失的页用 0 填充防错位
                        f.write(b'\x00' * 4096)
                        current_addr += 4096
            
            print(f"[✔️] 保存成功！解密后的 SO 文件路径: {os.path.abspath(OUTPUT_FILE)}")
            print("[*] 等待 Frida 提取外部依赖和地址对齐数据...")
            
        # 3. 接收并保存地址对齐映射 JSON，完成后退出
        elif payload.get('type') == 'alignment_data':
            alignment_info = payload.get('data')
            
            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(alignment_info, f, indent=4, ensure_ascii=False)
                
            print("\n[✔️] 地址对齐和外部依赖数据已提取！")
            print(f"[✔️] 保存路径: {os.path.abspath(JSON_FILE)}")
            
            print("\n--- 引用的外部库及其基址 ---")
            for lib, base in alignment_info['libraries'].items():
                print(f"  - {lib}: {base}")
                
            print("\n[*] 所有任务完成，安全退出。")
            sys.exit(0)

    elif message['type'] == 'error':
        print(f"[-] Frida Error: {message['stack']}")

def main():
    try:
        device = frida.get_device_manager().add_remote_device('127.0.0.1:31337')
        pid = device.spawn([PACKAGE_NAME])
        session = device.attach(pid)
        
        with open(JS_FILE, 'r', encoding='utf-8') as f:
            script_code = f.read()
            
        script = session.create_script(script_code)
        script.on('message', on_message)
        script.load()
        
        device.resume(pid)
        print(f"[*] 已启动 App: {PACKAGE_NAME}，等待 SO 解密...")
        
        sys.stdin.read()
    except Exception as e:
        print(f"[-] 发生错误: {e}")

if __name__ == '__main__':
    main()