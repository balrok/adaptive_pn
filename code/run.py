#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import reconfnet_root
import sys
from subprocess import PIPE
from subprocess import Popen
import os

current_dir = os.path.abspath(os.path.dirname(__file__))

def run(sargs, stdin="", encode="utf-8"):
    proc = Popen(sargs, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    out, err = proc.communicate(input=stdin.encode(encode))
    print(out.decode(encode))
    print(err.decode(encode))
    exitcode = proc.returncode
    print(exitcode)

def run_tina(grs_file):
    sargs = [
        os.path.join(reconfnet_root, "tools", "pnml2grgen.py"),
        grs_file,
    ]
    run(sargs)
    sargs = [
        "tina",
        grs_file + ".pnml",
    ]
    run(sargs)
def run_lola(pnml_file):
    lola_file = pnml_file+".lola"
    sargs = [
        "ndrio",
        pnml_file,
        lola_file,
    ]
    run(sargs)
    print("No deadlocks:")
    sargs = [
        "lola",
        "--path",
        "--state",
        '--formula',
        'NOT EF DEADLOCK',
        lola_file,
    ]
    run(sargs)
    print("Reversible:")
    sargs = [
        "lola",
        "--path",
        "--state",
        '--formula',
        'AGEF INITIAL',
        lola_file,
    ]
    run(sargs)


def get_stats(grs_file):
    places = 0
    transitions = 0
    arcs = 0
    with open(grs_file) as f:
        for l in f.read().split("\n"):
            if ":Transition" in l:
                transitions +=1
            if ":Place" in l:
                places +=1
            if ":inArc" in l:
                arcs +=1
            if ":outArc" in l:
                arcs +=1
            if ":inhibitorArc" in l:
                arcs +=1
    print(f"Stats for file: {grs_file}")
    print(f"Places:      {places}")
    print(f"Transitions: {transitions}")
    print(f"Arcs:        {arcs}")

def buko():
    buko_grs = os.path.join(current_dir, 'buko.grs')
    os.chdir(os.path.join(reconfnet_root, "grgen", "allinone"))
    sargs = [
        'GrShell',
        '-N',
        buko_grs,
    ]
    run(sargs, "exit")
    flat = os.path.join(current_dir, "buko_flat.grsi")
    os.rename("paper_flat.grsi", flat)
    get_stats(buko_grs)
    get_stats("paper_flati.grsi")
    analyze(flat)

def analyze(flat):
    print("Analyze flat")
    get_stats(flat)
    run_tina(flat)
    run_lola(flat+".pnml")

def dfop():
    na_file = os.path.join(os.path.dirname(current_dir), "figures", "05_feature_dyn3.na")
    sargs = [
        os.path.join(reconfnet_root, "grgen", "petri_net_addition", "gen.py"),
        "-I",
        na_file,
    ]
    run(sargs)
    grs_file = os.path.join(current_dir, "dfop.grs")
    os.rename(na_file+".grsi", grs_file)

    os.chdir(os.path.join(reconfnet_root, "grgen", "petri_net_addition"))
    sargs = [
        'GrShell',
        '-N',
        grs_file,
    ]
    grs_file_noinh = grs_file + ".noinh.grs"
    run(sargs, "export "+grs_file_noinh+";; exit")
    get_stats(na_file+".transformed.grs")
    get_stats(na_file+".nodyn.grs")
    analyze(grs_file_noinh)

#def phil():
#    na_file = os.path.join(os.path.dirname(current_dir), "figures", "philosopher.na")
#    sargs = [
#        os.path.join(reconfnet_root, "grgen", "petri_net_addition", "gen.py"),
#        "-I",
#        "-b 3",
#        na_file,
#    ]
#    run(sargs)
#    grs_file = os.path.join(current_dir, "philosopher.grs")
#    os.rename(na_file+".grsi", grs_file)
#
#    os.chdir(os.path.join(reconfnet_root, "grgen", "petri_net_addition"))
#    sargs = [
#        'GrShell',
#        '-N',
#        grs_file,
#    ]
#    grs_file_noinh = grs_file + ".noinh.grs"
#    run(sargs, "export "+grs_file_noinh+";; exit")
#    get_stats(na_file+".transformed.grs")
#    get_stats(na_file+".nodyn.grs")
#    analyze(grs_file_noinh)


if __name__ == "__main__":
    os.chdir(current_dir)
    buko()
    os.chdir(current_dir)
    dfop()
    os.chdir(current_dir)
    phil()

