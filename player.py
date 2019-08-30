#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygame import *
from pygame.transform import scale

MOVE_SPEED = 7
WIDTH = 32
HEIGHT = 52
COLOR = "#888888"


class Player(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.xvel = 0  # скорость перемещения. 0 - стоять на месте
        self.startX = x  # Начальная позиция Х, пригодится когда будем переигрывать уровень
        self.startY = y
        self.rect = Rect(x, y, WIDTH, HEIGHT)  # прямоугольный объект
        self.images = {}
        for t in ['up', 'down', 'left', 'right']:
            self.images[t] = []
            for i in range(3):
                self.images[t].append(scale(image.load(f"player/{t}{i}.png"), (32,52)))
        self.index = 0
        self.image = self.images['down'][1]

    def load(self, server_stats):
        sprite.Sprite.__init__(self)
        self.xvel = server_stats['xvel']
        self.yvel = server_stats['yvel']
        self.rect = Rect(server_stats['x'], server_stats['y'], WIDTH, HEIGHT)  # прямоугольный объект
        self.index = server_stats['index']
        self.image = self.images['down'][1]

        if self.xvel > 0:
            self.image = self.images['right'][self.index]
        if self.xvel < 0:
            self.image = self.images['left'][self.index]
        if self.yvel < 0:
            self.image = self.images['up'][self.index]
        if self.yvel > 0:
            self.image = self.images['down'][self.index]

    def update(self, left, right, up, down, platforms):
        if up:
            self.yvel = -MOVE_SPEED  # Лево = x- n
            self.image = self.images['up'][self.index]

        if down:
            self.yvel = MOVE_SPEED  # Право = x + n
            self.image = self.images['down'][self.index]


        if left:
            self.xvel = -MOVE_SPEED  # Лево = x- n
            self.image = self.images['left'][self.index]

        if right:
            self.xvel = MOVE_SPEED  # Право = x + n
            self.image = self.images['right'][self.index]


        if not (left or right):  # стоим, когда нет указаний идти
            self.xvel = 0

        if not (up or down):  # стоим, когда нет указаний идти
            self.yvel = 0

        if not (up or down or left or right):
            self.image = self.images['down'][1]
        else:
            self.index = (self.index + 1) % 3
        self.collide(platforms)

        self.rect.x += self.xvel  # переносим свои положение на xvel
        self.rect.y += self.yvel  # переносим свои положение на xvel





    def collide(self, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p):  # если есть пересечение платформы с игроком
                if self.xvel < 0 and self.rect.left < p.rect.right and self.rect.right > p.rect.right:  # если движется вправо
                    self.xvel = 0

                if self.xvel > 0 and self.rect.right > p.rect.left and self.rect.left < p.rect.left:  # если движется вправо
                    self.xvel = 0

                if self.yvel < 0 and self.rect.top < p.rect.bottom and self.rect.bottom > p.rect.bottom:  # если движется вправо
                    self.yvel = 0

                if self.yvel > 0 and self.rect.bottom > p.rect.top and self.rect.top < p.rect.top:  # если движется вправо
                    self.yvel = 0