import tkinter as tk
import tkinter.messagebox as msgBox
import time
import math

# 全局变量声明
# 窗口
root = tk.Tk()  # 创建一个窗口对象
root.geometry("960x630+16+9")  # 参数：宽、高、左侧偏移量、上方偏移量
root.title("计算机动画 - 实验2")
# 画布
canvas = tk.Canvas(root, bg="white", width=960, height=540)
canvas.pack()  # 将部件放置到主窗口
# 点列表
srcCoordList = []
targetCoordList = []
# 绘图控制变量
finishedDrawing = False
drawingSrc = True
lineWidth = 1
duration = 5
grain = 50  # 生成中间图形的数量
srcColor = "#E16B8C"  # 红梅
targetColor = "#2EA9DF"  # 露草
transitColor = "#86C166"  # 苗


def placePoint(event):
    global drawingSrc
    global srcCoordList
    global targetCoordList
    global finishedDrawing
    global canvas
    # 完成绘制，直接返回
    if finishedDrawing:
        return
    if drawingSrc:
        color = srcColor
    else:
        color = targetColor

    if drawingSrc:
        # 判断当前点是否与第一个点重合
        # 当前点与第一个点重合，图形封闭
        if len(srcCoordList) > 0 and abs(event.x - srcCoordList[0][0]) <= 3 and abs(event.y - srcCoordList[0][1]) <= 3:
            drawingSrc = False
            srcCoordList.append([srcCoordList[0][0], srcCoordList[0][1]])
            drawLines(srcCoordList, color)
        # 图形未封闭
        else:
            drawPoint(event.x, event.y, color)
            srcCoordList.append([event.x, event.y])
    else:
        # 图形封闭
        if len(targetCoordList) > 0 and abs(event.x - targetCoordList[0][0]) <= 3 and abs(
                event.y - targetCoordList[0][1]) <= 3:
            drawingSrc = True
            targetCoordList.append([targetCoordList[0][0], targetCoordList[0][1]])
            # 原图形与目标图形点数不一致，清空画布要求重画
            if len(srcCoordList) != len(targetCoordList):
                msgBox.showwarning("警告", "目标图形的点数必须与原图形一致，请重新绘制。")
                canvas.delete("all")
                srcCoordList.clear()
                targetCoordList.clear()
                return
            finishedDrawing = True
            drawLines(targetCoordList, color)
        # 图形未封闭
        else:
            drawPoint(event.x, event.y, color)
            targetCoordList.append([event.x, event.y])


def drawPoint(x, y, color):
    global canvas
    canvas.create_oval(x - 3, y + 3, x + 3, y - 3, fill=color, outline=color)


def drawLines(pointList, color):
    global lineWidth
    for i in range(0, len(pointList) - 1):
        canvas.create_line(pointList[i][0], pointList[i][1], pointList[i + 1][0],
                           pointList[i + 1][1], width=lineWidth, fill=color)


def generateTransitPoints_linear(i):
    transitCoordList = []
    for j in range(0, len(srcCoordList)):
        srcCoord = srcCoordList[j]
        targetCoord = targetCoordList[j]
        x = round(i / (grain + 2) * targetCoord[0] + (grain + 2 - i) / (grain + 2) * srcCoord[0])
        y = round(i / (grain + 2) * targetCoord[1] + (grain + 2 - i) / (grain + 2) * srcCoord[1])
        transitCoordList.append([x, y])
    return transitCoordList


def linearInterpolate():
    global canvas
    global srcCoordList
    global targetCoordList
    global transitColor
    sleepTime = duration / grain  # 动画时长固定，且一帧动画的时间不得长于0.1秒
    if (sleepTime > 0.1):
        sleepTime = 0.1
    for i in range(1, grain + 1):
        transitCoordList = generateTransitPoints_linear(i)
        drawLines(transitCoordList, transitColor)
        canvas.update()  # 立即刷新画布，否则画布将等到回调函数结束再刷新
        time.sleep(sleepTime)
        canvas.delete("all")
        transitCoordList.clear()
        drawSrcAndTarget()


def calcNormalizeRad(deltaX, deltaY):
    """计算弧度并归一化到[0,2pi]之间"""
    if deltaX == 0:
        if deltaY > 0:
            rad = math.pi / 2
        else:
            rad = math.pi / 2 * 3
    else:
        rad = math.atan(deltaY / deltaX)
        # 角度归一化到[0,2pi]
        if deltaX > 0 and deltaY > 0:
            rad = rad
        elif deltaX > 0 and deltaY < 0:
            rad = rad + 2 * math.pi
        elif deltaX < 0 and deltaY > 0:
            rad = rad + math.pi
        else:
            rad = rad + math.pi
    return rad


def calcVList(pointList):
    """根据点列表，计算相邻两点之间的向量，封装在列表中返回"""
    VList = []
    for i in range(0, len(pointList) - 1):
        this = pointList[i]
        next = pointList[i + 1]
        deltaX = next[0] - this[0]
        deltaY = next[1] - this[1]
        length = math.sqrt(deltaX * deltaX + deltaY * deltaY)
        rad = calcNormalizeRad(deltaX, deltaY)
        VList.append([length, rad])
    return VList


def adjustTargetVList(srcVList, targetVList, mode):
    """
    调整目标图形中各个向量的角度，以使得图形能够顺时针/逆时针旋转
    函数假定所有向量的角度都已经在[0,2pi]之间
    """
    if mode == "clockwise":
        for i in range(0, len(srcVList)):
            targetRad = targetVList[i][1]
            srcRad = srcVList[i][1]
            if targetRad > srcRad:
                targetRad -= 2 * math.pi
                targetVList[i][1] = targetRad
    else:
        for i in range(0, len(srcVList)):
            targetRad = targetVList[i][1]
            srcRad = srcVList[i][1]
            if targetRad < srcRad:
                targetRad += 2 * math.pi
                targetVList[i][1] = targetRad


