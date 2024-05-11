#importer les libreries nécessaires
import pygame 
from pygame.locals import *
import random
#initialisation de Pygame
pygame.init()

#configuration de l'horloge et du nombre d'images par seconde(fps)
clock = pygame.time.Clock()
fps = 60
#dimension de l'écran
screen_width = 864
screen_height = 936
#configuration de l'écran de jeu
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

#definir la police
font = pygame.font.SysFont('Bauhaus 93', 60)

#definir les couleurs
white = (255,255,255)

#definir les variables du jeu
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500 #ms
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0 
pass_pipe = False


#chagrement des images
bg = pygame.image.load('Assets/bg.png')
ground_img = pygame.image.load('Assets/ground.png')
button_img = pygame.image.load('Assets/restart.png')

#chargement des sons 
flap_sound = pygame.mixer.Sound('Assets/flap.mp3')
point_sound = pygame.mixer.Sound('Assets/point.mp3')
die_sound = pygame.mixer.Sound('Assets/die.mp3')
#définition de la fonction pour afficher du texte
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

#foction de réinitialisation du jeu 
def reset_game() :
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score

#définition de la classe Bird
class Bird(pygame.sprite.Sprite) :

    def __init__(self, x, y) :

        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range (1, 4) :
            img = pygame.image.load(f'Assets/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self) :

        if flying == True :
            #gravité
            self.vel += 0.5
            if self.vel > 8 :
                self.vel = 8
            if self.rect.bottom < 768 :
                self.rect.y += int(self.vel)

        if game_over == False : 

            #saut
            if pygame.mouse.get_pressed()[0] ==1 and self.clicked == False :
                self.clicked = True
                self.vel = -10
                flap_sound.play()
            if pygame.mouse.get_pressed()[0] == 0 :
                self.clicked = False

            #animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown :
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images) :
                    self.index = 0
            self.image = self.images[self.index]

            #rotation de l'oiseau
            self.image = pygame.transform.rotate(self.images[self.index],self.vel * -2)
        else : 
            self.image = pygame.transform.rotate(self.images[self.index], -90)

#definiton de la classe pipe
class Pipe(pygame.sprite.Sprite) :

    def __init__(self,x ,y, position) :

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Assets/pipe.png')
        self.rect = self.image.get_rect()

        #position 1 corresepond au tuyau du haut, -1 au tuyau de bas
        if position == 1 :
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1 :
            self.rect.topleft = [x, y + int(pipe_gap / 2)]


    def update(self) :

        self.rect.x -= scroll_speed
        if self.rect.right <= 0 :
            self.kill()

#definition de la classe button
class button () :
        def __init__(self,x ,y, image) :
            self.image = image
            self.rect = self.image.get_rect()
            self.rect.topleft = (x, y)

        def draw(self) :

            action = False

            #recuperer la positionde la souris
            pos = pygame.mouse.get_pos()

            #verfier si la souris est sur le bouton 
            if self.rect.collidepoint(pos) :
                if pygame.mouse.get_pressed()[0] == 1 :
                    action =True

            #afficher le bouton 
            screen.blit(self.image, (self.rect.x, self.rect.y))

            return action
        
#gropue d'oiseaux(des diff images) et de tuyaux
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

#ajout de l'oiseau au groupe d'oiseaux
flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

#creation d'une instance du bouton restart
button = button(screen_width // 2 -50, screen_height // 2 -100, button_img)
#boucle principale du jeu
run = True
while run :
    
    clock.tick(fps)

    #affichage du fond d'écran 
    screen.blit(bg, (0,0))
    #mise à jour et affichage de l'oiseau
    bird_group.draw(screen)
    bird_group.update()
    #affichage des tuyaux
    pipe_group.draw(screen)
    #affichage du sol
    screen.blit(ground_img,(ground_scroll,768))

    #vérification du score
    if len(pipe_group) > 0 :

        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False :
            pass_pipe = True
        if pass_pipe == True :
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right :
                score +=1 
                pass_pipe = False
                point_sound.play()
    #affichage du score
    draw_text(str(score), font, white, int(screen_width / 2), 50)


    #vérification des collisions
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0 :
        game_over = True
        die_sound.play()
        pygame.time.delay(1000)  # Attendez le temps spécifié
        die_sound.stop()


    #vérification si Bird a touché le sol
    if flappy.rect.bottom >= 768 :
        game_over = True
        flying = False

    #si le jeu n'est pas terminé et que Bird vole
    if game_over == False and flying == True:

        #generation des nouveuax tuyaux
        time_now = pygame.time.get_ticks()

        if time_now - last_pipe > pipe_frequency :

            pipe_height = random.randint(-100,100)
            btm_pipe = Pipe(screen_width,  int(screen_height / 2) + pipe_height,-1)
            top_pipe = Pipe(screen_width,  int(screen_height / 2) + pipe_height, 1)

            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)

            last_pipe = time_now


        #défilement du sol
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35 :
            ground_scroll =0

        #mise à jour des tuyaux
        pipe_group.update()

    #vérification du game over et réintialisation
    if game_over == True :
        if button.draw () == True :
            game_over = False
            score = reset_game()

    #gestion des évènements
    for event in pygame.event.get() :
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False :
            flying = True
            
    #mise à jour de l'affichage
    pygame.display.update()  
    
#quitter pygame à la fin du jeu
pygame.quit()