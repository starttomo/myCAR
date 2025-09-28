#!/usr/bin/env python3
import subprocess
import sys

# 获取提交次数
count = int(subprocess.run(['git', 'rev-list', '--count', 'HEAD'],
                         capture_output=True, text=True).stdout.strip())

subprocess.run(f'git add . && git commit -m "这是第{count+1}次提交" && git push origin main',
               shell=True, check=True)