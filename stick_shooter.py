import pygame # type: ignore
import math
import random
import os

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("火柴人射击游戏")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Weapon:
    def __init__(self, name, damage, fire_rate, bullet_speed, color, model_type):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
        self.bullet_speed = bullet_speed
        self.color = color
        self.model_type = model_type  # 武器模型类型
        self.last_shot = 0
    
    def draw(self, surface, x, y, angle):
        if self.model_type == "pistol":
            # 手枪：短管
            end_x = x + math.cos(angle) * 30
            end_y = y + math.sin(angle) * 30
            pygame.draw.line(surface, self.color, (x, y), (end_x, end_y), 4)
            
        elif self.model_type == "smg":
            # 冲锋枪：短管+弹夹
            end_x = x + math.cos(angle) * 35
            end_y = y + math.sin(angle) * 35
            pygame.draw.line(surface, self.color, (x, y), (end_x, end_y), 4)
            # 弹夹
            mag_x = x + math.cos(angle + math.pi/2) * 8
            mag_y = y + math.sin(angle + math.pi/2) * 8
            pygame.draw.line(surface, self.color, (mag_x, mag_y), 
                           (mag_x + math.cos(angle + math.pi/2) * 12, 
                            mag_y + math.sin(angle + math.pi/2) * 12), 4)
            
        elif self.model_type == "rifle":
            # 步枪：长管+握把
            end_x = x + math.cos(angle) * 45
            end_y = y + math.sin(angle) * 45
            pygame.draw.line(surface, self.color, (x, y), (end_x, end_y), 4)
            # 握把
            grip_x = x + math.cos(angle) * 15
            grip_y = y + math.sin(angle) * 15
            pygame.draw.line(surface, self.color, 
                           (grip_x, grip_y),
                           (grip_x + math.cos(angle + math.pi/2) * 15, 
                            grip_y + math.sin(angle + math.pi/2) * 15), 3)
            
        elif self.model_type == "sniper":
            # 狙击枪：超长管+瞄准镜
            end_x = x + math.cos(angle) * 55
            end_y = y + math.sin(angle) * 55
            pygame.draw.line(surface, self.color, (x, y), (end_x, end_y), 4)
            # 瞄准镜
            scope_x = x + math.cos(angle) * 20
            scope_y = y + math.sin(angle) * 20
            pygame.draw.circle(surface, self.color, 
                             (int(scope_x), int(scope_y)), 5)
            
        elif self.model_type == "shotgun":
            # 霰弹枪：双管
            end_x = x + math.cos(angle) * 40
            end_y = y + math.sin(angle) * 40
            offset = 3
            # 上管
            pygame.draw.line(surface, self.color,
                           (x + math.cos(angle + math.pi/2) * offset,
                            y + math.sin(angle + math.pi/2) * offset),
                           (end_x + math.cos(angle + math.pi/2) * offset,
                            end_y + math.sin(angle + math.pi/2) * offset), 3)
            # 下管
            pygame.draw.line(surface, self.color,
                           (x - math.cos(angle + math.pi/2) * offset,
                            y - math.sin(angle + math.pi/2) * offset),
                           (end_x - math.cos(angle + math.pi/2) * offset,
                            end_y - math.sin(angle + math.pi/2) * offset), 3)

