import app

def main():
    app.log('Reseting to Default Settings')
    app.config().reset()
    app.log('Reseting to Default Settings Complete \n')

if __name__ == '__main__':
    main()
