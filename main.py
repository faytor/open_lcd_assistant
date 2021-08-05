from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QPixmap
from PIL import Image
import numpy as np
import sys
import os

"""
References:
    - https://xbm.jazzychad.net/
"""

main_gui_file_name = "/Users/anonymous/Desktop/open_lcd_assissatnt/open_lcd_assistant/main_gui.ui"
EIGHT_BIT = 8

Ui_MainWindow, QtBaseClass = uic.loadUiType(main_gui_file_name)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    __image_path = None
    __image_width = 0
    __image_height = 0
    image_array = None

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.init_gui()
        self.load_button.clicked.connect(self.load_image)
        self.save_button.clicked.connect(self.save_bmp_txt)
        self.convert_button.clicked.connect(self.convert_image)


    def init_gui(self):
        self.radio_vertical.setChecked(True)
        self.convert_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.radio_vertical.setEnabled(False)
        self.radio_horizontal.setEnabled(False)


    def load_image(self):
        # Get the image path
        self.__image_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File', QtCore.QDir.rootPath() , '*.bmp')
        self.path_line_edit.setText(self.__image_path)

        if os.path.isfile(self.__image_path):
            # Load the image
            image = Image.open(self.__image_path)
            # convert it to monochrom bitmap and creat np array
            image_bmp = image.convert('1')
            self.image_array = np.asarray(image_bmp,dtype=int)
            self.__image_width, self.__image_height = self.image_array.shape
            # display the image
            self.__display_image()
            self.convert_button.setEnabled(True)
            self.radio_vertical.setEnabled(True)
            self.radio_horizontal.setEnabled(True)


    def __display_image(self):
        """
        Ref : https://www.codespeedy.com/displaying-an-image-using-pyqt5-in-python/
        """
        scene = QtWidgets.QGraphicsScene(self)
        pixmap = QPixmap(self.__image_path)
        item = QtWidgets.QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        self.image_view.setScene(scene)


    def convert_image(self):
        vertical = self.radio_vertical.isChecked()
        horizontal = self.radio_horizontal.isChecked()
        if vertical:
            self.__convert_vertical()
            self.save_button.setEnabled(True)
        if horizontal:
            self.__convert_horizontal()
            self.save_button.setEnabled(True)


    def save_bmp_txt(self):
        save_file_name = f'bitmap_{os.path.basename(self.__image_path)[:-4]}'
        save_path, filter = QFileDialog.getSaveFileName(self, "Save file as (*.txt)", save_file_name, "Text files (*.txt)")

        if not save_path:
            return
        text = self.plainTextEdit.toPlainText()
        with open(save_path, 'w') as f:
            f.write(text)


    def __format_image(self):
        pad_x, pad_y =(EIGHT_BIT - (self.__image_width % EIGHT_BIT)), (EIGHT_BIT - (self.__image_height%EIGHT_BIT))
        formated_image_array  = np.pad(self.image_array,  [(0,pad_x ), (0,pad_y )], mode='constant')
        print(formated_image_array.shape)
        return formated_image_array


    def __convert_vertical(self):
        byte_array = ''
        index = 0
        pad_array = self.__format_image()
        for y in range(0,self.__image_width,EIGHT_BIT):
            for x in range(self.__image_height):
                one_byte = pad_array[y:y+8,x]
                a = (''.join(str(y) for y in np.flip(one_byte)))
                #a = (''.join(str(y) for y in one_byte))
                byte_array += '0x'+format((int(a, 2)), '02x')+','
                index += 1
                if index%16 == 0:
                    byte_array += '\n'
                    
        byte_array = f'const unsigned char bitmap_{os.path.basename(self.__image_path)[:-4]} [] PROGMEM ={{\n' + byte_array.strip()[:-1] + '};' # remove the last comma  
        #print(byte_array)
        self.plainTextEdit.setPlainText(byte_array)
        return byte_array 

    def __convert_horizontal(self):
        byte_array = ''
        index = 0
        pad_array = self.__format_image()
        for y in range(self.__image_height):
            for x in range(0,self.__image_width,EIGHT_BIT):
                one_byte = pad_array[x:x+EIGHT_BIT,y]
                a = (''.join(str(i) for i in np.flip(one_byte)))
                #a = (''.join(str(i) for i in one_byte))
                byte_array += '0x'+format((int(a, 2)), '02x')+','
                index += 1
                if index%16 == 0:
                    byte_array += '\n'
                
        byte_array = '{\n' + byte_array.strip()[:-1] + '};' # remove the last comma  
        self.plainTextEdit.setPlainText(byte_array)
        return byte_array 



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())