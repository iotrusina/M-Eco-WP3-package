from timer import Timer
from boardDownload import BoardDownloader

def main():
    bd = BoardDownloader()
    timer = Timer(0)
    timer.registerFunction(bd.getWrapper())
    timer.start()

if __name__ == '__main__':
    main()


