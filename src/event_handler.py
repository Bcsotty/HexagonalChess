import pygame
from piece import Piece
from pygame.locals import *


class EventHandler:
    def __init__(self, event_type: int, subscribers: list[object]):
        self.event_type = event_type
        self.subscribers = subscribers

    def add_subscriber(self, subscriber: object):
        self.subscribers.append(subscriber)

    def remove_subscriber(self, subscriber: object):
        self.subscribers.remove(subscriber)

    def event_triggered(self, event: pygame.event.Event):
        for subscriber in self.subscribers:
            if event.type == MOUSEBUTTONDOWN:
                subscriber.mouse_button_down_handler(event)
            elif event.type == MOUSEBUTTONUP:
                subscriber.mouse_button_up_handler(event)
            elif event.type == KEYDOWN:
                subscriber.key_pressed_handler(event)
