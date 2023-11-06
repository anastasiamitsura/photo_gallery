import PIL
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
import os
import sys
import time
import sqlite3 as sl
from PIL import Image
from io import BytesIO


# главный класс приложения или же главное окно
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100,
                         800, 600)

        # стиль окна
        self.setStyleSheet("background : lightgrey;")
        # разрешение виджета к доступу к камере
        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
            sys.exit()

        # штука, где все уведомления высвечиваются
        self.status = QStatusBar()
        self.status.setStyleSheet("background : white;")
        self.setStatusBar(self.status)
        # путь к сохранению файла
        self.save_path = ""
        # виджет видео искателя камеры
        self.viewfinder = QCameraViewfinder()
        self.viewfinder.show()
        # установка этого виджета на весь экран
        self.setCentralWidget(self.viewfinder)
        # выбирает доступ к первой камере из всех возможных на устройстве
        self.select_camera(0)
        # переменная времени
        self.timestamp = ""
        # тулбар приложения с моими любимыми кнопками
        toolbar = QToolBar("Camera Tool Bar")
        # добавление тулбара как виджета
        self.addToolBar(toolbar)
        # кнопочка делания снимка, моя любимая, ненавижу
        click_action = QAction("Click photo", self)
        click_action.setStatusTip("This will capture picture")
        click_action.setToolTip("Capture picture")
        click_action.triggered.connect(self.click_photo)
        toolbar.addAction(click_action)

        # сохранение в бд последнего снимка
        save_action = QAction("Save photo", self)
        save_action.setStatusTip("This will save picture")
        save_action.setToolTip("Save picture")
        save_action.triggered.connect(self.saveToDataBase)
        toolbar.addAction(save_action)

        # кнопочка для выбора расположения файла
        change_folder_action = QAction("Change save location",
                                       self)
        change_folder_action.setStatusTip("Change folder where \
        picture will be saved saved.")
        change_folder_action.setToolTip("Change save location")
        change_folder_action.triggered.connect(self.change_folder)
        toolbar.addAction(change_folder_action)

        # выбор камеры через ComboBox очень крутая кнопка и функция
        camera_selector = QComboBox()
        camera_selector.setStatusTip("Choose camera to take pictures")
        camera_selector.setToolTip("Select Camera")
        camera_selector.setToolTipDuration(2500)
        camera_selector.addItems([camera.description()
                                  for camera in self.available_cameras])
        camera_selector.currentIndexChanged.connect(self.select_camera)
        toolbar.addWidget(camera_selector)

        # кнопка для открытия галереи
        open_gallery = QAction("Open Gallery", self)
        open_gallery.setStatusTip("Open gallery to see your picture")
        open_gallery.triggered.connect(self.open_gallery)
        toolbar.addAction(open_gallery)

        # установка стиля и названия окна
        toolbar.setStyleSheet("background : white;")
        self.setWindowTitle("PyQt5 Cam")

        self.save_seq = 0
        self.way = ""
        self.show()

    # открывает окно галереи
    def open_gallery(self):
        self.window = GalleryWindow()
        self.hide()
        self.window.show()

    # выбор камеры
    def select_camera(self, i):  # передаётся аргумент индекса камеры
        self.camera = QCamera(self.available_cameras[i])
        self.camera.setViewfinder(self.viewfinder)
        self.camera.setCaptureMode(QCamera.CaptureStillImage)
        self.camera.error.connect(lambda:
                                  self.alert(self.camera.errorString()))
        self.camera.start()
        self.capture = QCameraImageCapture(self.camera)
        self.capture.error.connect(lambda error_msg, error,
                                   msg: self.alert(msg))
        self.capture.imageCaptured.connect(lambda d,
                                           i: self.status.showMessage(
                                                      "Image captured : "
                                                      + str(self.save_seq)
                                                    ))
        self.current_camera_name = self.available_cameras[i].description()

    # сохранение в базу данных
    def saveToDataBase(self):
        if self.way != "":
            try:
                data = (self.save_seq, DataBase.convertToBinaryData(self.way))
                DataBase.con.executemany(DataBase.sqlite_insert_blob_query, data)
                with DataBase.con:
                    data = DataBase.con.execute("SELECT * FROM photos")
                    for row in data:
                        print(row)
            except:
                print("О неееет, что то пошло не так :(")
            self.save_seq += 1

    # делает снимок и сохраняет его в проводник
    def click_photo(self):
        if self.save_path == "":
            self.change_folder()
        self.timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")

        self.capture.capture(os.path.join(self.save_path,
                                          "%s-%04d-%s.jpg" % (
                                              self.current_camera_name,
                                              self.save_seq,
                                              self.timestamp
                                          )))
        self.way = os.path.abspath("%s-%04d-%s.jpg" % (
                                              self.current_camera_name,
                                              self.save_seq,
                                              self.timestamp
                                          ))
        print(self.way)

    # изменяет путь хранения
    def change_folder(self):
        path = QFileDialog.getExistingDirectory(self,
                                                "Picture Location", "")
        if path:
            self.save_path = path

    # вывод ошибки
    def alert(self, msg):
        error = QErrorMessage(self)
        error.showMessage(msg)


