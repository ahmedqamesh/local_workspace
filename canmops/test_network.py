from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import networkx as nx

class PrettyWidget(QWidget):

    NumButtons = ['plot3']

    def __init__(self):


        super(PrettyWidget, self).__init__()        
        font = QFont()
        font.setPointSize(16)
        self.initUI()

    def initUI(self):

        self.setGeometry(100, 100, 800, 600)
        self.center()
        self.setWindowTitle('S Plot')

        grid = QGridLayout()
        self.setLayout(grid)
        self.createVerticalGroupBox() 

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.verticalGroupBox)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)        
        grid.addWidget(self.canvas, 0, 1, 9, 9)          
        grid.addLayout(buttonLayout, 0, 0)

        self.show()


    def createVerticalGroupBox(self):
        self.verticalGroupBox = QGroupBox()

        layout = QVBoxLayout()
        for i in  self.NumButtons:
                button = QPushButton(i)
                button.setObjectName(i)
                layout.addWidget(button)
                layout.setSpacing(10)
                self.verticalGroupBox.setLayout(layout)
                button.clicked.connect(self.submitCommand)

    def submitCommand(self):
        eval('self.' + str(self.sender().objectName()) + '()')

    def add_button(self,i):
        def _print():
            print("hi")
        cic_button = QPushButton("CIC%s"%i)
        cic_button.clicked.connect(_print)
        return cic_button
        
    def plot3(self):
        self.figure.clf()
        B = nx.Graph()
        B.add_nodes_from([1, 2, 3, 4], bipartite=0)
        B.add_nodes_from(['a', 'b', 'c', 'd', 'e'], bipartite=1)
        B.add_edges_from([(1, 'a'), (2, 'c'), (3, 'd'), (3, 'e'), (4, 'e'), (4, 'd')])
        
        B.add_edge('a', 'b', weight=0.6)
        B.add_edge('a', 'c', weight=0.2)
        B.add_edge('c', 'd', weight=0.1)
        B.add_edge('c', 'e', weight=0.7)
        B.add_edge('c', 'f', weight=0.9)
        B.add_edge('a', 'd', weight=0.3)

        #X = set(n for n, d in B.nodes(data=True) if d['bipartite'] == 0)
        #Y = set(B) - X

        #X = sorted(X, reverse=True)
        #Y = sorted(Y, reverse=True)
        colors = range(20)
        #pos = dict()
        pos = nx.spring_layout(B)
        #pos.update( (n, (2, i)) for i, n in enumerate(X) ) # put nodes from X at x=1
        #pos.update( (n, (0, i)) for i, n in enumerate(Y) ) # put nodes from Y at x=2
        nx.draw(B, node_color='#A0CBE2', pos=pos,edge_cmap=plt.cm.Blues, with_labels=True)
        self.canvas.draw_idle()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':

    import sys  
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))
    screen = PrettyWidget() 
    screen.show()   
    sys.exit(app.exec_())

"""
Modify base on:
http://stackoverflow.com/questions/36086361/embed-matplotlib-in-pyqt-with-multiple-plot/36093604

"""