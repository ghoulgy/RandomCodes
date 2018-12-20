from pwn import *
r = remote('206.189.93.101',4343)
r.recvuntil("\n> ")
r.sendline("start")

for i in range(31):
    if i<30:
        r.recvuntil("30] ")
        equation = r.recvline()
        print equation
        if "x" in equation:
            equation = equation.replace("x", "*")
            # print "yaya"
        if ";" in equation:
            equation = equation.split(';')[0]
        r.recvuntil("Answer > ")
        ans = eval(equation)
        # print ans
        r.sendline(str(ans))
        print i
    else:
        r.interactive()

