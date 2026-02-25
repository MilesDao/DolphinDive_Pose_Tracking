import pygame
import sys
import random
import cv2
import numpy as np
from PoseDetector import PoseDetector

class PoseSmoother:
    def __init__(self, alpha=0.4):
        self.alpha = alpha
        self.smoothed_value_x = None
        self.smoothed_value_y = None

    def update(self, current_x, current_y):
        if self.smoothed_value_x is None:
            self.smoothed_value_x = current_x
            self.smoothed_value_y = current_y
        else:
            self.smoothed_value_x = (self.alpha * current_x) + ((1.0 - self.alpha) * self.smoothed_value_x)
            self.smoothed_value_y = (self.alpha * current_y) + ((1.0 - self.alpha) * self.smoothed_value_y)
        return int(self.smoothed_value_x), int(self.smoothed_value_y)


wCam, hCam = 640, 360

GAME_W, GAME_H = 432, 768

CAM_H = GAME_H
CAM_W = int(CAM_H * 16 / 9)

WINDOW_W = CAM_W + GAME_W
WINDOW_H = GAME_H

def play_flappy_bird():
    # --- CAMERA & POSE ---
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    detector = PoseDetector(model_path="runs/pose/train/weights/best.pt", use_gpu=True)

    # Initialize smoothers for the hand/arm keypoints
    left_smoother = PoseSmoother(alpha=0.5)
    right_smoother = PoseSmoother(alpha=0.5)

    arm_raised = False
    trigger_fly = False
    flap_count = 0

    # ------------ FLAPPY BIRD CORE ------------
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    game_surface = pygame.Surface((GAME_W, GAME_H))
    clock = pygame.time.Clock()
    game_font = pygame.font.Font('assets/font/04B_19.TTF', 35)


    gravity = 0.45
    bird_movement = 0
    game_active = True
    score = 0
    high_score = 0

    bg = pygame.image.load('assets/background_day.png').convert()
    bg = pygame.transform.smoothscale(bg, (GAME_W, GAME_H))

    floor = pygame.image.load('assets/floortemp.png').convert()
    floor = pygame.transform.scale2x(floor)
    floor_x_pos = 0

    bird_down = pygame.transform.scale2x(pygame.image.load(
        'assets/yellowbird-downflap.png').convert_alpha())
    bird_mid = pygame.transform.scale2x(pygame.image.load(
        'assets/yellowbird-midflap.png').convert_alpha())
    bird_up = pygame.transform.scale2x(pygame.image.load(
        'assets/yellowbird-upflap.png').convert_alpha())

    bird_list = [bird_down, bird_mid, bird_up]
    bird_index = 0
    bird = bird_list[bird_index]
    bird_rect = bird.get_rect(center=(100, 384))

    birdflap = pygame.USEREVENT + 1
    pygame.time.set_timer(birdflap, 200)

    pipe_surface = pygame.image.load('assets/pipe-green.png').convert()
    pipe_surface = pygame.transform.scale2x(pipe_surface)
    pipe_list = []
    scored_pipes = set()

    pipe_height = range(250, 500)
    last_pipe_time = pygame.time.get_ticks()
    PIPE_INTERVAL = 3000   

    game_over_surface = pygame.transform.scale2x(
        pygame.image.load('assets/messagetemp.png').convert_alpha())
    game_over_rect = game_over_surface.get_rect(center=(216, 384))

    flap_sound = pygame.mixer.Sound('assets/audio/sfx_wing.wav')
    hit_sound = pygame.mixer.Sound('assets/audio/sfx_hit.wav')
    score_sound = pygame.mixer.Sound('assets/audio/sfx_point.wav')
    score_sound_countdown = 100

    # ------------ GAME FUNCTIONS ------------
    def draw_floor():
        game_surface.blit(floor, (floor_x_pos, 650))
        game_surface.blit(floor, (floor_x_pos + 432, 650))

    def create_pipe():
        random_pipe_pos = random.choice(pipe_height)
        bottom_pipe = pipe_surface.get_rect(midtop=(500, random_pipe_pos))
        top_pipe = pipe_surface.get_rect(midbottom=(500, random_pipe_pos - 200))
        return bottom_pipe, top_pipe

    def move_pipe(pipes):
        pipes = [pipe for pipe in pipes if pipe.right > -50]
        for pipe in pipes:
            pipe.centerx -= 5 
        return pipes

    def draw_pipe(pipes):
        for pipe in pipes:
            if pipe.bottom >= 600:
                game_surface.blit(pipe_surface, pipe)
            else:
                flip_pipe = pygame.transform.flip(pipe_surface, False, True)
                game_surface.blit(flip_pipe, pipe)

    def pipe_score_check(pipes, bird_rect):
        nonlocal score, scored_pipes

        for pipe in pipes:
            # only count the bottom pipe
            if pipe.bottom >= 600:

                # bird has flown through the pipe
                if pipe.centerx < bird_rect.centerx:
                    pid = id(pipe)

                    if pid not in scored_pipes:
                        scored_pipes.add(pid)
                        score += 1
                        score_sound.play()

    def check_collision(pipes):
        for pipe in pipes:
            if bird_rect.colliderect(pipe):
                hit_sound.play()
                return False
        if bird_rect.top <= -75 or bird_rect.bottom >= 650:
            return False
        return True

    def perform_flap():
        nonlocal game_active, bird_movement, score, last_pipe_time
        if game_active:
            bird_movement = 0
            bird_movement = -10
            flap_sound.play()
        else:
            game_active = True
            pipe_list.clear()
            bird_rect.center = (100, 384)
            bird_movement = 0
            score = 0
            last_pipe_time = pygame.time.get_ticks()
            scored_pipes.clear()

    def rotate_bird(bird1):
        return pygame.transform.rotozoom(bird1, -bird_movement * 3, 1)

    def bird_animation():
        new_bird = bird_list[bird_index]
        new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery))
        return new_bird, new_bird_rect

    def score_display(game_state):
        if game_state == 'main game':
            score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(216, 100))
            game_surface.blit(score_surface, score_rect)
        if game_state == 'game_over':
            score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(216, 100))
            game_surface.blit(score_surface, score_rect)
            high_score_surface = game_font.render(
                f'High Score: {int(high_score)}', True, (255, 255, 255))
            high_score_rect = high_score_surface.get_rect(center=(216, 630))
            game_surface.blit(high_score_surface, high_score_rect)

    def update_score(score, high_score):
        return score if score > high_score else high_score

    # ------------ MAIN LOOP ------------
    try:
        while True:
            success, img = cap.read()
            img = cv2.flip(img, 1)
            if not success:
                break
            img = detector.findPose(img, draw=True)
            lmList = detector.findPosition(img, draw=False)


            if len(lmList) != 0:
                hand_ids = [5, 6, 7, 8] # shoulder, elbow
                
                # Apply smoothing to keypoints before using them
                smoothed_lmList = [list(item) for item in lmList] # deeply copy
                for i in range(len(lmList)):
                    if i in [5, 7]: # Left arm
                        if lmList[i][1] != 0:
                            sx, sy = left_smoother.update(lmList[i][1], lmList[i][2])
                            smoothed_lmList[i] = [lmList[i][0], sx, sy]
                    elif i in [6, 8]: # Right arm
                        if lmList[i][1] != 0:
                            sx, sy = right_smoother.update(lmList[i][1], lmList[i][2])
                            smoothed_lmList[i] = [lmList[i][0], sx, sy]
                
                # Overwrite original list with smoothed for calculation and drawing
                lmList = smoothed_lmList
                
                for fid in hand_ids:
                    if len(lmList) > fid and lmList[fid][1] != 0:
                        _, x, y = lmList[fid]
                        cv2.circle(img, (x, y), 8, (0, 128, 255), cv2.FILLED)  # orange
                        cv2.putText(img, str(fid), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

                # Connect left & right arm bones
                if len(lmList) > 8 and lmList[5][1] != 0 and lmList[7][1] != 0:
                    cv2.line(img, tuple(lmList[5][1:3]), tuple(lmList[7][1:3]), (0, 128, 255), 2)
                if len(lmList) > 8 and lmList[6][1] != 0 and lmList[8][1] != 0:
                    cv2.line(img, tuple(lmList[6][1:3]), tuple(lmList[8][1:3]), (0, 128, 255), 2)

                # --- HAND CONTROL ---
                angleRight = detector.findAngle(img, 8, 6, 12)
                angleLeft = detector.findAngle(img, 7, 5, 11)
                perRight = np.interp(angleRight, (30, 80), (0, 100))
                perLeft = np.interp(angleLeft, (30, 80), (0, 100))

                if perRight > 20 and perLeft > 20:
                    arm_raised = True
                elif perRight < 5 and perLeft < 5:
                    if arm_raised:
                        trigger_fly = True
                        arm_raised = False
                
                cv2.putText(img, f"L:{int(perLeft)} R:{int(perRight)}", 
                (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

                status = "FLAP!" if trigger_fly else "UP" if arm_raised else "READY"
                cv2.rectangle(img, (30, 150), (260, 25), (255, 255, 255), cv2.FILLED)
                cv2.putText(img, status, (40, 100),
                            cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 0, 0), 2)

            # cv2.imshow("hehe", img)
            # if cv2.waitKey(1) == ord("q"):
            #     break
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_rgb = np.transpose(img_rgb, (1, 0, 2))
            frame_surface = pygame.surfarray.make_surface(img_rgb)

            # --- PYGAME EVENTS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        perform_flap()

                if event.type == birdflap:
                    bird_index = (bird_index + 1) % 3
                    bird, bird_rect = bird_animation()
                    
            if trigger_fly:
                flap_count += 1
                perform_flap()
                trigger_fly = False

            # --- GAME LOGIC ---
            game_surface.blit(bg, (0, 0))

            if game_active:
                # Pipe spawning
                now = pygame.time.get_ticks()
                if now - last_pipe_time >= PIPE_INTERVAL:
                    pipe_list.extend(create_pipe())
                    last_pipe_time = now
                
                bird_movement += gravity  
                rotated_bird = rotate_bird(bird)
                bird_rect.centery += bird_movement
                game_surface.blit(rotated_bird, bird_rect)

                game_active = check_collision(pipe_list)
                pipe_list = move_pipe(pipe_list)
                draw_pipe(pipe_list)
                pipe_score_check(pipe_list, bird_rect)

                score_display('main game')

            else:
                game_surface.blit(game_over_surface, game_over_rect)
                high_score = update_score(score, high_score)
                score_display('game_over')

            floor_x_pos -= 1
            draw_floor()
            if floor_x_pos <= -432:
                floor_x_pos = 0

            # --- RENDER TO MAIN SCREEN ---
            screen.fill((0, 0, 0))  # Clear background
            cam_surface = pygame.transform.scale(frame_surface, (CAM_W, CAM_H))
            screen.blit(cam_surface, (0, 0))
            screen.blit(game_surface, (CAM_W, 0))

            pygame.display.update()
            clock.tick(120)  

    finally:
        cap.release()
        # cv2.destroyAllWindows()
        pygame.quit()


# if __name__ == "__main__":
#     play_flappy_bird()
