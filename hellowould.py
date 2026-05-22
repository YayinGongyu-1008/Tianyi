import random

print("欢迎来到猜数字游戏！")
print("我已经想好了一个1到100之间的整数，来猜猜看吧。")

number = random.randint(1, 100)
guess = None
attempts = 0

while guess != number:
    try:
        guess = int(input("请输入你的猜测: "))
        attempts += 1

        if guess < number:
            print("猜小了，再试试！")
        elif guess > number:
            print("猜大了，再试试！")
        else:
            print(f"太棒了！你用了 {attempts} 次就猜对了！")
    except ValueError:
        print("请输入一个有效的数字哦！")



