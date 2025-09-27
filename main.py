import sys
import os
import cv2
from PyQt5.QtWidgets import QApplication
from ui_main import LicensePlateRecognizer
import traceback
def exception_hook(exctype, value, tb):
    print("全局异常捕获:")
    traceback.print_exception(exctype, value, tb)
    sys.__excepthook__(exctype, value, tb)

if __name__ == "__main__":
    # 添加当前目录到Python路径

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    app = QApplication(sys.argv)
    window = LicensePlateRecognizer()
    window.show()
    sys.exit(app.exec_())
    sys.excepthook = exception_hook