import pygame


class Animator:
    def __init__(self, sprite_sheet, animation_data):
        self.sprite_sheet = sprite_sheet
        self.frames = []
        self.durations = []
        self.total_time = 0
        self.current_time = 0
        self.current_frame = 0

        # Parse frames from JSON
        for frame_name, frame_data in animation_data["frames"].items():
            frame_rect = pygame.Rect(
                frame_data["frame"]["x"],
                frame_data["frame"]["y"],
                frame_data["frame"]["w"],
                frame_data["frame"]["h"],
            )
            self.frames.append(frame_rect)
            self.durations.append(frame_data["duration"])
            self.total_time += frame_data["duration"]

    def update(self, dt):
        """Update the animation frame based on elapsed time."""
        self.current_time += dt
        while self.current_time >= self.durations[self.current_frame]:
            self.current_time -= self.durations[self.current_frame]
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def get_current_frame(self):
        """Return the current frame's rectangle."""
        return self.frames[self.current_frame]
