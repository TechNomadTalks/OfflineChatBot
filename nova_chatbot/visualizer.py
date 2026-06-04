"""
3D Circular Dust Visualizer for Nova Chatbot.
A PyGame overlay window showing orange dust particles with audio-reactive animation.
"""

import os
import sys
import math
import random
import threading
import time

try:
    import pygame
    pygame_AVAILABLE = True
except ImportError:
    pygame_AVAILABLE = False


class Particle:
    """Individual dust particle with orbital motion."""
    
    def __init__(self, center_x, center_y, rng):
        self.center_x = center_x
        self.center_y = center_y
        self.orbit_radius = rng.gauss(150, 50)
        self.orbit_radius = max(30, min(250, self.orbit_radius))
        self.angle = rng.uniform(0, 2 * math.pi)
        self.angular_velocity = rng.uniform(0.01, 0.05)
        self.z_offset = rng.uniform(-0.5, 0.5)
        self.size = rng.uniform(1, 4)
        self.base_color = (
            int(255 - rng.uniform(0, 55)),
            int(107 + rng.uniform(0, 49)),
            0
        )
        self.target_radius = self.orbit_radius
    
    def update(self, activity_level, dt):
        if activity_level > 0:
            self.angle += self.angular_velocity * (1 + activity_level * 2)
        self.orbit_radius += (self.target_radius - self.orbit_radius) * 0.05
        self.orbit_radius += activity_level * 30 * dt
    
    def get_position(self):
        x = self.center_x + self.orbit_radius * math.cos(self.angle) * (1 + self.z_offset * 0.3)
        y = self.center_y + self.orbit_radius * math.sin(self.angle) * (1 + self.z_offset * 0.3)
        return x, y
    
    def get_brightness(self, activity_level):
        base_brightness = 0.3 + self.z_offset * 0.15
        activity_brightness = 1.0 + activity_level * 0.7
        return min(1.0, base_brightness * activity_brightness)


class DustVisualizer:
    """Main PyGame window and particle system."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.screen = None
        self.clock = None
        self.running = False
        self.thread = None
        self.activity_level = 0.0
        self.target_activity = 0.0
        self.username = "User"
        self.particles = []
        self.particle_count = 250
        self.font = None
        self.text_surface = None
        self._activity_lock = threading.Lock()
        self._initialized = True
    
    def start(self, username="User"):
        if not pygame_AVAILABLE:
            print("[Visualizer] PyGame not available")
            return
        
        if self.running or (self.thread and self.thread.is_alive()):
            return
        
        self.username = username
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.thread = None
        if pygame_AVAILABLE and self.screen:
            try:
                pygame.display.quit()
                pygame.quit()
            except:
                pass
        self.screen = None
        self.clock = None
        self.activity_level = 0.0
        self.target_activity = 0.0
        self.font = None
        self.text_surface = None
    
    def set_activity(self, level):
        with self._activity_lock:
            self.target_activity = max(0.0, min(1.0, level))
    
    def update_text(self, text):
        self.username = text
        self._render_text()
    
    def _run(self):
        try:
            pygame.init()
            pygame.display.init()
            
            self.screen = pygame.display.set_mode((600, 600), pygame.NOFRAME)
            pygame.display.set_caption("Nova Visualizer")
            pygame.display.set_allow_screensaver(False)
            
            try:
                import ctypes
                from ctypes import wintypes
                hwnd = pygame.display.get_wm_info()['window']
                HWND_TOPMOST = -1
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
            except Exception:
                pass
            
            self.clock = pygame.time.Clock()
            self._init_particles()
            self._render_text()
            
            self.running = True
            last_time = time.time()
            
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time
                
                if dt <= 0 or dt > 1:
                    dt = 0.016
                
                with self._activity_lock:
                    self.activity_level += (self.target_activity - self.activity_level) * 5 * dt
                    self.activity_level = max(0.0, min(1.0, self.activity_level))
                
                self._update_particles(dt)
                self._draw()
                
                pygame.display.flip()
                self.clock.tick(60)
            
            pygame.quit()
        except Exception as e:
            print(f"[Visualizer] Error: {e}")
            self.running = False
            try:
                pygame.quit()
            except:
                pass
    
    def _init_particles(self):
        rng = random.Random(42)
        center_x, center_y = 300, 300
        self.particles = [Particle(center_x, center_y, rng) for _ in range(self.particle_count)]
    
    def _update_particles(self, dt):
        for p in self.particles:
            p.update(self.activity_level, dt)
    
    def _render_text(self):
        if not pygame_AVAILABLE or not pygame.font:
            return
        try:
            self.font = pygame.font.SysFont('segoeui', 36, bold=True)
            text = f"Welcome {self.username}"
            surface = self.font.render(text, True, (255, 107, 0))
            self.text_surface = surface
        except:
            pass
    
    def _draw(self):
        if not self.screen:
            return
        
        self.screen.fill((0, 0, 0))
        
        for p in self.particles:
            x, y = p.get_position()
            px, py = int(x), int(y)
            
            if 0 <= px < 600 and 0 <= py < 600:
                brightness = p.get_brightness(self.activity_level)
                color = (
                    int(p.base_color[0] * brightness),
                    int(p.base_color[1] * brightness),
                    0
                )
                size = max(1, int(p.size * (1 + self.activity_level * 0.5)))
                pygame.draw.circle(self.screen, color, (px, py), size)
        
        if self.text_surface:
            x = (600 - self.text_surface.get_width()) // 2
            self.screen.blit(self.text_surface, (x, 30))


_visualizer = None


def start_visualizer(username="User"):
    global _visualizer
    if not pygame_AVAILABLE:
        print("[Visualizer] PyGame not available, skipping")
        return
    
    try:
        _visualizer = DustVisualizer()
        _visualizer.start(username)
    except Exception as e:
        print(f"[Visualizer] Failed to start: {e}")


def stop_visualizer():
    global _visualizer
    if _visualizer:
        _visualizer.stop()
        _visualizer = None


def set_visualizer_activity(level):
    global _visualizer
    if _visualizer:
        _visualizer.set_activity(level)


def is_visualizer_available():
    return pygame_AVAILABLE