class WeaponDrop:
    def __init__(self, x, y, weapon):
        self.x = x
        self.y = y
        self.weapon = weapon
        self.hover = False  # 添加鼠标悬停状态
        
    def draw(self, surface):
        # 武器掉落显示
        radius = 10 if self.hover else 8  # 悬停时略微放大
        pygame.draw.circle(surface, self.weapon.color, (int(self.x), int(self.y)), radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), radius, 1)
        # 添加小型武器图标
        self.weapon.draw(surface, self.x, self.y, 0)
        
        # 如果鼠标悬停，显示武器名称
        if self.hover:
            font = pygame.font.Font(None, 24)
            text = font.render(f"点击拾取: {self.weapon.name}", True, BLACK)
            surface.blit(text, (self.x - 50, self.y - 30))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.health = 200
        self.score = 0
        self.speed = 5
        self.max_speed = 8
        self.acceleration = 0.5
        self.deceleration = 0.3
        self.velocity_x = 0
        self.velocity_y = 0
        self.diagonal_factor = 0.7071  # 1/√2，用于对角线移动速度修正
        # 定义所有可能的武器
        self.weapons = [WEAPONS[0]]  # 开始只有手枪
        self.current_weapon = 0
        self.max_health = 200
        self.armor = 0
        self.max_armor = 100
    
    def add_weapon(self, weapon):
        if not any(w.name == weapon.name for w in self.weapons):
            self.weapons.append(weapon)
            self.current_weapon = len(self.weapons) - 1

    def draw(self, surface):
        # 修改血条显示
        health_width = 200  # 血条宽度
        health_percentage = self.health / self.max_health
        pygame.draw.rect(surface, (100, 100, 100), (10, 10, health_width, 20))  # 血条背景
        pygame.draw.rect(surface, RED, (10, 10, health_width * health_percentage, 20))  # 当前血量
        
        # 绘制火柴人
        pygame.draw.circle(surface, BLACK, (self.x, self.y), 20)  # 头
        pygame.draw.line(surface, BLACK, (self.x, self.y + 20), (self.x, self.y + 60), 2)  # 身体
        pygame.draw.line(surface, BLACK, (self.x, self.y + 60), (self.x - 20, self.y + 100), 2)  # 左腿
        pygame.draw.line(surface, BLACK, (self.x, self.y + 60), (self.x + 20, self.y + 100), 2)  # 右腿
        
        # 画手臂
        arm_end_x = self.x + math.cos(self.angle) * 30
        arm_end_y = self.y + math.sin(self.angle) * 30
        pygame.draw.line(surface, BLACK, (self.x, self.y + 30), (arm_end_x, arm_end_y), 2)
        
        # 绘制当前武器
        current_weapon = self.weapons[self.current_weapon]
        current_weapon.draw(surface, arm_end_x, arm_end_y, self.angle)
        
        # 绘制护甲条
        if self.armor > 0:
            armor_width = 200
            armor_percentage = self.armor / self.max_armor
            pygame.draw.rect(surface, (100, 100, 100), (10, 35, armor_width, 10))
            pygame.draw.rect(surface, BLUE, (10, 35, armor_width * armor_percentage, 10))

    def move(self, keys):
        # 计算目标速度
        target_vel_x = 0
        target_vel_y = 0
        
        if keys[pygame.K_a]: target_vel_x -= self.max_speed
        if keys[pygame.K_d]: target_vel_x += self.max_speed
        if keys[pygame.K_w]: target_vel_y -= self.max_speed
        if keys[pygame.K_s]: target_vel_y += self.max_speed
        
        # 对角线移动速度修正
        if target_vel_x != 0 and target_vel_y != 0:
            target_vel_x *= self.diagonal_factor
            target_vel_y *= self.diagonal_factor
        
        # X轴速度渐变
        if target_vel_x != 0:
            # 加速
            if abs(self.velocity_x - target_vel_x) > self.acceleration:
                self.velocity_x += self.acceleration if target_vel_x > self.velocity_x else -self.acceleration
        else:
            # 减速
            if abs(self.velocity_x) > self.deceleration:
                self.velocity_x -= self.deceleration if self.velocity_x > 0 else -self.deceleration
            else:
                self.velocity_x = 0
        
        # Y轴速度渐变
        if target_vel_y != 0:
            # 加速
            if abs(self.velocity_y - target_vel_y) > self.acceleration:
                self.velocity_y += self.acceleration if target_vel_y > self.velocity_y else -self.acceleration
        else:
            # 减速
            if abs(self.velocity_y) > self.deceleration:
                self.velocity_y -= self.deceleration if self.velocity_y > 0 else -self.deceleration
            else:
                self.velocity_y = 0
        
        # 更新位置
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # 边界检查
        self.x = max(20, min(self.x, 780))
        self.y = max(20, min(self.y, 580))
        
        # 碰到边界时停止相应方向的速度
        if self.x <= 20 or self.x >= 780:
            self.velocity_x = 0
        if self.y <= 20 or self.y >= 580:
            self.velocity_y = 0

