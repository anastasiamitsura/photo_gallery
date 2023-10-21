from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
import os
import sys
import time


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100,
                         800, 600)
        self.setStyleSheet("background : lightgrey;")
        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
            sys.exit()

        self.status = QStatusBar()
        self.status.setStyleSheet("background : white;")
        self.setStatusBar(self.status)
        self.save_path = ""
        self.viewfinder = QCameraViewfinder()
        self.viewfinder.show()
        self.setCentralWidget(self.viewfinder)
        self.select_camera(0)
        toolbar = QToolBar("Camera Tool Bar")
        self.addToolBar(toolbar)
        click_action = QAction("Click photo", self)
        click_action.setStatusTip("This will capture picture")
        click_action.setToolTip("Capture picture")
        click_action.triggered.connect(self.click_photo)
        toolbar.addAction(click_action)
        change_folder_action = QAction("Change save location",
                                       self)
        change_folder_action.setStatusTip("Change folder where picture will be saved saved.")
        change_folder_action.setToolTip("Change save location")
        change_folder_action.triggered.connect(self.change_folder)
        toolbar.addAction(change_folder_action)
        camera_selector = QComboBox()
        camera_selector.setStatusTip("Choose camera to take pictures")
        camera_selector.setToolTip("Select Camera")
        camera_selector.setToolTipDuration(2500)
        camera_selector.addItems([camera.description()
                                  for camera in self.available_cameras])
        camera_selector.currentIndexChanged.connect(self.select_camera)
        toolbar.addWidget(camera_selector)

        open_gallery = QAction("Open Gallery",
                                       self)
        open_gallery.setStatusTip("Open gallery to see your picture")
        open_gallery.triggered.connect(self.open_gallery)
        toolbar.addAction(open_gallery)

        toolbar.setStyleSheet("background : white;")
        self.setWindowTitle("PyQt5 Cam")

        self.show()

    def open_gallery(self):
        self.window = SecondWindow()
        self.hide()
        self.window.show()

    def select_camera(self, i):
        self.camera = QCamera(self.available_cameras[i])
        self.camera.setViewfinder(self.viewfinder)
        self.camera.setCaptureMode(QCamera.CaptureStillImage)
        self.camera.error.connect(lambda: self.alert(self.camera.errorString()))
        self.camera.start()
        self.capture = QCameraImageCapture(self.camera)
        self.capture.error.connect(lambda error_msg, error,
                                          msg: self.alert(msg))
        self.capture.imageCaptured.connect(lambda d,
                                                  i: self.status.showMessage("Image captured : "
                                                                             + str(self.save_seq)))
        self.current_camera_name = self.available_cameras[i].description()
        self.save_seq = 0


    def click_photo(self):

        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")

        self.capture.capture(os.path.join(self.save_path,
                                          "%s-%04d-%s.jpg" % (
                                              self.current_camera_name,
                                              self.save_seq,
                                              timestamp
                                          )))

        self.save_seq += 1


    def change_folder(self):
        path = QFileDialog.getExistingDirectory(self,
                                                "Picture Location", "")
        if path:
            self.save_path = path

            self.save_seq = 0

    def alert(self, msg):
        error = QErrorMessage(self)
        error.showMessage(msg)

class SecondWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100,
                         800, 600)
        self.setStyleSheet("background : lightgrey;")

        self.status = QStatusBar()
        self.status.setStyleSheet("background : white;")
        self.setStatusBar(self.status)
        self.save_path = ""
        toolbar = QToolBar("Camera Tool Bar")
        self.addToolBar(toolbar)
        open_camera = QAction("Open Camera",
                               self)
        open_camera.setStatusTip("Open camera to take your picture")
        open_camera.triggered.connect(self.open_camera)
        toolbar.addAction(open_camera)
        toolbar.setStyleSheet("background : white;")
        self.setWindowTitle("PyQt5 Gallery")

        self.show()

    def open_camera(self):
        self.window = MainWindow()
        self.hide()
        self.window.show()



if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(App.exec())