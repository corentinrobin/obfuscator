#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Auteur : Corentin Robin - Version : 21 février 2018
# Script d'offuscation de dossier Web

import sys, os, re, shutil, time

# FONCTION PRINCIPALE D'OFFUSCATION
# -------------------------------------

def obfuscate_file(file_path, format):
    # remplacements à effectuer
    js_replacements = [[r"(\t| {2,})", ""], [r"[\n\r]{2,}", "\n"], # tabulations, espaces
                       [r"//.*\n*", ""], [re.compile("\/\*.*?\*\/\n*", re.DOTALL), ""], # commentaires
                       [r" *([\+\-\*\%\/\(\)\{\}\[\]\|\&\<\>\!\?\=\,\;\:]+) *", r"\1"]] # caractères spéciaux

    css_replacements = [[re.compile("\/\*.*?\*\/\n*", re.DOTALL), ""],
                        [r"(\t| {2,})", ""], [r"[\n\r]{2,}", "\n"],
                        [r" *([\{\}\,\:\>\+\~]) *", r"\1"]]

    # on lit le fichier
    file = open(file_path, "r")
    content = file.read()
    file.close()

    # on sauvegarde les chaînes de caractères
    strings = re.findall(r"('(.+?)'|\"(.+?)\")", content)

    # on met des marqueurs à la place des chaînes, pour éviter qu'elles ne soient altérées par les remplacements
    content = re.sub(r"('.+?'|\".+?\")", "<<<<STRING>>>>", content)

    i = 0
    replacements = (js_replacements if format == "js" else css_replacements)

    # on effectue les remplacements
    while i < len(replacements):
        content = re.sub(replacements[i][0], replacements[i][1], content)
        i = i + 1

    i = 0

    # on rétablit les chaînes de caractères
    while i < len(strings):
        content = re.sub("<<<<STRING>>>>", strings[i][0], content, 1) # on ne remplace que la première occurence
        i = i + 1

    file = open(file_path, "w")
    file.write(content)
    file.close()

# PARTIE PRINCIPALE
# -------------------------------------

# test des paramètres en console
if len(sys.argv) < 2:
    print("Please choose a folder to obfuscate.")

# bloc principal
else:
    # on récupère le nom du dossier
    input_path = sys.argv[1]

    # on teste si il existe
    if os.path.exists(input_path):
        files_count = 0
        js_count = 0
        css_count = 0
        output_path = input_path + "-obfuscated"

        # si le dossier de sortie existe déjà, on le supprime
        if os.path.exists(output_path):
            shutil.rmtree(output_path)

        # on commence par copier tout le dossier
        shutil.copytree(input_path, output_path)

        # on boucle dans tout les fichiers du dossier
        for root, dirs, files in os.walk(output_path):
            for name in files:
                files_count = files_count + 1
                current_file = os.path.join(root, name)

                if re.match(r"^.*?\.js$", current_file, re.IGNORECASE):
                    js_count = js_count + 1
                    obfuscate_file(current_file, "js")
                    print "Processing " + current_file

                elif re.match(r"^.*?\.css$", current_file, re.IGNORECASE):
                    css_count = css_count + 1
                    obfuscate_file(current_file, "css")
                    print "Processing " + current_file

        # message de résumé
        print("Processing done. " + str(js_count) + " JavaScript file" + ("s" if js_count > 1 else "") + " and " + str(css_count) + " CSS file" + ("s" if css_count > 1 else "") + " have been obfuscated, over " + str(files_count) + " files.")

    else:
        print("Unable to find " + input_path)
