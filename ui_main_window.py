# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDockWidget,
    QDoubleSpinBox, QFormLayout, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QProgressBar, QPushButton, QRadioButton, QSizePolicy,
    QSlider, QSpacerItem, QStackedWidget, QStatusBar,
    QTabWidget, QTextBrowser, QToolButton, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1209, 856)
        MainWindow.setMinimumSize(QSize(800, 600))
        self.actionImport_OBJ = QAction(MainWindow)
        self.actionImport_OBJ.setObjectName(u"actionImport_OBJ")
        self.actionImport_CAD = QAction(MainWindow)
        self.actionImport_CAD.setObjectName(u"actionImport_CAD")
        self.actionSet_Working_Directory = QAction(MainWindow)
        self.actionSet_Working_Directory.setObjectName(u"actionSet_Working_Directory")
        self.actionSave_ProjectAs = QAction(MainWindow)
        self.actionSave_ProjectAs.setObjectName(u"actionSave_ProjectAs")
        self.actionOpen_Project = QAction(MainWindow)
        self.actionOpen_Project.setObjectName(u"actionOpen_Project")
        self.actionNew_Project = QAction(MainWindow)
        self.actionNew_Project.setObjectName(u"actionNew_Project")
        self.actionSave_Project = QAction(MainWindow)
        self.actionSave_Project.setObjectName(u"actionSave_Project")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionSetWorkingDir = QAction(MainWindow)
        self.actionSetWorkingDir.setObjectName(u"actionSetWorkingDir")
        self.actionAbout_SimPhant = QAction(MainWindow)
        self.actionAbout_SimPhant.setObjectName(u"actionAbout_SimPhant")
        self.actionShowTraceback = QAction(MainWindow)
        self.actionShowTraceback.setObjectName(u"actionShowTraceback")
        self.actionDocumentation = QAction(MainWindow)
        self.actionDocumentation.setObjectName(u"actionDocumentation")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setEnabled(True)
        self.verticalLayout_43 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_43.setObjectName(u"verticalLayout_43")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMinimumSize(QSize(0, 100))
        self.tabWidget.setMaximumSize(QSize(5000, 160))
        self.tabBodies = QWidget()
        self.tabBodies.setObjectName(u"tabBodies")
        self.btnBody = QToolButton(self.tabBodies)
        self.btnBody.setObjectName(u"btnBody")
        self.btnBody.setGeometry(QRect(10, 0, 61, 61))
        self.btnBody.setIconSize(QSize(40, 40))
        self.btnBody.setPopupMode(QToolButton.ToolButtonPopupMode.DelayedPopup)
        self.btnBody.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonFollowStyle)
        self.btnBody.setAutoRaise(True)
        self.btnRF = QToolButton(self.tabBodies)
        self.btnRF.setObjectName(u"btnRF")
        self.btnRF.setGeometry(QRect(90, 0, 61, 61))
        self.btnRF.setIconSize(QSize(40, 40))
        self.btnRF.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnRF.setAutoRaise(True)
        self.line_9 = QFrame(self.tabBodies)
        self.line_9.setObjectName(u"line_9")
        self.line_9.setGeometry(QRect(160, 0, 3, 61))
        self.line_9.setFrameShape(QFrame.Shape.VLine)
        self.line_9.setFrameShadow(QFrame.Shadow.Sunken)
        self.btnBox = QToolButton(self.tabBodies)
        self.btnBox.setObjectName(u"btnBox")
        self.btnBox.setGeometry(QRect(170, 0, 61, 61))
        self.btnBox.setIconSize(QSize(40, 40))
        self.btnBox.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnBox.setAutoRaise(True)
        self.btnTube = QToolButton(self.tabBodies)
        self.btnTube.setObjectName(u"btnTube")
        self.btnTube.setGeometry(QRect(230, 0, 61, 61))
        self.btnTube.setIconSize(QSize(40, 40))
        self.btnTube.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnTube.setAutoRaise(True)
        self.btnSphere = QToolButton(self.tabBodies)
        self.btnSphere.setObjectName(u"btnSphere")
        self.btnSphere.setGeometry(QRect(290, 0, 61, 61))
        self.btnSphere.setIconSize(QSize(40, 40))
        self.btnSphere.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnSphere.setAutoRaise(True)
        self.btnPrism = QToolButton(self.tabBodies)
        self.btnPrism.setObjectName(u"btnPrism")
        self.btnPrism.setGeometry(QRect(350, 0, 61, 61))
        self.btnPrism.setIconSize(QSize(40, 40))
        self.btnPrism.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnPrism.setAutoRaise(True)
        self.btnTorus = QToolButton(self.tabBodies)
        self.btnTorus.setObjectName(u"btnTorus")
        self.btnTorus.setGeometry(QRect(410, 0, 61, 61))
        self.btnTorus.setIconSize(QSize(40, 40))
        self.btnTorus.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnTorus.setAutoRaise(True)
        self.btnCone = QToolButton(self.tabBodies)
        self.btnCone.setObjectName(u"btnCone")
        self.btnCone.setGeometry(QRect(470, 0, 61, 61))
        self.btnCone.setIconSize(QSize(40, 40))
        self.btnCone.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnCone.setAutoRaise(True)
        self.btnLink = QToolButton(self.tabBodies)
        self.btnLink.setObjectName(u"btnLink")
        self.btnLink.setGeometry(QRect(530, 0, 61, 61))
        self.btnLink.setIconSize(QSize(40, 40))
        self.btnLink.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnLink.setAutoRaise(True)
        self.line_10 = QFrame(self.tabBodies)
        self.line_10.setObjectName(u"line_10")
        self.line_10.setGeometry(QRect(80, 0, 3, 61))
        self.line_10.setFrameShape(QFrame.Shape.VLine)
        self.line_10.setFrameShadow(QFrame.Shadow.Sunken)
        self.line_12 = QFrame(self.tabBodies)
        self.line_12.setObjectName(u"line_12")
        self.line_12.setGeometry(QRect(600, 0, 3, 61))
        self.line_12.setFrameShape(QFrame.Shape.VLine)
        self.line_12.setFrameShadow(QFrame.Shadow.Sunken)
        self.btnBoolean = QToolButton(self.tabBodies)
        self.btnBoolean.setObjectName(u"btnBoolean")
        self.btnBoolean.setGeometry(QRect(610, 0, 61, 61))
        self.btnBoolean.setIconSize(QSize(40, 40))
        self.btnBoolean.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnBoolean.setAutoRaise(True)
        self.line_21 = QFrame(self.tabBodies)
        self.line_21.setObjectName(u"line_21")
        self.line_21.setGeometry(QRect(680, 0, 3, 61))
        self.line_21.setFrameShape(QFrame.Shape.VLine)
        self.line_21.setFrameShadow(QFrame.Shadow.Sunken)
        self.tabWidget.addTab(self.tabBodies, "")
        self.tabJoints = QWidget()
        self.tabJoints.setObjectName(u"tabJoints")
        self.btnRevoluteJt = QToolButton(self.tabJoints)
        self.btnRevoluteJt.setObjectName(u"btnRevoluteJt")
        self.btnRevoluteJt.setGeometry(QRect(140, 0, 61, 61))
        self.btnRevoluteJt.setIconSize(QSize(40, 40))
        self.btnRevoluteJt.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnRevoluteJt.setAutoRaise(True)
        self.btnFixedJt = QToolButton(self.tabJoints)
        self.btnFixedJt.setObjectName(u"btnFixedJt")
        self.btnFixedJt.setGeometry(QRect(10, 0, 61, 61))
        self.btnFixedJt.setIconSize(QSize(40, 40))
        self.btnFixedJt.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnFixedJt.setAutoRaise(True)
        self.btnSphericalJt = QToolButton(self.tabJoints)
        self.btnSphericalJt.setObjectName(u"btnSphericalJt")
        self.btnSphericalJt.setGeometry(QRect(80, 0, 61, 61))
        self.btnSphericalJt.setIconSize(QSize(40, 40))
        self.btnSphericalJt.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnSphericalJt.setAutoRaise(True)
        self.btnCylindricalJt = QToolButton(self.tabJoints)
        self.btnCylindricalJt.setObjectName(u"btnCylindricalJt")
        self.btnCylindricalJt.setGeometry(QRect(200, 0, 61, 61))
        self.btnCylindricalJt.setIconSize(QSize(40, 40))
        self.btnCylindricalJt.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnCylindricalJt.setAutoRaise(True)
        self.btnPrismaticJt = QToolButton(self.tabJoints)
        self.btnPrismaticJt.setObjectName(u"btnPrismaticJt")
        self.btnPrismaticJt.setGeometry(QRect(270, 0, 61, 61))
        self.btnPrismaticJt.setIconSize(QSize(40, 40))
        self.btnPrismaticJt.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnPrismaticJt.setAutoRaise(True)
        self.btnPlanarJt = QToolButton(self.tabJoints)
        self.btnPlanarJt.setObjectName(u"btnPlanarJt")
        self.btnPlanarJt.setGeometry(QRect(340, 0, 61, 61))
        self.btnPlanarJt.setIconSize(QSize(40, 40))
        self.btnPlanarJt.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnPlanarJt.setAutoRaise(True)
        self.tabWidget.addTab(self.tabJoints, "")
        self.tabForces = QWidget()
        self.tabForces.setObjectName(u"tabForces")
        self.btnForce = QToolButton(self.tabForces)
        self.btnForce.setObjectName(u"btnForce")
        self.btnForce.setGeometry(QRect(10, 0, 61, 61))
        self.btnForce.setIconSize(QSize(40, 40))
        self.btnForce.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnForce.setAutoRaise(True)
        self.btnTorque = QToolButton(self.tabForces)
        self.btnTorque.setObjectName(u"btnTorque")
        self.btnTorque.setGeometry(QRect(80, 0, 61, 61))
        self.btnTorque.setIconSize(QSize(40, 40))
        self.btnTorque.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnTorque.setAutoRaise(True)
        self.btnActuator = QToolButton(self.tabForces)
        self.btnActuator.setObjectName(u"btnActuator")
        self.btnActuator.setGeometry(QRect(150, 0, 61, 61))
        self.btnActuator.setIconSize(QSize(40, 40))
        self.btnActuator.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnActuator.setAutoRaise(True)
        self.btnEmotor = QToolButton(self.tabForces)
        self.btnEmotor.setObjectName(u"btnEmotor")
        self.btnEmotor.setGeometry(QRect(220, 0, 61, 61))
        self.btnEmotor.setIconSize(QSize(40, 40))
        self.btnEmotor.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnEmotor.setAutoRaise(True)
        self.btnContact = QToolButton(self.tabForces)
        self.btnContact.setObjectName(u"btnContact")
        self.btnContact.setGeometry(QRect(290, 0, 61, 61))
        self.btnContact.setIconSize(QSize(40, 40))
        self.btnContact.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnContact.setAutoRaise(True)
        self.line_13 = QFrame(self.tabForces)
        self.line_13.setObjectName(u"line_13")
        self.line_13.setGeometry(QRect(140, 0, 3, 61))
        self.line_13.setFrameShape(QFrame.Shape.VLine)
        self.line_13.setFrameShadow(QFrame.Shadow.Sunken)
        self.line_14 = QFrame(self.tabForces)
        self.line_14.setObjectName(u"line_14")
        self.line_14.setGeometry(QRect(280, 0, 3, 61))
        self.line_14.setFrameShape(QFrame.Shape.VLine)
        self.line_14.setFrameShadow(QFrame.Shadow.Sunken)
        self.line_17 = QFrame(self.tabForces)
        self.line_17.setObjectName(u"line_17")
        self.line_17.setGeometry(QRect(350, 0, 3, 61))
        self.line_17.setFrameShape(QFrame.Shape.VLine)
        self.line_17.setFrameShadow(QFrame.Shadow.Sunken)
        self.tabWidget.addTab(self.tabForces, "")
        self.tabSprings = QWidget()
        self.tabSprings.setObjectName(u"tabSprings")
        self.btnComprSpring = QToolButton(self.tabSprings)
        self.btnComprSpring.setObjectName(u"btnComprSpring")
        self.btnComprSpring.setGeometry(QRect(10, 0, 81, 61))
        self.btnComprSpring.setIconSize(QSize(40, 40))
        self.btnComprSpring.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnComprSpring.setAutoRaise(True)
        self.btnTorsionSpring = QToolButton(self.tabSprings)
        self.btnTorsionSpring.setObjectName(u"btnTorsionSpring")
        self.btnTorsionSpring.setGeometry(QRect(90, 0, 71, 61))
        self.btnTorsionSpring.setIconSize(QSize(40, 40))
        self.btnTorsionSpring.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnTorsionSpring.setAutoRaise(True)
        self.btnBushing = QToolButton(self.tabSprings)
        self.btnBushing.setObjectName(u"btnBushing")
        self.btnBushing.setGeometry(QRect(180, 0, 61, 61))
        self.btnBushing.setIconSize(QSize(40, 40))
        self.btnBushing.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnBushing.setAutoRaise(True)
        self.line_18 = QFrame(self.tabSprings)
        self.line_18.setObjectName(u"line_18")
        self.line_18.setGeometry(QRect(170, 0, 3, 61))
        self.line_18.setFrameShape(QFrame.Shape.VLine)
        self.line_18.setFrameShadow(QFrame.Shadow.Sunken)
        self.line_19 = QFrame(self.tabSprings)
        self.line_19.setObjectName(u"line_19")
        self.line_19.setGeometry(QRect(250, 0, 3, 61))
        self.line_19.setFrameShape(QFrame.Shape.VLine)
        self.line_19.setFrameShadow(QFrame.Shadow.Sunken)
        self.tabWidget.addTab(self.tabSprings, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.btnHelicalGear = QToolButton(self.tab)
        self.btnHelicalGear.setObjectName(u"btnHelicalGear")
        self.btnHelicalGear.setGeometry(QRect(10, 0, 71, 61))
        self.btnHelicalGear.setIconSize(QSize(40, 40))
        self.btnHelicalGear.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnHelicalGear.setAutoRaise(True)
        self.btnGearJoint = QToolButton(self.tab)
        self.btnGearJoint.setObjectName(u"btnGearJoint")
        self.btnGearJoint.setGeometry(QRect(240, 0, 61, 61))
        self.btnGearJoint.setIconSize(QSize(40, 40))
        self.btnGearJoint.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnGearJoint.setAutoRaise(True)
        self.line_11 = QFrame(self.tab)
        self.line_11.setObjectName(u"line_11")
        self.line_11.setGeometry(QRect(230, 0, 3, 61))
        self.line_11.setFrameShape(QFrame.Shape.VLine)
        self.line_11.setFrameShadow(QFrame.Shadow.Sunken)
        self.btnInnerGear = QToolButton(self.tab)
        self.btnInnerGear.setObjectName(u"btnInnerGear")
        self.btnInnerGear.setGeometry(QRect(80, 0, 71, 61))
        self.btnInnerGear.setIconSize(QSize(40, 40))
        self.btnInnerGear.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnInnerGear.setAutoRaise(True)
        self.btnBevelGear = QToolButton(self.tab)
        self.btnBevelGear.setObjectName(u"btnBevelGear")
        self.btnBevelGear.setGeometry(QRect(150, 0, 71, 61))
        self.btnBevelGear.setIconSize(QSize(40, 40))
        self.btnBevelGear.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnBevelGear.setAutoRaise(True)
        self.line_20 = QFrame(self.tab)
        self.line_20.setObjectName(u"line_20")
        self.line_20.setGeometry(QRect(300, 0, 3, 61))
        self.line_20.setFrameShape(QFrame.Shape.VLine)
        self.line_20.setFrameShadow(QFrame.Shadow.Sunken)
        self.tabWidget.addTab(self.tab, "")
        self.tabMotions = QWidget()
        self.tabMotions.setObjectName(u"tabMotions")
        self.btnTranslMotion = QToolButton(self.tabMotions)
        self.btnTranslMotion.setObjectName(u"btnTranslMotion")
        self.btnTranslMotion.setGeometry(QRect(10, 0, 71, 61))
        self.btnTranslMotion.setIconSize(QSize(40, 40))
        self.btnTranslMotion.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnTranslMotion.setAutoRaise(True)
        self.btnRotMotion = QToolButton(self.tabMotions)
        self.btnRotMotion.setObjectName(u"btnRotMotion")
        self.btnRotMotion.setGeometry(QRect(90, 0, 61, 61))
        self.btnRotMotion.setIconSize(QSize(40, 40))
        self.btnRotMotion.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnRotMotion.setAutoRaise(True)
        self.tabWidget.addTab(self.tabMotions, "")
        self.tabSimulation = QWidget()
        self.tabSimulation.setObjectName(u"tabSimulation")
        self.btnSimulation = QToolButton(self.tabSimulation)
        self.btnSimulation.setObjectName(u"btnSimulation")
        self.btnSimulation.setGeometry(QRect(10, 0, 61, 61))
        self.btnSimulation.setIconSize(QSize(40, 40))
        self.btnSimulation.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnSimulation.setAutoRaise(True)
        self.btnTelemetry = QToolButton(self.tabSimulation)
        self.btnTelemetry.setObjectName(u"btnTelemetry")
        self.btnTelemetry.setEnabled(False)
        self.btnTelemetry.setGeometry(QRect(80, 0, 81, 61))
        self.btnTelemetry.setIconSize(QSize(40, 40))
        self.btnTelemetry.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnTelemetry.setAutoRaise(True)
        self.btnExportCSV = QToolButton(self.tabSimulation)
        self.btnExportCSV.setObjectName(u"btnExportCSV")
        self.btnExportCSV.setGeometry(QRect(170, 0, 61, 61))
        self.btnExportCSV.setIconSize(QSize(40, 40))
        self.btnExportCSV.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnExportCSV.setAutoRaise(True)
        self.tabWidget.addTab(self.tabSimulation, "")

        self.verticalLayout_43.addWidget(self.tabWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.treeHierarchy = QTreeWidget(self.centralwidget)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1")
        self.treeHierarchy.setHeaderItem(__qtreewidgetitem)
        self.treeHierarchy.setObjectName(u"treeHierarchy")
        self.treeHierarchy.setMinimumSize(QSize(80, 200))
        self.treeHierarchy.setMaximumSize(QSize(200, 16777215))

        self.horizontalLayout.addWidget(self.treeHierarchy)

        self.viewportWidget = QWidget(self.centralwidget)
        self.viewportWidget.setObjectName(u"viewportWidget")
        self.viewportWidget.setMinimumSize(QSize(400, 300))

        self.horizontalLayout.addWidget(self.viewportWidget)


        self.verticalLayout_43.addLayout(self.horizontalLayout)

        self.frmVPSetting = QFrame(self.centralwidget)
        self.frmVPSetting.setObjectName(u"frmVPSetting")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frmVPSetting.sizePolicy().hasHeightForWidth())
        self.frmVPSetting.setSizePolicy(sizePolicy1)
        self.frmVPSetting.setMinimumSize(QSize(300, 48))
        self.frmVPSetting.setMaximumSize(QSize(16777215, 40))
        self.frmVPSetting.setBaseSize(QSize(0, 20))
        self.frmVPSetting.setFrameShape(QFrame.Shape.StyledPanel)
        self.frmVPSetting.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frmVPSetting)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.btnXY_view = QToolButton(self.frmVPSetting)
        self.btnXY_view.setObjectName(u"btnXY_view")
        self.btnXY_view.setIconSize(QSize(40, 40))
        self.btnXY_view.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnXY_view.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.btnXY_view)

        self.btnZY_view = QToolButton(self.frmVPSetting)
        self.btnZY_view.setObjectName(u"btnZY_view")
        self.btnZY_view.setIconSize(QSize(40, 40))
        self.btnZY_view.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnZY_view.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.btnZY_view)

        self.btnXZ_view = QToolButton(self.frmVPSetting)
        self.btnXZ_view.setObjectName(u"btnXZ_view")
        self.btnXZ_view.setIconSize(QSize(40, 40))
        self.btnXZ_view.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnXZ_view.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.btnXZ_view)

        self.btnEdges = QToolButton(self.frmVPSetting)
        self.btnEdges.setObjectName(u"btnEdges")
        self.btnEdges.setIconSize(QSize(40, 40))
        self.btnEdges.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnEdges.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.btnEdges)

        self.btnGrid = QToolButton(self.frmVPSetting)
        self.btnGrid.setObjectName(u"btnGrid")
        self.btnGrid.setIconSize(QSize(40, 40))
        self.btnGrid.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnGrid.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.btnGrid)

        self.btnHideAllExceptSelected = QToolButton(self.frmVPSetting)
        self.btnHideAllExceptSelected.setObjectName(u"btnHideAllExceptSelected")
        self.btnHideAllExceptSelected.setIconSize(QSize(40, 40))
        self.btnHideAllExceptSelected.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnHideAllExceptSelected.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.btnHideAllExceptSelected)

        self.btnUnhideAll = QToolButton(self.frmVPSetting)
        self.btnUnhideAll.setObjectName(u"btnUnhideAll")
        self.btnUnhideAll.setIconSize(QSize(40, 40))
        self.btnUnhideAll.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnUnhideAll.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.btnUnhideAll)

        self.btnBackgroundTheme = QToolButton(self.frmVPSetting)
        self.btnBackgroundTheme.setObjectName(u"btnBackgroundTheme")
        self.btnBackgroundTheme.setIconSize(QSize(40, 40))
        self.btnBackgroundTheme.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnBackgroundTheme.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.btnBackgroundTheme)

        self.btnUnselectAll = QToolButton(self.frmVPSetting)
        self.btnUnselectAll.setObjectName(u"btnUnselectAll")
        self.btnUnselectAll.setIconSize(QSize(40, 40))
        self.btnUnselectAll.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnUnselectAll.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.btnUnselectAll)

        self.btnHideShowObjects = QToolButton(self.frmVPSetting)
        self.btnHideShowObjects.setObjectName(u"btnHideShowObjects")
        self.btnHideShowObjects.setIconSize(QSize(40, 40))
        self.btnHideShowObjects.setCheckable(True)
        self.btnHideShowObjects.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnHideShowObjects.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.btnHideShowObjects)

        self.btnScaleVisuals = QToolButton(self.frmVPSetting)
        self.btnScaleVisuals.setObjectName(u"btnScaleVisuals")
        self.btnScaleVisuals.setIconSize(QSize(40, 40))
        self.btnScaleVisuals.setCheckable(True)
        self.btnScaleVisuals.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnScaleVisuals.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.btnScaleVisuals)

        self.btnProjection = QToolButton(self.frmVPSetting)
        self.btnProjection.setObjectName(u"btnProjection")
        self.btnProjection.setIconSize(QSize(40, 40))
        self.btnProjection.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnProjection.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.btnProjection)

        self.btnFitAll = QToolButton(self.frmVPSetting)
        self.btnFitAll.setObjectName(u"btnFitAll")
        self.btnFitAll.setIconSize(QSize(40, 40))
        self.btnFitAll.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.btnFitAll.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.btnFitAll)


        self.verticalLayout_43.addWidget(self.frmVPSetting)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1209, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dckProperties = QDockWidget(MainWindow)
        self.dckProperties.setObjectName(u"dckProperties")
        self.dckProperties.setEnabled(True)
        self.dckProperties.setMinimumSize(QSize(168, 789))
        self.dckProperties.setMaximumSize(QSize(524287, 524287))
        self.dckProperties.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.verticalLayout = QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.stckProperties = QStackedWidget(self.dockWidgetContents_2)
        self.stckProperties.setObjectName(u"stckProperties")
        self.stckProperties.setMinimumSize(QSize(150, 0))
        self.pageBody = QWidget()
        self.pageBody.setObjectName(u"pageBody")
        self.verticalLayout_4 = QVBoxLayout(self.pageBody)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(3, 3, 3, 3)
        self.grbBodyProperties = QGroupBox(self.pageBody)
        self.grbBodyProperties.setObjectName(u"grbBodyProperties")
        self.grbBodyProperties.setMinimumSize(QSize(150, 0))
        self.verticalLayout_3 = QVBoxLayout(self.grbBodyProperties)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.grbBodyProperties)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.EditName = QLineEdit(self.grbBodyProperties)
        self.EditName.setObjectName(u"EditName")
        self.EditName.setReadOnly(True)

        self.gridLayout.addWidget(self.EditName, 0, 1, 1, 1)

        self.btnRenameBody = QPushButton(self.grbBodyProperties)
        self.btnRenameBody.setObjectName(u"btnRenameBody")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        self.btnRenameBody.setIcon(icon)

        self.gridLayout.addWidget(self.btnRenameBody, 0, 2, 1, 2)

        self.btnDeleteBody = QPushButton(self.grbBodyProperties)
        self.btnDeleteBody.setObjectName(u"btnDeleteBody")
        self.btnDeleteBody.setMinimumSize(QSize(36, 26))
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditDelete))
        self.btnDeleteBody.setIcon(icon1)

        self.gridLayout.addWidget(self.btnDeleteBody, 0, 4, 1, 1)

        self.label_2 = QLabel(self.grbBodyProperties)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setWordWrap(True)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.EditDensity = QLineEdit(self.grbBodyProperties)
        self.EditDensity.setObjectName(u"EditDensity")

        self.gridLayout.addWidget(self.EditDensity, 1, 1, 1, 1)

        self.btnUpdateBody = QPushButton(self.grbBodyProperties)
        self.btnUpdateBody.setObjectName(u"btnUpdateBody")
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.SyncSynchronizing))
        self.btnUpdateBody.setIcon(icon2)

        self.gridLayout.addWidget(self.btnUpdateBody, 1, 2, 1, 1)

        self.btnCopyBody = QPushButton(self.grbBodyProperties)
        self.btnCopyBody.setObjectName(u"btnCopyBody")
        self.btnCopyBody.setMinimumSize(QSize(36, 26))
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditCopy))
        self.btnCopyBody.setIcon(icon3)

        self.gridLayout.addWidget(self.btnCopyBody, 1, 3, 1, 2)


        self.verticalLayout_3.addLayout(self.gridLayout)

        self.gridLayout_48 = QGridLayout()
        self.gridLayout_48.setObjectName(u"gridLayout_48")
        self.horizontalSpacer_17 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_48.addItem(self.horizontalSpacer_17, 0, 0, 1, 1)

        self.chkApplyAllDensity = QCheckBox(self.grbBodyProperties)
        self.chkApplyAllDensity.setObjectName(u"chkApplyAllDensity")

        self.gridLayout_48.addWidget(self.chkApplyAllDensity, 0, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_48)

        self.txbBodyProperties = QTextBrowser(self.grbBodyProperties)
        self.txbBodyProperties.setObjectName(u"txbBodyProperties")
        self.txbBodyProperties.setMinimumSize(QSize(150, 100))

        self.verticalLayout_3.addWidget(self.txbBodyProperties)

        self.grbInitialVelocities = QGroupBox(self.grbBodyProperties)
        self.grbInitialVelocities.setObjectName(u"grbInitialVelocities")
        self.horizontalLayout_6 = QHBoxLayout(self.grbInitialVelocities)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.gridLayout_68 = QGridLayout()
        self.gridLayout_68.setObjectName(u"gridLayout_68")
        self.label_112 = QLabel(self.grbInitialVelocities)
        self.label_112.setObjectName(u"label_112")
        self.label_112.setMinimumSize(QSize(0, 30))
        self.label_112.setMaximumSize(QSize(60, 16777215))
        self.label_112.setWordWrap(True)

        self.gridLayout_68.addWidget(self.label_112, 0, 1, 1, 1)

        self.label_115 = QLabel(self.grbInitialVelocities)
        self.label_115.setObjectName(u"label_115")

        self.gridLayout_68.addWidget(self.label_115, 1, 0, 1, 1)

        self.Edit_Vx0 = QLineEdit(self.grbInitialVelocities)
        self.Edit_Vx0.setObjectName(u"Edit_Vx0")

        self.gridLayout_68.addWidget(self.Edit_Vx0, 1, 1, 1, 1)

        self.label_116 = QLabel(self.grbInitialVelocities)
        self.label_116.setObjectName(u"label_116")

        self.gridLayout_68.addWidget(self.label_116, 2, 0, 1, 1)

        self.Edit_Vy0 = QLineEdit(self.grbInitialVelocities)
        self.Edit_Vy0.setObjectName(u"Edit_Vy0")

        self.gridLayout_68.addWidget(self.Edit_Vy0, 2, 1, 1, 1)

        self.label_117 = QLabel(self.grbInitialVelocities)
        self.label_117.setObjectName(u"label_117")

        self.gridLayout_68.addWidget(self.label_117, 3, 0, 1, 1)

        self.Edit_Vz0 = QLineEdit(self.grbInitialVelocities)
        self.Edit_Vz0.setObjectName(u"Edit_Vz0")

        self.gridLayout_68.addWidget(self.Edit_Vz0, 3, 1, 1, 1)


        self.horizontalLayout_6.addLayout(self.gridLayout_68)

        self.gridLayout_69 = QGridLayout()
        self.gridLayout_69.setObjectName(u"gridLayout_69")
        self.label_114 = QLabel(self.grbInitialVelocities)
        self.label_114.setObjectName(u"label_114")
        self.label_114.setMinimumSize(QSize(0, 30))
        self.label_114.setMaximumSize(QSize(60, 16777215))
        self.label_114.setWordWrap(True)

        self.gridLayout_69.addWidget(self.label_114, 0, 1, 1, 1)

        self.label_118 = QLabel(self.grbInitialVelocities)
        self.label_118.setObjectName(u"label_118")

        self.gridLayout_69.addWidget(self.label_118, 1, 0, 1, 1)

        self.Edit_Wx0 = QLineEdit(self.grbInitialVelocities)
        self.Edit_Wx0.setObjectName(u"Edit_Wx0")

        self.gridLayout_69.addWidget(self.Edit_Wx0, 1, 1, 1, 1)

        self.label_120 = QLabel(self.grbInitialVelocities)
        self.label_120.setObjectName(u"label_120")

        self.gridLayout_69.addWidget(self.label_120, 2, 0, 1, 1)

        self.Edit_Wy0 = QLineEdit(self.grbInitialVelocities)
        self.Edit_Wy0.setObjectName(u"Edit_Wy0")

        self.gridLayout_69.addWidget(self.Edit_Wy0, 2, 1, 1, 1)

        self.label_119 = QLabel(self.grbInitialVelocities)
        self.label_119.setObjectName(u"label_119")

        self.gridLayout_69.addWidget(self.label_119, 3, 0, 1, 1)

        self.Edit_Wz0 = QLineEdit(self.grbInitialVelocities)
        self.Edit_Wz0.setObjectName(u"Edit_Wz0")

        self.gridLayout_69.addWidget(self.Edit_Wz0, 3, 1, 1, 1)


        self.horizontalLayout_6.addLayout(self.gridLayout_69)


        self.verticalLayout_3.addWidget(self.grbInitialVelocities)

        self.gridLayout_67 = QGridLayout()
        self.gridLayout_67.setObjectName(u"gridLayout_67")
        self.horizontalSpacer_25 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_67.addItem(self.horizontalSpacer_25, 0, 0, 1, 1)

        self.btnAssignVelocities = QPushButton(self.grbBodyProperties)
        self.btnAssignVelocities.setObjectName(u"btnAssignVelocities")

        self.gridLayout_67.addWidget(self.btnAssignVelocities, 0, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_67)

        self.grbDefineColors = QGroupBox(self.grbBodyProperties)
        self.grbDefineColors.setObjectName(u"grbDefineColors")
        self.grbDefineColors.setMaximumSize(QSize(2000, 16777215))
        self.horizontalLayout_3 = QHBoxLayout(self.grbDefineColors)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.btnColorPicker = QPushButton(self.grbDefineColors)
        self.btnColorPicker.setObjectName(u"btnColorPicker")

        self.horizontalLayout_3.addWidget(self.btnColorPicker)

        self.btnColorAllBodies = QPushButton(self.grbDefineColors)
        self.btnColorAllBodies.setObjectName(u"btnColorAllBodies")

        self.horizontalLayout_3.addWidget(self.btnColorAllBodies)

        self.btnRandomColor = QPushButton(self.grbDefineColors)
        self.btnRandomColor.setObjectName(u"btnRandomColor")

        self.horizontalLayout_3.addWidget(self.btnRandomColor)


        self.verticalLayout_3.addWidget(self.grbDefineColors)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.chkEnabled = QCheckBox(self.grbBodyProperties)
        self.chkEnabled.setObjectName(u"chkEnabled")
        self.chkEnabled.setChecked(True)

        self.horizontalLayout_4.addWidget(self.chkEnabled)

        self.horizontalSpacer_26 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_26)

        self.chkVisible = QCheckBox(self.grbBodyProperties)
        self.chkVisible.setObjectName(u"chkVisible")
        self.chkVisible.setChecked(True)

        self.horizontalLayout_4.addWidget(self.chkVisible)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)


        self.verticalLayout_4.addWidget(self.grbBodyProperties)

        self.stckProperties.addWidget(self.pageBody)
        self.pageRF = QWidget()
        self.pageRF.setObjectName(u"pageRF")
        self.verticalLayout_7 = QVBoxLayout(self.pageRF)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.grbRFProperties = QGroupBox(self.pageRF)
        self.grbRFProperties.setObjectName(u"grbRFProperties")
        self.verticalLayout_6 = QVBoxLayout(self.grbRFProperties)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(3, -1, 3, -1)
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_3 = QLabel(self.grbRFProperties)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_3.addWidget(self.label_3, 0, 0, 1, 1)

        self.Edit_RFName = QLineEdit(self.grbRFProperties)
        self.Edit_RFName.setObjectName(u"Edit_RFName")
        self.Edit_RFName.setReadOnly(True)

        self.gridLayout_3.addWidget(self.Edit_RFName, 0, 1, 1, 1)

        self.btnRenameRF = QPushButton(self.grbRFProperties)
        self.btnRenameRF.setObjectName(u"btnRenameRF")
        self.btnRenameRF.setMinimumSize(QSize(36, 26))
        self.btnRenameRF.setIcon(icon)

        self.gridLayout_3.addWidget(self.btnRenameRF, 0, 2, 1, 1)

        self.btnDeleteRF = QPushButton(self.grbRFProperties)
        self.btnDeleteRF.setObjectName(u"btnDeleteRF")
        self.btnDeleteRF.setMinimumSize(QSize(36, 26))
        self.btnDeleteRF.setIcon(icon1)

        self.gridLayout_3.addWidget(self.btnDeleteRF, 0, 3, 1, 1)


        self.verticalLayout_6.addLayout(self.gridLayout_3)

        self.frame_2 = QFrame(self.grbRFProperties)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_4 = QLabel(self.frame_2)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 0, 0, 1, 2)

        self.label_8 = QLabel(self.frame_2)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 0, 2, 1, 2)

        self.label_5 = QLabel(self.frame_2)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 1, 0, 1, 1)

        self.EditRF_X_Pos = QLineEdit(self.frame_2)
        self.EditRF_X_Pos.setObjectName(u"EditRF_X_Pos")

        self.gridLayout_2.addWidget(self.EditRF_X_Pos, 1, 1, 1, 1)

        self.label_9 = QLabel(self.frame_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_2.addWidget(self.label_9, 1, 2, 1, 1)

        self.EditRF_X_Angle = QLineEdit(self.frame_2)
        self.EditRF_X_Angle.setObjectName(u"EditRF_X_Angle")

        self.gridLayout_2.addWidget(self.EditRF_X_Angle, 1, 3, 1, 1)

        self.label_6 = QLabel(self.frame_2)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 2, 0, 1, 1)

        self.EditRF_Y_Pos = QLineEdit(self.frame_2)
        self.EditRF_Y_Pos.setObjectName(u"EditRF_Y_Pos")

        self.gridLayout_2.addWidget(self.EditRF_Y_Pos, 2, 1, 1, 1)

        self.label_10 = QLabel(self.frame_2)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_2.addWidget(self.label_10, 2, 2, 1, 1)

        self.EditRF_Y_Angle = QLineEdit(self.frame_2)
        self.EditRF_Y_Angle.setObjectName(u"EditRF_Y_Angle")

        self.gridLayout_2.addWidget(self.EditRF_Y_Angle, 2, 3, 1, 1)

        self.label_7 = QLabel(self.frame_2)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_2.addWidget(self.label_7, 3, 0, 1, 1)

        self.EditRF_Z_Pos = QLineEdit(self.frame_2)
        self.EditRF_Z_Pos.setObjectName(u"EditRF_Z_Pos")

        self.gridLayout_2.addWidget(self.EditRF_Z_Pos, 3, 1, 1, 1)

        self.label_11 = QLabel(self.frame_2)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_2.addWidget(self.label_11, 3, 2, 1, 1)

        self.EditRF_Z_Angle = QLineEdit(self.frame_2)
        self.EditRF_Z_Angle.setObjectName(u"EditRF_Z_Angle")

        self.gridLayout_2.addWidget(self.EditRF_Z_Angle, 3, 3, 1, 1)


        self.verticalLayout_5.addLayout(self.gridLayout_2)


        self.verticalLayout_6.addWidget(self.frame_2)

        self.gridLayout_17 = QGridLayout()
        self.gridLayout_17.setObjectName(u"gridLayout_17")
        self.btnUpdateRF = QPushButton(self.grbRFProperties)
        self.btnUpdateRF.setObjectName(u"btnUpdateRF")
        self.btnUpdateRF.setMinimumSize(QSize(36, 26))
        self.btnUpdateRF.setIcon(icon2)

        self.gridLayout_17.addWidget(self.btnUpdateRF, 0, 2, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_17.addItem(self.horizontalSpacer_2, 0, 1, 1, 1)

        self.btnAddUpdateRF = QPushButton(self.grbRFProperties)
        self.btnAddUpdateRF.setObjectName(u"btnAddUpdateRF")

        self.gridLayout_17.addWidget(self.btnAddUpdateRF, 0, 0, 1, 1)


        self.verticalLayout_6.addLayout(self.gridLayout_17)


        self.verticalLayout_7.addWidget(self.grbRFProperties)

        self.frame_3 = QFrame(self.pageRF)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMinimumSize(QSize(0, 160))
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.grbRFMove = QGroupBox(self.frame_3)
        self.grbRFMove.setObjectName(u"grbRFMove")
        self.grbRFMove.setGeometry(QRect(10, 0, 131, 126))
        self.gridLayout_45 = QGridLayout(self.grbRFMove)
        self.gridLayout_45.setObjectName(u"gridLayout_45")
        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.rbnRFalongX = QRadioButton(self.grbRFMove)
        self.rbnRFalongX.setObjectName(u"rbnRFalongX")
        self.rbnRFalongX.setChecked(True)

        self.gridLayout_4.addWidget(self.rbnRFalongX, 0, 0, 1, 1)

        self.dsbShift_RF = QDoubleSpinBox(self.grbRFMove)
        self.dsbShift_RF.setObjectName(u"dsbShift_RF")
        self.dsbShift_RF.setDecimals(1)
        self.dsbShift_RF.setMinimum(0.000000000000000)
        self.dsbShift_RF.setMaximum(500.000000000000000)
        self.dsbShift_RF.setSingleStep(5.000000000000000)
        self.dsbShift_RF.setValue(5.000000000000000)

        self.gridLayout_4.addWidget(self.dsbShift_RF, 0, 1, 1, 1)


        self.gridLayout_45.addLayout(self.gridLayout_4, 0, 0, 1, 2)

        self.rbnRFalongY = QRadioButton(self.grbRFMove)
        self.rbnRFalongY.setObjectName(u"rbnRFalongY")

        self.gridLayout_45.addWidget(self.rbnRFalongY, 1, 0, 1, 1)

        self.btnShiftRF = QPushButton(self.grbRFMove)
        self.btnShiftRF.setObjectName(u"btnShiftRF")
        self.btnShiftRF.setMinimumSize(QSize(0, 50))
        self.btnShiftRF.setAutoDefault(False)
        self.btnShiftRF.setFlat(False)

        self.gridLayout_45.addWidget(self.btnShiftRF, 1, 1, 2, 1)

        self.rbnRFalongZ = QRadioButton(self.grbRFMove)
        self.rbnRFalongZ.setObjectName(u"rbnRFalongZ")

        self.gridLayout_45.addWidget(self.rbnRFalongZ, 2, 0, 1, 1)

        self.grbRFRotate = QGroupBox(self.frame_3)
        self.grbRFRotate.setObjectName(u"grbRFRotate")
        self.grbRFRotate.setGeometry(QRect(150, 0, 131, 126))
        self.gridLayout_47 = QGridLayout(self.grbRFRotate)
        self.gridLayout_47.setObjectName(u"gridLayout_47")
        self.gridLayout_46 = QGridLayout()
        self.gridLayout_46.setObjectName(u"gridLayout_46")
        self.rbnRFaroundX = QRadioButton(self.grbRFRotate)
        self.rbnRFaroundX.setObjectName(u"rbnRFaroundX")
        self.rbnRFaroundX.setChecked(True)

        self.gridLayout_46.addWidget(self.rbnRFaroundX, 0, 0, 1, 1)

        self.dsbRotate_RF = QDoubleSpinBox(self.grbRFRotate)
        self.dsbRotate_RF.setObjectName(u"dsbRotate_RF")
        self.dsbRotate_RF.setDecimals(1)
        self.dsbRotate_RF.setMinimum(0.000000000000000)
        self.dsbRotate_RF.setMaximum(500.000000000000000)
        self.dsbRotate_RF.setSingleStep(5.000000000000000)
        self.dsbRotate_RF.setValue(5.000000000000000)

        self.gridLayout_46.addWidget(self.dsbRotate_RF, 0, 1, 1, 1)


        self.gridLayout_47.addLayout(self.gridLayout_46, 0, 0, 1, 2)

        self.rbnRFaroundY = QRadioButton(self.grbRFRotate)
        self.rbnRFaroundY.setObjectName(u"rbnRFaroundY")

        self.gridLayout_47.addWidget(self.rbnRFaroundY, 1, 0, 1, 1)

        self.btnRotateRF = QPushButton(self.grbRFRotate)
        self.btnRotateRF.setObjectName(u"btnRotateRF")
        self.btnRotateRF.setMinimumSize(QSize(0, 50))

        self.gridLayout_47.addWidget(self.btnRotateRF, 1, 1, 2, 1)

        self.rbnRFaroundZ = QRadioButton(self.grbRFRotate)
        self.rbnRFaroundZ.setObjectName(u"rbnRFaroundZ")

        self.gridLayout_47.addWidget(self.rbnRFaroundZ, 2, 0, 1, 1)

        self.chkMoveBody = QCheckBox(self.frame_3)
        self.chkMoveBody.setObjectName(u"chkMoveBody")
        self.chkMoveBody.setGeometry(QRect(10, 130, 171, 24))

        self.verticalLayout_7.addWidget(self.frame_3)

        self.verticalSpacer = QSpacerItem(20, 251, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer)

        self.stckProperties.addWidget(self.pageRF)
        self.pageJoint = QWidget()
        self.pageJoint.setObjectName(u"pageJoint")
        self.verticalLayout_13 = QVBoxLayout(self.pageJoint)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.grbJoints = QGroupBox(self.pageJoint)
        self.grbJoints.setObjectName(u"grbJoints")
        self.verticalLayout_12 = QVBoxLayout(self.grbJoints)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.gridLayout_13 = QGridLayout()
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.label_15 = QLabel(self.grbJoints)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_13.addWidget(self.label_15, 0, 0, 1, 1)

        self.Edit_Joint_Name = QLineEdit(self.grbJoints)
        self.Edit_Joint_Name.setObjectName(u"Edit_Joint_Name")
        self.Edit_Joint_Name.setReadOnly(True)

        self.gridLayout_13.addWidget(self.Edit_Joint_Name, 0, 1, 1, 1)

        self.btnRenameJoint = QPushButton(self.grbJoints)
        self.btnRenameJoint.setObjectName(u"btnRenameJoint")
        self.btnRenameJoint.setMaximumSize(QSize(36, 26))
        self.btnRenameJoint.setIcon(icon)

        self.gridLayout_13.addWidget(self.btnRenameJoint, 0, 2, 1, 1)

        self.btnDelJoint = QPushButton(self.grbJoints)
        self.btnDelJoint.setObjectName(u"btnDelJoint")
        self.btnDelJoint.setMinimumSize(QSize(36, 26))
        self.btnDelJoint.setIcon(icon1)

        self.gridLayout_13.addWidget(self.btnDelJoint, 0, 3, 1, 1)

        self.label_29 = QLabel(self.grbJoints)
        self.label_29.setObjectName(u"label_29")

        self.gridLayout_13.addWidget(self.label_29, 1, 0, 1, 1)

        self.cmbJointType = QComboBox(self.grbJoints)
        self.cmbJointType.addItem("")
        self.cmbJointType.addItem("")
        self.cmbJointType.addItem("")
        self.cmbJointType.addItem("")
        self.cmbJointType.addItem("")
        self.cmbJointType.addItem("")
        self.cmbJointType.setObjectName(u"cmbJointType")

        self.gridLayout_13.addWidget(self.cmbJointType, 1, 1, 1, 1)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_13.addItem(self.horizontalSpacer_6, 1, 2, 1, 2)


        self.verticalLayout_12.addLayout(self.gridLayout_13)

        self.gridLayout_10 = QGridLayout()
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.label_20 = QLabel(self.grbJoints)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_10.addWidget(self.label_20, 1, 0, 1, 1)

        self.Edit_Body_J = QLineEdit(self.grbJoints)
        self.Edit_Body_J.setObjectName(u"Edit_Body_J")
        self.Edit_Body_J.setReadOnly(True)

        self.gridLayout_10.addWidget(self.Edit_Body_J, 1, 1, 1, 1)

        self.label_19 = QLabel(self.grbJoints)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout_10.addWidget(self.label_19, 0, 0, 1, 1)

        self.Edit_Body_I = QLineEdit(self.grbJoints)
        self.Edit_Body_I.setObjectName(u"Edit_Body_I")
        self.Edit_Body_I.setReadOnly(True)

        self.gridLayout_10.addWidget(self.Edit_Body_I, 0, 1, 1, 1)


        self.verticalLayout_12.addLayout(self.gridLayout_10)

        self.gridLayout_11 = QGridLayout()
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.Edit_RF_Target = QLineEdit(self.grbJoints)
        self.Edit_RF_Target.setObjectName(u"Edit_RF_Target")
        self.Edit_RF_Target.setReadOnly(True)

        self.gridLayout_11.addWidget(self.Edit_RF_Target, 1, 1, 1, 1)

        self.label_22 = QLabel(self.grbJoints)
        self.label_22.setObjectName(u"label_22")

        self.gridLayout_11.addWidget(self.label_22, 1, 0, 1, 1)

        self.label_21 = QLabel(self.grbJoints)
        self.label_21.setObjectName(u"label_21")

        self.gridLayout_11.addWidget(self.label_21, 0, 0, 1, 1)

        self.Edit_RF_Anchor = QLineEdit(self.grbJoints)
        self.Edit_RF_Anchor.setObjectName(u"Edit_RF_Anchor")
        self.Edit_RF_Anchor.setReadOnly(True)

        self.gridLayout_11.addWidget(self.Edit_RF_Anchor, 0, 1, 1, 1)

        self.cmbAnchorXYZ = QComboBox(self.grbJoints)
        self.cmbAnchorXYZ.addItem("")
        self.cmbAnchorXYZ.addItem("")
        self.cmbAnchorXYZ.addItem("")
        self.cmbAnchorXYZ.setObjectName(u"cmbAnchorXYZ")

        self.gridLayout_11.addWidget(self.cmbAnchorXYZ, 0, 2, 1, 1)


        self.verticalLayout_12.addLayout(self.gridLayout_11)

        self.gridLayout_12 = QGridLayout()
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.btnAddJoint = QPushButton(self.grbJoints)
        self.btnAddJoint.setObjectName(u"btnAddJoint")

        self.gridLayout_12.addWidget(self.btnAddJoint, 0, 0, 1, 1)

        self.btnCleanBodiesRFs = QPushButton(self.grbJoints)
        self.btnCleanBodiesRFs.setObjectName(u"btnCleanBodiesRFs")
        icon4 = QIcon(QIcon.fromTheme(u"edit-clear"))
        self.btnCleanBodiesRFs.setIcon(icon4)

        self.gridLayout_12.addWidget(self.btnCleanBodiesRFs, 0, 1, 1, 1)

        self.chkEnabledJoint = QCheckBox(self.grbJoints)
        self.chkEnabledJoint.setObjectName(u"chkEnabledJoint")
        self.chkEnabledJoint.setChecked(True)

        self.gridLayout_12.addWidget(self.chkEnabledJoint, 0, 2, 1, 1)


        self.verticalLayout_12.addLayout(self.gridLayout_12)


        self.verticalLayout_13.addWidget(self.grbJoints)

        self.verticalSpacer_3 = QSpacerItem(20, 358, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_13.addItem(self.verticalSpacer_3)

        self.stckProperties.addWidget(self.pageJoint)
        self.pageForce = QWidget()
        self.pageForce.setObjectName(u"pageForce")
        self.verticalLayout_17 = QVBoxLayout(self.pageForce)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.grbForcesTorques = QGroupBox(self.pageForce)
        self.grbForcesTorques.setObjectName(u"grbForcesTorques")
        self.verticalLayout_16 = QVBoxLayout(self.grbForcesTorques)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.gridLayout_15 = QGridLayout()
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.label_16 = QLabel(self.grbForcesTorques)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setFrameShape(QFrame.Shape.NoFrame)
        self.label_16.setFrameShadow(QFrame.Shadow.Plain)

        self.gridLayout_15.addWidget(self.label_16, 0, 0, 1, 1)

        self.Edit_ForceName = QLineEdit(self.grbForcesTorques)
        self.Edit_ForceName.setObjectName(u"Edit_ForceName")
        self.Edit_ForceName.setEnabled(True)
        self.Edit_ForceName.setReadOnly(True)

        self.gridLayout_15.addWidget(self.Edit_ForceName, 0, 1, 1, 1)

        self.btnRenameForce = QPushButton(self.grbForcesTorques)
        self.btnRenameForce.setObjectName(u"btnRenameForce")
        self.btnRenameForce.setMaximumSize(QSize(36, 26))
        self.btnRenameForce.setIcon(icon)

        self.gridLayout_15.addWidget(self.btnRenameForce, 0, 2, 1, 1)

        self.btnDelForceTorque = QPushButton(self.grbForcesTorques)
        self.btnDelForceTorque.setObjectName(u"btnDelForceTorque")
        self.btnDelForceTorque.setMaximumSize(QSize(36, 26))
        self.btnDelForceTorque.setIcon(icon1)

        self.gridLayout_15.addWidget(self.btnDelForceTorque, 0, 3, 1, 1)


        self.verticalLayout_16.addLayout(self.gridLayout_15)

        self.gridLayout_16 = QGridLayout()
        self.gridLayout_16.setObjectName(u"gridLayout_16")
        self.label_17 = QLabel(self.grbForcesTorques)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setFrameShape(QFrame.Shape.NoFrame)
        self.label_17.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout_16.addWidget(self.label_17, 0, 0, 1, 1)

        self.Edit_BodyForce = QLineEdit(self.grbForcesTorques)
        self.Edit_BodyForce.setObjectName(u"Edit_BodyForce")
        self.Edit_BodyForce.setReadOnly(True)

        self.gridLayout_16.addWidget(self.Edit_BodyForce, 0, 1, 1, 1)

        self.label_18 = QLabel(self.grbForcesTorques)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_16.addWidget(self.label_18, 1, 0, 1, 1)

        self.Edit_RFForce = QLineEdit(self.grbForcesTorques)
        self.Edit_RFForce.setObjectName(u"Edit_RFForce")
        self.Edit_RFForce.setReadOnly(True)

        self.gridLayout_16.addWidget(self.Edit_RFForce, 1, 1, 1, 1)

        self.cmbForceAnchorXYZ = QComboBox(self.grbForcesTorques)
        self.cmbForceAnchorXYZ.addItem("")
        self.cmbForceAnchorXYZ.addItem("")
        self.cmbForceAnchorXYZ.addItem("")
        self.cmbForceAnchorXYZ.setObjectName(u"cmbForceAnchorXYZ")

        self.gridLayout_16.addWidget(self.cmbForceAnchorXYZ, 1, 2, 1, 1)


        self.verticalLayout_16.addLayout(self.gridLayout_16)

        self.line_2 = QFrame(self.grbForcesTorques)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_16.addWidget(self.line_2)

        self.gridLayout_14 = QGridLayout()
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.cmbForceType = QComboBox(self.grbForcesTorques)
        self.cmbForceType.addItem("")
        self.cmbForceType.addItem("")
        self.cmbForceType.setObjectName(u"cmbForceType")
        self.cmbForceType.setEditable(False)

        self.gridLayout_14.addWidget(self.cmbForceType, 0, 0, 1, 3)

        self.cmbSpaceBody = QComboBox(self.grbForcesTorques)
        self.cmbSpaceBody.addItem("")
        self.cmbSpaceBody.addItem("")
        self.cmbSpaceBody.setObjectName(u"cmbSpaceBody")
        self.cmbSpaceBody.setEditable(False)

        self.gridLayout_14.addWidget(self.cmbSpaceBody, 0, 3, 1, 3)

        self.lblNNm = QLabel(self.grbForcesTorques)
        self.lblNNm.setObjectName(u"lblNNm")

        self.gridLayout_14.addWidget(self.lblNNm, 1, 0, 1, 1)

        self.Edit_ForceValue = QLineEdit(self.grbForcesTorques)
        self.Edit_ForceValue.setObjectName(u"Edit_ForceValue")

        self.gridLayout_14.addWidget(self.Edit_ForceValue, 1, 1, 1, 4)

        self.btnUpdateForceTorque = QPushButton(self.grbForcesTorques)
        self.btnUpdateForceTorque.setObjectName(u"btnUpdateForceTorque")
        self.btnUpdateForceTorque.setMaximumSize(QSize(36, 26))
        self.btnUpdateForceTorque.setIcon(icon2)

        self.gridLayout_14.addWidget(self.btnUpdateForceTorque, 1, 5, 1, 1)

        self.btnAddForceTorque = QPushButton(self.grbForcesTorques)
        self.btnAddForceTorque.setObjectName(u"btnAddForceTorque")

        self.gridLayout_14.addWidget(self.btnAddForceTorque, 2, 0, 1, 2)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_14.addItem(self.horizontalSpacer_5, 2, 2, 1, 2)

        self.chkEnabledForce = QCheckBox(self.grbForcesTorques)
        self.chkEnabledForce.setObjectName(u"chkEnabledForce")
        self.chkEnabledForce.setChecked(True)

        self.gridLayout_14.addWidget(self.chkEnabledForce, 2, 4, 1, 2)


        self.verticalLayout_16.addLayout(self.gridLayout_14)

        self.line = QFrame(self.grbForcesTorques)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_16.addWidget(self.line)

        self.gridLayout_18 = QGridLayout()
        self.gridLayout_18.setObjectName(u"gridLayout_18")
        self.chkActuatorMode = QCheckBox(self.grbForcesTorques)
        self.chkActuatorMode.setObjectName(u"chkActuatorMode")

        self.gridLayout_18.addWidget(self.chkActuatorMode, 0, 0, 1, 1)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_18.addItem(self.horizontalSpacer_7, 0, 1, 1, 1)


        self.verticalLayout_16.addLayout(self.gridLayout_18)

        self.frmActuatorSettings = QFrame(self.grbForcesTorques)
        self.frmActuatorSettings.setObjectName(u"frmActuatorSettings")
        self.frmActuatorSettings.setEnabled(False)
        self.frmActuatorSettings.setFrameShape(QFrame.Shape.StyledPanel)
        self.frmActuatorSettings.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_14 = QVBoxLayout(self.frmActuatorSettings)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.gridLayout_20 = QGridLayout()
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.lblSpeedUnit = QLabel(self.frmActuatorSettings)
        self.lblSpeedUnit.setObjectName(u"lblSpeedUnit")

        self.gridLayout_20.addWidget(self.lblSpeedUnit, 0, 0, 1, 1)

        self.Edit_MaxActuatorSpeed = QLineEdit(self.frmActuatorSettings)
        self.Edit_MaxActuatorSpeed.setObjectName(u"Edit_MaxActuatorSpeed")

        self.gridLayout_20.addWidget(self.Edit_MaxActuatorSpeed, 0, 1, 1, 1)

        self.label_31 = QLabel(self.frmActuatorSettings)
        self.label_31.setObjectName(u"label_31")

        self.gridLayout_20.addWidget(self.label_31, 1, 0, 1, 1)

        self.Edit_ActPowerLimit = QLineEdit(self.frmActuatorSettings)
        self.Edit_ActPowerLimit.setObjectName(u"Edit_ActPowerLimit")
        self.Edit_ActPowerLimit.setReadOnly(True)

        self.gridLayout_20.addWidget(self.Edit_ActPowerLimit, 1, 1, 1, 1)


        self.verticalLayout_14.addLayout(self.gridLayout_20)

        self.chkAllowActuatorBraking = QCheckBox(self.frmActuatorSettings)
        self.chkAllowActuatorBraking.setObjectName(u"chkAllowActuatorBraking")
        self.chkAllowActuatorBraking.setChecked(True)

        self.verticalLayout_14.addWidget(self.chkAllowActuatorBraking)


        self.verticalLayout_16.addWidget(self.frmActuatorSettings)


        self.verticalLayout_17.addWidget(self.grbForcesTorques)

        self.verticalSpacer_4 = QSpacerItem(20, 205, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_17.addItem(self.verticalSpacer_4)

        self.grbGravity = QGroupBox(self.pageForce)
        self.grbGravity.setObjectName(u"grbGravity")
        self.verticalLayout_15 = QVBoxLayout(self.grbGravity)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.gridLayout_19 = QGridLayout()
        self.gridLayout_19.setObjectName(u"gridLayout_19")
        self.label_12 = QLabel(self.grbGravity)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_19.addWidget(self.label_12, 0, 0, 1, 1)

        self.Edit_GravityX = QLineEdit(self.grbGravity)
        self.Edit_GravityX.setObjectName(u"Edit_GravityX")

        self.gridLayout_19.addWidget(self.Edit_GravityX, 0, 1, 1, 1)

        self.chkEnabledGravity = QCheckBox(self.grbGravity)
        self.chkEnabledGravity.setObjectName(u"chkEnabledGravity")
        self.chkEnabledGravity.setChecked(True)

        self.gridLayout_19.addWidget(self.chkEnabledGravity, 0, 2, 1, 1)

        self.label_13 = QLabel(self.grbGravity)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_19.addWidget(self.label_13, 1, 0, 1, 1)

        self.Edit_GravityY = QLineEdit(self.grbGravity)
        self.Edit_GravityY.setObjectName(u"Edit_GravityY")

        self.gridLayout_19.addWidget(self.Edit_GravityY, 1, 1, 1, 1)

        self.chkVisibleGravity = QCheckBox(self.grbGravity)
        self.chkVisibleGravity.setObjectName(u"chkVisibleGravity")
        self.chkVisibleGravity.setChecked(False)

        self.gridLayout_19.addWidget(self.chkVisibleGravity, 1, 2, 1, 1)

        self.label_14 = QLabel(self.grbGravity)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_19.addWidget(self.label_14, 2, 0, 1, 1)

        self.Edit_GravityZ = QLineEdit(self.grbGravity)
        self.Edit_GravityZ.setObjectName(u"Edit_GravityZ")

        self.gridLayout_19.addWidget(self.Edit_GravityZ, 2, 1, 1, 1)

        self.btnUpdateGravity = QPushButton(self.grbGravity)
        self.btnUpdateGravity.setObjectName(u"btnUpdateGravity")
        self.btnUpdateGravity.setIcon(icon2)

        self.gridLayout_19.addWidget(self.btnUpdateGravity, 2, 2, 1, 1)


        self.verticalLayout_15.addLayout(self.gridLayout_19)


        self.verticalLayout_17.addWidget(self.grbGravity)

        self.stckProperties.addWidget(self.pageForce)
        self.pageSimulation = QWidget()
        self.pageSimulation.setObjectName(u"pageSimulation")
        self.verticalLayout_30 = QVBoxLayout(self.pageSimulation)
        self.verticalLayout_30.setObjectName(u"verticalLayout_30")
        self.grbSolverSetting = QGroupBox(self.pageSimulation)
        self.grbSolverSetting.setObjectName(u"grbSolverSetting")
        self.grbSolverSetting.setMinimumSize(QSize(0, 330))
        self.verticalLayout_11 = QVBoxLayout(self.grbSolverSetting)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.label_23 = QLabel(self.grbSolverSetting)
        self.label_23.setObjectName(u"label_23")

        self.gridLayout_8.addWidget(self.label_23, 0, 0, 1, 2)

        self.Edit_SimulationTime = QLineEdit(self.grbSolverSetting)
        self.Edit_SimulationTime.setObjectName(u"Edit_SimulationTime")

        self.gridLayout_8.addWidget(self.Edit_SimulationTime, 0, 2, 1, 1)

        self.label_24 = QLabel(self.grbSolverSetting)
        self.label_24.setObjectName(u"label_24")

        self.gridLayout_8.addWidget(self.label_24, 1, 0, 1, 2)

        self.Edit_StepsPerSec = QLineEdit(self.grbSolverSetting)
        self.Edit_StepsPerSec.setObjectName(u"Edit_StepsPerSec")

        self.gridLayout_8.addWidget(self.Edit_StepsPerSec, 1, 2, 1, 1)

        self.label_30 = QLabel(self.grbSolverSetting)
        self.label_30.setObjectName(u"label_30")

        self.gridLayout_8.addWidget(self.label_30, 2, 0, 1, 1)

        self.cmbSolverMethod = QComboBox(self.grbSolverSetting)
        self.cmbSolverMethod.addItem("")
        self.cmbSolverMethod.addItem("")
        self.cmbSolverMethod.addItem("")
        self.cmbSolverMethod.addItem("")
        self.cmbSolverMethod.addItem("")
        self.cmbSolverMethod.addItem("")
        self.cmbSolverMethod.addItem("")
        self.cmbSolverMethod.addItem("")
        self.cmbSolverMethod.addItem("")
        self.cmbSolverMethod.setObjectName(u"cmbSolverMethod")

        self.gridLayout_8.addWidget(self.cmbSolverMethod, 2, 1, 1, 2)


        self.verticalLayout_11.addLayout(self.gridLayout_8)

        self.gridLayout_9 = QGridLayout()
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.btnSolve = QPushButton(self.grbSolverSetting)
        self.btnSolve.setObjectName(u"btnSolve")
        self.btnSolve.setMinimumSize(QSize(70, 50))

        self.gridLayout_9.addWidget(self.btnSolve, 0, 0, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_9.addItem(self.horizontalSpacer_3, 0, 1, 1, 1)

        self.btnBreakSolving = QToolButton(self.grbSolverSetting)
        self.btnBreakSolving.setObjectName(u"btnBreakSolving")
        self.btnBreakSolving.setIconSize(QSize(30, 30))
        self.btnBreakSolving.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.btnBreakSolving.setAutoRaise(True)

        self.gridLayout_9.addWidget(self.btnBreakSolving, 0, 2, 1, 1)


        self.verticalLayout_11.addLayout(self.gridLayout_9)

        self.progressBar = QProgressBar(self.grbSolverSetting)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.verticalLayout_11.addWidget(self.progressBar)

        self.label_87 = QLabel(self.grbSolverSetting)
        self.label_87.setObjectName(u"label_87")

        self.verticalLayout_11.addWidget(self.label_87)

        self.line_15 = QFrame(self.grbSolverSetting)
        self.line_15.setObjectName(u"line_15")
        self.line_15.setFrameShape(QFrame.Shape.HLine)
        self.line_15.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_11.addWidget(self.line_15)

        self.frame_4 = QFrame(self.grbSolverSetting)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.frame_4)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_27 = QLabel(self.frame_4)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setWordWrap(True)

        self.gridLayout_5.addWidget(self.label_27, 0, 0, 1, 1)

        self.label_28 = QLabel(self.frame_4)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setWordWrap(True)

        self.gridLayout_5.addWidget(self.label_28, 0, 1, 1, 1)

        self.cmbSolverCompliance = QComboBox(self.frame_4)
        self.cmbSolverCompliance.addItem("")
        self.cmbSolverCompliance.addItem("")
        self.cmbSolverCompliance.addItem("")
        self.cmbSolverCompliance.addItem("")
        self.cmbSolverCompliance.addItem("")
        self.cmbSolverCompliance.setObjectName(u"cmbSolverCompliance")

        self.gridLayout_5.addWidget(self.cmbSolverCompliance, 1, 0, 1, 1)

        self.Edit_Alpha_Beta = QLineEdit(self.frame_4)
        self.Edit_Alpha_Beta.setObjectName(u"Edit_Alpha_Beta")

        self.gridLayout_5.addWidget(self.Edit_Alpha_Beta, 1, 1, 1, 1)


        self.verticalLayout_10.addLayout(self.gridLayout_5)


        self.verticalLayout_11.addWidget(self.frame_4)

        self.frmAdvancedSolver = QFrame(self.grbSolverSetting)
        self.frmAdvancedSolver.setObjectName(u"frmAdvancedSolver")
        self.frmAdvancedSolver.setFrameShape(QFrame.Shape.StyledPanel)
        self.frmAdvancedSolver.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.frmAdvancedSolver)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.gridLayout_49 = QGridLayout()
        self.gridLayout_49.setObjectName(u"gridLayout_49")
        self.label_82 = QLabel(self.frmAdvancedSolver)
        self.label_82.setObjectName(u"label_82")

        self.gridLayout_49.addWidget(self.label_82, 0, 0, 1, 1)

        self.cmbRtol = QComboBox(self.frmAdvancedSolver)
        self.cmbRtol.addItem("")
        self.cmbRtol.addItem("")
        self.cmbRtol.addItem("")
        self.cmbRtol.addItem("")
        self.cmbRtol.setObjectName(u"cmbRtol")

        self.gridLayout_49.addWidget(self.cmbRtol, 0, 1, 1, 1)

        self.label_85 = QLabel(self.frmAdvancedSolver)
        self.label_85.setObjectName(u"label_85")

        self.gridLayout_49.addWidget(self.label_85, 1, 0, 1, 1)

        self.cmbAtol = QComboBox(self.frmAdvancedSolver)
        self.cmbAtol.addItem("")
        self.cmbAtol.addItem("")
        self.cmbAtol.addItem("")
        self.cmbAtol.addItem("")
        self.cmbAtol.addItem("")
        self.cmbAtol.setObjectName(u"cmbAtol")

        self.gridLayout_49.addWidget(self.cmbAtol, 1, 1, 1, 1)

        self.label_86 = QLabel(self.frmAdvancedSolver)
        self.label_86.setObjectName(u"label_86")

        self.gridLayout_49.addWidget(self.label_86, 2, 0, 1, 1)

        self.cmbMaxStep = QComboBox(self.frmAdvancedSolver)
        self.cmbMaxStep.addItem("")
        self.cmbMaxStep.addItem("")
        self.cmbMaxStep.addItem("")
        self.cmbMaxStep.addItem("")
        self.cmbMaxStep.setObjectName(u"cmbMaxStep")

        self.gridLayout_49.addWidget(self.cmbMaxStep, 2, 1, 1, 1)


        self.verticalLayout_9.addLayout(self.gridLayout_49)


        self.verticalLayout_11.addWidget(self.frmAdvancedSolver)


        self.verticalLayout_30.addWidget(self.grbSolverSetting)

        self.verticalSpacer_2 = QSpacerItem(20, 170, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_30.addItem(self.verticalSpacer_2)

        self.grbAnimation = QGroupBox(self.pageSimulation)
        self.grbAnimation.setObjectName(u"grbAnimation")
        self.verticalLayout_8 = QVBoxLayout(self.grbAnimation)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_26 = QLabel(self.grbAnimation)
        self.label_26.setObjectName(u"label_26")

        self.gridLayout_6.addWidget(self.label_26, 0, 0, 1, 1)

        self.Edit_FPS = QLineEdit(self.grbAnimation)
        self.Edit_FPS.setObjectName(u"Edit_FPS")

        self.gridLayout_6.addWidget(self.Edit_FPS, 0, 1, 1, 1)

        self.label_25 = QLabel(self.grbAnimation)
        self.label_25.setObjectName(u"label_25")

        self.gridLayout_6.addWidget(self.label_25, 1, 0, 1, 1)

        self.Edit_AnimationSpeed = QLineEdit(self.grbAnimation)
        self.Edit_AnimationSpeed.setObjectName(u"Edit_AnimationSpeed")

        self.gridLayout_6.addWidget(self.Edit_AnimationSpeed, 1, 1, 1, 1)


        self.verticalLayout_8.addLayout(self.gridLayout_6)

        self.hslAnimSpeed = QSlider(self.grbAnimation)
        self.hslAnimSpeed.setObjectName(u"hslAnimSpeed")
        self.hslAnimSpeed.setMinimum(5)
        self.hslAnimSpeed.setMaximum(200)
        self.hslAnimSpeed.setPageStep(5)
        self.hslAnimSpeed.setValue(30)
        self.hslAnimSpeed.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout_8.addWidget(self.hslAnimSpeed)

        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.btnRunAnimation = QPushButton(self.grbAnimation)
        self.btnRunAnimation.setObjectName(u"btnRunAnimation")
        icon5 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStart))
        self.btnRunAnimation.setIcon(icon5)

        self.gridLayout_7.addWidget(self.btnRunAnimation, 0, 0, 1, 1)

        self.btnPauseAnimation = QPushButton(self.grbAnimation)
        self.btnPauseAnimation.setObjectName(u"btnPauseAnimation")
        icon6 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackPause))
        self.btnPauseAnimation.setIcon(icon6)

        self.gridLayout_7.addWidget(self.btnPauseAnimation, 0, 1, 1, 1)

        self.btnStopAnimation = QPushButton(self.grbAnimation)
        self.btnStopAnimation.setObjectName(u"btnStopAnimation")
        icon7 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStop))
        self.btnStopAnimation.setIcon(icon7)

        self.gridLayout_7.addWidget(self.btnStopAnimation, 0, 2, 1, 1)

        self.btnStepBackward = QPushButton(self.grbAnimation)
        self.btnStepBackward.setObjectName(u"btnStepBackward")
        icon8 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaSkipBackward))
        self.btnStepBackward.setIcon(icon8)

        self.gridLayout_7.addWidget(self.btnStepBackward, 0, 3, 1, 1)

        self.btnStepForward = QPushButton(self.grbAnimation)
        self.btnStepForward.setObjectName(u"btnStepForward")
        icon9 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaSkipForward))
        self.btnStepForward.setIcon(icon9)

        self.gridLayout_7.addWidget(self.btnStepForward, 0, 4, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_7.addItem(self.horizontalSpacer_4, 0, 5, 1, 1)


        self.verticalLayout_8.addLayout(self.gridLayout_7)

        self.lblAnimationTime = QLabel(self.grbAnimation)
        self.lblAnimationTime.setObjectName(u"lblAnimationTime")

        self.verticalLayout_8.addWidget(self.lblAnimationTime)

        self.gridLayout_56 = QGridLayout()
        self.gridLayout_56.setObjectName(u"gridLayout_56")
        self.horizontalSpacer_20 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_56.addItem(self.horizontalSpacer_20, 0, 0, 1, 1)

        self.btnExportVideo = QPushButton(self.grbAnimation)
        self.btnExportVideo.setObjectName(u"btnExportVideo")

        self.gridLayout_56.addWidget(self.btnExportVideo, 0, 1, 1, 1)


        self.verticalLayout_8.addLayout(self.gridLayout_56)


        self.verticalLayout_30.addWidget(self.grbAnimation)

        self.stckProperties.addWidget(self.pageSimulation)
        self.pageSpringCompression = QWidget()
        self.pageSpringCompression.setObjectName(u"pageSpringCompression")
        self.verticalLayout_20 = QVBoxLayout(self.pageSpringCompression)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.grbSpringCompression = QGroupBox(self.pageSpringCompression)
        self.grbSpringCompression.setObjectName(u"grbSpringCompression")
        self.verticalLayout_19 = QVBoxLayout(self.grbSpringCompression)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.gridLayout_21 = QGridLayout()
        self.gridLayout_21.setObjectName(u"gridLayout_21")
        self.label_46 = QLabel(self.grbSpringCompression)
        self.label_46.setObjectName(u"label_46")

        self.gridLayout_21.addWidget(self.label_46, 0, 0, 1, 1)

        self.Edit_CompSpringName = QLineEdit(self.grbSpringCompression)
        self.Edit_CompSpringName.setObjectName(u"Edit_CompSpringName")
        self.Edit_CompSpringName.setReadOnly(True)

        self.gridLayout_21.addWidget(self.Edit_CompSpringName, 0, 1, 1, 1)

        self.btnRenameCompSpring = QPushButton(self.grbSpringCompression)
        self.btnRenameCompSpring.setObjectName(u"btnRenameCompSpring")
        self.btnRenameCompSpring.setMaximumSize(QSize(36, 26))
        self.btnRenameCompSpring.setIcon(icon)

        self.gridLayout_21.addWidget(self.btnRenameCompSpring, 0, 2, 1, 1)

        self.btnDelCompSpring = QPushButton(self.grbSpringCompression)
        self.btnDelCompSpring.setObjectName(u"btnDelCompSpring")
        self.btnDelCompSpring.setMinimumSize(QSize(36, 26))
        self.btnDelCompSpring.setIcon(icon1)

        self.gridLayout_21.addWidget(self.btnDelCompSpring, 0, 3, 1, 1)


        self.verticalLayout_19.addLayout(self.gridLayout_21)

        self.gridLayout_22 = QGridLayout()
        self.gridLayout_22.setObjectName(u"gridLayout_22")
        self.label_48 = QLabel(self.grbSpringCompression)
        self.label_48.setObjectName(u"label_48")

        self.gridLayout_22.addWidget(self.label_48, 0, 0, 1, 1)

        self.Edit_BodyI_CompSpring = QLineEdit(self.grbSpringCompression)
        self.Edit_BodyI_CompSpring.setObjectName(u"Edit_BodyI_CompSpring")
        self.Edit_BodyI_CompSpring.setReadOnly(True)

        self.gridLayout_22.addWidget(self.Edit_BodyI_CompSpring, 0, 1, 1, 1)

        self.label_47 = QLabel(self.grbSpringCompression)
        self.label_47.setObjectName(u"label_47")

        self.gridLayout_22.addWidget(self.label_47, 1, 0, 1, 1)

        self.Edit_BodyJ_CompSpring = QLineEdit(self.grbSpringCompression)
        self.Edit_BodyJ_CompSpring.setObjectName(u"Edit_BodyJ_CompSpring")
        self.Edit_BodyJ_CompSpring.setReadOnly(True)

        self.gridLayout_22.addWidget(self.Edit_BodyJ_CompSpring, 1, 1, 1, 1)

        self.label_50 = QLabel(self.grbSpringCompression)
        self.label_50.setObjectName(u"label_50")

        self.gridLayout_22.addWidget(self.label_50, 2, 0, 1, 1)

        self.Edit_RFBodyI_CompSpring = QLineEdit(self.grbSpringCompression)
        self.Edit_RFBodyI_CompSpring.setObjectName(u"Edit_RFBodyI_CompSpring")
        self.Edit_RFBodyI_CompSpring.setReadOnly(True)

        self.gridLayout_22.addWidget(self.Edit_RFBodyI_CompSpring, 2, 1, 1, 1)

        self.label_49 = QLabel(self.grbSpringCompression)
        self.label_49.setObjectName(u"label_49")

        self.gridLayout_22.addWidget(self.label_49, 3, 0, 1, 1)

        self.Edit_RFBodyJ_CompSpring = QLineEdit(self.grbSpringCompression)
        self.Edit_RFBodyJ_CompSpring.setObjectName(u"Edit_RFBodyJ_CompSpring")
        self.Edit_RFBodyJ_CompSpring.setReadOnly(True)

        self.gridLayout_22.addWidget(self.Edit_RFBodyJ_CompSpring, 3, 1, 1, 1)


        self.verticalLayout_19.addLayout(self.gridLayout_22)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.btnAddCompSpring = QPushButton(self.grbSpringCompression)
        self.btnAddCompSpring.setObjectName(u"btnAddCompSpring")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.btnAddCompSpring)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.formLayout.setItem(0, QFormLayout.ItemRole.FieldRole, self.horizontalSpacer_8)


        self.verticalLayout_19.addLayout(self.formLayout)

        self.line_4 = QFrame(self.grbSpringCompression)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_19.addWidget(self.line_4)

        self.gridLayout_35 = QGridLayout()
        self.gridLayout_35.setObjectName(u"gridLayout_35")
        self.label_51 = QLabel(self.grbSpringCompression)
        self.label_51.setObjectName(u"label_51")

        self.gridLayout_35.addWidget(self.label_51, 0, 0, 1, 1)

        self.Edit_StiffnessCompSpring = QLineEdit(self.grbSpringCompression)
        self.Edit_StiffnessCompSpring.setObjectName(u"Edit_StiffnessCompSpring")

        self.gridLayout_35.addWidget(self.Edit_StiffnessCompSpring, 0, 1, 1, 1)

        self.label_52 = QLabel(self.grbSpringCompression)
        self.label_52.setObjectName(u"label_52")

        self.gridLayout_35.addWidget(self.label_52, 1, 0, 1, 1)

        self.Edit_DampingCompSpring = QLineEdit(self.grbSpringCompression)
        self.Edit_DampingCompSpring.setObjectName(u"Edit_DampingCompSpring")

        self.gridLayout_35.addWidget(self.Edit_DampingCompSpring, 1, 1, 1, 1)

        self.label_53 = QLabel(self.grbSpringCompression)
        self.label_53.setObjectName(u"label_53")

        self.gridLayout_35.addWidget(self.label_53, 2, 0, 1, 1)

        self.Edit_PreloadCompSpring = QLineEdit(self.grbSpringCompression)
        self.Edit_PreloadCompSpring.setObjectName(u"Edit_PreloadCompSpring")

        self.gridLayout_35.addWidget(self.Edit_PreloadCompSpring, 2, 1, 1, 1)


        self.verticalLayout_19.addLayout(self.gridLayout_35)

        self.gridLayout_36 = QGridLayout()
        self.gridLayout_36.setObjectName(u"gridLayout_36")
        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_36.addItem(self.horizontalSpacer_12, 0, 1, 1, 1)

        self.btnUpdateCompSpring = QPushButton(self.grbSpringCompression)
        self.btnUpdateCompSpring.setObjectName(u"btnUpdateCompSpring")
        self.btnUpdateCompSpring.setMaximumSize(QSize(36, 26))
        self.btnUpdateCompSpring.setIcon(icon2)

        self.gridLayout_36.addWidget(self.btnUpdateCompSpring, 0, 3, 1, 1)

        self.chkEnabledCompSpring = QCheckBox(self.grbSpringCompression)
        self.chkEnabledCompSpring.setObjectName(u"chkEnabledCompSpring")
        self.chkEnabledCompSpring.setChecked(True)

        self.gridLayout_36.addWidget(self.chkEnabledCompSpring, 0, 0, 1, 1)


        self.verticalLayout_19.addLayout(self.gridLayout_36)


        self.verticalLayout_20.addWidget(self.grbSpringCompression)

        self.verticalSpacer_5 = QSpacerItem(20, 331, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_20.addItem(self.verticalSpacer_5)

        self.stckProperties.addWidget(self.pageSpringCompression)
        self.pageSpringTorsion = QWidget()
        self.pageSpringTorsion.setObjectName(u"pageSpringTorsion")
        self.verticalLayout_21 = QVBoxLayout(self.pageSpringTorsion)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.grbSpringTorsion = QGroupBox(self.pageSpringTorsion)
        self.grbSpringTorsion.setObjectName(u"grbSpringTorsion")
        self.verticalLayout_18 = QVBoxLayout(self.grbSpringTorsion)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(9, -1, -1, -1)
        self.gridLayout_30 = QGridLayout()
        self.gridLayout_30.setObjectName(u"gridLayout_30")
        self.label_38 = QLabel(self.grbSpringTorsion)
        self.label_38.setObjectName(u"label_38")

        self.gridLayout_30.addWidget(self.label_38, 0, 0, 1, 1)

        self.Edit_TorsSpringName = QLineEdit(self.grbSpringTorsion)
        self.Edit_TorsSpringName.setObjectName(u"Edit_TorsSpringName")
        self.Edit_TorsSpringName.setReadOnly(True)

        self.gridLayout_30.addWidget(self.Edit_TorsSpringName, 0, 1, 1, 1)

        self.btnRenameTorsSpring = QPushButton(self.grbSpringTorsion)
        self.btnRenameTorsSpring.setObjectName(u"btnRenameTorsSpring")
        self.btnRenameTorsSpring.setMaximumSize(QSize(36, 26))
        self.btnRenameTorsSpring.setIcon(icon)

        self.gridLayout_30.addWidget(self.btnRenameTorsSpring, 0, 2, 1, 1)

        self.btnDelTorsSpring = QPushButton(self.grbSpringTorsion)
        self.btnDelTorsSpring.setObjectName(u"btnDelTorsSpring")
        self.btnDelTorsSpring.setMinimumSize(QSize(36, 26))
        self.btnDelTorsSpring.setIcon(icon1)

        self.gridLayout_30.addWidget(self.btnDelTorsSpring, 0, 3, 1, 1)


        self.verticalLayout_18.addLayout(self.gridLayout_30)

        self.gridLayout_26 = QGridLayout()
        self.gridLayout_26.setObjectName(u"gridLayout_26")
        self.label_40 = QLabel(self.grbSpringTorsion)
        self.label_40.setObjectName(u"label_40")

        self.gridLayout_26.addWidget(self.label_40, 1, 0, 1, 1)

        self.Edit_BodyJ_TorsSpring = QLineEdit(self.grbSpringTorsion)
        self.Edit_BodyJ_TorsSpring.setObjectName(u"Edit_BodyJ_TorsSpring")
        self.Edit_BodyJ_TorsSpring.setReadOnly(True)

        self.gridLayout_26.addWidget(self.Edit_BodyJ_TorsSpring, 1, 1, 1, 1)

        self.label_41 = QLabel(self.grbSpringTorsion)
        self.label_41.setObjectName(u"label_41")

        self.gridLayout_26.addWidget(self.label_41, 0, 0, 1, 1)

        self.Edit_BodyI_TorsSpring = QLineEdit(self.grbSpringTorsion)
        self.Edit_BodyI_TorsSpring.setObjectName(u"Edit_BodyI_TorsSpring")
        self.Edit_BodyI_TorsSpring.setReadOnly(True)

        self.gridLayout_26.addWidget(self.Edit_BodyI_TorsSpring, 0, 1, 1, 1)


        self.verticalLayout_18.addLayout(self.gridLayout_26)

        self.gridLayout_27 = QGridLayout()
        self.gridLayout_27.setObjectName(u"gridLayout_27")
        self.Edit_RFBodyJ_TorsSpring = QLineEdit(self.grbSpringTorsion)
        self.Edit_RFBodyJ_TorsSpring.setObjectName(u"Edit_RFBodyJ_TorsSpring")
        self.Edit_RFBodyJ_TorsSpring.setReadOnly(True)

        self.gridLayout_27.addWidget(self.Edit_RFBodyJ_TorsSpring, 1, 1, 1, 1)

        self.label_42 = QLabel(self.grbSpringTorsion)
        self.label_42.setObjectName(u"label_42")

        self.gridLayout_27.addWidget(self.label_42, 1, 0, 1, 1)

        self.label_43 = QLabel(self.grbSpringTorsion)
        self.label_43.setObjectName(u"label_43")

        self.gridLayout_27.addWidget(self.label_43, 0, 0, 1, 1)

        self.Edit_RFBodyI_TorsSpring = QLineEdit(self.grbSpringTorsion)
        self.Edit_RFBodyI_TorsSpring.setObjectName(u"Edit_RFBodyI_TorsSpring")
        self.Edit_RFBodyI_TorsSpring.setReadOnly(True)

        self.gridLayout_27.addWidget(self.Edit_RFBodyI_TorsSpring, 0, 1, 1, 1)

        self.cmbSpringBodyIAnchorXYZ = QComboBox(self.grbSpringTorsion)
        self.cmbSpringBodyIAnchorXYZ.addItem("")
        self.cmbSpringBodyIAnchorXYZ.addItem("")
        self.cmbSpringBodyIAnchorXYZ.addItem("")
        self.cmbSpringBodyIAnchorXYZ.setObjectName(u"cmbSpringBodyIAnchorXYZ")

        self.gridLayout_27.addWidget(self.cmbSpringBodyIAnchorXYZ, 0, 2, 1, 1)


        self.verticalLayout_18.addLayout(self.gridLayout_27)

        self.gridLayout_28 = QGridLayout()
        self.gridLayout_28.setObjectName(u"gridLayout_28")
        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_28.addItem(self.horizontalSpacer_9, 0, 1, 1, 1)

        self.btnAddTorsSpring = QPushButton(self.grbSpringTorsion)
        self.btnAddTorsSpring.setObjectName(u"btnAddTorsSpring")

        self.gridLayout_28.addWidget(self.btnAddTorsSpring, 0, 0, 1, 1)


        self.verticalLayout_18.addLayout(self.gridLayout_28)

        self.line_3 = QFrame(self.grbSpringTorsion)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_18.addWidget(self.line_3)

        self.gridLayout_25 = QGridLayout()
        self.gridLayout_25.setObjectName(u"gridLayout_25")
        self.label_39 = QLabel(self.grbSpringTorsion)
        self.label_39.setObjectName(u"label_39")

        self.gridLayout_25.addWidget(self.label_39, 0, 0, 1, 1)

        self.Edit_StiffnessTorsSpring = QLineEdit(self.grbSpringTorsion)
        self.Edit_StiffnessTorsSpring.setObjectName(u"Edit_StiffnessTorsSpring")

        self.gridLayout_25.addWidget(self.Edit_StiffnessTorsSpring, 0, 1, 1, 1)

        self.label_44 = QLabel(self.grbSpringTorsion)
        self.label_44.setObjectName(u"label_44")

        self.gridLayout_25.addWidget(self.label_44, 1, 0, 1, 1)

        self.Edit_DampingTorsSpring = QLineEdit(self.grbSpringTorsion)
        self.Edit_DampingTorsSpring.setObjectName(u"Edit_DampingTorsSpring")

        self.gridLayout_25.addWidget(self.Edit_DampingTorsSpring, 1, 1, 1, 1)

        self.label_45 = QLabel(self.grbSpringTorsion)
        self.label_45.setObjectName(u"label_45")

        self.gridLayout_25.addWidget(self.label_45, 2, 0, 1, 1)

        self.Edit_PreloadTorsSpring = QLineEdit(self.grbSpringTorsion)
        self.Edit_PreloadTorsSpring.setObjectName(u"Edit_PreloadTorsSpring")

        self.gridLayout_25.addWidget(self.Edit_PreloadTorsSpring, 2, 1, 1, 1)


        self.verticalLayout_18.addLayout(self.gridLayout_25)

        self.gridLayout_29 = QGridLayout()
        self.gridLayout_29.setObjectName(u"gridLayout_29")
        self.chkEnabledTorsSpring = QCheckBox(self.grbSpringTorsion)
        self.chkEnabledTorsSpring.setObjectName(u"chkEnabledTorsSpring")
        self.chkEnabledTorsSpring.setChecked(True)

        self.gridLayout_29.addWidget(self.chkEnabledTorsSpring, 0, 0, 1, 1)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_29.addItem(self.horizontalSpacer_10, 0, 2, 1, 1)

        self.btnUpdateTorsSpring = QPushButton(self.grbSpringTorsion)
        self.btnUpdateTorsSpring.setObjectName(u"btnUpdateTorsSpring")
        self.btnUpdateTorsSpring.setMaximumSize(QSize(36, 26))
        self.btnUpdateTorsSpring.setIcon(icon2)

        self.gridLayout_29.addWidget(self.btnUpdateTorsSpring, 0, 3, 1, 1)


        self.verticalLayout_18.addLayout(self.gridLayout_29)


        self.verticalLayout_21.addWidget(self.grbSpringTorsion)

        self.verticalSpacer_6 = QSpacerItem(20, 331, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_21.addItem(self.verticalSpacer_6)

        self.stckProperties.addWidget(self.pageSpringTorsion)
        self.pageBushing = QWidget()
        self.pageBushing.setObjectName(u"pageBushing")
        self.verticalLayout_23 = QVBoxLayout(self.pageBushing)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.grbBushing = QGroupBox(self.pageBushing)
        self.grbBushing.setObjectName(u"grbBushing")
        self.verticalLayout_22 = QVBoxLayout(self.grbBushing)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.gridLayout_31 = QGridLayout()
        self.gridLayout_31.setObjectName(u"gridLayout_31")
        self.label_54 = QLabel(self.grbBushing)
        self.label_54.setObjectName(u"label_54")

        self.gridLayout_31.addWidget(self.label_54, 0, 0, 1, 1)

        self.Edit_BushingName = QLineEdit(self.grbBushing)
        self.Edit_BushingName.setObjectName(u"Edit_BushingName")
        self.Edit_BushingName.setReadOnly(True)

        self.gridLayout_31.addWidget(self.Edit_BushingName, 0, 1, 1, 1)

        self.btnRenameBushing = QPushButton(self.grbBushing)
        self.btnRenameBushing.setObjectName(u"btnRenameBushing")
        self.btnRenameBushing.setMaximumSize(QSize(36, 26))
        self.btnRenameBushing.setIcon(icon)

        self.gridLayout_31.addWidget(self.btnRenameBushing, 0, 2, 1, 1)

        self.btnDelBushing = QPushButton(self.grbBushing)
        self.btnDelBushing.setObjectName(u"btnDelBushing")
        self.btnDelBushing.setMinimumSize(QSize(36, 26))
        self.btnDelBushing.setIcon(icon1)

        self.gridLayout_31.addWidget(self.btnDelBushing, 0, 3, 1, 1)


        self.verticalLayout_22.addLayout(self.gridLayout_31)

        self.gridLayout_32 = QGridLayout()
        self.gridLayout_32.setObjectName(u"gridLayout_32")
        self.label_55 = QLabel(self.grbBushing)
        self.label_55.setObjectName(u"label_55")

        self.gridLayout_32.addWidget(self.label_55, 1, 0, 1, 1)

        self.Edit_BodyJ_Bushing = QLineEdit(self.grbBushing)
        self.Edit_BodyJ_Bushing.setObjectName(u"Edit_BodyJ_Bushing")
        self.Edit_BodyJ_Bushing.setReadOnly(True)

        self.gridLayout_32.addWidget(self.Edit_BodyJ_Bushing, 1, 1, 1, 1)

        self.label_56 = QLabel(self.grbBushing)
        self.label_56.setObjectName(u"label_56")

        self.gridLayout_32.addWidget(self.label_56, 0, 0, 1, 1)

        self.Edit_BodyI_Bushing = QLineEdit(self.grbBushing)
        self.Edit_BodyI_Bushing.setObjectName(u"Edit_BodyI_Bushing")
        self.Edit_BodyI_Bushing.setReadOnly(True)

        self.gridLayout_32.addWidget(self.Edit_BodyI_Bushing, 0, 1, 1, 1)


        self.verticalLayout_22.addLayout(self.gridLayout_32)

        self.gridLayout_33 = QGridLayout()
        self.gridLayout_33.setObjectName(u"gridLayout_33")
        self.lbl_Bushing_RFBodyJ = QLabel(self.grbBushing)
        self.lbl_Bushing_RFBodyJ.setObjectName(u"lbl_Bushing_RFBodyJ")

        self.gridLayout_33.addWidget(self.lbl_Bushing_RFBodyJ, 1, 0, 1, 1)

        self.Edit_RFBodyI_Bushing = QLineEdit(self.grbBushing)
        self.Edit_RFBodyI_Bushing.setObjectName(u"Edit_RFBodyI_Bushing")
        self.Edit_RFBodyI_Bushing.setReadOnly(True)

        self.gridLayout_33.addWidget(self.Edit_RFBodyI_Bushing, 0, 1, 1, 1)

        self.lbl_Bushing_RFBodyI = QLabel(self.grbBushing)
        self.lbl_Bushing_RFBodyI.setObjectName(u"lbl_Bushing_RFBodyI")

        self.gridLayout_33.addWidget(self.lbl_Bushing_RFBodyI, 0, 0, 1, 1)

        self.Edit_RFBodyJ_Bushing = QLineEdit(self.grbBushing)
        self.Edit_RFBodyJ_Bushing.setObjectName(u"Edit_RFBodyJ_Bushing")
        self.Edit_RFBodyJ_Bushing.setEnabled(True)
        self.Edit_RFBodyJ_Bushing.setReadOnly(True)

        self.gridLayout_33.addWidget(self.Edit_RFBodyJ_Bushing, 1, 1, 1, 1)


        self.verticalLayout_22.addLayout(self.gridLayout_33)

        self.gridLayout_37 = QGridLayout()
        self.gridLayout_37.setObjectName(u"gridLayout_37")
        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_37.addItem(self.horizontalSpacer_11, 0, 1, 1, 1)

        self.btnAddBushing = QPushButton(self.grbBushing)
        self.btnAddBushing.setObjectName(u"btnAddBushing")

        self.gridLayout_37.addWidget(self.btnAddBushing, 0, 0, 1, 1)


        self.verticalLayout_22.addLayout(self.gridLayout_37)

        self.line_5 = QFrame(self.grbBushing)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_22.addWidget(self.line_5)

        self.groupBox = QGroupBox(self.grbBushing)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_24 = QVBoxLayout(self.groupBox)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(-1, 0, -1, -1)
        self.gridLayout_23 = QGridLayout()
        self.gridLayout_23.setObjectName(u"gridLayout_23")
        self.label_65 = QLabel(self.groupBox)
        self.label_65.setObjectName(u"label_65")
        self.label_65.setMaximumSize(QSize(16777215, 10))
        font = QFont()
        font.setKerning(True)
        self.label_65.setFont(font)
        self.label_65.setTextFormat(Qt.TextFormat.AutoText)

        self.gridLayout_23.addWidget(self.label_65, 0, 1, 1, 1)

        self.label_59 = QLabel(self.groupBox)
        self.label_59.setObjectName(u"label_59")
        self.label_59.setMaximumSize(QSize(16777215, 10))

        self.gridLayout_23.addWidget(self.label_59, 0, 3, 1, 1)

        self.label_32 = QLabel(self.groupBox)
        self.label_32.setObjectName(u"label_32")

        self.gridLayout_23.addWidget(self.label_32, 1, 0, 1, 1)

        self.Edit_Kx = QLineEdit(self.groupBox)
        self.Edit_Kx.setObjectName(u"Edit_Kx")

        self.gridLayout_23.addWidget(self.Edit_Kx, 1, 1, 1, 1)

        self.label_35 = QLabel(self.groupBox)
        self.label_35.setObjectName(u"label_35")

        self.gridLayout_23.addWidget(self.label_35, 1, 2, 1, 1)

        self.Edit_KRx = QLineEdit(self.groupBox)
        self.Edit_KRx.setObjectName(u"Edit_KRx")

        self.gridLayout_23.addWidget(self.Edit_KRx, 1, 3, 1, 1)

        self.label_33 = QLabel(self.groupBox)
        self.label_33.setObjectName(u"label_33")

        self.gridLayout_23.addWidget(self.label_33, 2, 0, 1, 1)

        self.Edit_Ky = QLineEdit(self.groupBox)
        self.Edit_Ky.setObjectName(u"Edit_Ky")

        self.gridLayout_23.addWidget(self.Edit_Ky, 2, 1, 1, 1)

        self.label_36 = QLabel(self.groupBox)
        self.label_36.setObjectName(u"label_36")

        self.gridLayout_23.addWidget(self.label_36, 2, 2, 1, 1)

        self.Edit_KRy = QLineEdit(self.groupBox)
        self.Edit_KRy.setObjectName(u"Edit_KRy")

        self.gridLayout_23.addWidget(self.Edit_KRy, 2, 3, 1, 1)

        self.label_34 = QLabel(self.groupBox)
        self.label_34.setObjectName(u"label_34")

        self.gridLayout_23.addWidget(self.label_34, 3, 0, 1, 1)

        self.Edit_Kz = QLineEdit(self.groupBox)
        self.Edit_Kz.setObjectName(u"Edit_Kz")

        self.gridLayout_23.addWidget(self.Edit_Kz, 3, 1, 1, 1)

        self.label_37 = QLabel(self.groupBox)
        self.label_37.setObjectName(u"label_37")

        self.gridLayout_23.addWidget(self.label_37, 3, 2, 1, 1)

        self.Edit_KRz = QLineEdit(self.groupBox)
        self.Edit_KRz.setObjectName(u"Edit_KRz")

        self.gridLayout_23.addWidget(self.Edit_KRz, 3, 3, 1, 1)


        self.verticalLayout_24.addLayout(self.gridLayout_23)


        self.verticalLayout_22.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.grbBushing)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_25 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.verticalLayout_25.setContentsMargins(-1, 0, -1, -1)
        self.gridLayout_24 = QGridLayout()
        self.gridLayout_24.setObjectName(u"gridLayout_24")
        self.label_66 = QLabel(self.groupBox_2)
        self.label_66.setObjectName(u"label_66")
        self.label_66.setMaximumSize(QSize(16777215, 10))
        self.label_66.setTextFormat(Qt.TextFormat.AutoText)

        self.gridLayout_24.addWidget(self.label_66, 0, 1, 1, 1)

        self.label_62 = QLabel(self.groupBox_2)
        self.label_62.setObjectName(u"label_62")
        self.label_62.setMaximumSize(QSize(16777215, 10))

        self.gridLayout_24.addWidget(self.label_62, 0, 3, 1, 1)

        self.label_67 = QLabel(self.groupBox_2)
        self.label_67.setObjectName(u"label_67")

        self.gridLayout_24.addWidget(self.label_67, 1, 0, 1, 1)

        self.Edit_Cx = QLineEdit(self.groupBox_2)
        self.Edit_Cx.setObjectName(u"Edit_Cx")

        self.gridLayout_24.addWidget(self.Edit_Cx, 1, 1, 1, 1)

        self.label_68 = QLabel(self.groupBox_2)
        self.label_68.setObjectName(u"label_68")

        self.gridLayout_24.addWidget(self.label_68, 1, 2, 1, 1)

        self.Edit_CRx = QLineEdit(self.groupBox_2)
        self.Edit_CRx.setObjectName(u"Edit_CRx")

        self.gridLayout_24.addWidget(self.Edit_CRx, 1, 3, 1, 1)

        self.label_69 = QLabel(self.groupBox_2)
        self.label_69.setObjectName(u"label_69")

        self.gridLayout_24.addWidget(self.label_69, 2, 0, 1, 1)

        self.Edit_Cy = QLineEdit(self.groupBox_2)
        self.Edit_Cy.setObjectName(u"Edit_Cy")

        self.gridLayout_24.addWidget(self.Edit_Cy, 2, 1, 1, 1)

        self.label_70 = QLabel(self.groupBox_2)
        self.label_70.setObjectName(u"label_70")

        self.gridLayout_24.addWidget(self.label_70, 2, 2, 1, 1)

        self.Edit_CRy = QLineEdit(self.groupBox_2)
        self.Edit_CRy.setObjectName(u"Edit_CRy")

        self.gridLayout_24.addWidget(self.Edit_CRy, 2, 3, 1, 1)

        self.label_71 = QLabel(self.groupBox_2)
        self.label_71.setObjectName(u"label_71")

        self.gridLayout_24.addWidget(self.label_71, 3, 0, 1, 1)

        self.Edit_Cz = QLineEdit(self.groupBox_2)
        self.Edit_Cz.setObjectName(u"Edit_Cz")

        self.gridLayout_24.addWidget(self.Edit_Cz, 3, 1, 1, 1)

        self.label_72 = QLabel(self.groupBox_2)
        self.label_72.setObjectName(u"label_72")

        self.gridLayout_24.addWidget(self.label_72, 3, 2, 1, 1)

        self.Edit_CRz = QLineEdit(self.groupBox_2)
        self.Edit_CRz.setObjectName(u"Edit_CRz")

        self.gridLayout_24.addWidget(self.Edit_CRz, 3, 3, 1, 1)


        self.verticalLayout_25.addLayout(self.gridLayout_24)


        self.verticalLayout_22.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(self.grbBushing)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_26 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.verticalLayout_26.setContentsMargins(-1, 0, -1, -1)
        self.gridLayout_38 = QGridLayout()
        self.gridLayout_38.setObjectName(u"gridLayout_38")
        self.label_73 = QLabel(self.groupBox_3)
        self.label_73.setObjectName(u"label_73")
        self.label_73.setMaximumSize(QSize(16777215, 10))
        self.label_73.setTextFormat(Qt.TextFormat.AutoText)

        self.gridLayout_38.addWidget(self.label_73, 0, 1, 1, 1)

        self.label_63 = QLabel(self.groupBox_3)
        self.label_63.setObjectName(u"label_63")
        self.label_63.setMaximumSize(QSize(16777215, 10))

        self.gridLayout_38.addWidget(self.label_63, 0, 3, 1, 1)

        self.label_74 = QLabel(self.groupBox_3)
        self.label_74.setObjectName(u"label_74")

        self.gridLayout_38.addWidget(self.label_74, 1, 0, 1, 1)

        self.Edit_Px = QLineEdit(self.groupBox_3)
        self.Edit_Px.setObjectName(u"Edit_Px")

        self.gridLayout_38.addWidget(self.Edit_Px, 1, 1, 1, 1)

        self.label_75 = QLabel(self.groupBox_3)
        self.label_75.setObjectName(u"label_75")

        self.gridLayout_38.addWidget(self.label_75, 1, 2, 1, 1)

        self.Edit_PRx = QLineEdit(self.groupBox_3)
        self.Edit_PRx.setObjectName(u"Edit_PRx")

        self.gridLayout_38.addWidget(self.Edit_PRx, 1, 3, 1, 1)

        self.label_76 = QLabel(self.groupBox_3)
        self.label_76.setObjectName(u"label_76")

        self.gridLayout_38.addWidget(self.label_76, 2, 0, 1, 1)

        self.Edit_Py = QLineEdit(self.groupBox_3)
        self.Edit_Py.setObjectName(u"Edit_Py")

        self.gridLayout_38.addWidget(self.Edit_Py, 2, 1, 1, 1)

        self.label_77 = QLabel(self.groupBox_3)
        self.label_77.setObjectName(u"label_77")

        self.gridLayout_38.addWidget(self.label_77, 2, 2, 1, 1)

        self.Edit_PRy = QLineEdit(self.groupBox_3)
        self.Edit_PRy.setObjectName(u"Edit_PRy")

        self.gridLayout_38.addWidget(self.Edit_PRy, 2, 3, 1, 1)

        self.label_78 = QLabel(self.groupBox_3)
        self.label_78.setObjectName(u"label_78")

        self.gridLayout_38.addWidget(self.label_78, 3, 0, 1, 1)

        self.Edit_Pz = QLineEdit(self.groupBox_3)
        self.Edit_Pz.setObjectName(u"Edit_Pz")

        self.gridLayout_38.addWidget(self.Edit_Pz, 3, 1, 1, 1)

        self.label_79 = QLabel(self.groupBox_3)
        self.label_79.setObjectName(u"label_79")

        self.gridLayout_38.addWidget(self.label_79, 3, 2, 1, 1)

        self.Edit_PRz = QLineEdit(self.groupBox_3)
        self.Edit_PRz.setObjectName(u"Edit_PRz")

        self.gridLayout_38.addWidget(self.Edit_PRz, 3, 3, 1, 1)


        self.verticalLayout_26.addLayout(self.gridLayout_38)


        self.verticalLayout_22.addWidget(self.groupBox_3)

        self.gridLayout_39 = QGridLayout()
        self.gridLayout_39.setObjectName(u"gridLayout_39")
        self.chkEnabledBushing = QCheckBox(self.grbBushing)
        self.chkEnabledBushing.setObjectName(u"chkEnabledBushing")
        self.chkEnabledBushing.setChecked(True)

        self.gridLayout_39.addWidget(self.chkEnabledBushing, 0, 0, 1, 1)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_39.addItem(self.horizontalSpacer_13, 0, 2, 1, 1)

        self.btnUpdateBushing = QPushButton(self.grbBushing)
        self.btnUpdateBushing.setObjectName(u"btnUpdateBushing")
        self.btnUpdateBushing.setMaximumSize(QSize(36, 26))
        self.btnUpdateBushing.setIcon(icon2)

        self.gridLayout_39.addWidget(self.btnUpdateBushing, 0, 3, 1, 1)


        self.verticalLayout_22.addLayout(self.gridLayout_39)


        self.verticalLayout_23.addWidget(self.grbBushing)

        self.stckProperties.addWidget(self.pageBushing)
        self.pageContact = QWidget()
        self.pageContact.setObjectName(u"pageContact")
        self.verticalLayout_29 = QVBoxLayout(self.pageContact)
        self.verticalLayout_29.setObjectName(u"verticalLayout_29")
        self.grbContacts = QGroupBox(self.pageContact)
        self.grbContacts.setObjectName(u"grbContacts")
        self.verticalLayout_28 = QVBoxLayout(self.grbContacts)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.gridLayout_40 = QGridLayout()
        self.gridLayout_40.setObjectName(u"gridLayout_40")
        self.label_60 = QLabel(self.grbContacts)
        self.label_60.setObjectName(u"label_60")

        self.gridLayout_40.addWidget(self.label_60, 0, 0, 1, 1)

        self.Edit_ContactName = QLineEdit(self.grbContacts)
        self.Edit_ContactName.setObjectName(u"Edit_ContactName")
        self.Edit_ContactName.setReadOnly(True)

        self.gridLayout_40.addWidget(self.Edit_ContactName, 0, 1, 1, 1)

        self.btnRenameContact = QPushButton(self.grbContacts)
        self.btnRenameContact.setObjectName(u"btnRenameContact")
        self.btnRenameContact.setMaximumSize(QSize(36, 26))
        self.btnRenameContact.setIcon(icon)

        self.gridLayout_40.addWidget(self.btnRenameContact, 0, 2, 1, 1)

        self.btnDelContact = QPushButton(self.grbContacts)
        self.btnDelContact.setObjectName(u"btnDelContact")
        self.btnDelContact.setMinimumSize(QSize(36, 26))
        self.btnDelContact.setIcon(icon1)

        self.gridLayout_40.addWidget(self.btnDelContact, 0, 3, 1, 1)


        self.verticalLayout_28.addLayout(self.gridLayout_40)

        self.gridLayout_34 = QGridLayout()
        self.gridLayout_34.setObjectName(u"gridLayout_34")
        self.label_61 = QLabel(self.grbContacts)
        self.label_61.setObjectName(u"label_61")

        self.gridLayout_34.addWidget(self.label_61, 0, 0, 1, 1)

        self.Edit_BodyI_Contact = QLineEdit(self.grbContacts)
        self.Edit_BodyI_Contact.setObjectName(u"Edit_BodyI_Contact")
        self.Edit_BodyI_Contact.setReadOnly(True)

        self.gridLayout_34.addWidget(self.Edit_BodyI_Contact, 0, 1, 1, 1)

        self.label_64 = QLabel(self.grbContacts)
        self.label_64.setObjectName(u"label_64")

        self.gridLayout_34.addWidget(self.label_64, 1, 0, 1, 1)

        self.Edit_BodyJ_Contact = QLineEdit(self.grbContacts)
        self.Edit_BodyJ_Contact.setObjectName(u"Edit_BodyJ_Contact")
        self.Edit_BodyJ_Contact.setReadOnly(True)

        self.gridLayout_34.addWidget(self.Edit_BodyJ_Contact, 1, 1, 1, 1)


        self.verticalLayout_28.addLayout(self.gridLayout_34)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.btnAddContact = QPushButton(self.grbContacts)
        self.btnAddContact.setObjectName(u"btnAddContact")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.btnAddContact)

        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.formLayout_2.setItem(0, QFormLayout.ItemRole.FieldRole, self.horizontalSpacer_14)


        self.verticalLayout_28.addLayout(self.formLayout_2)

        self.line_6 = QFrame(self.grbContacts)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.Shape.HLine)
        self.line_6.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_28.addWidget(self.line_6)

        self.gridLayout_41 = QGridLayout()
        self.gridLayout_41.setObjectName(u"gridLayout_41")
        self.lblContactStiffness = QLabel(self.grbContacts)
        self.lblContactStiffness.setObjectName(u"lblContactStiffness")

        self.gridLayout_41.addWidget(self.lblContactStiffness, 0, 0, 1, 1)

        self.Edit_ContactStiffness = QLineEdit(self.grbContacts)
        self.Edit_ContactStiffness.setObjectName(u"Edit_ContactStiffness")

        self.gridLayout_41.addWidget(self.Edit_ContactStiffness, 0, 1, 1, 1)

        self.label_83 = QLabel(self.grbContacts)
        self.label_83.setObjectName(u"label_83")

        self.gridLayout_41.addWidget(self.label_83, 1, 0, 1, 1)

        self.Edit_ContactDamping = QLineEdit(self.grbContacts)
        self.Edit_ContactDamping.setObjectName(u"Edit_ContactDamping")

        self.gridLayout_41.addWidget(self.Edit_ContactDamping, 1, 1, 1, 1)

        self.label_84 = QLabel(self.grbContacts)
        self.label_84.setObjectName(u"label_84")

        self.gridLayout_41.addWidget(self.label_84, 2, 0, 1, 1)

        self.dsbForceExponent = QDoubleSpinBox(self.grbContacts)
        self.dsbForceExponent.setObjectName(u"dsbForceExponent")
        self.dsbForceExponent.setMinimum(1.000000000000000)
        self.dsbForceExponent.setMaximum(2.500000000000000)
        self.dsbForceExponent.setSingleStep(0.100000000000000)

        self.gridLayout_41.addWidget(self.dsbForceExponent, 2, 1, 1, 1)


        self.verticalLayout_28.addLayout(self.gridLayout_41)

        self.gridLayout_42 = QGridLayout()
        self.gridLayout_42.setObjectName(u"gridLayout_42")
        self.horizontalSpacer_15 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_42.addItem(self.horizontalSpacer_15, 0, 1, 1, 1)

        self.btnUpdateContact = QPushButton(self.grbContacts)
        self.btnUpdateContact.setObjectName(u"btnUpdateContact")
        self.btnUpdateContact.setMaximumSize(QSize(36, 26))
        self.btnUpdateContact.setIcon(icon2)

        self.gridLayout_42.addWidget(self.btnUpdateContact, 0, 3, 1, 1)

        self.chkEnabledContact = QCheckBox(self.grbContacts)
        self.chkEnabledContact.setObjectName(u"chkEnabledContact")
        self.chkEnabledContact.setChecked(True)

        self.gridLayout_42.addWidget(self.chkEnabledContact, 0, 0, 1, 1)


        self.verticalLayout_28.addLayout(self.gridLayout_42)

        self.line_7 = QFrame(self.grbContacts)
        self.line_7.setObjectName(u"line_7")
        self.line_7.setFrameShape(QFrame.Shape.HLine)
        self.line_7.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_28.addWidget(self.line_7)

        self.cmbContactMesh = QComboBox(self.grbContacts)
        self.cmbContactMesh.addItem("")
        self.cmbContactMesh.addItem("")
        self.cmbContactMesh.addItem("")
        self.cmbContactMesh.addItem("")
        self.cmbContactMesh.setObjectName(u"cmbContactMesh")

        self.verticalLayout_28.addWidget(self.cmbContactMesh)

        self.line_16 = QFrame(self.grbContacts)
        self.line_16.setObjectName(u"line_16")
        self.line_16.setFrameShape(QFrame.Shape.HLine)
        self.line_16.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_28.addWidget(self.line_16)

        self.gridLayout_44 = QGridLayout()
        self.gridLayout_44.setObjectName(u"gridLayout_44")
        self.chkContactFriction = QCheckBox(self.grbContacts)
        self.chkContactFriction.setObjectName(u"chkContactFriction")

        self.gridLayout_44.addWidget(self.chkContactFriction, 0, 0, 1, 1)

        self.horizontalSpacer_16 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_44.addItem(self.horizontalSpacer_16, 0, 1, 1, 1)


        self.verticalLayout_28.addLayout(self.gridLayout_44)

        self.frmContactFriction = QFrame(self.grbContacts)
        self.frmContactFriction.setObjectName(u"frmContactFriction")
        self.frmContactFriction.setEnabled(False)
        self.frmContactFriction.setFrameShape(QFrame.Shape.StyledPanel)
        self.frmContactFriction.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_27 = QVBoxLayout(self.frmContactFriction)
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.gridLayout_43 = QGridLayout()
        self.gridLayout_43.setObjectName(u"gridLayout_43")
        self.label_81 = QLabel(self.frmContactFriction)
        self.label_81.setObjectName(u"label_81")

        self.gridLayout_43.addWidget(self.label_81, 0, 0, 1, 1)

        self.dsbContactFrictionCoeff = QDoubleSpinBox(self.frmContactFriction)
        self.dsbContactFrictionCoeff.setObjectName(u"dsbContactFrictionCoeff")
        self.dsbContactFrictionCoeff.setMinimum(0.000000000000000)
        self.dsbContactFrictionCoeff.setMaximum(2.000000000000000)
        self.dsbContactFrictionCoeff.setSingleStep(0.010000000000000)
        self.dsbContactFrictionCoeff.setValue(0.100000000000000)

        self.gridLayout_43.addWidget(self.dsbContactFrictionCoeff, 0, 1, 1, 1)

        self.label_80 = QLabel(self.frmContactFriction)
        self.label_80.setObjectName(u"label_80")

        self.gridLayout_43.addWidget(self.label_80, 1, 0, 1, 1)

        self.dsbTolVelocity = QDoubleSpinBox(self.frmContactFriction)
        self.dsbTolVelocity.setObjectName(u"dsbTolVelocity")
        self.dsbTolVelocity.setMinimum(0.100000000000000)
        self.dsbTolVelocity.setMaximum(1000.000000000000000)
        self.dsbTolVelocity.setSingleStep(1.000000000000000)
        self.dsbTolVelocity.setValue(10.000000000000000)

        self.gridLayout_43.addWidget(self.dsbTolVelocity, 1, 1, 1, 1)


        self.verticalLayout_27.addLayout(self.gridLayout_43)


        self.verticalLayout_28.addWidget(self.frmContactFriction)


        self.verticalLayout_29.addWidget(self.grbContacts)

        self.verticalSpacer_7 = QSpacerItem(20, 425, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_29.addItem(self.verticalSpacer_7)

        self.stckProperties.addWidget(self.pageContact)
        self.pageGear = QWidget()
        self.pageGear.setObjectName(u"pageGear")
        self.verticalLayout_32 = QVBoxLayout(self.pageGear)
        self.verticalLayout_32.setObjectName(u"verticalLayout_32")
        self.grbGear = QGroupBox(self.pageGear)
        self.grbGear.setObjectName(u"grbGear")
        self.verticalLayout_31 = QVBoxLayout(self.grbGear)
        self.verticalLayout_31.setObjectName(u"verticalLayout_31")
        self.gridLayout_51 = QGridLayout()
        self.gridLayout_51.setObjectName(u"gridLayout_51")
        self.label_88 = QLabel(self.grbGear)
        self.label_88.setObjectName(u"label_88")

        self.gridLayout_51.addWidget(self.label_88, 0, 0, 1, 1)

        self.Edit_RFGear = QLineEdit(self.grbGear)
        self.Edit_RFGear.setObjectName(u"Edit_RFGear")
        self.Edit_RFGear.setReadOnly(True)

        self.gridLayout_51.addWidget(self.Edit_RFGear, 0, 1, 1, 1)

        self.cmbRF_GearXYZ = QComboBox(self.grbGear)
        self.cmbRF_GearXYZ.addItem("")
        self.cmbRF_GearXYZ.addItem("")
        self.cmbRF_GearXYZ.addItem("")
        self.cmbRF_GearXYZ.setObjectName(u"cmbRF_GearXYZ")

        self.gridLayout_51.addWidget(self.cmbRF_GearXYZ, 0, 2, 1, 1)


        self.verticalLayout_31.addLayout(self.gridLayout_51)

        self.gridLayout_50 = QGridLayout()
        self.gridLayout_50.setObjectName(u"gridLayout_50")
        self.label_97 = QLabel(self.grbGear)
        self.label_97.setObjectName(u"label_97")

        self.gridLayout_50.addWidget(self.label_97, 0, 0, 1, 1)

        self.cmbGearType = QComboBox(self.grbGear)
        self.cmbGearType.addItem("")
        self.cmbGearType.addItem("")
        self.cmbGearType.addItem("")
        self.cmbGearType.setObjectName(u"cmbGearType")

        self.gridLayout_50.addWidget(self.cmbGearType, 0, 1, 1, 2)

        self.label_89 = QLabel(self.grbGear)
        self.label_89.setObjectName(u"label_89")

        self.gridLayout_50.addWidget(self.label_89, 1, 0, 1, 2)

        self.dsbModule = QDoubleSpinBox(self.grbGear)
        self.dsbModule.setObjectName(u"dsbModule")
        self.dsbModule.setDecimals(1)
        self.dsbModule.setMinimum(0.100000000000000)
        self.dsbModule.setMaximum(49.000000000000000)
        self.dsbModule.setSingleStep(0.250000000000000)
        self.dsbModule.setValue(1.000000000000000)

        self.gridLayout_50.addWidget(self.dsbModule, 1, 2, 1, 1)

        self.label_90 = QLabel(self.grbGear)
        self.label_90.setObjectName(u"label_90")

        self.gridLayout_50.addWidget(self.label_90, 2, 0, 1, 2)

        self.dsbNTeeth = QDoubleSpinBox(self.grbGear)
        self.dsbNTeeth.setObjectName(u"dsbNTeeth")
        self.dsbNTeeth.setDecimals(1)
        self.dsbNTeeth.setMinimum(8.000000000000000)
        self.dsbNTeeth.setMaximum(500.000000000000000)
        self.dsbNTeeth.setSingleStep(1.000000000000000)
        self.dsbNTeeth.setValue(24.000000000000000)

        self.gridLayout_50.addWidget(self.dsbNTeeth, 2, 2, 1, 1)

        self.label_91 = QLabel(self.grbGear)
        self.label_91.setObjectName(u"label_91")

        self.gridLayout_50.addWidget(self.label_91, 3, 0, 1, 2)

        self.dsbPressureAngle = QDoubleSpinBox(self.grbGear)
        self.dsbPressureAngle.setObjectName(u"dsbPressureAngle")
        self.dsbPressureAngle.setDecimals(1)
        self.dsbPressureAngle.setMinimum(10.000000000000000)
        self.dsbPressureAngle.setMaximum(32.000000000000000)
        self.dsbPressureAngle.setSingleStep(0.500000000000000)
        self.dsbPressureAngle.setValue(20.000000000000000)

        self.gridLayout_50.addWidget(self.dsbPressureAngle, 3, 2, 1, 1)

        self.lblHelixAngle = QLabel(self.grbGear)
        self.lblHelixAngle.setObjectName(u"lblHelixAngle")

        self.gridLayout_50.addWidget(self.lblHelixAngle, 4, 0, 1, 2)

        self.dsbHelixAngle = QDoubleSpinBox(self.grbGear)
        self.dsbHelixAngle.setObjectName(u"dsbHelixAngle")
        self.dsbHelixAngle.setDecimals(1)
        self.dsbHelixAngle.setMinimum(0.000000000000000)
        self.dsbHelixAngle.setMaximum(45.000000000000000)
        self.dsbHelixAngle.setSingleStep(0.500000000000000)
        self.dsbHelixAngle.setValue(15.000000000000000)

        self.gridLayout_50.addWidget(self.dsbHelixAngle, 4, 2, 1, 1)

        self.label_93 = QLabel(self.grbGear)
        self.label_93.setObjectName(u"label_93")

        self.gridLayout_50.addWidget(self.label_93, 5, 0, 1, 2)

        self.dsbGearWidth = QDoubleSpinBox(self.grbGear)
        self.dsbGearWidth.setObjectName(u"dsbGearWidth")
        self.dsbGearWidth.setDecimals(1)
        self.dsbGearWidth.setMinimum(1.000000000000000)
        self.dsbGearWidth.setMaximum(500.000000000000000)
        self.dsbGearWidth.setSingleStep(1.000000000000000)
        self.dsbGearWidth.setValue(8.000000000000000)

        self.gridLayout_50.addWidget(self.dsbGearWidth, 5, 2, 1, 1)

        self.lblPitchAngle = QLabel(self.grbGear)
        self.lblPitchAngle.setObjectName(u"lblPitchAngle")

        self.gridLayout_50.addWidget(self.lblPitchAngle, 6, 0, 1, 2)

        self.dsbPitchAngle = QDoubleSpinBox(self.grbGear)
        self.dsbPitchAngle.setObjectName(u"dsbPitchAngle")
        self.dsbPitchAngle.setDecimals(1)
        self.dsbPitchAngle.setMinimum(1.000000000000000)
        self.dsbPitchAngle.setMaximum(90.000000000000000)
        self.dsbPitchAngle.setSingleStep(1.000000000000000)
        self.dsbPitchAngle.setValue(45.000000000000000)

        self.gridLayout_50.addWidget(self.dsbPitchAngle, 6, 2, 1, 1)

        self.lblBoreDia = QLabel(self.grbGear)
        self.lblBoreDia.setObjectName(u"lblBoreDia")

        self.gridLayout_50.addWidget(self.lblBoreDia, 7, 0, 1, 2)

        self.dsbBoreDia = QDoubleSpinBox(self.grbGear)
        self.dsbBoreDia.setObjectName(u"dsbBoreDia")
        self.dsbBoreDia.setDecimals(1)
        self.dsbBoreDia.setMinimum(0.000000000000000)
        self.dsbBoreDia.setMaximum(500.000000000000000)
        self.dsbBoreDia.setSingleStep(1.000000000000000)
        self.dsbBoreDia.setValue(5.000000000000000)

        self.gridLayout_50.addWidget(self.dsbBoreDia, 7, 2, 1, 1)

        self.lblRimDia = QLabel(self.grbGear)
        self.lblRimDia.setObjectName(u"lblRimDia")

        self.gridLayout_50.addWidget(self.lblRimDia, 8, 0, 1, 2)

        self.dsbRimDia = QDoubleSpinBox(self.grbGear)
        self.dsbRimDia.setObjectName(u"dsbRimDia")
        self.dsbRimDia.setDecimals(1)
        self.dsbRimDia.setMinimum(10.000000000000000)
        self.dsbRimDia.setMaximum(500.000000000000000)
        self.dsbRimDia.setSingleStep(1.000000000000000)
        self.dsbRimDia.setValue(32.000000000000000)

        self.gridLayout_50.addWidget(self.dsbRimDia, 8, 2, 1, 1)


        self.verticalLayout_31.addLayout(self.gridLayout_50)

        self.gridLayout_52 = QGridLayout()
        self.gridLayout_52.setObjectName(u"gridLayout_52")
        self.btnCreateGear = QPushButton(self.grbGear)
        self.btnCreateGear.setObjectName(u"btnCreateGear")

        self.gridLayout_52.addWidget(self.btnCreateGear, 0, 0, 1, 1)

        self.horizontalSpacer_18 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_18, 0, 1, 1, 1)


        self.verticalLayout_31.addLayout(self.gridLayout_52)


        self.verticalLayout_32.addWidget(self.grbGear)

        self.verticalSpacer_8 = QSpacerItem(20, 342, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_32.addItem(self.verticalSpacer_8)

        self.stckProperties.addWidget(self.pageGear)
        self.pageGearPair = QWidget()
        self.pageGearPair.setObjectName(u"pageGearPair")
        self.verticalLayout_34 = QVBoxLayout(self.pageGearPair)
        self.verticalLayout_34.setObjectName(u"verticalLayout_34")
        self.grbGear_2 = QGroupBox(self.pageGearPair)
        self.grbGear_2.setObjectName(u"grbGear_2")
        self.verticalLayout_33 = QVBoxLayout(self.grbGear_2)
        self.verticalLayout_33.setObjectName(u"verticalLayout_33")
        self.gridLayout_55 = QGridLayout()
        self.gridLayout_55.setObjectName(u"gridLayout_55")
        self.label_108 = QLabel(self.grbGear_2)
        self.label_108.setObjectName(u"label_108")

        self.gridLayout_55.addWidget(self.label_108, 0, 0, 1, 1)

        self.Edit_GearPairName = QLineEdit(self.grbGear_2)
        self.Edit_GearPairName.setObjectName(u"Edit_GearPairName")
        self.Edit_GearPairName.setReadOnly(True)

        self.gridLayout_55.addWidget(self.Edit_GearPairName, 0, 1, 1, 1)

        self.btnRenameGearPair = QPushButton(self.grbGear_2)
        self.btnRenameGearPair.setObjectName(u"btnRenameGearPair")
        self.btnRenameGearPair.setMaximumSize(QSize(36, 26))
        self.btnRenameGearPair.setIcon(icon)

        self.gridLayout_55.addWidget(self.btnRenameGearPair, 0, 2, 1, 1)

        self.btnDelGearPair = QPushButton(self.grbGear_2)
        self.btnDelGearPair.setObjectName(u"btnDelGearPair")
        self.btnDelGearPair.setMinimumSize(QSize(36, 26))
        self.btnDelGearPair.setIcon(icon1)

        self.gridLayout_55.addWidget(self.btnDelGearPair, 0, 3, 1, 1)


        self.verticalLayout_33.addLayout(self.gridLayout_55)

        self.gridLayout_53 = QGridLayout()
        self.gridLayout_53.setObjectName(u"gridLayout_53")
        self.label_99 = QLabel(self.grbGear_2)
        self.label_99.setObjectName(u"label_99")

        self.gridLayout_53.addWidget(self.label_99, 0, 0, 1, 1)

        self.cmbJointGearType = QComboBox(self.grbGear_2)
        self.cmbJointGearType.addItem("")
        self.cmbJointGearType.addItem("")
        self.cmbJointGearType.addItem("")
        self.cmbJointGearType.setObjectName(u"cmbJointGearType")

        self.gridLayout_53.addWidget(self.cmbJointGearType, 0, 1, 1, 1)

        self.label_98 = QLabel(self.grbGear_2)
        self.label_98.setObjectName(u"label_98")

        self.gridLayout_53.addWidget(self.label_98, 1, 0, 1, 1)

        self.Edit_JointGear1 = QLineEdit(self.grbGear_2)
        self.Edit_JointGear1.setObjectName(u"Edit_JointGear1")
        self.Edit_JointGear1.setReadOnly(True)

        self.gridLayout_53.addWidget(self.Edit_JointGear1, 1, 1, 1, 1)

        self.label_101 = QLabel(self.grbGear_2)
        self.label_101.setObjectName(u"label_101")

        self.gridLayout_53.addWidget(self.label_101, 2, 0, 1, 1)

        self.Edit_JointGear2 = QLineEdit(self.grbGear_2)
        self.Edit_JointGear2.setObjectName(u"Edit_JointGear2")
        self.Edit_JointGear2.setReadOnly(True)

        self.gridLayout_53.addWidget(self.Edit_JointGear2, 2, 1, 1, 1)

        self.label_107 = QLabel(self.grbGear_2)
        self.label_107.setObjectName(u"label_107")

        self.gridLayout_53.addWidget(self.label_107, 3, 0, 1, 1)

        self.Edit_JointCarrier = QLineEdit(self.grbGear_2)
        self.Edit_JointCarrier.setObjectName(u"Edit_JointCarrier")
        self.Edit_JointCarrier.setReadOnly(True)

        self.gridLayout_53.addWidget(self.Edit_JointCarrier, 3, 1, 1, 1)

        self.label_104 = QLabel(self.grbGear_2)
        self.label_104.setObjectName(u"label_104")

        self.gridLayout_53.addWidget(self.label_104, 4, 0, 1, 1)

        self.dsbNTeethGear1 = QDoubleSpinBox(self.grbGear_2)
        self.dsbNTeethGear1.setObjectName(u"dsbNTeethGear1")
        self.dsbNTeethGear1.setDecimals(1)
        self.dsbNTeethGear1.setMinimum(8.000000000000000)
        self.dsbNTeethGear1.setMaximum(500.000000000000000)
        self.dsbNTeethGear1.setSingleStep(1.000000000000000)
        self.dsbNTeethGear1.setValue(24.000000000000000)

        self.gridLayout_53.addWidget(self.dsbNTeethGear1, 4, 1, 1, 1)

        self.label_106 = QLabel(self.grbGear_2)
        self.label_106.setObjectName(u"label_106")

        self.gridLayout_53.addWidget(self.label_106, 5, 0, 1, 1)

        self.dsbNTeethGear2 = QDoubleSpinBox(self.grbGear_2)
        self.dsbNTeethGear2.setObjectName(u"dsbNTeethGear2")
        self.dsbNTeethGear2.setDecimals(1)
        self.dsbNTeethGear2.setMinimum(8.000000000000000)
        self.dsbNTeethGear2.setMaximum(500.000000000000000)
        self.dsbNTeethGear2.setSingleStep(1.000000000000000)
        self.dsbNTeethGear2.setValue(24.000000000000000)

        self.gridLayout_53.addWidget(self.dsbNTeethGear2, 5, 1, 1, 1)

        self.label_100 = QLabel(self.grbGear_2)
        self.label_100.setObjectName(u"label_100")

        self.gridLayout_53.addWidget(self.label_100, 6, 0, 1, 1)

        self.dsbJointModule = QDoubleSpinBox(self.grbGear_2)
        self.dsbJointModule.setObjectName(u"dsbJointModule")
        self.dsbJointModule.setDecimals(1)
        self.dsbJointModule.setMinimum(0.100000000000000)
        self.dsbJointModule.setMaximum(49.000000000000000)
        self.dsbJointModule.setSingleStep(0.250000000000000)
        self.dsbJointModule.setValue(1.000000000000000)

        self.gridLayout_53.addWidget(self.dsbJointModule, 6, 1, 1, 1)

        self.label_102 = QLabel(self.grbGear_2)
        self.label_102.setObjectName(u"label_102")

        self.gridLayout_53.addWidget(self.label_102, 7, 0, 1, 1)

        self.dsbJointPressureAngle = QDoubleSpinBox(self.grbGear_2)
        self.dsbJointPressureAngle.setObjectName(u"dsbJointPressureAngle")
        self.dsbJointPressureAngle.setDecimals(1)
        self.dsbJointPressureAngle.setMinimum(10.000000000000000)
        self.dsbJointPressureAngle.setMaximum(32.000000000000000)
        self.dsbJointPressureAngle.setSingleStep(0.500000000000000)
        self.dsbJointPressureAngle.setValue(20.000000000000000)

        self.gridLayout_53.addWidget(self.dsbJointPressureAngle, 7, 1, 1, 1)

        self.lblJointHelixAngle = QLabel(self.grbGear_2)
        self.lblJointHelixAngle.setObjectName(u"lblJointHelixAngle")

        self.gridLayout_53.addWidget(self.lblJointHelixAngle, 8, 0, 1, 1)

        self.dsbJointHelixAngle = QDoubleSpinBox(self.grbGear_2)
        self.dsbJointHelixAngle.setObjectName(u"dsbJointHelixAngle")
        self.dsbJointHelixAngle.setDecimals(1)
        self.dsbJointHelixAngle.setMinimum(0.000000000000000)
        self.dsbJointHelixAngle.setMaximum(45.000000000000000)
        self.dsbJointHelixAngle.setSingleStep(0.500000000000000)
        self.dsbJointHelixAngle.setValue(15.000000000000000)

        self.gridLayout_53.addWidget(self.dsbJointHelixAngle, 8, 1, 1, 1)

        self.lblJointPitchAngle = QLabel(self.grbGear_2)
        self.lblJointPitchAngle.setObjectName(u"lblJointPitchAngle")

        self.gridLayout_53.addWidget(self.lblJointPitchAngle, 9, 0, 1, 1)

        self.dsbJointPitchAngle = QDoubleSpinBox(self.grbGear_2)
        self.dsbJointPitchAngle.setObjectName(u"dsbJointPitchAngle")
        self.dsbJointPitchAngle.setEnabled(False)
        self.dsbJointPitchAngle.setDecimals(1)
        self.dsbJointPitchAngle.setMinimum(1.000000000000000)
        self.dsbJointPitchAngle.setMaximum(90.000000000000000)
        self.dsbJointPitchAngle.setSingleStep(0.500000000000000)
        self.dsbJointPitchAngle.setValue(45.000000000000000)

        self.gridLayout_53.addWidget(self.dsbJointPitchAngle, 9, 1, 1, 1)


        self.verticalLayout_33.addLayout(self.gridLayout_53)

        self.gridLayout_54 = QGridLayout()
        self.gridLayout_54.setObjectName(u"gridLayout_54")
        self.btnCreateGearPair = QPushButton(self.grbGear_2)
        self.btnCreateGearPair.setObjectName(u"btnCreateGearPair")

        self.gridLayout_54.addWidget(self.btnCreateGearPair, 0, 0, 1, 1)

        self.horizontalSpacer_19 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_54.addItem(self.horizontalSpacer_19, 0, 1, 1, 1)

        self.btnUpdateGearPair = QPushButton(self.grbGear_2)
        self.btnUpdateGearPair.setObjectName(u"btnUpdateGearPair")
        self.btnUpdateGearPair.setMaximumSize(QSize(36, 26))
        self.btnUpdateGearPair.setIcon(icon2)

        self.gridLayout_54.addWidget(self.btnUpdateGearPair, 0, 2, 1, 1)


        self.verticalLayout_33.addLayout(self.gridLayout_54)

        self.gridLayout_65 = QGridLayout()
        self.gridLayout_65.setObjectName(u"gridLayout_65")
        self.chkEnabledGearPair = QCheckBox(self.grbGear_2)
        self.chkEnabledGearPair.setObjectName(u"chkEnabledGearPair")
        self.chkEnabledGearPair.setChecked(True)

        self.gridLayout_65.addWidget(self.chkEnabledGearPair, 0, 0, 1, 1)

        self.horizontalSpacer_24 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_65.addItem(self.horizontalSpacer_24, 0, 1, 1, 1)


        self.verticalLayout_33.addLayout(self.gridLayout_65)


        self.verticalLayout_34.addWidget(self.grbGear_2)

        self.verticalSpacer_9 = QSpacerItem(20, 344, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_34.addItem(self.verticalSpacer_9)

        self.stckProperties.addWidget(self.pageGearPair)
        self.pagePrimitives = QWidget()
        self.pagePrimitives.setObjectName(u"pagePrimitives")
        self.verticalLayout_36 = QVBoxLayout(self.pagePrimitives)
        self.verticalLayout_36.setObjectName(u"verticalLayout_36")
        self.grbPrimitives = QGroupBox(self.pagePrimitives)
        self.grbPrimitives.setObjectName(u"grbPrimitives")
        self.verticalLayout_35 = QVBoxLayout(self.grbPrimitives)
        self.verticalLayout_35.setObjectName(u"verticalLayout_35")
        self.gridLayout_57 = QGridLayout()
        self.gridLayout_57.setObjectName(u"gridLayout_57")
        self.label_109 = QLabel(self.grbPrimitives)
        self.label_109.setObjectName(u"label_109")

        self.gridLayout_57.addWidget(self.label_109, 0, 0, 1, 1)

        self.Edit_RFPrimitive = QLineEdit(self.grbPrimitives)
        self.Edit_RFPrimitive.setObjectName(u"Edit_RFPrimitive")
        self.Edit_RFPrimitive.setReadOnly(True)

        self.gridLayout_57.addWidget(self.Edit_RFPrimitive, 0, 1, 1, 1)

        self.cmbRF_PrimXYZ = QComboBox(self.grbPrimitives)
        self.cmbRF_PrimXYZ.addItem("")
        self.cmbRF_PrimXYZ.addItem("")
        self.cmbRF_PrimXYZ.addItem("")
        self.cmbRF_PrimXYZ.setObjectName(u"cmbRF_PrimXYZ")

        self.gridLayout_57.addWidget(self.cmbRF_PrimXYZ, 0, 2, 1, 1)

        self.lblPrimRFTarget = QLabel(self.grbPrimitives)
        self.lblPrimRFTarget.setObjectName(u"lblPrimRFTarget")

        self.gridLayout_57.addWidget(self.lblPrimRFTarget, 1, 0, 1, 1)

        self.Edit_RFPrimTarget = QLineEdit(self.grbPrimitives)
        self.Edit_RFPrimTarget.setObjectName(u"Edit_RFPrimTarget")
        self.Edit_RFPrimTarget.setReadOnly(True)

        self.gridLayout_57.addWidget(self.Edit_RFPrimTarget, 1, 1, 1, 1)


        self.verticalLayout_35.addLayout(self.gridLayout_57)

        self.gridLayout_58 = QGridLayout()
        self.gridLayout_58.setObjectName(u"gridLayout_58")
        self.label_110 = QLabel(self.grbPrimitives)
        self.label_110.setObjectName(u"label_110")

        self.gridLayout_58.addWidget(self.label_110, 0, 0, 1, 1)

        self.cmbPrimitiveType = QComboBox(self.grbPrimitives)
        self.cmbPrimitiveType.addItem("")
        self.cmbPrimitiveType.addItem("")
        self.cmbPrimitiveType.addItem("")
        self.cmbPrimitiveType.addItem("")
        self.cmbPrimitiveType.addItem("")
        self.cmbPrimitiveType.addItem("")
        self.cmbPrimitiveType.addItem("")
        self.cmbPrimitiveType.setObjectName(u"cmbPrimitiveType")

        self.gridLayout_58.addWidget(self.cmbPrimitiveType, 0, 1, 1, 1)

        self.lblPrimDim1 = QLabel(self.grbPrimitives)
        self.lblPrimDim1.setObjectName(u"lblPrimDim1")

        self.gridLayout_58.addWidget(self.lblPrimDim1, 1, 0, 1, 1)

        self.dsbPrimDim1 = QDoubleSpinBox(self.grbPrimitives)
        self.dsbPrimDim1.setObjectName(u"dsbPrimDim1")
        self.dsbPrimDim1.setDecimals(1)
        self.dsbPrimDim1.setMinimum(0.000000000000000)
        self.dsbPrimDim1.setMaximum(9999.000000000000000)
        self.dsbPrimDim1.setSingleStep(1.000000000000000)
        self.dsbPrimDim1.setValue(50.000000000000000)

        self.gridLayout_58.addWidget(self.dsbPrimDim1, 1, 1, 1, 1)

        self.lblPrimDim2 = QLabel(self.grbPrimitives)
        self.lblPrimDim2.setObjectName(u"lblPrimDim2")

        self.gridLayout_58.addWidget(self.lblPrimDim2, 2, 0, 1, 1)

        self.dsbPrimDim2 = QDoubleSpinBox(self.grbPrimitives)
        self.dsbPrimDim2.setObjectName(u"dsbPrimDim2")
        self.dsbPrimDim2.setDecimals(1)
        self.dsbPrimDim2.setMinimum(0.000000000000000)
        self.dsbPrimDim2.setMaximum(9999.000000000000000)
        self.dsbPrimDim2.setSingleStep(1.000000000000000)
        self.dsbPrimDim2.setValue(50.000000000000000)

        self.gridLayout_58.addWidget(self.dsbPrimDim2, 2, 1, 1, 1)

        self.lblPrimDim3 = QLabel(self.grbPrimitives)
        self.lblPrimDim3.setObjectName(u"lblPrimDim3")

        self.gridLayout_58.addWidget(self.lblPrimDim3, 3, 0, 1, 1)

        self.dsbPrimDim3 = QDoubleSpinBox(self.grbPrimitives)
        self.dsbPrimDim3.setObjectName(u"dsbPrimDim3")
        self.dsbPrimDim3.setDecimals(1)
        self.dsbPrimDim3.setMinimum(0.000000000000000)
        self.dsbPrimDim3.setMaximum(9999.000000000000000)
        self.dsbPrimDim3.setSingleStep(1.000000000000000)
        self.dsbPrimDim3.setValue(50.000000000000000)

        self.gridLayout_58.addWidget(self.dsbPrimDim3, 3, 1, 1, 1)


        self.verticalLayout_35.addLayout(self.gridLayout_58)

        self.gridLayout_59 = QGridLayout()
        self.gridLayout_59.setObjectName(u"gridLayout_59")
        self.btnCreatePrimitive = QPushButton(self.grbPrimitives)
        self.btnCreatePrimitive.setObjectName(u"btnCreatePrimitive")

        self.gridLayout_59.addWidget(self.btnCreatePrimitive, 0, 0, 1, 1)

        self.horizontalSpacer_21 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_59.addItem(self.horizontalSpacer_21, 0, 1, 1, 1)


        self.verticalLayout_35.addLayout(self.gridLayout_59)


        self.verticalLayout_36.addWidget(self.grbPrimitives)

        self.verticalSpacer_10 = QSpacerItem(20, 502, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_36.addItem(self.verticalSpacer_10)

        self.stckProperties.addWidget(self.pagePrimitives)
        self.pageMotion = QWidget()
        self.pageMotion.setObjectName(u"pageMotion")
        self.verticalLayout_38 = QVBoxLayout(self.pageMotion)
        self.verticalLayout_38.setObjectName(u"verticalLayout_38")
        self.grbForcesTorques_2 = QGroupBox(self.pageMotion)
        self.grbForcesTorques_2.setObjectName(u"grbForcesTorques_2")
        self.verticalLayout_37 = QVBoxLayout(self.grbForcesTorques_2)
        self.verticalLayout_37.setObjectName(u"verticalLayout_37")
        self.gridLayout_63 = QGridLayout()
        self.gridLayout_63.setObjectName(u"gridLayout_63")
        self.label_111 = QLabel(self.grbForcesTorques_2)
        self.label_111.setObjectName(u"label_111")
        self.label_111.setFrameShape(QFrame.Shape.NoFrame)
        self.label_111.setFrameShadow(QFrame.Shadow.Plain)

        self.gridLayout_63.addWidget(self.label_111, 0, 0, 1, 1)

        self.Edit_MotionName = QLineEdit(self.grbForcesTorques_2)
        self.Edit_MotionName.setObjectName(u"Edit_MotionName")
        self.Edit_MotionName.setEnabled(True)
        self.Edit_MotionName.setReadOnly(True)

        self.gridLayout_63.addWidget(self.Edit_MotionName, 0, 1, 1, 1)

        self.btnRenameMotion = QPushButton(self.grbForcesTorques_2)
        self.btnRenameMotion.setObjectName(u"btnRenameMotion")
        self.btnRenameMotion.setMaximumSize(QSize(36, 26))
        self.btnRenameMotion.setIcon(icon)

        self.gridLayout_63.addWidget(self.btnRenameMotion, 0, 2, 1, 1)

        self.btnDelMotion = QPushButton(self.grbForcesTorques_2)
        self.btnDelMotion.setObjectName(u"btnDelMotion")
        self.btnDelMotion.setMaximumSize(QSize(36, 26))
        self.btnDelMotion.setIcon(icon1)

        self.gridLayout_63.addWidget(self.btnDelMotion, 0, 3, 1, 1)

        self.label_113 = QLabel(self.grbForcesTorques_2)
        self.label_113.setObjectName(u"label_113")

        self.gridLayout_63.addWidget(self.label_113, 1, 0, 1, 1)

        self.Edit_MotionJoint = QLineEdit(self.grbForcesTorques_2)
        self.Edit_MotionJoint.setObjectName(u"Edit_MotionJoint")
        self.Edit_MotionJoint.setReadOnly(True)

        self.gridLayout_63.addWidget(self.Edit_MotionJoint, 1, 1, 1, 1)


        self.verticalLayout_37.addLayout(self.gridLayout_63)

        self.line_8 = QFrame(self.grbForcesTorques_2)
        self.line_8.setObjectName(u"line_8")
        self.line_8.setFrameShape(QFrame.Shape.HLine)
        self.line_8.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_37.addWidget(self.line_8)

        self.gridLayout_62 = QGridLayout()
        self.gridLayout_62.setObjectName(u"gridLayout_62")
        self.cmbMotionTransRot = QComboBox(self.grbForcesTorques_2)
        self.cmbMotionTransRot.addItem("")
        self.cmbMotionTransRot.addItem("")
        self.cmbMotionTransRot.setObjectName(u"cmbMotionTransRot")
        self.cmbMotionTransRot.setEditable(False)

        self.gridLayout_62.addWidget(self.cmbMotionTransRot, 0, 0, 1, 1)

        self.cmbMotionType = QComboBox(self.grbForcesTorques_2)
        self.cmbMotionType.addItem("")
        self.cmbMotionType.addItem("")
        self.cmbMotionType.setObjectName(u"cmbMotionType")
        self.cmbMotionType.setEditable(False)

        self.gridLayout_62.addWidget(self.cmbMotionType, 0, 1, 1, 1)


        self.verticalLayout_37.addLayout(self.gridLayout_62)

        self.gridLayout_61 = QGridLayout()
        self.gridLayout_61.setObjectName(u"gridLayout_61")
        self.lblMotion = QLabel(self.grbForcesTorques_2)
        self.lblMotion.setObjectName(u"lblMotion")

        self.gridLayout_61.addWidget(self.lblMotion, 0, 0, 1, 1)

        self.Edit_MotionFunction = QLineEdit(self.grbForcesTorques_2)
        self.Edit_MotionFunction.setObjectName(u"Edit_MotionFunction")

        self.gridLayout_61.addWidget(self.Edit_MotionFunction, 0, 1, 1, 1)

        self.btnUpdateMotion = QPushButton(self.grbForcesTorques_2)
        self.btnUpdateMotion.setObjectName(u"btnUpdateMotion")
        self.btnUpdateMotion.setMaximumSize(QSize(36, 26))
        self.btnUpdateMotion.setIcon(icon2)

        self.gridLayout_61.addWidget(self.btnUpdateMotion, 0, 2, 1, 1)


        self.verticalLayout_37.addLayout(self.gridLayout_61)

        self.gridLayout_60 = QGridLayout()
        self.gridLayout_60.setObjectName(u"gridLayout_60")
        self.btnAddMotion = QPushButton(self.grbForcesTorques_2)
        self.btnAddMotion.setObjectName(u"btnAddMotion")

        self.gridLayout_60.addWidget(self.btnAddMotion, 0, 0, 1, 1)

        self.horizontalSpacer_22 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_60.addItem(self.horizontalSpacer_22, 0, 1, 1, 1)

        self.chkEnabledMotion = QCheckBox(self.grbForcesTorques_2)
        self.chkEnabledMotion.setObjectName(u"chkEnabledMotion")
        self.chkEnabledMotion.setChecked(True)

        self.gridLayout_60.addWidget(self.chkEnabledMotion, 0, 2, 1, 1)


        self.verticalLayout_37.addLayout(self.gridLayout_60)


        self.verticalLayout_38.addWidget(self.grbForcesTorques_2)

        self.verticalSpacer_11 = QSpacerItem(20, 523, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_38.addItem(self.verticalSpacer_11)

        self.stckProperties.addWidget(self.pageMotion)
        self.pageSettings = QWidget()
        self.pageSettings.setObjectName(u"pageSettings")
        self.verticalLayout_40 = QVBoxLayout(self.pageSettings)
        self.verticalLayout_40.setObjectName(u"verticalLayout_40")
        self.grbVisuals = QGroupBox(self.pageSettings)
        self.grbVisuals.setObjectName(u"grbVisuals")
        self.verticalLayout_39 = QVBoxLayout(self.grbVisuals)
        self.verticalLayout_39.setObjectName(u"verticalLayout_39")
        self.gridLayout_64 = QGridLayout()
        self.gridLayout_64.setObjectName(u"gridLayout_64")
        self.lbl_RFLength = QLabel(self.grbVisuals)
        self.lbl_RFLength.setObjectName(u"lbl_RFLength")

        self.gridLayout_64.addWidget(self.lbl_RFLength, 0, 0, 1, 1)

        self.dsbRF_Length = QDoubleSpinBox(self.grbVisuals)
        self.dsbRF_Length.setObjectName(u"dsbRF_Length")
        self.dsbRF_Length.setDecimals(1)
        self.dsbRF_Length.setMinimum(1.000000000000000)
        self.dsbRF_Length.setMaximum(9999.000000000000000)
        self.dsbRF_Length.setSingleStep(5.000000000000000)
        self.dsbRF_Length.setValue(40.000000000000000)

        self.gridLayout_64.addWidget(self.dsbRF_Length, 0, 1, 1, 1)

        self.lblJoints_Length = QLabel(self.grbVisuals)
        self.lblJoints_Length.setObjectName(u"lblJoints_Length")

        self.gridLayout_64.addWidget(self.lblJoints_Length, 1, 0, 1, 1)

        self.dsbJoints_Length = QDoubleSpinBox(self.grbVisuals)
        self.dsbJoints_Length.setObjectName(u"dsbJoints_Length")
        self.dsbJoints_Length.setDecimals(1)
        self.dsbJoints_Length.setMinimum(1.000000000000000)
        self.dsbJoints_Length.setMaximum(9999.000000000000000)
        self.dsbJoints_Length.setSingleStep(5.000000000000000)
        self.dsbJoints_Length.setValue(40.000000000000000)

        self.gridLayout_64.addWidget(self.dsbJoints_Length, 1, 1, 1, 1)

        self.lblForce_Length = QLabel(self.grbVisuals)
        self.lblForce_Length.setObjectName(u"lblForce_Length")

        self.gridLayout_64.addWidget(self.lblForce_Length, 2, 0, 1, 1)

        self.dsbForce_Length = QDoubleSpinBox(self.grbVisuals)
        self.dsbForce_Length.setObjectName(u"dsbForce_Length")
        self.dsbForce_Length.setDecimals(1)
        self.dsbForce_Length.setMinimum(1.000000000000000)
        self.dsbForce_Length.setMaximum(9999.000000000000000)
        self.dsbForce_Length.setSingleStep(10.000000000000000)
        self.dsbForce_Length.setValue(60.000000000000000)

        self.gridLayout_64.addWidget(self.dsbForce_Length, 2, 1, 1, 1)


        self.verticalLayout_39.addLayout(self.gridLayout_64)

        self.gridLayout_66 = QGridLayout()
        self.gridLayout_66.setObjectName(u"gridLayout_66")
        self.btnUpdateVisuals = QPushButton(self.grbVisuals)
        self.btnUpdateVisuals.setObjectName(u"btnUpdateVisuals")

        self.gridLayout_66.addWidget(self.btnUpdateVisuals, 0, 0, 1, 1)

        self.horizontalSpacer_23 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_66.addItem(self.horizontalSpacer_23, 0, 1, 1, 1)


        self.verticalLayout_39.addLayout(self.gridLayout_66)


        self.verticalLayout_40.addWidget(self.grbVisuals)

        self.verticalSpacer_12 = QSpacerItem(20, 568, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_40.addItem(self.verticalSpacer_12)

        self.stckProperties.addWidget(self.pageSettings)
        self.pageBoolean = QWidget()
        self.pageBoolean.setObjectName(u"pageBoolean")
        self.verticalLayout_42 = QVBoxLayout(self.pageBoolean)
        self.verticalLayout_42.setObjectName(u"verticalLayout_42")
        self.grbJoints_2 = QGroupBox(self.pageBoolean)
        self.grbJoints_2.setObjectName(u"grbJoints_2")
        self.verticalLayout_41 = QVBoxLayout(self.grbJoints_2)
        self.verticalLayout_41.setObjectName(u"verticalLayout_41")
        self.gridLayout_71 = QGridLayout()
        self.gridLayout_71.setObjectName(u"gridLayout_71")
        self.label_92 = QLabel(self.grbJoints_2)
        self.label_92.setObjectName(u"label_92")

        self.gridLayout_71.addWidget(self.label_92, 1, 0, 1, 1)

        self.Edit_Body_J_Boolean = QLineEdit(self.grbJoints_2)
        self.Edit_Body_J_Boolean.setObjectName(u"Edit_Body_J_Boolean")
        self.Edit_Body_J_Boolean.setReadOnly(True)

        self.gridLayout_71.addWidget(self.Edit_Body_J_Boolean, 1, 1, 1, 1)

        self.label_94 = QLabel(self.grbJoints_2)
        self.label_94.setObjectName(u"label_94")

        self.gridLayout_71.addWidget(self.label_94, 0, 0, 1, 1)

        self.Edit_Body_I_Boolean = QLineEdit(self.grbJoints_2)
        self.Edit_Body_I_Boolean.setObjectName(u"Edit_Body_I_Boolean")
        self.Edit_Body_I_Boolean.setReadOnly(True)

        self.gridLayout_71.addWidget(self.Edit_Body_I_Boolean, 0, 1, 1, 1)


        self.verticalLayout_41.addLayout(self.gridLayout_71)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.btnUniteBodies = QPushButton(self.grbJoints_2)
        self.btnUniteBodies.setObjectName(u"btnUniteBodies")

        self.horizontalLayout_5.addWidget(self.btnUniteBodies)

        self.btnCleanBoolBodies = QPushButton(self.grbJoints_2)
        self.btnCleanBoolBodies.setObjectName(u"btnCleanBoolBodies")
        self.btnCleanBoolBodies.setIcon(icon4)

        self.horizontalLayout_5.addWidget(self.btnCleanBoolBodies)

        self.horizontalSpacer_27 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_27)


        self.verticalLayout_41.addLayout(self.horizontalLayout_5)


        self.verticalLayout_42.addWidget(self.grbJoints_2)

        self.verticalSpacer_13 = QSpacerItem(20, 600, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_42.addItem(self.verticalSpacer_13)

        self.stckProperties.addWidget(self.pageBoolean)

        self.verticalLayout.addWidget(self.stckProperties)

        self.dckProperties.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dckProperties)
        self.dckTraceback = QDockWidget(MainWindow)
        self.dckTraceback.setObjectName(u"dckTraceback")
        self.dckTraceback.setMaximumSize(QSize(524287, 524287))
        self.dckTraceback.setDockLocation(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.dockWidgetContents_5 = QWidget()
        self.dockWidgetContents_5.setObjectName(u"dockWidgetContents_5")
        self.verticalLayout_2 = QVBoxLayout(self.dockWidgetContents_5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.txbTraceback = QTextBrowser(self.dockWidgetContents_5)
        self.txbTraceback.setObjectName(u"txbTraceback")
        self.txbTraceback.setMinimumSize(QSize(150, 70))
        self.txbTraceback.setMaximumSize(QSize(16777215, 16777215))
        self.txbTraceback.setReadOnly(False)

        self.verticalLayout_2.addWidget(self.txbTraceback)

        self.dckTraceback.setWidget(self.dockWidgetContents_5)
        MainWindow.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dckTraceback)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menuFile.addAction(self.actionNew_Project)
        self.menuFile.addAction(self.actionOpen_Project)
        self.menuFile.addAction(self.actionSave_Project)
        self.menuFile.addAction(self.actionSave_ProjectAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionImport_OBJ)
        self.menuFile.addAction(self.actionImport_CAD)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuSettings.addAction(self.actionSetWorkingDir)
        self.menuSettings.addAction(self.actionShowTraceback)
        self.menuSettings.addSeparator()
        self.menuSettings.addAction(self.actionDocumentation)
        self.menuSettings.addAction(self.actionAbout_SimPhant)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.stckProperties.setCurrentIndex(0)
        self.btnShiftRF.setDefault(False)
        self.cmbForceType.setCurrentIndex(0)
        self.cmbSpaceBody.setCurrentIndex(0)
        self.cmbSolverMethod.setCurrentIndex(3)
        self.cmbSolverCompliance.setCurrentIndex(2)
        self.cmbRtol.setCurrentIndex(1)
        self.cmbAtol.setCurrentIndex(2)
        self.cmbContactMesh.setCurrentIndex(0)
        self.cmbRF_GearXYZ.setCurrentIndex(0)
        self.cmbMotionTransRot.setCurrentIndex(0)
        self.cmbMotionType.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionImport_OBJ.setText(QCoreApplication.translate("MainWindow", u"Import OBJ...", None))
        self.actionImport_CAD.setText(QCoreApplication.translate("MainWindow", u"Import STL...", None))
        self.actionSet_Working_Directory.setText(QCoreApplication.translate("MainWindow", u"Set Working Directory", None))
        self.actionSave_ProjectAs.setText(QCoreApplication.translate("MainWindow", u"Save Project As...", None))
        self.actionOpen_Project.setText(QCoreApplication.translate("MainWindow", u"Open Project...", None))
        self.actionNew_Project.setText(QCoreApplication.translate("MainWindow", u"New Project", None))
        self.actionSave_Project.setText(QCoreApplication.translate("MainWindow", u"Save Project", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionSetWorkingDir.setText(QCoreApplication.translate("MainWindow", u"Set Working Directory", None))
        self.actionAbout_SimPhant.setText(QCoreApplication.translate("MainWindow", u"About SimPhant", None))
        self.actionShowTraceback.setText(QCoreApplication.translate("MainWindow", u"Show Traceback Window", None))
        self.actionDocumentation.setText(QCoreApplication.translate("MainWindow", u"Documentation", None))
#if QT_CONFIG(tooltip)
        self.btnBody.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Open Body Properties panel</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnBody.setText(QCoreApplication.translate("MainWindow", u"Body", None))
#if QT_CONFIG(tooltip)
        self.btnRF.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Open Reference Frame Properties panel</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnRF.setText(QCoreApplication.translate("MainWindow", u"Ref.Frame", None))
#if QT_CONFIG(tooltip)
        self.btnBox.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create Box with defined dimensions</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnBox.setText(QCoreApplication.translate("MainWindow", u"Box", None))
#if QT_CONFIG(tooltip)
        self.btnTube.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create Hollow Cylinder (Tube) with defined dimensions</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnTube.setText(QCoreApplication.translate("MainWindow", u"Tube", None))
#if QT_CONFIG(tooltip)
        self.btnSphere.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create solid Sphere with defined radius</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnSphere.setText(QCoreApplication.translate("MainWindow", u"Sphere", None))
#if QT_CONFIG(tooltip)
        self.btnPrism.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create Uniform Prism with defined dimensions</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnPrism.setText(QCoreApplication.translate("MainWindow", u"Prism", None))
#if QT_CONFIG(tooltip)
        self.btnTorus.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create solid Torus with defined dimensions</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnTorus.setText(QCoreApplication.translate("MainWindow", u"Torus", None))
#if QT_CONFIG(tooltip)
        self.btnCone.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create Truncated Cone with defined dimensions</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnCone.setText(QCoreApplication.translate("MainWindow", u"Cone", None))
#if QT_CONFIG(tooltip)
        self.btnLink.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create rigid Connecting Rod (Link) with defined dimensions</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnLink.setText(QCoreApplication.translate("MainWindow", u"Link", None))
#if QT_CONFIG(tooltip)
        self.btnBoolean.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create rigid Connecting Rod (Link) with defined dimensions</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnBoolean.setText(QCoreApplication.translate("MainWindow", u"Boolean", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabBodies), QCoreApplication.translate("MainWindow", u"Bodies", None))
#if QT_CONFIG(tooltip)
        self.btnRevoluteJt.setToolTip(QCoreApplication.translate("MainWindow", u"Create a Revolute Joint", None))
#endif // QT_CONFIG(tooltip)
        self.btnRevoluteJt.setText(QCoreApplication.translate("MainWindow", u"Revolute", None))
#if QT_CONFIG(tooltip)
        self.btnFixedJt.setToolTip(QCoreApplication.translate("MainWindow", u"Create a Fixed Joint", None))
#endif // QT_CONFIG(tooltip)
        self.btnFixedJt.setText(QCoreApplication.translate("MainWindow", u"Fixed", None))
#if QT_CONFIG(tooltip)
        self.btnSphericalJt.setToolTip(QCoreApplication.translate("MainWindow", u"Create a Spherical Joint", None))
#endif // QT_CONFIG(tooltip)
        self.btnSphericalJt.setText(QCoreApplication.translate("MainWindow", u"Spherical", None))
#if QT_CONFIG(tooltip)
        self.btnCylindricalJt.setToolTip(QCoreApplication.translate("MainWindow", u"Create a Cylindrical Joint", None))
#endif // QT_CONFIG(tooltip)
        self.btnCylindricalJt.setText(QCoreApplication.translate("MainWindow", u"Cylindrical", None))
#if QT_CONFIG(tooltip)
        self.btnPrismaticJt.setToolTip(QCoreApplication.translate("MainWindow", u"Create a Prismatic Joint", None))
#endif // QT_CONFIG(tooltip)
        self.btnPrismaticJt.setText(QCoreApplication.translate("MainWindow", u"Prismatic", None))
#if QT_CONFIG(tooltip)
        self.btnPlanarJt.setToolTip(QCoreApplication.translate("MainWindow", u"Create a Planar Joint", None))
#endif // QT_CONFIG(tooltip)
        self.btnPlanarJt.setText(QCoreApplication.translate("MainWindow", u"Planar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabJoints), QCoreApplication.translate("MainWindow", u"Joints", None))
#if QT_CONFIG(tooltip)
        self.btnForce.setToolTip(QCoreApplication.translate("MainWindow", u"Create a Force", None))
#endif // QT_CONFIG(tooltip)
        self.btnForce.setText(QCoreApplication.translate("MainWindow", u"Force", None))
#if QT_CONFIG(tooltip)
        self.btnTorque.setToolTip(QCoreApplication.translate("MainWindow", u"Create a Torque", None))
#endif // QT_CONFIG(tooltip)
        self.btnTorque.setText(QCoreApplication.translate("MainWindow", u"Torque", None))
#if QT_CONFIG(tooltip)
        self.btnActuator.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create an Actuator (Force with limited Power)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnActuator.setText(QCoreApplication.translate("MainWindow", u"Actuator", None))
#if QT_CONFIG(tooltip)
        self.btnEmotor.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create an E-Motor (Torque with limited Power)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnEmotor.setText(QCoreApplication.translate("MainWindow", u"E-Motor", None))
#if QT_CONFIG(tooltip)
        self.btnContact.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define a Contact (collision) between two Bodies</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnContact.setText(QCoreApplication.translate("MainWindow", u"Contact", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabForces), QCoreApplication.translate("MainWindow", u"Forces", None))
#if QT_CONFIG(tooltip)
        self.btnComprSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create a Translational Spring-Damper</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnComprSpring.setText(QCoreApplication.translate("MainWindow", u"Compression", None))
#if QT_CONFIG(tooltip)
        self.btnTorsionSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create a Rotational Spring-Damper</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnTorsionSpring.setText(QCoreApplication.translate("MainWindow", u"Torsion", None))
#if QT_CONFIG(tooltip)
        self.btnBushing.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create a Bushing (flexible connection)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnBushing.setText(QCoreApplication.translate("MainWindow", u"Bushing", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSprings), QCoreApplication.translate("MainWindow", u"Springs", None))
#if QT_CONFIG(tooltip)
        self.btnHelicalGear.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create a Helical Gear (rigid Body)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnHelicalGear.setText(QCoreApplication.translate("MainWindow", u"Helical Gear", None))
#if QT_CONFIG(tooltip)
        self.btnGearJoint.setToolTip(QCoreApplication.translate("MainWindow", u"Define the Gear Pair Constraaint", None))
#endif // QT_CONFIG(tooltip)
        self.btnGearJoint.setText(QCoreApplication.translate("MainWindow", u"Gear Pair", None))
#if QT_CONFIG(tooltip)
        self.btnInnerGear.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create Inner Gear (rigid Body)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnInnerGear.setText(QCoreApplication.translate("MainWindow", u"Inner Gear", None))
#if QT_CONFIG(tooltip)
        self.btnBevelGear.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create a Bevel Gear (rigid Body)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnBevelGear.setText(QCoreApplication.translate("MainWindow", u"Bevel Gear", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Gears", None))
#if QT_CONFIG(tooltip)
        self.btnTranslMotion.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define Translational Motion (applicable to Prismatic and Cylindrical Joints)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnTranslMotion.setText(QCoreApplication.translate("MainWindow", u"Translation", None))
#if QT_CONFIG(tooltip)
        self.btnRotMotion.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define Rotational Motion (applicable to Revolute and Cylindrical Joints)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnRotMotion.setText(QCoreApplication.translate("MainWindow", u"Rotation", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMotions), QCoreApplication.translate("MainWindow", u"Motions", None))
#if QT_CONFIG(tooltip)
        self.btnSimulation.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Open Simulation Control panel to Run the Simulation and Animation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnSimulation.setText(QCoreApplication.translate("MainWindow", u"Simulation", None))
#if QT_CONFIG(tooltip)
        self.btnTelemetry.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Open Postprocessor Window to review the Simulation Results</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnTelemetry.setText(QCoreApplication.translate("MainWindow", u"PostProcessor", None))
#if QT_CONFIG(tooltip)
        self.btnExportCSV.setToolTip(QCoreApplication.translate("MainWindow", u"Export Simulation Results to CSV file", None))
#endif // QT_CONFIG(tooltip)
        self.btnExportCSV.setText(QCoreApplication.translate("MainWindow", u"Export CSV", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSimulation), QCoreApplication.translate("MainWindow", u"Simulation", None))
#if QT_CONFIG(tooltip)
        self.btnXY_view.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>XY View</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnXY_view.setText("")
#if QT_CONFIG(tooltip)
        self.btnZY_view.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>ZY View</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnZY_view.setText("")
#if QT_CONFIG(tooltip)
        self.btnXZ_view.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>XZ View</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnXZ_view.setText("")
#if QT_CONFIG(tooltip)
        self.btnEdges.setToolTip(QCoreApplication.translate("MainWindow", u"Display / hide 3D Body edges", None))
#endif // QT_CONFIG(tooltip)
        self.btnEdges.setText("")
#if QT_CONFIG(tooltip)
        self.btnGrid.setToolTip(QCoreApplication.translate("MainWindow", u"Display / hide Grid", None))
#endif // QT_CONFIG(tooltip)
        self.btnGrid.setText("")
#if QT_CONFIG(tooltip)
        self.btnHideAllExceptSelected.setToolTip(QCoreApplication.translate("MainWindow", u"Hide all objects except selected Body", None))
#endif // QT_CONFIG(tooltip)
        self.btnHideAllExceptSelected.setText("")
#if QT_CONFIG(tooltip)
        self.btnUnhideAll.setToolTip(QCoreApplication.translate("MainWindow", u"Unhide All objects in the Viewport", None))
#endif // QT_CONFIG(tooltip)
        self.btnUnhideAll.setText("")
#if QT_CONFIG(tooltip)
        self.btnBackgroundTheme.setToolTip(QCoreApplication.translate("MainWindow", u"Toggle bright / dark background in the Viewport", None))
#endif // QT_CONFIG(tooltip)
        self.btnBackgroundTheme.setText("")
#if QT_CONFIG(tooltip)
        self.btnUnselectAll.setToolTip(QCoreApplication.translate("MainWindow", u"Unselect All objects", None))
#endif // QT_CONFIG(tooltip)
        self.btnUnselectAll.setText("")
#if QT_CONFIG(tooltip)
        self.btnHideShowObjects.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Hide visuals for Reference Frames, Joints, Forces and Torques</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnHideShowObjects.setText("")
#if QT_CONFIG(tooltip)
        self.btnScaleVisuals.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Freeze the actual size of the visuals for Reference Frames, Joints, Forces and Torques</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnScaleVisuals.setText("")
#if QT_CONFIG(tooltip)
        self.btnProjection.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Toggle the 3D Viewport between Perspective and Orthographic (Parallel) projection</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnProjection.setText("")
#if QT_CONFIG(tooltip)
        self.btnFitAll.setToolTip(QCoreApplication.translate("MainWindow", u"Fit All object in the current view", None))
#endif // QT_CONFIG(tooltip)
        self.btnFitAll.setText("")
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.grbBodyProperties.setTitle(QCoreApplication.translate("MainWindow", u"Body Properties", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Name", None))
#if QT_CONFIG(tooltip)
        self.btnRenameBody.setToolTip(QCoreApplication.translate("MainWindow", u"Rename the Body", None))
#endif // QT_CONFIG(tooltip)
        self.btnRenameBody.setText("")
#if QT_CONFIG(tooltip)
        self.btnDeleteBody.setToolTip(QCoreApplication.translate("MainWindow", u"Delete Body", None))
#endif // QT_CONFIG(tooltip)
        self.btnDeleteBody.setText("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Density, kg/m3", None))
#if QT_CONFIG(tooltip)
        self.EditDensity.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Body Density, kg/m3</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.EditDensity.setText(QCoreApplication.translate("MainWindow", u"0", None))
#if QT_CONFIG(tooltip)
        self.btnUpdateBody.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Apply the Body Density</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnUpdateBody.setText("")
#if QT_CONFIG(tooltip)
        self.btnCopyBody.setToolTip(QCoreApplication.translate("MainWindow", u"Create the Copy of the selected Body", None))
#endif // QT_CONFIG(tooltip)
        self.btnCopyBody.setText("")
#if QT_CONFIG(tooltip)
        self.chkApplyAllDensity.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>If checked, the specified Density will be applied to all Bodies, and the Mass properties will be recalculated</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkApplyAllDensity.setText(QCoreApplication.translate("MainWindow", u"Apply Overall Density", None))
        self.txbBodyProperties.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">No body selected.</p></body></html>", None))
        self.grbInitialVelocities.setTitle(QCoreApplication.translate("MainWindow", u"Initial Velocity", None))
        self.label_112.setText(QCoreApplication.translate("MainWindow", u"mm/s (Global RF)", None))
        self.label_115.setText(QCoreApplication.translate("MainWindow", u"Vx", None))
#if QT_CONFIG(tooltip)
        self.Edit_Vx0.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Vx component of the initial Body velocity (at time: t=0)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Vx0.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_116.setText(QCoreApplication.translate("MainWindow", u"Vy", None))
#if QT_CONFIG(tooltip)
        self.Edit_Vy0.setToolTip(QCoreApplication.translate("MainWindow", u"Define the Vy component of the initial Body velocity (at time: t=0)", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Vy0.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_117.setText(QCoreApplication.translate("MainWindow", u"Vz", None))
#if QT_CONFIG(tooltip)
        self.Edit_Vz0.setToolTip(QCoreApplication.translate("MainWindow", u"Define the Vz component of the initial Body velocity (at time: t=0)", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Vz0.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_114.setText(QCoreApplication.translate("MainWindow", u"rad/s (Local RF)", None))
        self.label_118.setText(QCoreApplication.translate("MainWindow", u"\u0460x", None))
#if QT_CONFIG(tooltip)
        self.Edit_Wx0.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the \u0460x component of the initial Body angular velocity (at time: t=0)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Wx0.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_120.setText(QCoreApplication.translate("MainWindow", u"\u0460y", None))
#if QT_CONFIG(tooltip)
        self.Edit_Wy0.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the \u0460y component of the initial Body angular velocity (at time: t=0)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Wy0.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_119.setText(QCoreApplication.translate("MainWindow", u"\u0460z", None))
#if QT_CONFIG(tooltip)
        self.Edit_Wz0.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the \u0460z component of the initial Body angular velocity (at time: t=0)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Wz0.setText(QCoreApplication.translate("MainWindow", u"0", None))
#if QT_CONFIG(tooltip)
        self.btnAssignVelocities.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Apply the initial Body Velocities (at time: t=0)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnAssignVelocities.setText(QCoreApplication.translate("MainWindow", u"Apply Initial Velocities", None))
        self.grbDefineColors.setTitle(QCoreApplication.translate("MainWindow", u"Define Colors", None))
#if QT_CONFIG(tooltip)
        self.btnColorPicker.setToolTip(QCoreApplication.translate("MainWindow", u"Change the Body Color", None))
#endif // QT_CONFIG(tooltip)
        self.btnColorPicker.setText(QCoreApplication.translate("MainWindow", u"Body Color", None))
#if QT_CONFIG(tooltip)
        self.btnColorAllBodies.setToolTip(QCoreApplication.translate("MainWindow", u"Change the Color of All Bodies", None))
#endif // QT_CONFIG(tooltip)
        self.btnColorAllBodies.setText(QCoreApplication.translate("MainWindow", u"All Bodies", None))
#if QT_CONFIG(tooltip)
        self.btnRandomColor.setToolTip(QCoreApplication.translate("MainWindow", u"Apply a random Color to all Bodies", None))
#endif // QT_CONFIG(tooltip)
        self.btnRandomColor.setText(QCoreApplication.translate("MainWindow", u"Random", None))
#if QT_CONFIG(tooltip)
        self.chkEnabled.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Enable/disable selected Body in the Simulation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkEnabled.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
#if QT_CONFIG(tooltip)
        self.chkVisible.setToolTip(QCoreApplication.translate("MainWindow", u"Hide/unhide selected Body", None))
#endif // QT_CONFIG(tooltip)
        self.chkVisible.setText(QCoreApplication.translate("MainWindow", u"Visible", None))
        self.grbRFProperties.setTitle(QCoreApplication.translate("MainWindow", u"RF Properties", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Name", None))
#if QT_CONFIG(tooltip)
        self.btnRenameRF.setToolTip(QCoreApplication.translate("MainWindow", u"Rename Reference Frame", None))
#endif // QT_CONFIG(tooltip)
        self.btnRenameRF.setText("")
#if QT_CONFIG(tooltip)
        self.btnDeleteRF.setToolTip(QCoreApplication.translate("MainWindow", u"Delete Reference Frame", None))
#endif // QT_CONFIG(tooltip)
        self.btnDeleteRF.setText("")
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Global Position, mm", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Global Orientation, deg", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"X", None))
#if QT_CONFIG(tooltip)
        self.EditRF_X_Pos.setToolTip(QCoreApplication.translate("MainWindow", u"Define X-position of the Reference Frame", None))
#endif // QT_CONFIG(tooltip)
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"X", None))
#if QT_CONFIG(tooltip)
        self.EditRF_X_Angle.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Reference Frame rotation around X-axis. Note: the engine uses Tait\u2013Bryan angles (Roll-Pitch-Yaw). The rotations are applied sequentially around: X-&gt;Y-&gt;Z axes relative to the Global RF.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Y", None))
#if QT_CONFIG(tooltip)
        self.EditRF_Y_Pos.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define Y-position of the Reference Frame</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Y", None))
#if QT_CONFIG(tooltip)
        self.EditRF_Y_Angle.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Reference Frame rotation around Y-axis. Note: the engine uses Tait\u2013Bryan angles (Roll-Pitch-Yaw). The rotations are applied sequentially around: X-&gt;Y-&gt;Z axes relative to the Global RF.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Z", None))
#if QT_CONFIG(tooltip)
        self.EditRF_Z_Pos.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define Z-position of the Reference Frame</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Z", None))
#if QT_CONFIG(tooltip)
        self.EditRF_Z_Angle.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Reference Frame rotation around Z-axis. Note: the engine uses Tait\u2013Bryan angles (Roll-Pitch-Yaw). The rotations are applied sequentially around: X-&gt;Y-&gt;Z axes relative to the Global RF.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btnUpdateRF.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Apply XYZ-position and XYZ-orientation of the selected Reference Frame. Note: the engine uses Tait\u2013Bryan angles (Roll-Pitch-Yaw). The rotations are applied sequentially around: X-&gt;Y-&gt;Z axes relative to the Global RF.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnUpdateRF.setText("")
#if QT_CONFIG(tooltip)
        self.btnAddUpdateRF.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create new Reference Frame with defined XYZ-position and XYZ-orientation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnAddUpdateRF.setText(QCoreApplication.translate("MainWindow", u"Add RF", None))
        self.grbRFMove.setTitle(QCoreApplication.translate("MainWindow", u"Move in local RF, mm", None))
#if QT_CONFIG(tooltip)
        self.rbnRFalongX.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define shifting direction axis in Local Reference Frame</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.rbnRFalongX.setText(QCoreApplication.translate("MainWindow", u"X", None))
#if QT_CONFIG(tooltip)
        self.dsbShift_RF.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define step size for shifting the Reference Frame</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.rbnRFalongY.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define shifting direction axis in Local Reference Frame</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.rbnRFalongY.setText(QCoreApplication.translate("MainWindow", u"Y", None))
#if QT_CONFIG(tooltip)
        self.btnShiftRF.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Move selected Reference Frame in XYZ-directions relative to its Local Reference Frame</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnShiftRF.setText(QCoreApplication.translate("MainWindow", u"Shift", None))
#if QT_CONFIG(tooltip)
        self.rbnRFalongZ.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define shifting direction axis in Local Reference Frame</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.rbnRFalongZ.setText(QCoreApplication.translate("MainWindow", u"Z", None))
        self.grbRFRotate.setTitle(QCoreApplication.translate("MainWindow", u"Rotate in local RF, deg", None))
#if QT_CONFIG(tooltip)
        self.rbnRFaroundX.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define rotational axis in the Local Reference Frame</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.rbnRFaroundX.setText(QCoreApplication.translate("MainWindow", u"X", None))
#if QT_CONFIG(tooltip)
        self.dsbRotate_RF.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define step size for rotation the Reference Frame</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.rbnRFaroundY.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define rotational axis in the Local Reference Frame</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.rbnRFaroundY.setText(QCoreApplication.translate("MainWindow", u"Y", None))
#if QT_CONFIG(tooltip)
        self.btnRotateRF.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Rotate selected Reference Frame relative to its Local XYZ-axes. Note: the rotation is applied in Z-&gt;Y-&gt;X sequence in this case.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnRotateRF.setText(QCoreApplication.translate("MainWindow", u"Rotate", None))
#if QT_CONFIG(tooltip)
        self.rbnRFaroundZ.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define rotational axis in the Local Reference Frame</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.rbnRFaroundZ.setText(QCoreApplication.translate("MainWindow", u"Z", None))
#if QT_CONFIG(tooltip)
        self.chkMoveBody.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>This option is to move/rotate the Bodies in the model. If checked for CoG Reference Frame, the related Body will move/rotate with the selected Reference Frame.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkMoveBody.setText(QCoreApplication.translate("MainWindow", u"Move Body with CoG", None))
        self.grbJoints.setTitle(QCoreApplication.translate("MainWindow", u"Joint Properties", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Name", None))
#if QT_CONFIG(tooltip)
        self.btnRenameJoint.setToolTip(QCoreApplication.translate("MainWindow", u"Rename Joint", None))
#endif // QT_CONFIG(tooltip)
        self.btnRenameJoint.setText("")
#if QT_CONFIG(tooltip)
        self.btnDelJoint.setToolTip(QCoreApplication.translate("MainWindow", u"Delete Joint", None))
#endif // QT_CONFIG(tooltip)
        self.btnDelJoint.setText("")
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"Joint", None))
        self.cmbJointType.setItemText(0, QCoreApplication.translate("MainWindow", u"Fixed", None))
        self.cmbJointType.setItemText(1, QCoreApplication.translate("MainWindow", u"Spherical", None))
        self.cmbJointType.setItemText(2, QCoreApplication.translate("MainWindow", u"Revolute", None))
        self.cmbJointType.setItemText(3, QCoreApplication.translate("MainWindow", u"Cylindrical", None))
        self.cmbJointType.setItemText(4, QCoreApplication.translate("MainWindow", u"Prismatic", None))
        self.cmbJointType.setItemText(5, QCoreApplication.translate("MainWindow", u"Planar", None))

#if QT_CONFIG(tooltip)
        self.cmbJointType.setToolTip(QCoreApplication.translate("MainWindow", u"Define Joint Type", None))
#endif // QT_CONFIG(tooltip)
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"Body J", None))
#if QT_CONFIG(tooltip)
        self.Edit_Body_J.setToolTip(QCoreApplication.translate("MainWindow", u"Define second connected Body", None))
#endif // QT_CONFIG(tooltip)
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Body I", None))
#if QT_CONFIG(tooltip)
        self.Edit_Body_I.setToolTip(QCoreApplication.translate("MainWindow", u"Define first connected Body", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.Edit_RF_Target.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>If Target Reference Frame is defined, then Joint axis will connect the Anchor and the Target Reference Frames (XYZ-dropdown is ignored in this case).</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"Target", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"Anchor", None))
#if QT_CONFIG(tooltip)
        self.Edit_RF_Anchor.setToolTip(QCoreApplication.translate("MainWindow", u"Define Reference Frame of the Joint location", None))
#endif // QT_CONFIG(tooltip)
        self.cmbAnchorXYZ.setItemText(0, QCoreApplication.translate("MainWindow", u"X", None))
        self.cmbAnchorXYZ.setItemText(1, QCoreApplication.translate("MainWindow", u"Y", None))
        self.cmbAnchorXYZ.setItemText(2, QCoreApplication.translate("MainWindow", u"Z", None))

#if QT_CONFIG(tooltip)
        self.cmbAnchorXYZ.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>If Joint axis is one of the Anchor RF axes, then this axis can be selected by XYZ-dropdown box. The Target RF shall not be defined in this case (keep the Target empty). This is not applicable for the Spherical and Fixed Joints.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbAnchorXYZ.setCurrentText(QCoreApplication.translate("MainWindow", u"X", None))
#if QT_CONFIG(tooltip)
        self.btnAddJoint.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Crate new Joint. Note: only one Joint can be added for the same two Bodies (this is to eliminate the redundant over-constraint structure in the system).</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnAddJoint.setText(QCoreApplication.translate("MainWindow", u"Add Joint", None))
#if QT_CONFIG(tooltip)
        self.btnCleanBodiesRFs.setToolTip(QCoreApplication.translate("MainWindow", u"Clear all fields in the Joint panel", None))
#endif // QT_CONFIG(tooltip)
        self.btnCleanBodiesRFs.setText(QCoreApplication.translate("MainWindow", u"Clean", None))
#if QT_CONFIG(tooltip)
        self.chkEnabledJoint.setToolTip(QCoreApplication.translate("MainWindow", u"Enable / disable selected Joint in the Simulation", None))
#endif // QT_CONFIG(tooltip)
        self.chkEnabledJoint.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
        self.grbForcesTorques.setTitle(QCoreApplication.translate("MainWindow", u"Force / Torque definition", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Name   ", None))
#if QT_CONFIG(tooltip)
        self.btnRenameForce.setToolTip(QCoreApplication.translate("MainWindow", u"Rename Force / Torque", None))
#endif // QT_CONFIG(tooltip)
        self.btnRenameForce.setText("")
#if QT_CONFIG(tooltip)
        self.btnDelForceTorque.setToolTip(QCoreApplication.translate("MainWindow", u"Delete Force / Torque", None))
#endif // QT_CONFIG(tooltip)
        self.btnDelForceTorque.setText("")
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Part", None))
#if QT_CONFIG(tooltip)
        self.Edit_BodyForce.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Body to which the Force / Torque is applied</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"RFrame", None))
#if QT_CONFIG(tooltip)
        self.Edit_RFForce.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define Reference Frame as the point of application on the Body</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbForceAnchorXYZ.setItemText(0, QCoreApplication.translate("MainWindow", u"X", None))
        self.cmbForceAnchorXYZ.setItemText(1, QCoreApplication.translate("MainWindow", u"Y", None))
        self.cmbForceAnchorXYZ.setItemText(2, QCoreApplication.translate("MainWindow", u"Z", None))

#if QT_CONFIG(tooltip)
        self.cmbForceAnchorXYZ.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Reference Frame axis along which the Force / Torque is directed</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbForceAnchorXYZ.setCurrentText(QCoreApplication.translate("MainWindow", u"X", None))
        self.cmbForceType.setItemText(0, QCoreApplication.translate("MainWindow", u"Force", None))
        self.cmbForceType.setItemText(1, QCoreApplication.translate("MainWindow", u"Torque", None))

#if QT_CONFIG(tooltip)
        self.cmbForceType.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define whether the Force or Torque is being applied</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbForceType.setCurrentText(QCoreApplication.translate("MainWindow", u"Force", None))
        self.cmbForceType.setPlaceholderText("")
        self.cmbSpaceBody.setItemText(0, QCoreApplication.translate("MainWindow", u"Space Fixed", None))
        self.cmbSpaceBody.setItemText(1, QCoreApplication.translate("MainWindow", u"Body Fixed", None))

#if QT_CONFIG(tooltip)
        self.cmbSpaceBody.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define if the Force/Torque is dynamically constrained to the Space or to the Body. </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbSpaceBody.setCurrentText(QCoreApplication.translate("MainWindow", u"Space Fixed", None))
        self.cmbSpaceBody.setPlaceholderText("")
        self.lblNNm.setText(QCoreApplication.translate("MainWindow", u"Value, N", None))
#if QT_CONFIG(tooltip)
        self.Edit_ForceValue.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Specify the Force / Torque Value.</p><p>User-defined time dependent function f(t) is supported.</p><p>The Force / Torque can be defined as a combination of the math functions of time. </p><p>Following functions can be directly entered in the input field:</p><p>sin(t), cos(t), tan(t), sqrt(t) (Square root), exp(t) (Exponential), abs(t) (Absolute value), pi.</p><p>It is possible to use \u2018np.\u2019 to call any standard NumPy math function, for example:</p><p>np.cosh(t), np.round(t), np.sign(t), etc.</p><p>Following custom functions are supported in the program:</p><p>The STEP function changes smoothly between two specified values.</p><p>Syntax: step(t; t0; F0; t1; F1)</p><p>The IF function:</p><p>Syntax: if(&lt;condition&gt;; &lt;value if less or equal to 0&gt;; &lt;value if greater than 0&gt;).</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_ForceValue.setText(QCoreApplication.translate("MainWindow", u"1", None))
#if QT_CONFIG(tooltip)
        self.btnUpdateForceTorque.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Apply the specified Force / Torque type, value and Body/Space fixed location</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnUpdateForceTorque.setText("")
#if QT_CONFIG(tooltip)
        self.btnAddForceTorque.setToolTip(QCoreApplication.translate("MainWindow", u"Create new Force / Torque", None))
#endif // QT_CONFIG(tooltip)
        self.btnAddForceTorque.setText(QCoreApplication.translate("MainWindow", u"Create Force", None))
#if QT_CONFIG(tooltip)
        self.chkEnabledForce.setToolTip(QCoreApplication.translate("MainWindow", u"Enable / Disable Force / Torque in the Simulation", None))
#endif // QT_CONFIG(tooltip)
        self.chkEnabledForce.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
#if QT_CONFIG(tooltip)
        self.chkActuatorMode.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Actuator mode sets the Power limit to the actual Force or Torque by the user defined speed of the Body to which this Force / Torque is applied.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkActuatorMode.setText(QCoreApplication.translate("MainWindow", u"Actuator Mode", None))
        self.lblSpeedUnit.setText(QCoreApplication.translate("MainWindow", u"Max Speed, rpm", None))
#if QT_CONFIG(tooltip)
        self.Edit_MaxActuatorSpeed.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the max Speed of the Body to which the Force / Torque is applied. This transforms the defined Force to Actuator, and Torque to E-Motor.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_MaxActuatorSpeed.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"Power Limit, W", None))
#if QT_CONFIG(tooltip)
        self.Edit_ActPowerLimit.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Automatically calculated max Power of the Actuator or E-Motor</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_ActPowerLimit.setText(QCoreApplication.translate("MainWindow", u"0", None))
#if QT_CONFIG(tooltip)
        self.chkAllowActuatorBraking.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>If the Body's Speed exceeds the defined maximum value, the Force/Torque becomes negative and decelerates the Body, which is allowed if this option is checked. Otherwise, Force/Torque remains 0 once Body\u2019s speed exceeds the max threshold.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkAllowActuatorBraking.setText(QCoreApplication.translate("MainWindow", u"Allow Actuator Braking", None))
        self.grbGravity.setTitle(QCoreApplication.translate("MainWindow", u"Gravity, m/s^2", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"X", None))
#if QT_CONFIG(tooltip)
        self.Edit_GravityX.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Y-value of the Gravity vector (by default: 0).</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_GravityX.setText(QCoreApplication.translate("MainWindow", u"0", None))
#if QT_CONFIG(tooltip)
        self.chkEnabledGravity.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Enable / Disable Gravity in the Simulation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkEnabledGravity.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Y", None))
#if QT_CONFIG(tooltip)
        self.Edit_GravityY.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Y-value of the Gravity vector (by default: -9,81m/s^2).</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_GravityY.setText(QCoreApplication.translate("MainWindow", u"0", None))
#if QT_CONFIG(tooltip)
        self.chkVisibleGravity.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Hide / unhide Gravity Force vector for all Boides in the Viewport</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkVisibleGravity.setText(QCoreApplication.translate("MainWindow", u"Visible", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Z", None))
#if QT_CONFIG(tooltip)
        self.Edit_GravityZ.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Z-value of the Gravity vector (by default: 0).</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_GravityZ.setText(QCoreApplication.translate("MainWindow", u"0", None))
#if QT_CONFIG(tooltip)
        self.btnUpdateGravity.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Apply specified Gravity values</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnUpdateGravity.setText("")
        self.grbSolverSetting.setTitle(QCoreApplication.translate("MainWindow", u"Solver Settings", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"Simulation Time, s", None))
#if QT_CONFIG(tooltip)
        self.Edit_SimulationTime.setToolTip(QCoreApplication.translate("MainWindow", u"Define Simulation Time", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_SimulationTime.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"Steps per second", None))
#if QT_CONFIG(tooltip)
        self.Edit_StepsPerSec.setToolTip(QCoreApplication.translate("MainWindow", u"Define the number of steps per one second", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_StepsPerSec.setText(QCoreApplication.translate("MainWindow", u"500", None))
        self.label_30.setText(QCoreApplication.translate("MainWindow", u"Integrator", None))
        self.cmbSolverMethod.setItemText(0, QCoreApplication.translate("MainWindow", u"Custom RK4", None))
        self.cmbSolverMethod.setItemText(1, QCoreApplication.translate("MainWindow", u"Custom Euler", None))
        self.cmbSolverMethod.setItemText(2, QCoreApplication.translate("MainWindow", u"Custom Symplectic Euler", None))
        self.cmbSolverMethod.setItemText(3, QCoreApplication.translate("MainWindow", u"SciPy RK45", None))
        self.cmbSolverMethod.setItemText(4, QCoreApplication.translate("MainWindow", u"SciPy RK23 (Adaptive)", None))
        self.cmbSolverMethod.setItemText(5, QCoreApplication.translate("MainWindow", u"SciPy DOP853 (High Accuracy)", None))
        self.cmbSolverMethod.setItemText(6, QCoreApplication.translate("MainWindow", u"SciPy Radau (Stiff)", None))
        self.cmbSolverMethod.setItemText(7, QCoreApplication.translate("MainWindow", u"SciPy BDF (Stiff Heavy)", None))
        self.cmbSolverMethod.setItemText(8, QCoreApplication.translate("MainWindow", u"SciPy LSODA (ABM Auto)", None))

#if QT_CONFIG(tooltip)
        self.cmbSolverMethod.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Select the Integrator for Simulation:</p><p>Custom Solvers natively develoed in Python;</p><p>SciPy Library built-in Integrators.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btnSolve.setToolTip(QCoreApplication.translate("MainWindow", u"Run the Simulation!", None))
#endif // QT_CONFIG(tooltip)
        self.btnSolve.setText(QCoreApplication.translate("MainWindow", u"Solve", None))
#if QT_CONFIG(tooltip)
        self.btnBreakSolving.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Terminate the running Simulation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnBreakSolving.setText("")
#if QT_CONFIG(tooltip)
        self.progressBar.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Progress Bar indicates the status of the running Simulation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_87.setText(QCoreApplication.translate("MainWindow", u"Advanced Settings", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"Solver Compliance (for over-constraint)", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"Baumgarte Stabilization (for Joints): \u03b1,\u03b2", None))
        self.cmbSolverCompliance.setItemText(0, QCoreApplication.translate("MainWindow", u"0 (Deactivated)", None))
        self.cmbSolverCompliance.setItemText(1, QCoreApplication.translate("MainWindow", u"1E-5 (Soft)", None))
        self.cmbSolverCompliance.setItemText(2, QCoreApplication.translate("MainWindow", u"1E-7 (Standard)", None))
        self.cmbSolverCompliance.setItemText(3, QCoreApplication.translate("MainWindow", u"1E-9 (Stiff)", None))
        self.cmbSolverCompliance.setItemText(4, QCoreApplication.translate("MainWindow", u"1E-11 (Ultra-Stiff)", None))

#if QT_CONFIG(tooltip)
        self.cmbSolverCompliance.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Consider Matrix (Tikhonov) Regularization) in case if the System is overconstrained.</p><p>The input value represents Constraint Compliance (m/N), the exact opposite of Stiffness. Mathematically, it acts like a virtual spring inserted into the Joint, which allows to share the load between the Joints.</p><p>Example of Usage:</p><p>0.0 (deactivated) means the Joint is infinitely stiff. It can be set for the properly constrained systems without Overconstraints.</p><p>1E-5 (soft) means the Joint is made of rubber or similar soft material.</p><p>1E-7 (default value) means the Joint is made of hard steel.</p><p>1E-9 (hard) or lower is for the simulations of the heavy rigid systems (massive train wheels) .</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.Edit_Alpha_Beta.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>The Joint can physically drift apart due to numerical integration errors, and the Bodies can slowly disconnect from each other. Baumgarte stabilization pulls the Joints back together like a spring-damper system. </p><p>By default, the value is set to 20rad/s and can be modified as following:</p><p>Increase if the Joints are drifting too much;</p><p>If the simulation jitters or vibrates, then back the parameters down.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Alpha_Beta.setText(QCoreApplication.translate("MainWindow", u"20", None))
        self.label_82.setText(QCoreApplication.translate("MainWindow", u"Relative Tolerance", None))
        self.cmbRtol.setItemText(0, QCoreApplication.translate("MainWindow", u"1e-2 (Fast)", None))
        self.cmbRtol.setItemText(1, QCoreApplication.translate("MainWindow", u"1e-3 (Default)", None))
        self.cmbRtol.setItemText(2, QCoreApplication.translate("MainWindow", u"1e-4", None))
        self.cmbRtol.setItemText(3, QCoreApplication.translate("MainWindow", u"1e-5 (Strict)", None))

#if QT_CONFIG(tooltip)
        self.cmbRtol.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the acceptable error relative to the size of the state variable. The defaults value is set to 1e-3 (0.1% error).</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_85.setText(QCoreApplication.translate("MainWindow", u"Absolute Tolerance", None))
        self.cmbAtol.setItemText(0, QCoreApplication.translate("MainWindow", u"1e-4", None))
        self.cmbAtol.setItemText(1, QCoreApplication.translate("MainWindow", u"1e-5", None))
        self.cmbAtol.setItemText(2, QCoreApplication.translate("MainWindow", u"1e-6 (Default)", None))
        self.cmbAtol.setItemText(3, QCoreApplication.translate("MainWindow", u"1e-7", None))
        self.cmbAtol.setItemText(4, QCoreApplication.translate("MainWindow", u"1e-8", None))

#if QT_CONFIG(tooltip)
        self.cmbAtol.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the acceptable error of the state variable. It is measured in the same units: Position in meters (m), Velocities in meters per second (m/s).</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_86.setText(QCoreApplication.translate("MainWindow", u"Max Step Limit", None))
        self.cmbMaxStep.setItemText(0, QCoreApplication.translate("MainWindow", u"Auto (no limit)", None))
        self.cmbMaxStep.setItemText(1, QCoreApplication.translate("MainWindow", u"Bound to dt", None))
        self.cmbMaxStep.setItemText(2, QCoreApplication.translate("MainWindow", u"Bound to dt / 2", None))
        self.cmbMaxStep.setItemText(3, QCoreApplication.translate("MainWindow", u"Bound to dt / 10", None))

#if QT_CONFIG(tooltip)
        self.cmbMaxStep.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the maximal Time interval (dt) during the simulation. The default value for Max Step in SciPy is Auto (no limit). It is recommended to limit the Time interval for Collision detection.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.grbAnimation.setTitle(QCoreApplication.translate("MainWindow", u"Animation Controls", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"FPS", None))
#if QT_CONFIG(tooltip)
        self.Edit_FPS.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Adjust the Video quality by the frame rate (Frames Per Second) setting</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_FPS.setText(QCoreApplication.translate("MainWindow", u"50", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"Animation Speed, %", None))
#if QT_CONFIG(tooltip)
        self.Edit_AnimationSpeed.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.Edit_AnimationSpeed.setText(QCoreApplication.translate("MainWindow", u"30", None))
#if QT_CONFIG(tooltip)
        self.hslAnimSpeed.setToolTip(QCoreApplication.translate("MainWindow", u"Set the animation speed relative to the real time", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btnRunAnimation.setToolTip(QCoreApplication.translate("MainWindow", u"Play", None))
#endif // QT_CONFIG(tooltip)
        self.btnRunAnimation.setText("")
#if QT_CONFIG(tooltip)
        self.btnPauseAnimation.setToolTip(QCoreApplication.translate("MainWindow", u"Pause", None))
#endif // QT_CONFIG(tooltip)
        self.btnPauseAnimation.setText("")
#if QT_CONFIG(tooltip)
        self.btnStopAnimation.setToolTip(QCoreApplication.translate("MainWindow", u"Stop", None))
#endif // QT_CONFIG(tooltip)
        self.btnStopAnimation.setText("")
#if QT_CONFIG(tooltip)
        self.btnStepBackward.setToolTip(QCoreApplication.translate("MainWindow", u"Step Backward", None))
#endif // QT_CONFIG(tooltip)
        self.btnStepBackward.setText("")
#if QT_CONFIG(tooltip)
        self.btnStepForward.setToolTip(QCoreApplication.translate("MainWindow", u"Step Forward", None))
#endif // QT_CONFIG(tooltip)
        self.btnStepForward.setText("")
        self.lblAnimationTime.setText(QCoreApplication.translate("MainWindow", u"Animation Time: 0s", None))
#if QT_CONFIG(tooltip)
        self.btnExportVideo.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Export the Animation of the entire Simulation in .webm format</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnExportVideo.setText(QCoreApplication.translate("MainWindow", u"Export Video", None))
        self.grbSpringCompression.setTitle(QCoreApplication.translate("MainWindow", u"Compression Spring", None))
        self.label_46.setText(QCoreApplication.translate("MainWindow", u"Name      ", None))
#if QT_CONFIG(tooltip)
        self.btnRenameCompSpring.setToolTip(QCoreApplication.translate("MainWindow", u"Rename the Spring", None))
#endif // QT_CONFIG(tooltip)
        self.btnRenameCompSpring.setText("")
#if QT_CONFIG(tooltip)
        self.btnDelCompSpring.setToolTip(QCoreApplication.translate("MainWindow", u"Delete the Spring", None))
#endif // QT_CONFIG(tooltip)
        self.btnDelCompSpring.setText("")
        self.label_48.setText(QCoreApplication.translate("MainWindow", u"Body I", None))
#if QT_CONFIG(tooltip)
        self.Edit_BodyI_CompSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define first action Body or Ground</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_47.setText(QCoreApplication.translate("MainWindow", u"Body J", None))
#if QT_CONFIG(tooltip)
        self.Edit_BodyJ_CompSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define second action Body or Ground</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_50.setText(QCoreApplication.translate("MainWindow", u"RF Body I", None))
#if QT_CONFIG(tooltip)
        self.Edit_RFBodyI_CompSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define Reference Frame as an action point on the Body_I</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_49.setText(QCoreApplication.translate("MainWindow", u"RF Body J", None))
#if QT_CONFIG(tooltip)
        self.Edit_RFBodyJ_CompSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define Reference Frame as an action point on the Body_J</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btnAddCompSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create new Translational Spring-Damper</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnAddCompSpring.setText(QCoreApplication.translate("MainWindow", u"Add Compression Spring", None))
        self.label_51.setText(QCoreApplication.translate("MainWindow", u"Stiffness, N/mm", None))
#if QT_CONFIG(tooltip)
        self.Edit_StiffnessCompSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Stiffness of the Spring</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_52.setText(QCoreApplication.translate("MainWindow", u"Damping, N/(mm/s)", None))
#if QT_CONFIG(tooltip)
        self.Edit_DampingCompSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Damping of the Spring</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_53.setText(QCoreApplication.translate("MainWindow", u"Preload, N", None))
#if QT_CONFIG(tooltip)
        self.Edit_PreloadCompSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Spring initial Preload</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btnUpdateCompSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Apply the Stiffness, Damping and Preload properties of the Spring</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnUpdateCompSpring.setText("")
#if QT_CONFIG(tooltip)
        self.chkEnabledCompSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Enable / disable selected Spring in the Simulation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkEnabledCompSpring.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
        self.grbSpringTorsion.setTitle(QCoreApplication.translate("MainWindow", u"Torsion Spring", None))
        self.label_38.setText(QCoreApplication.translate("MainWindow", u"Name      ", None))
#if QT_CONFIG(tooltip)
        self.btnRenameTorsSpring.setToolTip(QCoreApplication.translate("MainWindow", u"Rename the Spring", None))
#endif // QT_CONFIG(tooltip)
        self.btnRenameTorsSpring.setText("")
#if QT_CONFIG(tooltip)
        self.btnDelTorsSpring.setToolTip(QCoreApplication.translate("MainWindow", u"Delete the Spring", None))
#endif // QT_CONFIG(tooltip)
        self.btnDelTorsSpring.setText("")
        self.label_40.setText(QCoreApplication.translate("MainWindow", u"Body J", None))
#if QT_CONFIG(tooltip)
        self.Edit_BodyJ_TorsSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define second action Body or Ground</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_41.setText(QCoreApplication.translate("MainWindow", u"Body I", None))
#if QT_CONFIG(tooltip)
        self.Edit_BodyI_TorsSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define first action Body or Ground</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.Edit_RFBodyJ_TorsSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>This Reference Frame defines the Spring Torque direction as the axis between the Anchor and Target Reference Frames. XYZ-dropdown is ignored if Target RF is defined.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_42.setText(QCoreApplication.translate("MainWindow", u"Target", None))
        self.label_43.setText(QCoreApplication.translate("MainWindow", u"Anchor", None))
#if QT_CONFIG(tooltip)
        self.Edit_RFBodyI_TorsSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define Reference Frame of the Spring location</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbSpringBodyIAnchorXYZ.setItemText(0, QCoreApplication.translate("MainWindow", u"X", None))
        self.cmbSpringBodyIAnchorXYZ.setItemText(1, QCoreApplication.translate("MainWindow", u"Y", None))
        self.cmbSpringBodyIAnchorXYZ.setItemText(2, QCoreApplication.translate("MainWindow", u"Z", None))

#if QT_CONFIG(tooltip)
        self.cmbSpringBodyIAnchorXYZ.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the axis of the Anchor RF. It defines the Spring Torque axis. It is considered if Target RF is not defined (empty).</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbSpringBodyIAnchorXYZ.setCurrentText(QCoreApplication.translate("MainWindow", u"X", None))
#if QT_CONFIG(tooltip)
        self.btnAddTorsSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create new Rotational Spring-Damper</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnAddTorsSpring.setText(QCoreApplication.translate("MainWindow", u"Add Torsion Spring", None))
        self.label_39.setText(QCoreApplication.translate("MainWindow", u"Stiffness, Nmm/rad", None))
#if QT_CONFIG(tooltip)
        self.Edit_StiffnessTorsSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Stiffness of the Spring</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_44.setText(QCoreApplication.translate("MainWindow", u"Damping, Nmm/(rad/s)", None))
#if QT_CONFIG(tooltip)
        self.Edit_DampingTorsSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Damping of the Spring</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_45.setText(QCoreApplication.translate("MainWindow", u"Preload, Nmm", None))
#if QT_CONFIG(tooltip)
        self.Edit_PreloadTorsSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Spring initial Preload</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.chkEnabledTorsSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Enable / disable selected Spring in the Simulation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkEnabledTorsSpring.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
#if QT_CONFIG(tooltip)
        self.btnUpdateTorsSpring.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Apply the Stiffness, Damping and Preload properties of the Spring</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnUpdateTorsSpring.setText("")
        self.grbBushing.setTitle(QCoreApplication.translate("MainWindow", u"Bushing Properties", None))
        self.label_54.setText(QCoreApplication.translate("MainWindow", u"Name      ", None))
#if QT_CONFIG(tooltip)
        self.btnRenameBushing.setToolTip(QCoreApplication.translate("MainWindow", u"Rename Bushing", None))
#endif // QT_CONFIG(tooltip)
        self.btnRenameBushing.setText("")
#if QT_CONFIG(tooltip)
        self.btnDelBushing.setToolTip(QCoreApplication.translate("MainWindow", u"Delete Bushing", None))
#endif // QT_CONFIG(tooltip)
        self.btnDelBushing.setText("")
        self.label_55.setText(QCoreApplication.translate("MainWindow", u"Body J", None))
#if QT_CONFIG(tooltip)
        self.Edit_BodyJ_Bushing.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define second action Body or Ground</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_56.setText(QCoreApplication.translate("MainWindow", u"Body I", None))
#if QT_CONFIG(tooltip)
        self.Edit_BodyI_Bushing.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define first action Body or Ground</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_Bushing_RFBodyJ.setText(QCoreApplication.translate("MainWindow", u"RF Body J", None))
#if QT_CONFIG(tooltip)
        self.Edit_RFBodyI_Bushing.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>The Global Reference Frame defining the Bushing position as local Anchor points at Body_I and Body_J</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_Bushing_RFBodyI.setText(QCoreApplication.translate("MainWindow", u"Anchor RF", None))
#if QT_CONFIG(tooltip)
        self.btnAddBushing.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create new Bushing (flexible connection)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnAddBushing.setText(QCoreApplication.translate("MainWindow", u"Add Bushing", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Stiffness", None))
        self.label_65.setText(QCoreApplication.translate("MainWindow", u"N/mm", None))
        self.label_59.setText(QCoreApplication.translate("MainWindow", u"Nmm/rad", None))
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"Kx", None))
#if QT_CONFIG(tooltip)
        self.Edit_Kx.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Translational Stiffness oriented along the X-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Kx.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_35.setText(QCoreApplication.translate("MainWindow", u"KRx", None))
#if QT_CONFIG(tooltip)
        self.Edit_KRx.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Rotational Stiffness oriented along the X-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_KRx.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_33.setText(QCoreApplication.translate("MainWindow", u"Ky", None))
#if QT_CONFIG(tooltip)
        self.Edit_Ky.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Translational Stiffness oriented along the Y-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Ky.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_36.setText(QCoreApplication.translate("MainWindow", u"KRy", None))
#if QT_CONFIG(tooltip)
        self.Edit_KRy.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Rotational Stiffness oriented along the Y-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_KRy.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_34.setText(QCoreApplication.translate("MainWindow", u"Kz", None))
#if QT_CONFIG(tooltip)
        self.Edit_Kz.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Translational Stiffness oriented along the Z-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Kz.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_37.setText(QCoreApplication.translate("MainWindow", u"KRz", None))
#if QT_CONFIG(tooltip)
        self.Edit_KRz.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Rotational Stiffness oriented along the Z-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_KRz.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Damping", None))
        self.label_66.setText(QCoreApplication.translate("MainWindow", u"N/(mm/s)", None))
        self.label_62.setText(QCoreApplication.translate("MainWindow", u"Nmm/(rad/s)", None))
        self.label_67.setText(QCoreApplication.translate("MainWindow", u"Cx", None))
#if QT_CONFIG(tooltip)
        self.Edit_Cx.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Translational Damping oriented along the X-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Cx.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_68.setText(QCoreApplication.translate("MainWindow", u"CRx", None))
#if QT_CONFIG(tooltip)
        self.Edit_CRx.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Rotational Damping oriented along the X-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_CRx.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_69.setText(QCoreApplication.translate("MainWindow", u"Cy", None))
#if QT_CONFIG(tooltip)
        self.Edit_Cy.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Translational Damping oriented along the Y-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Cy.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_70.setText(QCoreApplication.translate("MainWindow", u"CRy", None))
#if QT_CONFIG(tooltip)
        self.Edit_CRy.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Rotational Damping oriented along the Y-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_CRy.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_71.setText(QCoreApplication.translate("MainWindow", u"Cz", None))
#if QT_CONFIG(tooltip)
        self.Edit_Cz.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Translational Damping oriented along the Z-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Cz.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_72.setText(QCoreApplication.translate("MainWindow", u"CRz", None))
#if QT_CONFIG(tooltip)
        self.Edit_CRz.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Rotational Damping oriented along the Z-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_CRz.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Preload", None))
        self.label_73.setText(QCoreApplication.translate("MainWindow", u"N", None))
        self.label_63.setText(QCoreApplication.translate("MainWindow", u"Nmm", None))
        self.label_74.setText(QCoreApplication.translate("MainWindow", u"Fx", None))
#if QT_CONFIG(tooltip)
        self.Edit_Px.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Force preload along the X-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Px.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_75.setText(QCoreApplication.translate("MainWindow", u"Tx", None))
#if QT_CONFIG(tooltip)
        self.Edit_PRx.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Torque preload along the X-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_PRx.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_76.setText(QCoreApplication.translate("MainWindow", u"Fy", None))
#if QT_CONFIG(tooltip)
        self.Edit_Py.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Force preload along the Y-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Py.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_77.setText(QCoreApplication.translate("MainWindow", u"Ty", None))
#if QT_CONFIG(tooltip)
        self.Edit_PRy.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Torque preload along the Y-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_PRy.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_78.setText(QCoreApplication.translate("MainWindow", u"Fz", None))
#if QT_CONFIG(tooltip)
        self.Edit_Pz.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Force preload along the Z-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_Pz.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_79.setText(QCoreApplication.translate("MainWindow", u"Tz", None))
#if QT_CONFIG(tooltip)
        self.Edit_PRz.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Torque preload along the Z-axis of the Anchor RF</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_PRz.setText(QCoreApplication.translate("MainWindow", u"0", None))
#if QT_CONFIG(tooltip)
        self.chkEnabledBushing.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Enable / disable Bushing in the Simulation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkEnabledBushing.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
#if QT_CONFIG(tooltip)
        self.btnUpdateBushing.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Apply the Stiffness, Damping and Preload properties of the Bushing</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnUpdateBushing.setText("")
        self.grbContacts.setTitle(QCoreApplication.translate("MainWindow", u"Contact Properties", None))
        self.label_60.setText(QCoreApplication.translate("MainWindow", u"Name      ", None))
#if QT_CONFIG(tooltip)
        self.btnRenameContact.setToolTip(QCoreApplication.translate("MainWindow", u"Rename Contact", None))
#endif // QT_CONFIG(tooltip)
        self.btnRenameContact.setText("")
#if QT_CONFIG(tooltip)
        self.btnDelContact.setToolTip(QCoreApplication.translate("MainWindow", u"Delete Contact", None))
#endif // QT_CONFIG(tooltip)
        self.btnDelContact.setText("")
        self.label_61.setText(QCoreApplication.translate("MainWindow", u"Body I", None))
#if QT_CONFIG(tooltip)
        self.Edit_BodyI_Contact.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define first body in the Contact</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_64.setText(QCoreApplication.translate("MainWindow", u"Body J", None))
#if QT_CONFIG(tooltip)
        self.Edit_BodyJ_Contact.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define second body in the Contact</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btnAddContact.setToolTip(QCoreApplication.translate("MainWindow", u"Create new Contact", None))
#endif // QT_CONFIG(tooltip)
        self.btnAddContact.setText(QCoreApplication.translate("MainWindow", u"Add Contact", None))
        self.lblContactStiffness.setText(QCoreApplication.translate("MainWindow", u"Stiffness, N/mm^e", None))
#if QT_CONFIG(tooltip)
        self.Edit_ContactStiffness.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define Contact Stiffness (k) for the normal force calculation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_ContactStiffness.setText(QCoreApplication.translate("MainWindow", u"1000", None))
        self.label_83.setText(QCoreApplication.translate("MainWindow", u"Damping, N/(mm/s)", None))
#if QT_CONFIG(tooltip)
        self.Edit_ContactDamping.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define Contact Damping (C) for the normal force calculation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_ContactDamping.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.label_84.setText(QCoreApplication.translate("MainWindow", u"Force Exponent (e)", None))
#if QT_CONFIG(tooltip)
        self.dsbForceExponent.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define Contact Force Exponent (e) depending on the contact pattern on the Hertzian contact model. For example: e=1.0 for the flat Contact, e=1.5 for cylindrical or spherical Contact.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btnUpdateContact.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Apply the Stiffness, Damping and force Exponent properties of the Contact</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnUpdateContact.setText("")
#if QT_CONFIG(tooltip)
        self.chkEnabledContact.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Enable / disable selected Contact in the Simulation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkEnabledContact.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
        self.cmbContactMesh.setItemText(0, QCoreApplication.translate("MainWindow", u"Standard Mesh", None))
        self.cmbContactMesh.setItemText(1, QCoreApplication.translate("MainWindow", u"Fine Mesh", None))
        self.cmbContactMesh.setItemText(2, QCoreApplication.translate("MainWindow", u"Decimate Mesh", None))
        self.cmbContactMesh.setItemText(3, QCoreApplication.translate("MainWindow", u"Convex Hull", None))

#if QT_CONFIG(tooltip)
        self.cmbContactMesh.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Contact processing method:</p><p>1) Standard Mesh: original CAD geometry of the contacted Bodies is considered.</p><p>2) Fine Mesh: the Body mesh is subdivided to increase the accuracy of the contact processing. Note: Simulation time is increased.</p><p>3) Proxy Meshes (Convex Hulls) is for CAD models with internal holes, chamfers. Generation of the &quot;Convex Hull&quot; (shrink-wrapping the geometry) reduces fine meshed model to lower vertices, speeding up the collision math.</p><p>4) Decimation (Simplification): If a Convex Hull is too simple (e.g., we need the teeth of a gear to collide), we can use mesh decimation instead of subdivision.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.chkContactFriction.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Activate / deactivate the Contact Friction (defined as Regularized Coulomb Friction)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkContactFriction.setText(QCoreApplication.translate("MainWindow", u"Contact Friction", None))
        self.label_81.setText(QCoreApplication.translate("MainWindow", u"Friction Coeff., mu", None))
#if QT_CONFIG(tooltip)
        self.dsbContactFrictionCoeff.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Friction Coefficient (mu)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_80.setText(QCoreApplication.translate("MainWindow", u"Slip Tol.Velocity, mm/s", None))
#if QT_CONFIG(tooltip)
        self.dsbTolVelocity.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Slip Tolerance Velocity (V_tol) for the Regularized Coulomb Friction model.</p><p>If the relative velocity of the contacted Bodies exceeds V_tol, then Friction Force is calculated based on the specified Friction Coefficient: F_friction=mu*N.</p><p>If the relative velocity of the contacted Bodies is below V_tol, then Friction Force is smoothly reduced to 0.0 together with the relative velocity. </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.grbGear.setTitle(QCoreApplication.translate("MainWindow", u"Gear Data", None))
        self.label_88.setText(QCoreApplication.translate("MainWindow", u"RF Gear", None))
#if QT_CONFIG(tooltip)
        self.Edit_RFGear.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Reference Frame defining the Global Gear position</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbRF_GearXYZ.setItemText(0, QCoreApplication.translate("MainWindow", u"X", None))
        self.cmbRF_GearXYZ.setItemText(1, QCoreApplication.translate("MainWindow", u"Y", None))
        self.cmbRF_GearXYZ.setItemText(2, QCoreApplication.translate("MainWindow", u"Z", None))

#if QT_CONFIG(tooltip)
        self.cmbRF_GearXYZ.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Select the Reference Frame axis, which defines the Gear axis of rotation. </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbRF_GearXYZ.setCurrentText(QCoreApplication.translate("MainWindow", u"X", None))
        self.label_97.setText(QCoreApplication.translate("MainWindow", u"Gear Type", None))
        self.cmbGearType.setItemText(0, QCoreApplication.translate("MainWindow", u"Helical Gear", None))
        self.cmbGearType.setItemText(1, QCoreApplication.translate("MainWindow", u"Inner Gear", None))
        self.cmbGearType.setItemText(2, QCoreApplication.translate("MainWindow", u"Bevel Gear", None))

#if QT_CONFIG(tooltip)
        self.cmbGearType.setToolTip(QCoreApplication.translate("MainWindow", u"Select the Gear Type", None))
#endif // QT_CONFIG(tooltip)
        self.label_89.setText(QCoreApplication.translate("MainWindow", u"Transverse Module, mm", None))
#if QT_CONFIG(tooltip)
        self.dsbModule.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Gear Transverse Module (m_t) calculated in the plane of rotation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_90.setText(QCoreApplication.translate("MainWindow", u"Number of Teeth", None))
#if QT_CONFIG(tooltip)
        self.dsbNTeeth.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Gear number of Teeth (z)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_91.setText(QCoreApplication.translate("MainWindow", u"Pressure Angle, deg", None))
#if QT_CONFIG(tooltip)
        self.dsbPressureAngle.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Gear Pressure Angle (alpha)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblHelixAngle.setText(QCoreApplication.translate("MainWindow", u"Helix Angle, deg", None))
#if QT_CONFIG(tooltip)
        self.dsbHelixAngle.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Gear Helix Angle (beta)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_93.setText(QCoreApplication.translate("MainWindow", u"Gear Width, mm", None))
#if QT_CONFIG(tooltip)
        self.dsbGearWidth.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Gear face width, which is the axial length of the gear teeth</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblPitchAngle.setText(QCoreApplication.translate("MainWindow", u"Pitch Angle, deg", None))
#if QT_CONFIG(tooltip)
        self.dsbPitchAngle.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Pitch Angle (gamma) defines the orientation of the Gear's pitch surface relative to its axis</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblBoreDia.setText(QCoreApplication.translate("MainWindow", u"Bore Diameter, mm", None))
#if QT_CONFIG(tooltip)
        self.dsbBoreDia.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Inner hole diameter of the Gear</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblRimDia.setText(QCoreApplication.translate("MainWindow", u"Outer Rim Diameter, mm", None))
#if QT_CONFIG(tooltip)
        self.dsbRimDia.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Outer Gear Rim diameter</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btnCreateGear.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create new Gear (as a rigid Body).</p><p>Consider following information for the Gear creation:</p><p>1) The Gears generated by the program have the rough teeth geometry for the visual purpose only.</p><p>2) Once the Gear is generated, it is stored as a normal rigid Body and does not have the Gear macro-geometry properties (module, number of teeth, \u03b1, \u03b2-angles, etc) visible to the Solver. Therefore, these properties must be defined on the Gear Pair Constraint interface.</p><p>3) Recommendation: Do not consider the Gear CoG as the Reference Frame for the Gear Joint definition, because the Gear CoG is calculated based on the Gear 3D mesh and can have the spatial position mismatch related to the theoretical Gear axis position, which can cause the inaccurate solver processing or errors. </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnCreateGear.setText(QCoreApplication.translate("MainWindow", u"Create Gear", None))
        self.grbGear_2.setTitle(QCoreApplication.translate("MainWindow", u"Gear Pair Constraint", None))
        self.label_108.setText(QCoreApplication.translate("MainWindow", u"Name      ", None))
#if QT_CONFIG(tooltip)
        self.btnRenameGearPair.setToolTip(QCoreApplication.translate("MainWindow", u"Rename Gear Constraint", None))
#endif // QT_CONFIG(tooltip)
        self.btnRenameGearPair.setText("")
#if QT_CONFIG(tooltip)
        self.btnDelGearPair.setToolTip(QCoreApplication.translate("MainWindow", u"Delete Gear Constraint", None))
#endif // QT_CONFIG(tooltip)
        self.btnDelGearPair.setText("")
        self.label_99.setText(QCoreApplication.translate("MainWindow", u"Gear Type", None))
        self.cmbJointGearType.setItemText(0, QCoreApplication.translate("MainWindow", u"Helical Gear", None))
        self.cmbJointGearType.setItemText(1, QCoreApplication.translate("MainWindow", u"Inner Gear", None))
        self.cmbJointGearType.setItemText(2, QCoreApplication.translate("MainWindow", u"Bevel Gear", None))

#if QT_CONFIG(tooltip)
        self.cmbJointGearType.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Type of the constrained Gears</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_98.setText(QCoreApplication.translate("MainWindow", u"Rev.Joint Gear 1", None))
#if QT_CONFIG(tooltip)
        self.Edit_JointGear1.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Revolute Joint constraining the Gear 1 to the Carrier Body.</p><p>Consider following rules for the Gear Joints definition:</p><p>1) The Joints axes of the Helical Gears must be parallel and spaced apart by a distance equal to the Center Distance between the Gears. </p><p>2) When defining the Gear Revolute Joint, the Carrier must be the Body_I, and the Gear must be the Body_J (as it is considered in the Solver).</p><p>3) When defining the Inner Gear Constraint, the Pinion Gear Joint must be the Joint 1, and the Inner Gear Joint must be the Joint 2.</p><p>4) The Revolute Joint axes (shafts) for Bevel gears must intersect perfectly in 3D space, and they must be positioned at a standard 90\u00b0 angle.</p><p>5) Recommendation: Do not consider the Gear CoG as the Reference Frame for the Gear Joint definition, because the Gear CoG is calculated based on the Gear 3D mesh and can have the spatial position mismatch related to the theoretical Gear axis position, which can cause the inacc"
                        "urate solver processing or errors.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_101.setText(QCoreApplication.translate("MainWindow", u"Rev.Joint Gear 2", None))
#if QT_CONFIG(tooltip)
        self.Edit_JointGear2.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Revolute Joint constraining the Gear 2 to the Carrier Body.</p><p>Consider following rules for the Gear Joints definition:</p><p>1) The Joints axes of the Helical Gears must be parallel and spaced apart by a distance equal to the Center Distance between the Gears. </p><p>2) When defining the Gear Revolute Joint, the Carrier must be the Body_I, and the Gear must be the Body_J (as it is considered in the Solver).</p><p>3) When defining the Inner Gear Constraint, the Pinion Gear Joint must be the Joint 1, and the Inner Gear Joint must be the Joint 2.</p><p>4) The Revolute Joint axes (shafts) for Bevel gears must intersect perfectly in 3D space, and they must be positioned at a standard 90\u00b0 angle.</p><p>5) Recommendation: Do not consider the Gear CoG as the Reference Frame for the Gear Joint definition, because the Gear CoG is calculated based on the Gear 3D mesh and can have the spatial position mismatch related to the theoretical Gear axis position, which can cause the inacc"
                        "urate solver processing or errors.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_107.setText(QCoreApplication.translate("MainWindow", u"Carrier", None))
