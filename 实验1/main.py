from tkinter import *
import tkinter.messagebox
from PIL import Image
from PIL import ImageTk
import time
import numpy as np

# 全局变量声明
# 窗口
root = Tk()  # 创建一个窗口对象
root.geometry("960x640+16+9")  # 参数：宽、高、左侧偏移量、上方偏移量
root.title("计算机动画 - 作业1")
# 画布
canvas = Canvas(root, bg="white", width=960, height=540)  # 创建一个画布对象
canvas.pack()  # 将部件放置到主窗口
# 枢轴点列表
pivotXList = []
pivotYList = []
# 路径点列表
routeXList = []
routeYList = []
# 图像
PIL_img = Image.open("img - 2.png")
img = ImageTk.PhotoImage(PIL_img)
# 动画控制参数
tau = 0.05
grain = 5
relativeSpeed = 0.1  # 用于计算实际速度speed，后者指示一次跳过多少路径点。speed的取值范围[1,grain]
inPlay = False


def insertPoint(x, y):
    pivotXList.append(x)
    pivotYList.append(y)


def placePoint(x, y):
    canvas.create_oval(x - 1, y + 1, x + 1, y - 1)


def linkPoints(x1, y1, x2, y2, w):
    canvas.create_line(x1, y1, x2, y2, width=w)


def generateRoutePoints(x1, y1, x2, y2):
    # 利用插值方法，在两个点的连线中插入10个路径点，用于播放动画
    for i in range(0, 10):
        tempX = (1 - i / 10) * x1 + i / 10 * x2
        tempY = (1 - i / 10) * y1 + i / 10 * y2
        routeXList.append(tempX)
        routeYList.append(tempY)


def drawSpline(index):
    numOfPoints = grain
    # 向头尾加入两个点，避免越界
    pivotXList.insert(0, pivotXList[0])
    pivotYList.insert(0, pivotYList[0])
    pivotXList.append(pivotXList[-1])
    pivotYList.append(pivotYList[-1])
    index += 1

    numOfSegments = numOfPoints + 1
    transitXList = []
    transitYList = []
    # 计算过渡点的坐标
    # 1~numOfPoints
    for i in range(1, numOfSegments):
        u = i / numOfSegments
        uVector = np.array([[u ** 3, u ** 2, u, 1]])
        M = np.array([[-1, 2 / tau - 1, -2 / tau + 1, 1],
                      [2, -3 / tau + 1, 3 / tau - 2, -1],
                      [-1, 0, 1, 0],
                      [0, 1 / tau, 0, 0]
                      ])
        PXVector = np.array([[pivotXList[index - 1]],
                             [pivotXList[index]],
                             [pivotXList[index + 1]],
                             [pivotXList[index + 2]]
                             ])
        PXVector = PXVector * tau
        PYVector = np.array([[pivotYList[index - 1]],
                             [pivotYList[index]],
                             [pivotYList[index + 1]],
                             [pivotYList[index + 2]]
                             ])
        PYVector = PYVector * tau
        x = np.matmul(np.matmul(uVector, M), PXVector)[0][0]
        y = np.matmul(np.matmul(uVector, M), PYVector)[0][0]
        transitXList.append(round(x))
        transitYList.append(round(y))
    # 生成路径点
    generateRoutePoints(pivotXList[index], pivotYList[index], transitXList[0], transitYList[0])
    for i in range(0, len(transitXList) - 1):
        generateRoutePoints(transitXList[i], transitYList[i], transitXList[i + 1], transitYList[i + 1])
    generateRoutePoints(transitXList[-1], transitYList[-1], pivotXList[index + 1], pivotYList[index + 1])
    # 连接过渡点
    linkPoints(pivotXList[index], pivotYList[index], transitXList[0], transitYList[0], 1)
    for i in range(0, len(transitXList) - 1):
        linkPoints(transitXList[i], transitYList[i], transitXList[i + 1], transitYList[i + 1], 1)
    linkPoints(transitXList[-1], transitYList[-1], pivotXList[index + 1], pivotYList[index + 1], 1)
    # 移除临时加入的点
    pivotXList.pop(0)
    pivotYList.pop(0)
    pivotXList.pop(-1)
    pivotYList.pop(-1)


