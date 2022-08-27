class Image:

    def __init__(self, img, x, y, width, height, src):
        self.img = img
        self.x =x
        self.y = y
        self.width = width
        self.height = height
        self.src = src


    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def update(self, x, y):
        self.x = x
        self.y = y

    def to_list(self):
        return [self.src, self.x, self.y, self.width,self.height]





class Button(Image):

    def __init__(self, img, x, y, width, height, func):
        super().__init__(img, x, y, width, height)

        self.func = func

    #all buttons are circles
    def clicked(self, mouse_x, mouse_y):
        print(((mouse_x - self.x) **2 + (mouse_y - self.y) ** 2) ** .5 )

        return ((mouse_x - (self.x + self.width/2)) **2 + (mouse_y - (self.y + self.width/2)) ** 2) ** .5 <= self.width/2


    def execute(self):
        self.func()