class Enemy:
    def __init__(self):
        # 随机生成敌人位置（在屏幕边缘）
        side = random.randint(0, 3)
        if side == 0:  # 上
            self.x = random.randint(0, 800)
            self.y = 0
        elif side == 1:  # 右
            self.x = 800
            self.y = random.randint(0, 600)
        elif side == 2:  # 下
            self.x = random.randint(0, 800)
            self.y = 600
        else:  # 左
            self.x = 0
            self.y = random.randint(0, 600)
        
        self.speed = 1.5
        self.health = 25
        self.damage = 5
        
    def move(self, target_x, target_y):
        angle = math.atan2(target_y - self.y, target_x - self.x)
        angle += random.uniform(-0.2, 0.2)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed
        
    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), 15)
        # 调整敌人血条显示
        health_percentage = self.health / 25  # 基于新的最大血量
        pygame.draw.rect(surface, GREEN, 
                        (self.x - 15, self.y - 25, 
                         30 * health_percentage, 5))

class Bullet:
    def __init__(self, x, y, angle, weapon):
        self.x = x
        self.y = y
        self.angle = angle
        self.weapon = weapon
        
    def draw(self, surface):
        # 根据武器类型绘制不同的子弹效果
        if self.weapon.model_type == "pistol":
            # 手枪：小圆形子弹
            pygame.draw.circle(surface, self.weapon.color, (int(self.x), int(self.y)), 3)
            
        elif self.weapon.model_type == "smg":
            # 冲锋枪：小而快的椭圆形子弹
            pygame.draw.ellipse(surface, self.weapon.color, 
                              (self.x - 4, self.y - 2, 8, 4))
            
        elif self.weapon.model_type == "rifle":
            # 步枪：较大的圆形子弹带尾迹
            pygame.draw.circle(surface, self.weapon.color, (int(self.x), int(self.y)), 4)
            # 尾迹效果
            tail_x = self.x - math.cos(self.angle) * 8
            tail_y = self.y - math.sin(self.angle) * 8
            pygame.draw.line(surface, self.weapon.color, 
                           (int(self.x), int(self.y)), 
                           (int(tail_x), int(tail_y)), 2)
            
        elif self.weapon.model_type == "sniper":
            # 狙击枪：大型穿透性子弹
            pygame.draw.circle(surface, self.weapon.color, (int(self.x), int(self.y)), 5)
            # 发光效果
            pygame.draw.circle(surface, (255, 255, 255), 
                             (int(self.x), int(self.y)), 3)
            # 长尾迹
            tail_x = self.x - math.cos(self.angle) * 12
            tail_y = self.y - math.sin(self.angle) * 12
            pygame.draw.line(surface, self.weapon.color, 
                           (int(self.x), int(self.y)), 
                           (int(tail_x), int(tail_y)), 3)
            
        elif self.weapon.model_type == "shotgun":
            # 霰弹枪：多个小型粒子
            for i in range(3):
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
                pygame.draw.circle(surface, self.weapon.color, 
                                 (int(self.x + offset_x), 
                                  int(self.y + offset_y)), 2)
    
    def move(self):
        self.x += math.cos(self.angle) * self.weapon.bullet_speed
        self.y += math.sin(self.angle) * self.weapon.bullet_speed

