from os import walk
import pygame

def import_folder(path):
    surface_list = []

    for _, _, img_files in walk(path):
        for img in img_files:
            full_path = path + '/' + img
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
            
    return surface_list

def import_folder_dictionary(path):
    surface_dictionary = {}
    for _,_, img_files in walk(path):
        for img in img_files:
            full_path = path + '/' + img
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dictionary[img.split('.')[0]] = image_surf
    return surface_dictionary