#if QT_CONFIG(tooltip)
        self.Edit_JointCarrier.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Carrier: Body holding both Gears.</p><p>Consider the Carrier definition Rule (important for Planetary gersets, Differentials, etc): </p><p>The Carrier Body is the body relative to which the centers of both gears do not move.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_104.setText(QCoreApplication.translate("MainWindow", u"Nr. of Teeth (z1)", None))
#if QT_CONFIG(tooltip)
        self.dsbNTeethGear1.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Number of teeth of the 1st Gear</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_106.setText(QCoreApplication.translate("MainWindow", u"Nr. of Teeth (z2)", None))
#if QT_CONFIG(tooltip)
        self.dsbNTeethGear2.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Number of teeth of the 2nd Gear</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_100.setText(QCoreApplication.translate("MainWindow", u"Trans. Module, mm", None))
#if QT_CONFIG(tooltip)
        self.dsbJointModule.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Gear Transverse Module (m_t) calculated in the plane of rotation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_102.setText(QCoreApplication.translate("MainWindow", u"Pressure Angle, deg", None))
#if QT_CONFIG(tooltip)
        self.dsbJointPressureAngle.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Gear Pressure Angle (alpha)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblJointHelixAngle.setText(QCoreApplication.translate("MainWindow", u"Helix Angle Gear 1, deg", None))
