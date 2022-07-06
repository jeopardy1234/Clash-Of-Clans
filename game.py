import os
import src.main as main
import src.input as input

InputVar = input.Get()

if __name__ == '__main__':
    os.system("setterm -cursor off")
    MainGame = main.COC()
    os.system("setterm -cursor on")