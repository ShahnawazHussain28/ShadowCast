class Config:
    def __init__(self):
        self.type = 'full' # or test

        self.file_name = "zoro.png"
        self.output_file_name = self.file_name
        self.image_resolution = 1024
        self.paper_width = 2480
        self.paper_height = 3508
        self.elevation_factor = 1.05
        self.display_image_size = 512

        if self.type == "test":
            self.output_file_name = "test.png"
            self.image_resolution = 256
            self.paper_height = int(self.paper_height / 4)
            self.paper_width = int(self.paper_width / 4)

        self.box_size = int(self.image_resolution * 0.1)
        self.paper_padding = int(self.paper_width * 0.1)