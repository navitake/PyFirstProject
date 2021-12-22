
import pyocr
import cv2
import numpy
import io
from PIL import Image,ImageOps


class OcrClass:
    @staticmethod
    def funcOCR(imageString) -> str:

        # tesseract取得
        pyocr.tesseract.TESSERACT_CMD = r"C:\Users\kakeh\scoop\apps\tesseract\5.0.0.20211201\tesseract.exe"
        tools = pyocr.get_available_tools()
        tool = tools[0]

        #文字列をバイナリに変換
        print(imageString)
        # rawImage = Image.open(imageString)
        imageArray = numpy.asarray(bytearray(imageString),dtype=numpy.uint8)

        # openCVで画像加工
        cvImage = cv2.imdecode(imageArray,flags=1)
        if cvImage.any() == None:
            print("cvImage is Null")
            return
        
        cv2.imwrite("read.png", cvImage)
        #cvImage = cv2.resize(cvImage,dsize=(1000,1000))
        gray = cv2.cvtColor(cvImage, cv2.COLOR_BGR2GRAY)
        ret,threded = cv2.threshold(gray,100,255,cv2.THRESH_BINARY_INV)

        # 書き出し
        cv2.imwrite("target.png", cvImage)
        outputString = tool.image_to_string(Image.open(
            "target.png"), lang="jpn+eng", builder=pyocr.builders.TextBuilder(tesseract_layout=6))

        return outputString

    def __init__(self) -> None:
        pass