def calcTransitPointsByVector(initialPoint, transitVList):
    """利用传入的向量列表，计算一帧中各个过渡点的坐标"""
    transitPoints = []
    transitPoints.append(initialPoint)
    lastPoint = initialPoint
    # 最后一个向量其实是无用的，因为图形的最后一个点就是起始点
    for i in range(0, len(transitVList) - 1):
        length = transitVList[i][0]
        angle = transitVList[i][1]
        nextPointX = lastPoint[0] + length * math.cos(angle)
        nextPointY = lastPoint[1] + length * math.sin(angle)
        transitPoints.append([round(nextPointX), round(nextPointY)])
        lastPoint = [nextPointX, nextPointY]
    transitPoints.append(initialPoint)
    return transitPoints


# vectorList应直接存储长度和角度（弧度制）
def generateTransitPoints_vector(i, srcVectorList, targetVectorList):
    """先计算过渡向量列表，然后调用calcTransitPointsByVector计算一帧中各个过渡点的坐标"""
    global srcCoordList
    global targetCoordList
    transitVectorList = []
    srcInitialPoint = srcCoordList[0]
    targetInitialPoint = targetCoordList[0]
    initialX = round(i / (grain + 2) * targetInitialPoint[0] + (grain + 2 - i) / (grain + 2) * srcInitialPoint[0])
    initialY = round(i / (grain + 2) * targetInitialPoint[1] + (grain + 2 - i) / (grain + 2) * srcInitialPoint[1])
    initialPoint = [initialX, initialY]
    # 计算过渡向量
    for j in range(0, len(srcVectorList)):
        srcV = srcVectorList[j]
        targetV = targetVectorList[j]
        length = i / (grain + 2) * targetV[0] + (grain + 2 - i) / (grain + 2) * srcV[0]
        phi = i / (grain + 2) * targetV[1] + (grain + 2 - i) / (grain + 2) * srcV[1]
        transitVectorList.append([length, phi])
    return calcTransitPointsByVector(initialPoint, transitVectorList)


def vectorInterpolate_clockWise():
    sleepTime = duration / grain  # 动画时长固定，且一帧动画的时间不得长于0.1秒
    if (sleepTime > 0.1):
        sleepTime = 0.1
    srcVList = calcVList(srcCoordList)
    targetVList = calcVList(targetCoordList)
    adjustTargetVList(srcVList, targetVList, "clockwise")
    for i in range(1, grain + 1):
        transitCoordList = generateTransitPoints_vector(i, srcVList, targetVList)
        drawLines(transitCoordList, transitColor)
        canvas.update()  # 立即刷新画布，否则画布将等到回调函数结束再刷新
        time.sleep(sleepTime)
        canvas.delete("all")
        transitCoordList.clear()
        drawSrcAndTarget()


def vectorInterpolate_counterClockWise():
    sleepTime = duration / grain  # 动画时长固定，且一帧动画的时间不得长于0.1秒
    if (sleepTime > 0.1):
        sleepTime = 0.1
    srcVList = calcVList(srcCoordList)
    targetVList = calcVList(targetCoordList)
    adjustTargetVList(srcVList, targetVList, "counterClockwise")
    for i in range(1, grain + 1):
        transitCoordList = generateTransitPoints_vector(i, srcVList, targetVList)
        drawLines(transitCoordList, transitColor)
        canvas.update()  # 立即刷新画布，否则画布将等到回调函数结束再刷新
        time.sleep(sleepTime)
        canvas.delete("all")
        transitCoordList.clear()
        drawSrcAndTarget()


def drawSrcAndTarget():
    for i in range(0, len(srcCoordList)):
        drawPoint(srcCoordList[i][0], srcCoordList[i][1], srcColor)
    for i in range(0, len(targetCoordList)):
        drawPoint(targetCoordList[i][0], targetCoordList[i][1], targetColor)
    drawLines(srcCoordList, srcColor)
    drawLines(targetCoordList, targetColor)


def clear():
    global drawingSrc
    global finishedDrawing
    canvas.delete("all")
    srcCoordList.clear()
    targetCoordList.clear()
    drawingSrc = True
    finishedDrawing = False


# 按钮
clearButton = tk.Button(root, text="清除", command=clear, relief="groove", height=2, width=20)
linearButton = tk.Button(root, text="线性插值", command=linearInterpolate, relief="groove",
                         height=2, width=20)
clockwiseButton = tk.Button(root, text="矢量线性插值\n（顺时针）", command=vectorInterpolate_clockWise,
                            relief="groove", height=2, width=20)
counterClockwiseButton = tk.Button(root, text="矢量线性插值\n（逆时针）", command=vectorInterpolate_counterClockWise,
                                   relief="groove", height=2, width=20)
clearButton.pack()
linearButton.pack()
clockwiseButton.pack()
counterClockwiseButton.pack()
clearButton.place(x=84, y=585, anchor='w')
linearButton.place(x=84 + 200, y=585, anchor='w')
clockwiseButton.place(x=84 + 200 * 2, y=585, anchor='w')
counterClockwiseButton.place(x=84 + 200 * 3, y=585, anchor='w')
canvas.bind("<Button-1>", placePoint)
root.mainloop()
