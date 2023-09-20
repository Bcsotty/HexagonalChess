import pygame
from piece import Piece
from pygame.locals import *
from time import time


class EventHandler:
    def __init__(self, event_type: int, subscribers: list[object], debounce_intervals=None):
        if debounce_intervals is None:
            debounce_intervals = []

        self.event_type = event_type
        self.subscribers = subscribers
        self.last_triggered = 0
        self.debounce_intervals = debounce_intervals

    def add_subscriber(self, subscriber: object, debounce_interval=0.):
        self.subscribers.append(subscriber)
        self.debounce_intervals.append(debounce_interval)

    def remove_subscriber(self, subscriber: object):
        self.subscribers.remove(subscriber)

    def event_triggered(self, event: pygame.event.Event):
        triggered_time = time()

        for i, subscriber in enumerate(self.subscribers):
            if triggered_time - self.last_triggered < self.debounce_intervals[i]:
                continue

            if event.type == MOUSEBUTTONDOWN:
                subscriber.mouse_button_down_handler(event)
            elif event.type == MOUSEBUTTONUP:
                subscriber.mouse_button_up_handler(event)
            elif event.type == KEYDOWN:
                subscriber.key_pressed_handler(event)

        self.last_triggered = triggered_time