# класс 2 окна галереи, где по идеи должны отображаться все картинки с бд
class GalleryWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100,
                         800, 600)

        self.status = QStatusBar()
        self.status.setStyleSheet("background : white;")
        self.setStatusBar(self.status)
        toolbar = QToolBar("Camera Tool Bar")
        self.addToolBar(toolbar)
        # кнопка открытия камеры
        open_camera = QAction("Open Camera",
                              self)
        open_camera.setStatusTip("Open camera to take your picture")
        open_camera.triggered.connect(self.open_camera)
        toolbar.addAction(open_camera)
        toolbar.setStyleSheet("background : white;")
        # объявление лэйаута для отображения галереи
        self.custom_layput = QGridLayout(self)
        self.scroll = QScrollArea()
        self.item = QLabel()

        with DataBase.con:
            data = DataBase.con.execute("SELECT * FROM photos")
            a = 0
            b = 0
            for row in data:
                rect = QLabel()
                img = Image.open(BytesIO(row[1]))
                img = img.resize((140, 140), PIL.Image.LANCZOS)
                img.save(str(b) + str(a) + ".png")
                pixmap = QPixmap(str(b) + str(a) + ".png")
                rect.resize(50, 50)
                rect.setPixmap(pixmap)
                self.custom_layput.addWidget(rect, b, a)
                if a == 4:
                    b += 1
                    a = 0
                else:
                    a += 1

        widget = QWidget()
        widget.setLayout(self.custom_layput)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(widget)
        self.setCentralWidget(self.scroll)
        self.setWindowTitle("PyQt5 Gallery")

        self.show()

    def open_camera(self):
        self.window = MainWindow()
        self.hide()
        self.window.show()

    def mousePressEvent(self, event):
        widget = self.childAt(event.pos())
        print("child widget", widget)
        if widget:
            label = widget.findChild(QLabel)
            if label:
                print("label", label.text())
            index = self.custom_layput.indexOf(widget)
            print("layout index", index)
            if index >= 0:
                self.item = self.custom_layput.itemAt(index)
                print("layout item", self.item)
                self.window1 = ImgWindow(self.item)
                self.window1.show()


class ImgWindow(QMainWindow):

    def __init__(self, item):
        super().__init__()

        self.setGeometry(400, 100,
                         200, 200)

        self.status = QStatusBar()
        self.status.setStyleSheet("background : white;")
        self.setStatusBar(self.status)
        toolbar = QToolBar("Camera Tool Bar")
        self.addToolBar(toolbar)
        # кнопка открытия камеры
        open_camera = QAction("Open Camera",
                              self)
        open_camera.setStatusTip("Open camera to take your picture")
        # open_camera.triggered.connect(self.open_camera)
        toolbar.addAction(open_camera)
        toolbar.setStyleSheet("background : white;")
        # объявление лэйаута для отображения галереи

        try:
            self.widget = QWidget()
            self.label = item
            self.layaut = QGridLayout()
            self.layaut.addItem(self.label)
            self.widget.setLayout(self.layaut)
        except:
            print("что то не так")
        self.setWindowTitle("PyQt5 Img")
        self.show()


class DataBase():

    def convertToBinaryData(filename):
        # конвертация изображения в список байтов
        with open(filename, 'rb') as file:
            blobData = file.read()
        return blobData

    con = sl.connect('gallery.db')

    with con:
        data = con.execute("select count(*) from sqlite_master \
        where type='table' and name='photos'")
        for row in data:
            if row[0] == 0:
                con.execute("""
                            CREATE TABLE photos (
                                id INTEGER PRIMARY KEY,
                                photo BLOB NOT NULL
                            );
                        """)
    sqlite_insert_blob_query = """ INSERT INTO photos
                                             (id, photo) VALUES (?, ?)"""

    a = 0
    files = ["h.jpg", "j.jpg", "l.jpg", "hh.jpg", "jj.jpg", "ii.jpg",
             "hhh.jpg", "jjj.jpg", "ll.jpg", "hhhh.jpg",
             "jjjj.jpg", "iiii.jpg"]
    for i in files:
        img = convertToBinaryData(i)
        data = (a, img)
        con.execute(sqlite_insert_blob_query, data)
        a += 1




if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(App.exec())