#if QT_CONFIG(tooltip)
        self.dsbJointHelixAngle.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Gear Helix Angle (beta) of the 1st Gear</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblJointPitchAngle.setText(QCoreApplication.translate("MainWindow", u"Pitch Angle Gear 1, deg", None))
#if QT_CONFIG(tooltip)
        self.dsbJointPitchAngle.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Pitch Angle (gamma) of the 1st Gear.</p><p>When defining the Bevel Gear Constraint, the Pitch Angle of Gear 1 is defined by the user, and the Pitch Angle of Gear 2 is automatically calculated considering the Bevel Gear axes relative angle is 90 degree.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btnCreateGearPair.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create new Gear Pair Constraint</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnCreateGearPair.setText(QCoreApplication.translate("MainWindow", u"Create Gear Pair", None))
#if QT_CONFIG(tooltip)
        self.btnUpdateGearPair.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Apply the numerical data of the Gear Pair</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnUpdateGearPair.setText("")
#if QT_CONFIG(tooltip)
        self.chkEnabledGearPair.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Enable / disable selected Gear Constraint in the Simulation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.chkEnabledGearPair.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
        self.grbPrimitives.setTitle(QCoreApplication.translate("MainWindow", u"Primitives", None))
        self.label_109.setText(QCoreApplication.translate("MainWindow", u"Anchor RF", None))