def drawSplines(event):
    canvas.delete("all")
    # 清空路径点列表，避免重复插入路径点
    routeXList.clear()
    routeYList.clear()
    if (event.x not in pivotXList and event.y not in pivotYList):
        insertPoint(event.x, event.y)
    # 绘制枢轴点
    for i in range(0, len(pivotXList)):
        placePoint(pivotXList[i], pivotYList[i])
    # 绘制样条曲线
    if (len(pivotXList) > 1):
        for i in range(0, len(pivotXList) - 1):
            drawSpline(i)


def clearAll():
    pivotXList.clear()
    pivotYList.clear()
    routeXList.clear()
    routeYList.clear()
    canvas.delete("all")


def play():
    global inPlay
    if (inPlay == False):
        inPlay = True
        i = 0
        speed = relativeSpeed * grain
        if (speed < 1):
            speed = 1
        while (i < len(routeXList) and inPlay == True):
            placeImage(routeXList[i], routeYList[i])
            i += round(speed)
        inPlay = False


def placeImage(x, y):
    canvas.delete("img")
    canvas.create_image(x, y, image=img, tag="img")
    canvas.update()
    time.sleep(0.04)


def updateRSpeed(text):
    global relativeSpeed
    relativeSpeed = float(text)


def updateGrain(text):
    global grain
    grain = int(text)


def updateTau(text):
    global tau
    tau = float(text)


# def placeImage(event):
#     canvas.create_image(event.x, event.y, image=img, tag="img")
#     canvas.update()


canvas.bind("<Button-1>", drawSplines)  # 为“鼠标左键点击”绑定回调函数

# 创建按钮
# 参数
# relief: 边框样式
# height: 高度，即字符的行数。
# width: 宽度，即字符的个数。
playButton = Button(root, text="Play", command=play, relief="groove", height=2, width=20)
playButton.pack()
# 参数
# anchor: 基准点。'w'表示窗口左上角
# x,y: 偏移量
playButton.place(x=32, y=572, anchor='w')
clearButton = Button(root, text="Clear", command=clearAll, relief="groove", height=2, width=20)
clearButton.pack()
clearButton.place(x=32 + 170, y=572, anchor='w')

# 创建滑动条
# 参数
# resolution: 步长
# show: 是否显示值。show=0表示不显示值。
# orient: 朝向
speedScale = Scale(root, label="Speed", from_=0.1, to=1, resolution=0.05, show=0, orient=HORIZONTAL,
                   command=updateRSpeed, length=160)
speedScale.pack()
speedScale.place(x=32 + 170 * 2 + 32, y=572, anchor='w')
grainScale = Scale(root, label="Grain", from_=5, to=100, resolution=5, show=0, orient=HORIZONTAL,
                   command=updateGrain, length=160)
grainScale.pack()
grainScale.place(x=32 + 170 * 2 + 32 + 180, y=572, anchor='w')
tauScale = Scale(root, label="Tau", from_=0.05, to=1, resolution=0.05, show=0, orient=HORIZONTAL,
                 command=updateTau, length=160)
tauScale.pack()
tauScale.place(x=32 + 170 * 2 + 32 + 180 * 2, y=572, anchor='w')

# 创建提示
noteLabel = Label(root, font=("等线", 12),
                  text="Note: Changes to \"Speed\" will take effect the next time it plays;\n"
                       "changes to \"Grain\" or \"Tau\" will take effect the next time you place a point.")
noteLabel.pack()
noteLabel.place(x=240, y=618, anchor='w')

root.mainloop()  # 进入消息循环

# 在两点之间插入numOfPoints个点，然后连接这些点
# def interpolate_line(x1, y1, x2, y2, numOfPoints, w):
#     numOfSegments=numOfPoints+1
#     for i in range(0, numOfSegments):
#         xStart = (numOfSegments - i) / numOfSegments * x1 + i / numOfSegments * x2
#         yStart = (numOfSegments - i) / numOfSegments * y1 + i /numOfSegments * y2
#         xEnd = (numOfSegments - i - 1) / numOfSegments * x1 + (i + 1) / numOfSegments * x2
#         yEnd = (numOfSegments - i - 1) /numOfSegments * y1 + (i + 1) / numOfSegments * y2
#         linkPoints(xStart, yStart, xEnd, yEnd, w)
#
#
# def drawLines_interpolate(event):
#     for i in range(0, len(xList) - 1):
#         interpolate_line(xList[i], yList[i], xList[i + 1], yList[i + 1], 50, 1)
