diffcult=0
from chessboard import ChessBoard
from ai import searcher
VALUE=270
WIDTH = 540      #宽度
HEIGHT = 540     #高度
MARGIN = 22      #边缘宽度
GRID = (WIDTH - 2 * MARGIN) / (15 - 1)
PIECE = 34
EMPTY = 0
BLACK = 1
WHITE = 2

import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QPainter
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox

class AI(QtCore.QThread):
    finishSignal = QtCore.pyqtSignal(int, int)

    # 构造函数里增加形参
    def __init__(self, board, parent=None):
        super(AI, self).__init__(parent)
        self.board = board

    # 重写 run() 函数
    def run(self):
        self.ai = searcher()
        self.ai.board = self.board
        score, x, y = self.ai.search(2, 2)
        self.finishSignal.emit(x, y)
        
#重新定义Lable类
class LaBel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)

    def enterEvent(self, element):
        element.ignore()

class GoBang(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.chessboard = ChessBoard()  # 棋盘类

        # 设置棋盘背景
        pare = QPalette()
        pare.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap('img/chessboard.jpg')))
        self.setPalette(pare)
        # self.setStyleSheet("board-image:url(img/chessboard.jpg)")
        self.setCursor(Qt.PointingHandCursor)        # 鼠标变成手指形状
        #音效加载
        #self.sound_piece = QSound("sound/move.wav")  # 加载落子音效
        self.sound_victory = QSound("sound/win.wav")     # 加载胜利音效
        self.sound_defeated = QSound("sound/defeated.wav")  # 加载失败音效

        self.resize(WIDTH, HEIGHT)  # 固定大小
        self.setMinimumSize(QtCore.QSize(WIDTH, HEIGHT))
        self.setMaximumSize(QtCore.QSize(WIDTH, HEIGHT))
        
        self.setWindowTitle("艾雨翱20193673")  # 窗口名称
        self.setWindowIcon(QIcon('img/black.png'))  # 窗口图标

        
        #加载黑白棋子
        self.black = QPixmap('img/black.png')
        self.white = QPixmap('img/white.png')

        self.chess_now = BLACK  # 黑棋先行


        self.my_turn = True# 玩家先行
        self.step = 0  # 步数

        self.x, self.y = 1000, 1000

        #将鼠标图标改为黑色棋子
        self.mouse_point = LaBel(self)  # 将鼠标图片改为棋子
        self.mouse_point.setScaledContents(True)
        self.mouse_point.setPixmap(self.black)  # 加载黑棋
        self.mouse_point.setGeometry(VALUE, VALUE, PIECE, PIECE)
        self.pieces = [LaBel(self) for i in range(225)]  # 新建棋子标签，准备在棋盘上绘制棋子
        for piece in self.pieces:
            piece.setVisible(True)  # 图片可视
            piece.setScaledContents(True)  # 图片大小根据标签大小可变
        global diffcult
        self.mouse_point.raise_()  # 鼠标始终在最上层
        self.ai_down = True  # AI已下棋，主要是为了加锁，当值是False的时候说明AI正在思考，这时候玩家鼠标点击失效



        reply = QMessageBox.question(self, '是否先手', '是否执先?（关闭弹窗默认后手）',
                                     QMessageBox.Yes | QMessageBox.No)
        self.setMouseTracking(True)
        self.show()
        self.judge=0#判断先后手对步数的记录
        self.player=True#默认玩家起手
        if reply==QMessageBox.No:#不执先
            self.draw(7, 7)
            self.my_turn = True
            self.mouse_point.setPixmap(self.white)
            self.player=False#此时玩家不是主角
            self.ai_down = True
            self.judge=1


    #用箭头显示出电脑落子的位置
    def paintEvent(self, event):
        qm = QPainter()
        qm.begin(self)
        self.drawLines(qm)
        qm.end()
    # 黑色棋子随鼠标移动
    def mouseMoveEvent(self, e):  
        # self.lb1.setText(str(e.x()) + ' ' + str(e.y()))
        self.mouse_point.move(e.x() - 16, e.y() - 16)
    # 实现玩家落子
    def mousePressEvent(self, e):  # 玩家下棋
        if e.button() == Qt.LeftButton and self.ai_down == True:
            x, y = e.x(), e.y()  # 鼠标坐标
            i, j = self.coordinate_transform_pixel2map(x, y)  # 对应棋盘坐标
            #print(i)
            if not i is None and not j is None:  # 棋子落在棋盘上，排除边缘
                if self.chessboard.get_xy_on_logic_state(i, j) == EMPTY:  # 棋子落在空白处
                    self.draw(i, j)
                    self.ai_down = False
                    board = self.chessboard.board()
                    self.AI = AI(board)  # 新建线程对象，传入棋盘参数
                    self.AI.finishSignal.connect(self.AI_draw)  # 结束线程，传出参数
                    self.AI.start()  # run
                    print("My_AI:我的第{0}次思考完成".format(round((self.step+1-self.judge)/2)))

    def AI_draw(self, i, j):
        if self.step != 0:
            self.draw(i, j)  # AI
            self.x, self.y = self.coordinate_transform_map2pixel(i, j)
        self.ai_down = True
        self.update()

    def draw(self, i, j):
        x, y = self.coordinate_transform_map2pixel(i, j)

        if self.chess_now == BLACK:
            self.pieces[self.step].setPixmap(self.black)  # 放置黑色棋子
            self.chess_now = WHITE
            self.chessboard.draw_xy(i, j, BLACK)
        else:
            self.pieces[self.step].setPixmap(self.white)  # 放置白色棋子
            self.chess_now = BLACK
            self.chessboard.draw_xy(i, j, WHITE)

        self.pieces[self.step].setGeometry(x, y, PIECE, PIECE)  # 画出棋子
        #self.sound_piece.play()  # 落子音效
        self.step += 1  # 步数+1
        winner = self.chessboard.anyone_win(i, j)  # 判断输赢

        #判断平局
        aya=0
        byb=0
        just=0
        for aya in range(0,15):
            for byb in range(0,15):
                if (self.chessboard)._board[aya][byb]==EMPTY:
                    just=3
        if not just:
            winner=3

        if winner != EMPTY:
            self.mouse_point.clear()
            self.gameover(winner)

    def drawLines(self, qp):  # 指示AI当前下的棋子
        if self.step != 0:
            pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(self.x - 5, self.y - 5, self.x + 3, self.y + 3)
            qp.drawLine(self.x + 3, self.y, self.x + 3, self.y + 3)
            qp.drawLine(self.x, self.y + 3, self.x + 3, self.y + 3)
    # 从 chessMap 里的逻辑坐标到 UI 上的绘制坐标的转换
    def coordinate_transform_map2pixel(self, i, j):
        return MARGIN + j * GRID - PIECE / 2, MARGIN + i * GRID - PIECE / 2
    # 从 UI 上的绘制坐标到 chessMap 里的逻辑坐标的转换
    def coordinate_transform_pixel2map(self, x, y):
        i, j = int(round((y - MARGIN) / GRID)), int(round((x - MARGIN) / GRID))
        # 有MAGIN, 排除边缘位置导致 i,j 越界
        if i < 0 or i >= 15 or j < 0 or j >= 15:
            return None, None
        else:
            return i, j
    #定义游戏结束后弹出QMessagebox
    def gameover(self, winner):
        #平局
        if winner==3:
            reply = QMessageBox.question(self, '平局', '再来一局？',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)



        #胜利

        if (winner == BLACK and self.player==True)or(winner == WHITE and self.player==False):
            #self.sound_victory.play()
            reply = QMessageBox.question(self, '赢了啊', '乘胜追击?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        #失败
        else:
           # self.sound_defeated.play()
            reply = QMessageBox.question(self, '很可惜', '我要复仇？',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # 若选择Yes，重置棋盘
        if reply == QMessageBox.Yes:  
            self.chess_now = BLACK
            self.mouse_point.setPixmap(self.black)
            self.step = 0
            for piece in self.pieces:
                piece.clear()
            self.chessboard.reset()
            self.update()
        #若选择No时关闭窗口
        else:
            reply = QMessageBox.question(self, '艾雨翱', '感谢您的游玩',
                                         QMessageBox.Yes )
            self.close()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GoBang()
    sys.exit(app.exec_())