import requests
import pygame
import sys

pygame.init()


submit_button = pygame.Rect(350, 400, 100, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

font = pygame.font.Font(None, 40)

input_rects = {
    "Username": pygame.Rect(300, 200, 300, 50),
    "Password": pygame.Rect(300, 300, 300, 50),
}
server_base_url = "http://localhost:5000"

input_data = {
    "Username": "",
    "Password": "",
}

active_field = None


def draw_login_form(screen):
    screen.fill(WHITE) 

    for label, rect in input_rects.items():
        color = BLUE if active_field == label else GRAY
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        text_surface = font.render(label, True, BLACK)
        screen.blit(text_surface, (rect.x - 150, rect.y + 10))

        input_surface = font.render(input_data[label], True, BLACK)
        screen.blit(input_surface, (rect.x + 10, rect.y + 10))

    pygame.draw.rect(screen, GRAY, submit_button)
    pygame.draw.rect(screen, BLACK, submit_button, 2)
    submit_text = font.render("Submit", True, BLACK)
    screen.blit(submit_text, (submit_button.x + 0, submit_button.y + 10))

def login(screen):
    password = ""
    global active_field

    while True:
        draw_login_form(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                mouse_pos = pygame.mouse.get_pos()

                for label, rect in input_rects.items():
                    if rect.collidepoint(mouse_pos):
                        active_field = label
                        break
                else:
                    active_field = None

                if submit_button.collidepoint(mouse_pos):
                    print("Form Submitted:")
                    print("Username:", input_data["Username"])
                    print("Password:", password)

                    data = {"username":input_data["Username"],"password":password }
                    ctx = requests.post(server_base_url+"/login", data)
                    if ctx.status_code == 200:
                        with open("config", "w") as k:
                            cookie = ctx.cookies["session"]
                            k.write("{\"session\":\"%s\"}" % (cookie))
                        print("Login successful.")
                        return 1
                    else:
                        return -1

            elif event.type == pygame.KEYDOWN and active_field is not None:
                if event.key == pygame.K_BACKSPACE:
                    if active_field == "Password":
                        password = password[:-1]
                    input_data[active_field] = input_data[active_field][:-1]  
                else:
                    if active_field == "Password":
                        input_data[active_field] += "*"
                        password += event.unicode
                    else:
                        input_data[active_field] += event.unicode 

        pygame.display.flip()

def register(screen):
    password = ""
    global active_field

    while True:
        draw_login_form(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                mouse_pos = pygame.mouse.get_pos()

                for label, rect in input_rects.items():
                    if rect.collidepoint(mouse_pos):
                        active_field = label
                        break
                else:
                    active_field = None

                if submit_button.collidepoint(mouse_pos):
                    print("Form Submitted:")
                    print("Username:", input_data["Username"])
                    print("Password:", password)

                    data = {"username":input_data["Username"],"password":password }
                    ctx = requests.post(server_base_url+"/register", data)
                    if ctx.status_code == 200:
                        with open("config", "w") as k:
                            cookie = ctx.cookies["session"]
                            k.write("{\"session\":\"%s\"}" % (cookie))
                        print("Register successful.")
                        return 1
                    else:
                        return -1
            elif event.type == pygame.KEYDOWN and active_field is not None:
                if event.key == pygame.K_BACKSPACE:
                    if active_field == "Password":
                        password = password[:-1]
                    input_data[active_field] = input_data[active_field][:-1]  
                else:
                    if active_field == "Password":
                        input_data[active_field] += "*"
                        password += event.unicode
                    else:
                        input_data[active_field] += event.unicode 

        pygame.display.flip()