#if QT_CONFIG(tooltip)
        self.Edit_RFPrimitive.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Reference Frame as a geometric center of symmetry of the new Body</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbRF_PrimXYZ.setItemText(0, QCoreApplication.translate("MainWindow", u"X", None))
        self.cmbRF_PrimXYZ.setItemText(1, QCoreApplication.translate("MainWindow", u"Y", None))
        self.cmbRF_PrimXYZ.setItemText(2, QCoreApplication.translate("MainWindow", u"Z", None))

#if QT_CONFIG(tooltip)
        self.cmbRF_PrimXYZ.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Body simmetry axis as the X,Y or Z-axis of the selected Reference Frame</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbRF_PrimXYZ.setCurrentText(QCoreApplication.translate("MainWindow", u"X", None))
        self.lblPrimRFTarget.setText(QCoreApplication.translate("MainWindow", u"Target RF", None))
        self.label_110.setText(QCoreApplication.translate("MainWindow", u"Type", None))
        self.cmbPrimitiveType.setItemText(0, QCoreApplication.translate("MainWindow", u"Box", None))
        self.cmbPrimitiveType.setItemText(1, QCoreApplication.translate("MainWindow", u"Cylinder / Tube", None))
        self.cmbPrimitiveType.setItemText(2, QCoreApplication.translate("MainWindow", u"Sphere", None))
        self.cmbPrimitiveType.setItemText(3, QCoreApplication.translate("MainWindow", u"Uniform n-sided Prism", None))
        self.cmbPrimitiveType.setItemText(4, QCoreApplication.translate("MainWindow", u"Torus", None))
        self.cmbPrimitiveType.setItemText(5, QCoreApplication.translate("MainWindow", u"Truncated Cone", None))
        self.cmbPrimitiveType.setItemText(6, QCoreApplication.translate("MainWindow", u"Link", None))

