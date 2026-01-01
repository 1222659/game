# Google Colab - Python游戏APK构建
# 在Google Colab中运行此代码来构建APK

# 1. 安装依赖
!pip install buildozer

# 2. 创建游戏文件
with open('main.py', 'w', encoding='utf-8') as f:
    f.write('''import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from kivy.uix.popup import Popup

# 设置窗口大小为手机屏幕
Window.size = (360, 640)

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        self.grid_size = 20
        self.grid_width = int(self.width / self.grid_size)
        self.grid_height = int(self.height / self.grid_size)
        
        # 游戏状态
        self.snake = [(10, 15)]  # 蛇身坐标列表
        self.direction = Vector(1, 0)  # 当前方向
        self.next_direction = Vector(1, 0)  # 下一方向
        self.food = self.generate_food()  # 食物位置
        self.score = 0
        self.game_over = False
        
        # 设置背景色
        with self.canvas:
            Color(0, 0, 0, 1)  # 黑色背景
            self.bg = Rectangle(pos=self.pos, size=self.size)
            
            Color(0, 1, 0, 1)  # 绿色蛇头
            self.head = Rectangle(pos=self.get_pixel_pos(self.snake[0]), 
                                size=(self.grid_size, self.grid_size))
            
            Color(0, 0, 1, 1)  # 蓝色蛇身
            self.body_parts = []
            for segment in self.snake[1:]:
                rect = Rectangle(pos=self.get_pixel_pos(segment), 
                               size=(self.grid_size, self.grid_size))
                self.body_parts.append(rect)
            
            Color(1, 0, 0, 1)  # 红色食物
            self.food_rect = Rectangle(pos=self.get_pixel_pos(self.food), 
                                     size=(self.grid_size, self.grid_size))
        
        # 绑定大小变化
        self.bind(size=self.update_canvas)
        
        # 启动游戏循环
        self.game_clock = Clock.schedule_interval(self.update, 0.2)
    
    def get_pixel_pos(self, grid_pos):
        """将网格坐标转换为像素坐标"""
        return (grid_pos[0] * self.grid_size, grid_pos[1] * self.grid_size)
    
    def generate_food(self):
        """生成食物位置"""
        while True:
            food_x = random.randint(0, self.grid_width - 1)
            food_y = random.randint(0, self.grid_height - 1)
            if (food_x, food_y) not in self.snake:
                return (food_x, food_y)
    
    def update_canvas(self, instance, size):
        """更新画布大小"""
        self.grid_width = int(size[0] / self.grid_size)
        self.grid_height = int(size[1] / self.grid_size)
        self.bg.size = size
        
        # 更新蛇和食物的位置
        self.head.pos = self.get_pixel_pos(self.snake[0])
        for i, rect in enumerate(self.body_parts):
            if i + 1 < len(self.snake):
                rect.pos = self.get_pixel_pos(self.snake[i + 1])
        self.food_rect.pos = self.get_pixel_pos(self.food)
    
    def update(self, dt):
        """游戏更新函数"""
        if self.game_over:
            return
        
        # 更新方向
        self.direction = self.next_direction
        
        # 移动蛇头
        head_x, head_y = self.snake[0]
        new_head = (int(head_x + self.direction.x), int(head_y + self.direction.y))
        
        # 检查碰撞
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or 
            new_head[1] < 0 or new_head[1] >= self.grid_height or
            new_head in self.snake):
            self.game_over = True
            self.show_game_over()
            return
        
        # 添加新蛇头
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            self.food_rect.pos = self.get_pixel_pos(self.food)
        else:
            # 移除蛇尾
            self.snake.pop()
        
        # 更新绘制
        self.update_snake_graphics()
    
    def update_snake_graphics(self):
        """更新蛇的图形显示"""
        # 更新蛇头位置
        self.head.pos = self.get_pixel_pos(self.snake[0])
        
        # 更新蛇身
        while len(self.body_parts) < len(self.snake) - 1:
            with self.canvas:
                Color(0, 0, 1, 1)
                rect = Rectangle(pos=(0, 0), size=(self.grid_size, self.grid_size))
                self.body_parts.append(rect)
        
        while len(self.body_parts) > len(self.snake) - 1:
            rect = self.body_parts.pop()
            self.canvas.remove(rect)
        
        for i, rect in enumerate(self.body_parts):
            if i + 1 < len(self.snake):
                rect.pos = self.get_pixel_pos(self.snake[i + 1])
    
    def change_direction(self, new_direction):
        """改变蛇的方向"""
        # 防止反向移动
        if (new_direction.x * -1, new_direction.y * -1) != (self.direction.x, self.direction.y):
            self.next_direction = new_direction
    
    def show_game_over(self):
        """显示游戏结束弹窗"""
        content = BoxLayout(orientation='vertical', padding=20)
        content.add_widget(Label(text=f'游戏结束!\\n最终分数: {self.score}', 
                                font_size='24sp', size_hint_y=0.7))
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        restart_btn = Button(text='重新开始', size_hint_x=0.5)
        quit_btn = Button(text='退出', size_hint_x=0.5)
        
        btn_layout.add_widget(restart_btn)
        btn_layout.add_widget(quit_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title='游戏结束', content=content, 
                     size_hint=(0.8, 0.4), auto_dismiss=False)
        
        def restart_game(instance):
            self.restart()
            popup.dismiss()
        
        def quit_game(instance):
            App.get_running_app().stop()
        
        restart_btn.bind(on_press=restart_game)
        quit_btn.bind(on_press=quit_game)
        
        popup.open()
    
    def restart(self):
        """重新开始游戏"""
        self.snake = [(10, 15)]
        self.direction = Vector(1, 0)
        self.next_direction = Vector(1, 0)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        
        # 清理蛇身图形
        for rect in self.body_parts:
            self.canvas.remove(rect)
        self.body_parts.clear()
        
        # 重新添加蛇头和蛇身
        with self.canvas:
            Color(0, 1, 0, 1)
            self.head.pos = self.get_pixel_pos(self.snake[0])
            
            Color(0, 0, 1, 1)
            for segment in self.snake[1:]:
                rect = Rectangle(pos=self.get_pixel_pos(segment), 
                               size=(self.grid_size, self.grid_size))
                self.body_parts.append(rect)
            
            Color(1, 0, 0, 1)
            self.food_rect.pos = self.get_pixel_pos(self.food)

class SnakeGameApp(App):
    def __init__(self, **kwargs):
        super(SnakeGameApp, self).__init__(**kwargs)
        self.title = "贪吃蛇游戏"
    
    def build(self):
        # 主布局
        main_layout = BoxLayout(orientation='vertical')
        
        # 分数标签
        self.score_label = Label(text='分数: 0', size_hint_y=0.1, font_size='20sp')
        main_layout.add_widget(self.score_label)
        
        # 游戏区域
        self.game_widget = GameWidget(size_hint_y=0.8)
        main_layout.add_widget(self.game_widget)
        
        # 控制按钮
        control_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        pause_btn = Button(text='暂停', size_hint_x=0.3)
        restart_btn = Button(text='重开', size_hint_x=0.3)
        score_btn = Button(text='分数', size_hint_x=0.3)
        
        control_layout.add_widget(pause_btn)
        control_layout.add_widget(restart_btn)
        control_layout.add_widget(score_btn)
        
        main_layout.add_widget(control_layout)
        
        # 绑定按钮事件
        def toggle_pause(instance):
            if hasattr(self.game_widget, 'game_clock'):
                if self.game_widget.game_clock.is_triggered:
                    self.game_widget.game_clock.cancel()
                    pause_btn.text = '继续'
                else:
                    self.game_widget.game_clock = Clock.schedule_interval(
                        self.game_widget.update, 0.2)
                    pause_btn.text = '暂停'
        
        def restart_game(instance):
            self.game_widget.restart()
            self.score_label.text = '分数: 0'
        
        def show_score(instance):
            popup = Popup(title='当前分数', 
                         content=Label(text=f'当前分数: {self.game_widget.score}', 
                                     font_size='20sp'),
                         size_hint=(0.6, 0.4))
            popup.open()
        
        pause_btn.bind(on_press=toggle_pause)
        restart_btn.bind(on_press=restart_game)
        score_btn.bind(on_press=show_score)
        
        # 更新分数显示
        def update_score(dt):
            self.score_label.text = f'分数: {self.game_widget.score}'
        
        Clock.schedule_interval(update_score, 0.1)
        
        return main_layout

def main():
    SnakeGameApp().run()

if __name__ == '__main__':
    main()
''')

# 3. 创建buildozer.spec配置文件
with open('buildozer.spec', 'w', encoding='utf-8') as f:
    f.write('''[app]

# (str) Title of your application
title = 贪吃蛇游戏

# (str) Package name
package.name = snakegame

# (str) Package domain (needed for android/ios packaging)
package.domain = com.snakegame.app

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
requirements = python3,kivy

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
''')

# 4. 构建APK
import os
os.environ['ANDROID_API'] = '31'
os.environ['ANDROID_MINAPI'] = '21'
os.environ['ANDROID_NDK'] = '23b'

!buildozer android debug

# 5. 显示构建结果
from google.colab import files
import os

if os.path.exists('bin'):
    apks = [f for f in os.listdir('bin') if f.endswith('.apk')]
    if apks:
        print(f"构建成功！找到APK文件: {apks[0]}")
        print("正在下载APK文件...")
        files.download(f'bin/{apks[0]}')
    else:
        print("构建失败，未找到APK文件")
else:
    print("构建失败，未找到bin目录")