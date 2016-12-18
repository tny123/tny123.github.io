#!/usr/bin/env python
# encoding: utf-8


"""
@version: python27
@author: fafa
@software: PyCharm Community Edition
@file: appiumCommon.py
@time: 2016/12/18 0018 上午 11:56
"""

import os
import time
import unittest
from appium.webdriver import Remote
from appium.webdriver.connectiontype import ConnectionType

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)
"""
Connection types are specified here:
    https://code.google.com/p/selenium/source/browse/spec-draft.md?repo=mobile#120
    Value (Alias)      | Data | Wifi | Airplane Mode
    -------------------------------------------------
    0 (None)           | 0    | 0    | 0
    1 (Airplane Mode)  | 0    | 0    | 1
    2 (Wifi only)      | 0    | 1    | 0
    4 (Data only)      | 1    | 0    | 0
    6 (All network on) | 1    | 1    | 0
"""


# class ConnectionType(object):
#     NO_CONNECTION = 0
#     AIRPLANE_MODE = 1
#     WIFI_ONLY = 2
#     DATA_ONLY = 4
#     ALL_NETWORK_ON = 6


class AppiumCommon(unittest.TestCase):
    def __init__(self, filepath):
        self.desired_caps = {}
        self._driver = None
        file_object = open(filepath, 'rb')
        try:
            for line in file_object:
                # 忽略注释行
                if line.startswith('#'):
                    continue
                line.strip()
                worlds = line.split('==')
                # 忽略如下数据 如 app = 2 =linux
                if len(worlds[0]) != 2:
                    continue
                if worlds[0] == 'app':
                    self.desired_caps[worlds[0]] = PATH(worlds[1])
                elif worlds[0] == 'remoteHost':
                    remoteHost = worlds[1]
                else:
                    self.desired_caps[worlds[0]] = worlds[1]
        except IOError as e:
            print e.message
        finally:
            file_object.close()

    # 初始化驱动
    def initDriver(self):
        self._driver = Remote(self.remoteHost, self.desired_caps)

    # 用例执行后环境清理 关闭session
    def quitDriver(self):
        self._driver.quit()

    """
    给定控件的Xpath、id、name 来定位控件
    :args：
        -controlInfo 控件的信息 如:xpath / id /name 等
    ：return：
        如果找到控件返回第一个
    :usrage:
        self.findElemen(controlInfo)
    """

    def findElement(self, controlinfo):
        element = ""
        if controlinfo.startwith('//'):
            # xpath
            element = self._driver.find_element_by_xpath(controlinfo)
            # id
        elif ':id' in controlinfo or ':string' in controlinfo:
            element = self._driver.find_element_by_id(controlinfo)
        else:
            # 剩下的字符串没有特点，无法区分，因此先尝试通过name查找
            try:
                element = self._driver.find_element_by_name(controlinfo)
            except:
                element = self._driver.find_element_by_class_name(controlinfo)
        return element

    """
        给定控件的xpatch, id 或者name来查找控件

        :Args:
             - controlInfo: 控件的信息，可以是xpath,id或者其他属性

        :Return:
            返回所有满足条件的控件，返回的类型是一个列表

        :Usage:
            self.findElements(controlInfo)
        """

    def findElements(self, controlinfo):
        elements = ""
        if controlinfo.startwith('//'):
            # xpath
            elements = self._driver.find_element_by_xpath(controlinfo)
            # id
        elif ':id' in controlinfo:
            elements = self._driver.find_element_by_id(controlinfo)
        else:
            # 剩下的字符串没有特点，无法区分，因此先尝试通过name查找
            elements = self._driver.find_element_by_name(controlinfo)
        if len(elements == 0):
            elements = self._driver.find_element_by_class_name(controlinfo)
        return elements

    """
        在一个已知的控件中通过给定控件的xpatch, id 或者name来查找子控件

        :Args:
            - parentElement: 父控件，是一个已知的WebElement
            - childElementInfo: 子控件的信息，可以是xpath,id或者其他属性

        :Return:
            如果找到控件，返回第一个

        :Usage:
            self.findElement(controlInfo)
        """

    def findElementInParentElement(self, parentElement, childElementInfo):
        element = ""
        if (childElementInfo.startswith("//")):
            element = parentElement.find_element_by_xpath(childElementInfo)
        elif (":id/" in childElementInfo):
            element = parentElement.find_element_by_id(childElementInfo)
        else:
            # 剩下的字符串没有特点，无法区分，因此先尝试通过名称查找
            try:
                element = parentElement.find_element_by_name(childElementInfo)
            except:
                # 如果通过名称不能找到则通过class name查找
                element = parentElement.find_element_by_class_name(childElementInfo)

        return element

    """
        在一个已知的控件中通过给定控件的xpatch, id 或者name来查找子控件

        :Args:
            - parentElement: 父控件，是一个已知的WebElement
            - childElementInfo: 子控件的信息，可以是xpath,id或者其他属性

        :Return:
            如果找到控件，返回所有符合条件的控件

        :Usage:
            self.findElementsInParentElement(parentElement, controlInfo)
        """

    def findElementsInParentElement(self, parentElement, chrildElementInfo):
        elements = ""
        if chrildElementInfo.startwith("//"):
            elements = self._driver.find_element_by_xpath(chrildElementInfo)
        elif ":id/" in chrildElementInfo:
            elements = self._driver.find_element_by_id(chrildElementInfo)
        else:
            # 剩下的字符串没有特点，无法区分，因此先尝试通过名称查找
            elements = parentElement.find_elements_by_name(chrildElementInfo)
            if (len(elements) == 0):
                # 如果通过名称不能找到则通过class name查找
                elements = parentElement.find_elements_by_class_name(chrildElementInfo)

        return elements

    """
    通过UIAutomator的uio_string 来查找控件
    :Args:
        -uia_string: UiSelector相关的代码，参考http://developer.android.com/
        tools/help/uiautomator/UiSelector.html#fromParent%28com.android.uiautomator.core.UiSelector%29
    Return：
        -找到的控件
    Useage：
        self.findElementByUIAutomator(new UiSelector().(android.widget.LinearLayout))
  """

    def findElementByUIAutomator(self, uia_string):
        return self._driver.find_element_by_android_uiautomator(uia_string)

    """
    滑动操作
    Args：
        -X1，Y1，X2，Y2 活动起点、结束的左表
    Useage：
        self.swipe(x1,y1,x2,y2,duration=None) duration位滑动操作的时间单位为毫秒
        self.flick(x1,y1,x2,y2) :快速滑动
    """

    def flick(self, x1, y1, x2, y2):
        self._driver.flick(x1, y1, x2, y2)

    """
        点击屏幕上的位置，最多五个位置
        Args：
            tap(position,duration)
            -position为一个列表 每一个列表是一个2元祖表示元素的坐标
            -duration=None
        Useage：
            self.driver.tap([(100,100),(200,200),(300,300),(400,400),(500,500)],500)
    """

    """
        长按点击操作
        :Args:
         - x,y： 长按点的坐标
         - peroid: 多长时间内完成该操作,单位是毫秒

        :Usage:
            self.longPress(50, 50, 500)
        """

    def longPress(self, x, y, peroid):
        self._driver.tap([(x, y)], peroid)

    """
        点击某一个控件，如果改控件不存在则会抛出异常

        :Args:
             - elementInfo: 控件的信息，可以是xpath,id或者其他属性

        :Usage:
            self.clickElement(elementInfo)
        """

    def clickElement(self, elementInfo):
        element = self.findElement(elementInfo)
        element.click()

    """
    获取某个控件显示的文本，如果该控件不能找到则会抛出异常

    :Args:
         - elementInfo: 控件的信息，可以是xpath,id或者其他属性

    :Return:
        返回该控件显示的文本

    :Usage:
        self.getTextOfElement(elementInfo)

    """

    def getTextOfElement(self, elementInfo):
        element = self.findElement(elementInfo)
        return element.text

    """
    清除文本框里面的文本

    :Usage:
        self.clearTextEdit(elementInfo)
    """

    def clearTextEdit(self, elementInfo):
        element = self.findElement(elementInfo)
        element.clear()

    """
    按返回键
    press_keycode(self,keycode,metastate=None) 模拟发送一个硬件码到手机
    Useage:
        self.pressBackKEY()
    """

    def pressBackKey(self):
        self._driver.press_keycode(4)

    """
    等待某个控件显示
    Args:
        elementInfo 控件信息 可以是XPATH ID NAME CLASS_NAME等
        priod等待的秒数
    Useage:
        self.waitForElement(elementInfo,priod)
    """

    def waitForElement(self, elementInfo, priod):
        for i in range(0, priod):
            try:
                element = self.findElement(elementInfo)
                if element.is_displayed():
                    break
            except:
                continue
            time.sleep(1)
        else:
            raise Exception("Cannot find %s in %d seconds" % (elementInfo, priod))

    """
    等待某个控件不再显示

    :Args:
         - elementInfo: 控件的信息，可以是xpath,id或者其他属性
         - period：等待的秒数

    :Usage:
        self.waitForElementNotPresent(elementInfo, 3)
    """

    def waitForElementNotPresent(self, elementInfo, priod):
        for i in range(priod):
            try:
                if not self.checkElementIsShown(elementInfo):
                    break
            except:
                continue
                time.sleep(1)
            else:
                raise Exception("Cannot find %s in %d seconds" % (elementInfo, period))

    """
    判断某个控件是否显示

    :Args:
      - elementInfo: 控件的信息，可以是xpath,id或者其他属性
    :Return:
        True: 如果当前画面中期望的控件能被找到

    :Usage:
        self.checkElementIsShown(elementInfo)
    """

    def checkElementIsShown(self, elementInfo):

        try:
            self.findElement(elementInfo)
            return True
        except:
            return False

    """
        判断某个控件是否显示在另外一个控件中

        :Args:
            - parentElement: 父控件，是一个已知的WebElement
            - childElementInfo: 子控件的信息，可以是xpath,id或者其他属性
        :Return:
            True: 如果当前画面中期望的控件能被找到

        :Usage:
            self.checkElementShownInParentElement(parentElement,elementInfo)
        """

    def checkElementShownParentElement(self, parentElement, childElementInfo):
        try:
            self.findElementInParentElement(parentElement, childElementInfo)
            return True
        except:
            return False

    """
        判断某个控件是否被选中

        :Args:
             - elementInfo: 控件的信息，可以是xpath,id或者其他属性
        :Return:
            True: 如果当前画面中期望的控件能被选中

        :Usage:
            self.checkElementIsSelected(elementInfo)
        """

    def checkElementIsSelected(self, elementInfo):
        element = self.findElement(elementInfo)
        return element.is_selected()

    """
        判断摸个控件是否enabled
        :Args:
             - elementInfo: 控件的信息，可以是xpath,id或者其他属性
        :Return:
            True: 如果当前画面中期望的控件enabled

        :Usage:
            self.checkElementIsEnabled(elementInfo)
    """

    def checkElementIsEnabled(self, elementInfo):
        element = self.findElement(elementInfo)
        return element.get_attribute("enabled")

    """
       获取当前的Activity

       :Return:
           当前Activity的名称
    """

    def getCurrentActivety(self):
        return self._driver.current_activity

    """
        等待某一个Activity显示
        备注：不确定是否适用于ios

        :Args:
            -activityName: 某acitivity的名称
            -period: 等待的时间，秒数
    """

    def waitForActivity(self, activetyName, priod):
        for i in range(priod)
            try:
                if activetyName in self.getCurrentActivety():
                    break
            except:
                continue
                time.sleep(1)
            else:
                raise Exception("Cannot find the activity %s in %d seconds" % (activityName, period))

    """
        保存当前手机的屏幕截图到电脑上指定位置

        :Args:
             - pathOnPC: 电脑上保存图片的位置

        :Usage:
            self.saveScreenshot("c:\test_POI1.jpg")
    """

    def saveScreenshort(self, filename):
        self._driver.get_screenshot_as_file()

    def setNetwork(self, netType):
        pass

    """
    启动测试程序
    """

    def launchApp(self):
        self._driver.launch_app()

    """
    关闭测试程序
    """

    def closeApp(self):
        self._driver.close_app()

    """
        获取测试设备的OS

        :Return: Android或者ios
     """

    def getDeviceOs(self):
        return self.desired_caps['platformName']

    """
    只打开wifi连接
    """

    def enableWifiOnly(self):
        if ((self._driver.network_connection & 0x2) == 2):
            return
        else:
            self._driver.set_network_connection(ConnectionType.WIFI_ONLY)

    """
    只打开数据连接
    """

    def enableDataOnly(self):
        # if self._driver.network_connection ==4
        if (int(self._driver.network_connection & 4) == 4):
            return
        else:
            self._driver.set_network_connection(ConnectionType.DATA_ONLY)

    """
    关闭所有网络连接
    """

    def disableAllConnection(self):

        self._driver.set_network_connection(ConnectionType.NO_CONNECTION)

    """
    获取context
    """

    def getContext(self):
        self._driver.contexts

    def switchContext(self, contextName):
        self._driver.switch_to.context(contextName)

    """
    打开所有的网络连接
    """

    def enableAllConnection(self):
        self._driver.set_network_connection(ConnectionType.ALL_NETWORK_ON)
