from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QPixmap
from PIL import Image
import numpy as np
import sys
import os

main_gui_file_name = "/Users/anonymous/Desktop/open_lcd_assissatnt/open_lcd_assistant/main_gui.ui"
EIGHT_BIT = 8

Ui_MainWindow, QtBaseClass = uic.loadUiType(main_gui_file_name)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    __image_path = ""
    __image_width = 0
    __image_height = 0

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.load_button.clicked.connect(self.load_image)
        self.save_button.clicked.connect(self.save_bmp_txt)

    def load_image(self):
        # Get the image path
        self.__image_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File', QtCore.QDir.rootPath() , '*.bmp')
        self.path_line_edit.setText(self.__image_path)

        if os.path.isfile(self.__image_path):
            # Load the image
            image = Image.open(self.__image_path)
            # convert it to monochrom bitmap and creat np array
            image_bmp = image.convert('1')
            image_array = np.asarray(image_bmp,dtype=int)
            self.__image_width, self.__image_height = image_array.shape
            # display the image
            self.__display_image()


    def __display_image(self):
        """
        Ref : https://www.codespeedy.com/displaying-an-image-using-pyqt5-in-python/
        """
        scene = QtWidgets.QGraphicsScene(self)
        pixmap = QPixmap(self.__image_path)
        item = QtWidgets.QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        self.image_view.setScene(scene)


    def save_bmp_txt(self):
        pass


    def __format_image(self, width, height, moon_array):
        pad_x, pad_y =(EIGHT_BIT - (width % EIGHT_BIT)), (EIGHT_BIT - (height%EIGHT_BIT))
        formated_image_array  = np.pad(moon_array,  [(0,pad_x ), (0,pad_y )], mode='constant')

        return formated_image_array


    def __convert_vertical(self):
        byte_array = ""
        index = 0
        for y in range(0,self.__image_width,EIGHT_BIT):
            for x in range(self.__image_height):
                one_byte = pad_array[y:y+8,x]
                a = (''.join(str(y) for y in np.flip(one_byte)))
                byte_array += '0x'+format((int(a, 2)), '02x')+','
                index += 1
                if index%16 == 0:
                    byte_array += '\n'
                    
        byte_array = '{\n' + byte_array.strip()[:-1] + '};' # remove the last comma  
        
        return byte_array 





if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())