#if QT_CONFIG(tooltip)
        self.cmbPrimitiveType.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Primitive Type to create</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lblPrimDim1.setText(QCoreApplication.translate("MainWindow", u"Dim 1, mm", None))
#if QT_CONFIG(tooltip)
        self.dsbPrimDim1.setToolTip(QCoreApplication.translate("MainWindow", u"Define the Dimension", None))
#endif // QT_CONFIG(tooltip)
        self.lblPrimDim2.setText(QCoreApplication.translate("MainWindow", u"Dim 2, mm", None))
#if QT_CONFIG(tooltip)
        self.dsbPrimDim2.setToolTip(QCoreApplication.translate("MainWindow", u"Define the Dimension", None))
#endif // QT_CONFIG(tooltip)
        self.lblPrimDim3.setText(QCoreApplication.translate("MainWindow", u"Dim 3, mm", None))
#if QT_CONFIG(tooltip)
        self.dsbPrimDim3.setToolTip(QCoreApplication.translate("MainWindow", u"Define the Dimension", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btnCreatePrimitive.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Create new Primitive with specified dimensions.</p><p>Note: once the Body is created, its dimensions cannot be modified.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnCreatePrimitive.setText(QCoreApplication.translate("MainWindow", u"Create Primitive", None))
        self.grbForcesTorques_2.setTitle(QCoreApplication.translate("MainWindow", u"Joint Motion definition", None))
        self.label_111.setText(QCoreApplication.translate("MainWindow", u"Name   ", None))
#if QT_CONFIG(tooltip)
        self.btnRenameMotion.setToolTip(QCoreApplication.translate("MainWindow", u"Rename Motion", None))
#endif // QT_CONFIG(tooltip)
        self.btnRenameMotion.setText("")
#if QT_CONFIG(tooltip)
        self.btnDelMotion.setToolTip(QCoreApplication.translate("MainWindow", u"Delete Motion", None))
#endif // QT_CONFIG(tooltip)
        self.btnDelMotion.setText("")
        self.label_113.setText(QCoreApplication.translate("MainWindow", u"Joint", None))
#if QT_CONFIG(tooltip)
        self.Edit_MotionJoint.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define the Joint to which the Motion constraint is applied. Following Joints are supported: Revolute, Prismatic and Cylindrical.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbMotionTransRot.setItemText(0, QCoreApplication.translate("MainWindow", u"Translational", None))
        self.cmbMotionTransRot.setItemText(1, QCoreApplication.translate("MainWindow", u"Rotational", None))

#if QT_CONFIG(tooltip)
        self.cmbMotionTransRot.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define Translational or Rotational Motion.</p><p>Translational Motion is applicable for the Prismatic and Cylindrical Joints.</p><p>Rotational Motion is applicable for the Revolute and Cylindrical Joints.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbMotionTransRot.setCurrentText(QCoreApplication.translate("MainWindow", u"Translational", None))
        self.cmbMotionTransRot.setPlaceholderText("")
        self.cmbMotionType.setItemText(0, QCoreApplication.translate("MainWindow", u"Displacement", None))
        self.cmbMotionType.setItemText(1, QCoreApplication.translate("MainWindow", u"Velocity", None))

#if QT_CONFIG(tooltip)
        self.cmbMotionType.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Specify how the Motion is defined: relative Displacement or Velocity.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.cmbMotionType.setCurrentText(QCoreApplication.translate("MainWindow", u"Displacement", None))
        self.cmbMotionType.setPlaceholderText("")
        self.lblMotion.setText(QCoreApplication.translate("MainWindow", u"mm", None))
#if QT_CONFIG(tooltip)
        self.Edit_MotionFunction.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>User-defined time dependent motion function f(t).</p><p>The Motion Constraint can be defined as a combination of the math functions of time. </p><p>Following functions can be directly entered in the input field:</p><p>sin(t), cos(t), tan(t), sqrt(t) (Square root), exp(t) (Exponential), abs(t) (Absolute value), pi.</p><p>It is possible to use \u2018np.\u2019 to call any standard NumPy math function, for example:</p><p>np.cosh(t),  np.round(t), np.sign(t), etc.</p><p>Following custom functions are supported in the program:</p><p>The STEP function changes smoothly between two specified values.</p><p>Syntax: step(t; t0; F0; t1; F1)</p><p>The IF function:</p><p>Syntax: if(&lt;condition&gt;; &lt;value if less or equal to 0&gt;; &lt;value if greater than 0&gt;).</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.Edit_MotionFunction.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.btnUpdateMotion.setText("")
        self.btnAddMotion.setText(QCoreApplication.translate("MainWindow", u"Create Motion", None))
        self.chkEnabledMotion.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
        self.grbVisuals.setTitle(QCoreApplication.translate("MainWindow", u"Visuals Length, mm", None))
        self.lbl_RFLength.setText(QCoreApplication.translate("MainWindow", u"Reference Frames", None))
        self.lblJoints_Length.setText(QCoreApplication.translate("MainWindow", u"Joints/ Bushings", None))
        self.lblForce_Length.setText(QCoreApplication.translate("MainWindow", u"Forces/ Torques", None))
        self.btnUpdateVisuals.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.grbJoints_2.setTitle(QCoreApplication.translate("MainWindow", u"Boolean Operation", None))
        self.label_92.setText(QCoreApplication.translate("MainWindow", u"Body J", None))
#if QT_CONFIG(tooltip)
        self.Edit_Body_J_Boolean.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define second Body for Boolean operation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_94.setText(QCoreApplication.translate("MainWindow", u"Body I", None))
#if QT_CONFIG(tooltip)
        self.Edit_Body_I_Boolean.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Define first Body for Boolean operation</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btnUniteBodies.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Crate new Body as a new united CAD mesh of the selected Body_I and Body_J.</p><p>If Body_I and Body_J do not intersect, the new Body will not created.</p><p>In any case, the original Body_I and Body_J remain untouched.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnUniteBodies.setText(QCoreApplication.translate("MainWindow", u"Unite as New Body", None))
#if QT_CONFIG(tooltip)
        self.btnCleanBoolBodies.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Clear the fields for bodies selection.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnCleanBoolBodies.setText(QCoreApplication.translate("MainWindow", u"Clean", None))
        self.txbTraceback.setMarkdown(QCoreApplication.translate("MainWindow", u"Welcome to SimPhant!\n"
"\n"
"", None))
        self.txbTraceback.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Welcome to SimPhant!</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
    # retranslateUi

