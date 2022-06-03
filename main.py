#!/usr/bin/env python3

import os
import OpenGL.GL as GL
import glfw
import numpy as np


def init_window():
    # initialisation de la librairie glfw
    glfw.init()
    # paramétrage du context opengl
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # création et parametrage de la fenêtre
    glfw.window_hint(glfw.RESIZABLE, True)  # changer en false
    window = glfw.create_window(800, 800, 'OpenGL', None, None)
    # parametrage de la fonction de gestion des évènements
    glfw.set_key_callback(window, key_callback)
    return window


def init_context(window):
    # activation du context OpenGL pour la fenêtre
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    # activation de la gestion de la profondeur
    GL.glEnable(GL.GL_DEPTH_TEST)
    # choix de la couleur de fond
    GL.glClearColor(0, 0, 1, 1)
    print(f"OpenGL: {GL.glGetString(GL.GL_VERSION).decode('ascii')}")


def init_program():
    program = create_program_from_file("shader.vert", "shader.frag")
    GL.glUseProgram(program)


def init_data():
    sommets = np.array(((0, 0, 0), (1, 0, 0), (0, 1, 0)), np.float32)
    # attribution d'une liste d'e ́tat (1 indique la cre ́ation d'une seule liste)
    vao = GL.glGenVertexArrays(1)
    # affectation de la liste d'e ́tat courante
    GL.glBindVertexArray(vao)
    # attribution d’un buffer de donnees (1 indique la cre ́ation d’un seul buffer)
    vbo = GL.glGenBuffers(1)
    # affectation du buffer courant
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
    # copie des donnees des sommets sur la carte graphique
    GL.glBufferData(GL.GL_ARRAY_BUFFER, sommets, GL.GL_STATIC_DRAW)
    # Les deux commandes suivantes sont stockees dans l'etat du vao courant
    # # Active l'utilisation des donnees de positions
    # (le 0 correspond a la location dans le vertex shader)
    GL.glEnableVertexAttribArray(0)
    # Indique comment le buffer courant (dernier vbo "binde")
    # est utilise pour les positions des sommets
    GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)


def run(window):
    # boucle d'affichage
    global boolleft
    global deltaX, deltaY
    while not glfw.window_should_close(window):
        # nettoyage de la fenêtre : fond et profondeur
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        #  l'affichage se fera ici
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)  # ou avec GL.GL_LINE_LOOP
        # GL.glPointSize(20.0) #changement de la taille des points
        # GL.glDrawArrays(GL.GL_POINTS, 0, 3)
        # GL.glDrawArrays(GL.GL_LINE_LOOP, 0, 3) affichage non plein

        # changement de buffer d'affichage pour éviter un effet de scintillement
        glfw.swap_buffers(window)
        # gestion des évènements
        glfw.poll_events()
        glfw.set_key_callback(window, key_callback)


def changeColorBack():
    global color_Back
    colorisation = (0, 0, 0)
    if color_Back == "g":
        colorisation = (0, 1, 0)
    if color_Back == "r":
        colorisation = (1, 0, 0)
    if color_Back == "b":
        colorisation = (0, 0, 1)
    r, g, b = colorisation
    GL.glClearColor(r, g, b, 1)


def key_callback(win, key, scancode, action, mods):
    # sortie du programme si appui sur la touche 'echap'
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(win, glfw.TRUE)

    global boolup, booldown, boolleft, boolright
    global color_Back

    deltaPos = 0.02

    global deltaX, deltaY

    if key == glfw.KEY_UP and action == glfw.PRESS:
        boolup = True
    if key == glfw.KEY_RIGHT and action == glfw.PRESS:
        boolright = True
    if key == glfw.KEY_DOWN and action == glfw.PRESS:
        booldown = True
    if key == glfw.KEY_LEFT and action == glfw.PRESS:
        boolleft = True

    if key == glfw.KEY_UP and action == glfw.RELEASE:
        boolup = False
    if key == glfw.KEY_RIGHT and action == glfw.RELEASE:
        boolright = False
    if key == glfw.KEY_DOWN and action == glfw.RELEASE:
        booldown = False
    if key == glfw.KEY_LEFT and action == glfw.RELEASE:
        boolleft = False

    if boolup:
        deltaY += deltaPos
    if booldown:
        deltaY += -deltaPos
    if boolright:
        deltaX += deltaPos
    if boolleft:
        deltaX += -deltaPos

    if key == glfw.KEY_G and action == glfw.PRESS:
        color_Back = "g"
    if key == glfw.KEY_R and action == glfw.PRESS:
        color_Back = "r"
    if key == glfw.KEY_B and action == glfw.PRESS:
        color_Back = "b"

    if key == glfw.KEY

    display_callback()
    changeColorBack()


def display_callback():
    global deltaX, deltaY
    # Re ́cupe`re l'identifiant du programme courant
    prog = GL.glGetIntegerv(GL.GL_CURRENT_PROGRAM)
    # Re ́cupe`re l'identifiant de la variable translation dans le programme courant
    loc = GL.glGetUniformLocation(prog, "translation")
    # Ve ́rifie que la variable existe
    if loc == -1:
        print("Pas de variable uniforme : translation")
    GL.glUniform4f(loc, deltaX, deltaY, 0, 0)
    # Modifie la variable pour le programme courant


# compilation d'un shader donne ́ selon son type
def compile_shader(shader_content, shader_type):
    shader_id = GL.glCreateShader(shader_type)
    GL.glShaderSource(shader_id, shader_content)
    GL.glCompileShader(shader_id)
    success = GL.glGetShaderiv(shader_id, GL.GL_COMPILE_STATUS)
    if not success:
        log = GL.glGetShaderInfoLog(shader_id).decode('ascii')
        print(
            f'{25*"-"}\nError compiling shader: \n\{shader_content}\n{5*"-"}\n{log}\n{25*"-"}')
    return shader_id


def create_program(vertex_source, fragment_source):
    # creation d'un programme gpu
    vs_id = compile_shader(vertex_source, GL.GL_VERTEX_SHADER)
    fs_id = compile_shader(fragment_source, GL.GL_FRAGMENT_SHADER)
    if vs_id and fs_id:
        program_id = GL.glCreateProgram()
        GL.glAttachShader(program_id, vs_id)
        GL.glAttachShader(program_id, fs_id)
        GL.glLinkProgram(program_id)
        success = GL.glGetProgramiv(program_id, GL.GL_LINK_STATUS)
        if not success:
            log = GL.glGetProgramInfoLog(program_id).decode('ascii')
            print(f'{25*"-"}\nError linking program:\n{log}\n{25*"-"}')
        GL.glDeleteShader(vs_id)
        GL.glDeleteShader(fs_id)
    return program_id


def create_program_from_file(vs_file, fs_file):
    # creation d'un programme gpu a` partir de fichiers
    vs_content = open(vs_file, 'r').read() if os.path.exists(vs_file)\
        else print(f'{25*"-"}\nError reading file:\n{vs_file}\n{25*"-"}')
    fs_content = open(fs_file, 'r').read() if os.path.exists(fs_file)\
        else print(f'{25*"-"}\nError reading file:\n{fs_file}\n{25*"-"}')
    return create_program(vs_content, fs_content)


def main():
    window = init_window()
    init_context(window)
    init_program()
    init_data()
    run(window)
    glfw.terminate()


if __name__ == '__main__':
    deltaX = 0
    deltaY = 0
    boolup = False
    booldown = False
    boolright = False
    boolleft = False
    color_Back = "b"
    main()
