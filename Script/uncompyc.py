if __name__ == '__main__':
    print('Welcome to the RootMe python crackme')
    # PASS = input('Enter the Flag: ')
    KEY = 'I know, you love decrypting Byte Code !'
    I = 5
    SOLUCE = [57, 73, 79, 16, 18, 26, 74, 50, 13, 38, 13, 79, 86, 86, 87]
    KEYOUT = []
    # for X in PASS:
    #     KEYOUT.append((ord(X) + I ^ ord(KEY[I])) % 255)
    #     I = (I + 1) % len(KEY)

    key = []
    for x in range(len(SOLUCE)):
        key.append(((SOLUCE[x]^ ord(KEY[I]))) - I)
        I = (I + 1) % len(KEY)

    results = ""
    for x in range(len(key)):
        results += chr(key[x])

    print(results)