from PIL import Image
import os
import numpy as np

WHITE_PNG = 255
EDGES_PNG = 10
WHITE_JPG = 1  # some images are weird, values are 0-1 instead of 0-255
EDGES_JPG = 0.05
IMAGE_SIZE = (30, 30)  # pixels
EDITED_DIRECTORY = 'edited'


class ImageMatrix:
    """a class for handling images (resize, trim, print, open)"""
    def __init__(self, image_path, one_letter=True):
        self.path = image_path
        self.name = self._create_name()
        print(f'\033[32m[OPENING IMAGE]\033[0m {self.name}')
        self.raw_img = Image.open(image_path).convert('L')  # converts colored image (3 channels) to 1 channel
        self.raw_img = np.array(self.raw_img)
        self.img_array = self.raw_img[:]
        self.convert_to_bool_matrix()
        if one_letter:
            # it's here for future upgrades, in which a bunch of letters are in one image.
            # if True = it means only one letter is present, hence no problem for trimming.
            self.trim()
            self.resize_image()

    def _create_name(self):
        """creates the name of the image from the full path"""
        name = []
        for letter in reversed(self.path):
            if letter == '/' or letter == '//' or letter == '\\':
                return ''.join(reversed(name))
            name.append(letter)

    def convert_to_bool_matrix(self):
        """converts an image to a 2D matrix"""
        black = (WHITE_PNG - EDGES_PNG)
        for i in range(len(self.raw_img)):
            for j in range(len(self.raw_img[i])):
                if self.raw_img[i][j] < black:
                    self.img_array[i][j] = 0
                else:
                    self.img_array[i][j] = WHITE_PNG

    def trim(self):
        """trims the sides of the image, such that the white spaces will be minimal"""
        min_row, max_row, min_col, max_col = len(self.img_array), 0, len(self.img_array[0]), 0
        # those are the maximal possible values, will be shrieked next.
        for i in range(len(self.img_array)):
            for j in range(len(self.img_array[i])):
                if not self.img_array[i][j]:
                    if i < min_row:
                        min_row = i
                    if i > max_row:
                        max_row = i
                    if j < min_col:
                        min_col = j
                    if j > max_col:
                        max_col = j
        trimmed_img = []
        for i in range(min_row, max_row + 1):  # create the updated image based on the values of the borders from above
            row = np.array(self.img_array[i][min_col:max_col + 1])
            trimmed_img.append(row)
        self.img_array = np.array(trimmed_img)  # convert list to np.array
        self.img = Image.fromarray(self.img_array)  # create Image object

    def __str__(self):
        """prints the image, such that values of 0 (black color) are displayed as dots"""
        pic = ' ' + '__' * len(self.img_array[0]) + ' \n'  # top border
        for row in self.img_array:
            pic += '|'  # left border
            for pixel in row:
                if not pixel:
                    pic += '**'  # black color, since white is True
                else:
                    pic += '  '  # white color
            pic += '|\n'  # right side border
        pic += ' ' + '__' * len(self.img_array[0])  # bottom border
        return pic

    def resize_image(self, size=IMAGE_SIZE):
        """resizes the image to the given size (default is 30*30)"""
        self.img = self.img.resize(size)
        self.img_array = np.array(self.img)

    def show(self):
        """opens the image with the default program for viewing images"""
        print(f"\033[36m[SHOWING IMAGE]\033[0m {self.name}")
        # y = np.array([np.array(xi) for xi in self.img])
        # y = self.img
        # i = Image.fromarray(y, "L")
        self.img.show()

    def print_raw_values(self):
        """prints the array of the raw image"""
        for row in self.raw_img:
            print(row)

    def get_dim(self):
        """returns the dimensions (size, pixels) of the image"""
        return len(self.img_array), len(self.img_array[0])


class SamplesLibrary:
    """creates a library of samples, each image will resize to 30x30 pixels"""
    def __init__(self, sample_folder_name):
        print(f"\033[36m[NEW SAMPLE LIBRARY]\033[0m {sample_folder_name}")
        self.samples = {}  # {ImageMatrix: str}
        for file in os.listdir(sample_folder_name):
            img = ImageMatrix(sample_folder_name+'/'+file)
            self.samples[img] = file[:-4]  # {ImageMatrix: str}

    def __iter__(self):
        """enables a for loop for cycling through images"""
        return iter(self.samples)

    def __next__(self):
        self.iter_images = iter(self.samples)
        return next(self.iter_images)

    def __str__(self):
        """print all the images in the library"""
        s = ''
        for img in self.samples:
            s = s + str(img) + '\n'
        return s

    def __getitem__(self, item: str):
        """
        enables the calling of a specific letter from the library
        :param item: string that is the desired letter. example 'a'
        :return: the image corresponding to the string. ImageMatrix object
        """
        for key in self.samples:
            if self.samples[key] == item:
                return key

    def print_names(self):
        """prints all the names of the letters in the library"""
        print(list(self.samples.values()))

    def identify(self, img_to_identify):
        """
        identify a given letter (in an ImageMatrix format), by the letters stored in the library
        :param img_to_identify: ImageMatrix format
        :return: the most similar letter from the library
        """
        print(f"\033[36m[IDENTIFYING IMAGE]\033[0m {img_to_identify.name}")
        how_similar = {}  # {letter, similarity score(lowest is most similar}
        for img in self.samples:
            how_similar[self.samples[img]] = compare(img_to_identify, img)
        similarity_sorted = list(how_similar.items())
        similarity_sorted.sort(key=lambda x: x[1], reverse=True)
        # print("similarity matrix: ", similarity_sorted)
        # print("most similar: ", similarity_sorted[0][0])
        return similarity_sorted[0][0]


def compare(image1, image2):
    """checks the similarity between two images of type ImageMatrix"""
    similarity = 0
    total_overlap = 0
    for i in range(min(len(image1.img_array), len(image2.img_array))):
        for j in range(min(len(image1.img_array[i]), len(image2.img_array[i]))):
            if image1.img_array[i][j] == image2.img_array[i][j]:
                similarity += 1
            total_overlap += 1
    return similarity/total_overlap


if __name__ == "__main__":
    sam = SamplesLibrary('test_lib')  # create the library
    for z in os.listdir('test pictures'):  # identify all the letters in this folder
        t = ImageMatrix('test pictures/'+z)
        y = sam.identify(t)
        print(t)
        print(sam[y])