class Boss(Enemy):
    def __init__(self):
        super().__init__()
        self.health = 1000
        self.max_health = 1000
        self.speed = 1.0
        self.damage = 20
        self.color = (150, 0, 0)
        self.last_attack = 0
        self.attack_delay = 2000
        self.rage_mode = False
        self.last_phase_change = pygame.time.get_ticks()
        self.phase_change_delay = 1000
        # 移动相关属性
        self.movement_timer = pygame.time.get_ticks()
        self.movement_delay = 1500
        self.target_x = random.randint(100, 700)
        self.target_y = random.randint(100, 500)
        self.min_distance = 150
        self.max_distance = 400
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.2
        self.max_velocity = 3.0
        # Boss投射物相关
        self.projectiles = []

    def update_phase(self):
        # 根据血量百分比更新阶段
        health_percent = self.health / self.max_health
        current_time = pygame.time.get_ticks()
        
        # 只在阶段改变时更新
        if current_time - self.last_phase_change > self.phase_change_delay:
            if health_percent <= 0.2 and self.phase < 4:
                self.phase = 4
                self.color = (255, 50, 50)
                self.speed = 2.5
                self.attack_delay = 800
                self.rage_mode = True
                self.last_phase_change = current_time
            elif health_percent <= 0.4 and self.phase < 3:
                self.phase = 3
                self.color = (255, 0, 0)
                self.speed = 2.0
                self.attack_delay = 1000
                self.rage_mode = True
                self.last_phase_change = current_time
            elif health_percent <= 0.7 and self.phase < 2:
                self.phase = 2
                self.color = (200, 0, 0)
                self.speed = 1.5
                self.attack_delay = 1500
                self.last_phase_change = current_time

    def draw(self, surface):
        # 绘制Boss本体
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        
        # 绘制血条
        health_percentage = self.health / self.max_health
        health_bar_width = 80
        health_bar_height = 8
        health_bar_x = self.x - health_bar_width // 2
        health_bar_y = self.y - self.size - 20
        
        # 血条背景
        pygame.draw.rect(surface, (100, 100, 100),
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        # 当前血量
        pygame.draw.rect(surface, self.color,
                        (health_bar_x, health_bar_y,
                         health_bar_width * health_percentage, health_bar_height))

    def attack(self, target_x, target_y, current_time):
        projectiles = []
        if current_time - self.last_attack > self.attack_delay:
            if self.phase == 1:
                # 第一阶段：单发直线攻击
                projectiles.append(BossProjectile(self.x, self.y, target_x, target_y))
            elif self.phase == 2:
                # 第二阶段：三发散射
                for angle_offset in [-0.3, 0, 0.3]:
                    angle = math.atan2(target_y - self.y, target_x - self.x) + angle_offset
                    proj = BossProjectile(self.x, self.y, 
                                        self.x + math.cos(angle) * 100,
                                        self.y + math.sin(angle) * 100)
                    projectiles.append(proj)
            elif self.phase == 3:
                # 第三阶段：环形弹幕
                for i in range(8):
                    angle = (i * math.pi / 4) + (current_time / 1000)
                    proj = BossProjectile(self.x, self.y,
                                        self.x + math.cos(angle) * 100,
                                        self.y + math.sin(angle) * 100)
                    projectiles.append(proj)
            else:
                # 第四阶段：混合攻击模式
                for i in range(12):
                    angle = (i * math.pi / 6) + (current_time / 800)
                    proj = BossProjectile(self.x, self.y,
                                        self.x + math.cos(angle) * 100,
                                        self.y + math.sin(angle) * 100)
                    proj.damage = 15
                    projectiles.append(proj)
                
                angle = math.atan2(target_y - self.y, target_x - self.x)
                for offset in [-0.2, 0, 0.2]:
                    proj = BossProjectile(self.x, self.y, 
                                        target_x + math.cos(angle + offset) * 50,
                                        target_y + math.sin(angle + offset) * 50)
                    proj.damage = 20
                    projectiles.append(proj)
            
            self.last_attack = current_time
        return projectiles

class BossProjectile:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        angle = math.atan2(target_y - y, target_x - x)
        self.speed = 4
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.damage = 10
        
    def move(self):
        self.x += self.vx
        self.y += self.vy
        
    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), 8)
        pygame.draw.circle(surface, (150, 0, 0), (int(self.x), int(self.y)), 8, 2)

