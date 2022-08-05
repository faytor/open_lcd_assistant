from PyQt5.QtWidgets import QApplication, QFileDialog, QStyle, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QPixmap, QIcon, QIntValidator
from PIL import Image, ImageOps
from PIL.ImageQt import ImageQt
import numpy as np
import sys
import os



# Constants
EIGHT_BIT = 8
main_gui_file_name = "main_gui.ui"
# Path to the icon
script_dir_path = os.path.dirname(os.path.realpath(__file__))
icon_path = os.sep.join([script_dir_path, "images", "icon.png"])

# Generate the path to the gui file
qtCreatorFile = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), main_gui_file_name) 
# Load the main GUI
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

#------------------------------------------------
#                   Main Class
#------------------------------------------------
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    __image_path = None
    __image_width = 0
    __image_height = 0
    original_width =0
    original_height =0
    image_ratio = 0
    __is_inverted = False # Flag to keep track if the image was inverted 
    image_array = None
    image = None
    original_image = None 


    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Open LCD Assisstant")
        self.init_gui()
        self.load_button.clicked.connect(self.load_image)
        self.save_button.clicked.connect(self.save_bmp_txt)
        self.convert_button.clicked.connect(self.convert_image)
        self.invert_button.clicked.connect(self.invert_image)
        self.resize_button.clicked.connect(self.resize_image)
        self.reset_button.clicked.connect(self.reset_image)
        self.width_lineEdit.textEdited.connect(self.set_new_height)
        self.height_lineEdit.textEdited.connect(self.set_new_width)


    def set_new_height(self):
        # Get the new Width and Height from the GUI
        new_width = self.width_lineEdit.text()
        if self.keep_ratio.isChecked():
            if new_width:
                new_height = round(int(new_width) / self.image_ratio)
                self.height_lineEdit.setText(str(new_height))


    def set_new_width(self):
        # Get the new Width and Height from the GUI
        new_height = self.height_lineEdit.text()
        if self.keep_ratio.isChecked():
            if new_height:
                new_width = round(int(new_height) * self.image_ratio)
                self.width_lineEdit.setText(str(new_width))


    def init_gui(self):
        # Set the window's size automatically to the UI made in QtDesigner
        self.setFixedSize(self.geometry().width(),self.geometry().height())
        self.radio_horizontal.setChecked(True)
        self.convert_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.radio_vertical.setEnabled(False)
        self.radio_horizontal.setEnabled(False)
        self.invert_button.setEnabled(False)
        # Add somne styl to :
        # convert button
        pixmapi = QStyle.SP_CommandLink
        icon = self.style().standardIcon(pixmapi)
        self.convert_button.setIcon(icon)
        # invert button
        pixmapi = QStyle.SP_BrowserReload
        icon = self.style().standardIcon(pixmapi)
        self.invert_button.setIcon(icon)
        # save button
        pixmapi = QStyle.SP_DialogSaveButton
        icon = self.style().standardIcon(pixmapi)
        self.save_button.setIcon(icon)
        # GUI elements Related to resize 
        # Restricts input to integer
        self.width_lineEdit.setValidator(QIntValidator())
        self.height_lineEdit.setValidator(QIntValidator())
        # Desable before loading the image
        self.width_lineEdit.setEnabled(False)
        self.height_lineEdit.setEnabled(False)
        self.keep_ratio.setEnabled(False)
        self.resize_button.setEnabled(False)
        self.reset_button.setEnabled(False)
    

    def load_image(self):
        # Get the image path
        self.__image_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File','', 'Image Files(*.png *.jpg *.bmp)')
        self.path_line_edit.setText(self.__image_path)

        if os.path.isfile(self.__image_path):
            # Load the image
            self.image = Image.open(self.__image_path)
            self.original_width, self.original_height = self.image.size
            self.width_lineEdit.setText(str(self.original_width))
            self.height_lineEdit.setText(str(self.original_height))
            self.image_ratio = self.original_width/self.original_height
            # Convert it to monochrom bitmap and creat np array
            self.image_to_array()
            # Display the image
            self.display_image()
            # Set is inverted? flag to default
            self.__is_inverted = False
            # Enable buttons and co.
            self.convert_button.setEnabled(True)
            self.radio_vertical.setEnabled(True)
            self.radio_horizontal.setEnabled(True)
            self.invert_button.setEnabled(True)
            self.width_lineEdit.setEnabled(True)
            self.height_lineEdit.setEnabled(True)
            self.keep_ratio.setEnabled(True)
            self.resize_button.setEnabled(True)
            self.reset_button.setEnabled(True)


    def display_image(self):
        '''
        Show the image in the GUI
        '''
        qim = ImageQt(self.image)
        pixmap = QtGui.QPixmap.fromImage(qim)
        scene = QtWidgets.QGraphicsScene(self)
        item = QtWidgets.QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        self.image_view.setScene(scene)


    def convert_image(self):
        vertical = self.radio_vertical.isChecked()
        horizontal = self.radio_horizontal.isChecked()
        if vertical:
            self.convert_vertical()
            self.save_button.setEnabled(True)
        if horizontal:
            self.convert_horizontal()
            self.save_button.setEnabled(True)


    def image_to_array(self):
        '''
        Convert the image to monochrom bitmap and creat Numpy array
        '''
        self.image = self.image.convert('1')
        self.original_image = self.image
        self.image_array = np.asarray(self.image,dtype=int)
        self.__image_height, self.__image_width = self.image_array.shape


    def save_bmp_txt(self):
        '''
        Save the result of the bitmap array in a text file
        '''        
        save_file_name = f'bitmap_{os.path.basename(self.__image_path)[:-4]}'
        save_path, filter = QFileDialog.getSaveFileName(self, "Save file as (*.txt)", save_file_name, "Text files (*.txt)")

        if not save_path:
            return
        text = self.plainTextEdit.toPlainText()
        with open(save_path, 'w') as f:
            f.write(text)


    def format_image(self):
        if (self.__image_width % EIGHT_BIT) == 0:
            pad_width = 0
        elif (self.__image_width % EIGHT_BIT) != 0:
            pad_width = EIGHT_BIT - (self.__image_width % EIGHT_BIT)

        if (self.__image_height % EIGHT_BIT) == 0:
            pad_height = 0
        elif (self.__image_height % EIGHT_BIT) != 0:
            pad_height = EIGHT_BIT - (self.__image_height % EIGHT_BIT)

        formated_image_array  = np.pad(self.image_array,  [(0,pad_height), (0, pad_width)], mode='constant')

        return formated_image_array


    def invert_image(self):
        '''
        Convert the image to a supported inversion format, before inverting 
        '''
        self.image = ImageOps.invert( self.image.convert('RGB') )
        #Display the new image
        self.display_image()
        #Set the flag to inverted state
        self.__is_inverted = not (self.__is_inverted)
        # Display a message to the status bar only if the image is inverted
        message = "Image inverted" if self.__is_inverted else ""
        self.statusBar().showMessage(message)


    def resize_image(self):
        '''
        Resize the image to the new size either by entering :
            Parameters:
            Width, Height : inputs from the G
        '''
        # Get the new Width and Height from the GUI
        new_width = self.width_lineEdit.text()
        new_height = self.height_lineEdit.text()

        # The inputs are not empty
        if not(new_width and new_height):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Widht or Height cannot be empty!")    
            msg.setInformativeText("Please enter a valide value")
            _ = msg.exec_()

        else :
            new_width = int(new_width)
            new_height = int(new_height)
            self.resized_image = self.image.resize((new_width, new_height))
            self.image = self.resized_image
            self.display_image()


    def reset_image(self):
        '''
        Reset the edited image to the original
        '''
        self.image = self.original_image
        self.width_lineEdit.setText(str(self.original_width))
        self.height_lineEdit.setText(str(self.original_height))
        self.__is_inverted = False
        self.statusBar().clearMessage()
        self.display_image()


    def convert_vertical(self):
        '''
        Convert the image into bitmap array using the vertical (byte orientation) method
        '''
        byte_array = ''
        index = 0
        pad_array = self.format_image()
        for y in range(0,self.__image_width,EIGHT_BIT):
            for x in range(self.__image_height):
                one_byte = pad_array[y:y+8,x]
                a = (''.join(str(y) for y in np.flip(one_byte)))
                byte_array += '0x'+format((int(a, 2)), '02x')+','
                index += 1
                if index%16 == 0:
                    byte_array += '\n'
                    
        byte_array = f'const unsigned char bitmap_{os.path.basename(self.__image_path)[:-4]} [] PROGMEM ={{\n' + byte_array.strip()[:-1] + '};' # remove the last comma  
        self.plainTextEdit.setPlainText(byte_array)
        return byte_array 


    def convert_horizontal(self):
        '''
        Convert the image into bitmap array using the horizontal (byte orientation) method
        '''
        self.image_to_array()
        image_size = f'#define {os.path.basename(self.__image_path)[:-4]}_width \t {self.__image_width}\n'
        image_size += f'#define {os.path.basename(self.__image_path)[:-4]}_height \t {self.__image_height}\n'
        byte_array = ''
        index = 0
        pad_array = self.format_image()
        height, width = pad_array.shape

        for x in range(height):
            for y in range(0,width,EIGHT_BIT):
                one_byte = pad_array[x, y:y+EIGHT_BIT]
                a = (''.join(str(i) for i in np.flip(one_byte))) # flip LSB and MSB
                byte_array += '0x'+format((int(a, 2)), '02x')+','
                index += 1
                if index%16 == 0:
                    byte_array += '\n'
                
        byte_array = f'const unsigned char {os.path.basename(self.__image_path)[:-4]}_bmp [] PROGMEM ={{\n' + byte_array.strip()[:-1] + '};' # remove the last comma   
        self.plainTextEdit.setPlainText(image_size+byte_array)
        return byte_array 


#------------------------------------------------
#                   App creation
#------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon(icon_path))
    app.setApplicationName("Open LCD")
    window = MyApp()
    window.show()
    sys.exit(app.exec_())