class HealthPack:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.heal_amount = 50
        self.hover = False
    
    def draw(self, surface):
        size = 15 if self.hover else 12
        # 红十字医疗包
        pygame.draw.rect(surface, WHITE, (self.x - size, self.y - size, size*2, size*2))
        pygame.draw.rect(surface, RED, (self.x - size + 2, self.y - size + 2, size*2 - 4, size*2 - 4))
        pygame.draw.rect(surface, RED, (self.x - size//3, self.y - size*2//3, size*2//3, size*4//3))
        pygame.draw.rect(surface, RED, (self.x - size*2//3, self.y - size//3, size*4//3, size*2//3))

class ArmorPack:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.armor_amount = 50
        self.hover = False
    
    def draw(self, surface):
        size = 15 if self.hover else 12
        # 蓝色盾牌形状
        pygame.draw.polygon(surface, (0, 100, 255),
                          [(self.x, self.y - size),
                           (self.x + size, self.y),
                           (self.x, self.y + size),
                           (self.x - size, self.y)])
        pygame.draw.polygon(surface, BLUE,
                          [(self.x, self.y - size + 4),
                           (self.x + size - 4, self.y),
                           (self.x, self.y + size - 4),
                           (self.x - size + 4, self.y)])

# 在主游戏代码开头添加武器定义
WEAPONS = [
    Weapon("手枪", 10, 500, 10, RED, "pistol"),
    Weapon("冲锋枪", 8, 100, 12, (255, 165, 0), "smg"),
    Weapon("步枪", 20, 200, 15, BLUE, "rifle"),
    Weapon("狙击枪", 50, 1000, 8, GREEN, "sniper"),
    Weapon("霰弹枪", 15, 800, 7, (128, 0, 128), "shotgun")
]

# 在主游戏循环前初始化武器掉落列表
weapon_drops = []

# 在主游戏循环前添加敌人生成控制参数
ENEMY_SPAWN_DELAY = 3000  # 敌人生成间隔（毫秒）
MAX_ENEMIES = 8  # 场上最大敌人数量
enemy_spawn_timer = 0

# 在主游戏循环前添加
boss_projectiles = []
BOSS_SPAWN_CHANCE = 0.25  # 调整为25%概率生成Boss
MIN_SCORE_FOR_BOSS = 60   # 保持当前的分数要求

# 在主游戏循环前添加
health_packs = []
armor_packs = []
ITEM_SPAWN_DELAY = 10000  # 物品生成间隔（毫秒）
item_spawn_timer = 0

# 初始化游戏对象
player = Player(400, 300)
enemies = []
bullets = []
font = pygame.font.Font(None, 36)

# 背景类
class Background:
    def __init__(self):
        # 创建网格背景
        self.grid_size = 50
        self.grid_color = (230, 230, 230)
        self.bg_color = (245, 245, 245)
        
        # 创建装饰元素
        self.decorations = []
        for _ in range(20):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            size = random.randint(5, 15)
            self.decorations.append({
                'x': x,
                'y': y,
                'size': size,
                'color': (220, 220, 220)
            })
    
    def draw(self, surface):
        # 填充基础背景色
        surface.fill(self.bg_color)
        
        # 绘制网格
        for x in range(0, 800, self.grid_size):
            pygame.draw.line(surface, self.grid_color, (x, 0), (x, 600), 1)
        for y in range(0, 600, self.grid_size):
            pygame.draw.line(surface, self.grid_color, (0, y), (800, y), 1)
        
        # 绘制装饰元素
        for dec in self.decorations:
            pygame.draw.circle(surface, dec['color'], 
                             (dec['x'], dec['y']), dec['size'])

# 在主游戏循环前初始化背景
background = Background()

running = True
clock = pygame.time.Clock()

while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键射击
                # 射击逻辑...
                weapon = player.weapons[player.current_weapon]
                if current_time - weapon.last_shot >= weapon.fire_rate:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    angle = math.atan2(mouse_y - player.y, mouse_x - player.x)
                    bullets.append(Bullet(player.x, player.y, angle, weapon))
                    weapon.last_shot = current_time
            elif event.button == 3:  # 右键拾取
                # 拾取物品和武器
                for pack in health_packs[:]:
                    if math.hypot(mouse_x - pack.x, mouse_y - pack.y) < 20:
                        player.health = min(player.max_health, player.health + pack.heal_amount)
                        health_packs.remove(pack)
                
                for pack in armor_packs[:]:
                    if math.hypot(mouse_x - pack.x, mouse_y - pack.y) < 20:
                        player.armor = min(player.max_armor, player.armor + pack.armor_amount)
                        armor_packs.remove(pack)
                
                for drop in weapon_drops[:]:
                    if math.hypot(mouse_x - drop.x, mouse_y - drop.y) < 20:
                        player.add_weapon(drop.weapon)
                        weapon_drops.remove(drop)
        elif event.type == pygame.KEYDOWN:
            # 切换武器
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                player.current_weapon = event.key - pygame.K_1
    
    # 敌人生成逻辑
    if len(enemies) < MAX_ENEMIES and current_time - enemy_spawn_timer > ENEMY_SPAWN_DELAY:
        # 检查是否生成Boss
        if (player.score >= MIN_SCORE_FOR_BOSS and 
            random.random() < BOSS_SPAWN_CHANCE and 
            not any(isinstance(e, Boss) for e in enemies)):
            enemies.append(Boss())
            # Boss出现警告效果
            warning_font = pygame.font.Font(None, 72)
            for i in range(2):  # 减少闪烁次数到2次
                # 红色警告
                warning_text = warning_font.render("警告：Boss出现！", True, RED)
                screen.blit(warning_text, (250, 250))
                pygame.display.flip()
                pygame.time.wait(400)  # 稍微延长警告显示时间
                # 清除警告
                background.draw(screen)
                pygame.display.flip()
                pygame.time.wait(200)
        else:
            enemies.append(Enemy())
        enemy_spawn_timer = current_time
    
    # 在主游戏循环中更新Boss
    for enemy in enemies:
        if isinstance(enemy, Boss):
            enemy.update_phase()  # 更新Boss阶段
            new_projectiles = enemy.attack(player.x, player.y, current_time)
            boss_projectiles.extend(new_projectiles)
        enemy.move(player.x, player.y)
        enemy.draw(screen)
    
    # 更新Boss投射物
    for proj in boss_projectiles[:]:
        proj.move()
        # 检查与玩家的碰撞
        if math.hypot(proj.x - player.x, proj.y - player.y) < 25:
            damage = proj.damage
            
            # 先扣除护甲
            if player.armor > 0:
                armor_damage = min(damage, player.armor)
                player.armor -= armor_damage
                damage -= armor_damage
            
            # 剩余伤害扣除血量
            if damage > 0:
                player.health -= damage
                
            boss_projectiles.remove(proj)
        # 检查是否出界
        elif (proj.x < 0 or proj.x > 800 or 
              proj.y < 0 or proj.y > 600):
            boss_projectiles.remove(proj)
    
    # 更新玩家角度
    mouse_x, mouse_y = pygame.mouse.get_pos()
    player.angle = math.atan2(mouse_y - player.y, mouse_x - player.x)
    
    # 更新敌人
    for enemy in enemies[:]:
        enemy.move(player.x, player.y)
        # 检查与玩家的碰撞
        if math.hypot(enemy.x - player.x, enemy.y - player.y) < 35:
            damage = enemy.damage  # 获取敌人的伤害值
            
            # 先扣除护甲
            if player.armor > 0:
                armor_damage = min(damage, player.armor)  # 护甲可以抵消的伤害
                player.armor -= armor_damage
                damage -= armor_damage  # 剩余伤害
            
            # 如果还有剩余伤害，扣除血量
            if damage > 0:
                player.health -= damage
            
            enemies.remove(enemy)
            if player.health <= 0:
                running = False
    
    # 获取按键状态
    keys = pygame.key.get_pressed()
    player.move(keys)
    
    # 更新武器掉落物的悬停状态
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for drop in weapon_drops:
        drop.hover = math.hypot(mouse_x - drop.x, mouse_y - drop.y) < 20
    
    # 更新子弹
    for bullet in bullets[:]:
        bullet.move()
        # 检查子弹是否击中敌人
        for enemy in enemies[:]:
            if math.hypot(bullet.x - enemy.x, bullet.y - enemy.y) < 15:
                enemy.health -= bullet.weapon.damage
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    player.score += 10
                    
                    # Boss掉落特殊武器
                    if isinstance(enemy, Boss):
                        # Boss死亡时30%概率掉落特殊武器
                        if random.random() < 0.3:  # 降低掉落率到30%
                            special_weapons = [
                                Weapon("等离子枪", 30, 300, 15, (0, 255, 255), "rifle"),  # 青色等离子枪
                                Weapon("激光炮", 45, 800, 20, (255, 0, 255), "sniper"),   # 紫色激光炮
                                Weapon("火焰喷射器", 25, 150, 8, (255, 165, 0), "shotgun") # 橙色火焰喷射器
                            ]
                            boss_weapon = random.choice(special_weapons)
                            weapon_drops.append(WeaponDrop(enemy.x, enemy.y, boss_weapon))
                        # Boss必定掉落一个普通武器作为基础奖励
                        available_weapons = [w for w in WEAPONS if not any(pw.name == w.name for pw in player.weapons)]
                        if available_weapons:
                            weapon = random.choice(available_weapons)
                            weapon_drops.append(WeaponDrop(enemy.x, enemy.y, weapon))
                    else:
                        # 普通敌人30%概率掉落普通武器
                        if random.random() < 0.3:  # 降低普通敌人掉落率也到30%
                            available_weapons = [w for w in WEAPONS if not any(pw.name == w.name for pw in player.weapons)]
                            if available_weapons:
                                weapon = random.choice(available_weapons)
                                weapon_drops.append(WeaponDrop(enemy.x, enemy.y, weapon))
                bullets.remove(bullet)
                break
        # 检查子弹是否出界
        if bullet.x < 0 or bullet.x > 800 or bullet.y < 0 or bullet.y > 600:
            bullets.remove(bullet)
    
    # 生成物品
    if current_time - item_spawn_timer > ITEM_SPAWN_DELAY:
        if random.random() < 0.5 and len(health_packs) < 3:  # 限制最大数量
            x = random.randint(50, 750)
            y = random.randint(50, 550)
            health_packs.append(HealthPack(x, y))
        elif len(armor_packs) < 2:  # 限制最大数量
            x = random.randint(50, 750)
            y = random.randint(50, 550)
            armor_packs.append(ArmorPack(x, y))
        item_spawn_timer = current_time
    
    # 处理物品拾取
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # 更新物品悬停状态
    for pack in health_packs:
        pack.hover = math.hypot(mouse_x - pack.x, mouse_y - pack.y) < 20
    for pack in armor_packs:
        pack.hover = math.hypot(mouse_x - pack.x, mouse_y - pack.y) < 20
    
    # 绘制
    background.draw(screen)  # 首先绘制背景
    
    # 绘制游戏元素
    for pack in health_packs:  # 添加医疗包绘制
        pack.draw(screen)
    
    for pack in armor_packs:   # 添加护甲包绘制
        pack.draw(screen)
        
    for drop in weapon_drops:
        drop.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    for bullet in bullets:
        bullet.draw(screen)
    for proj in boss_projectiles:
        proj.draw(screen)
    player.draw(screen)
    
    # 绘制分数
    score_text = font.render(f"分数: {player.score}", True, BLACK)
    screen.blit(score_text, (650, 10))
    
    # 绘制当前武器
    weapon_text = font.render(f"武器: {player.weapons[player.current_weapon].name}", True, BLACK)
    screen.blit(weapon_text, (650, 50))
    
    pygame.display.flip()
    clock.tick(60)

# 游戏结束
game_over_text = font.render(f"游戏结束! 最终分数: {player.score}", True, BLACK)
screen.blit(game_over_text, (300, 250))
pygame.display.flip()
pygame.time.wait(2000)
pygame.quit()