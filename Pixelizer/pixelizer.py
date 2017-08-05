'''
Created on 05.08.2017

@author: Heiko Nolte
'''
import argparse
import numpy as np
from PIL import Image, ImageDraw


''' ******************************************************
    *** Creates a raw pixeled output from input image. ***
    ****************************************************** '''
class Pixelizer:

    input_file = None
    output_file = None
    output_scale_from = None
    output_scale_to = None
    
    image = None
    img_width = None
    img_height = None
    pix_width = None
    pix_height = None
    old_pix_width = 0
    old_pix_height = 0

    def __init__(self, input_file, output_file, output_scale, output_scale_to=-1):
        self.input_file = input_file
        self.output_file = output_file
        self.output_scale_from = output_scale
        if output_scale_to == -1:
            self.output_scale_to = output_scale+1
        else:
            self.output_scale_to = output_scale_to
        
    def execute(self):
        self.image = Image.open(self.input_file)
        
        ndx = 0
        for output_scale in range(self.output_scale_from, self.output_scale_to):
            self.img_width, self.img_height = self.image.size[0], self.image.size[1]
            self.pix_width = int(self.img_width / output_scale)
            self.pix_height = int(self.img_height / output_scale)
            if self.old_pix_width == self.pix_width and self.old_pix_height == self.pix_height:
                continue
            print("Input image dims: %d x %d" % (self.img_width, self.img_height))
            print("Output pixel dims: %d x %d" % (self.pix_width, self.pix_height))
        
            if self.pix_width == 0 or self.pix_height == 0:
                print("Pixel width and pixel height must be at least 1, please decrease scale.")
                return
            else:
                print("Start pixelizing image.")
            self.pixelize(ndx)
            print("Finished pixelizing image.")
            self.old_pix_width = self.pix_width
            self.old_pix_height = self.pix_height
            ndx += 1
    
    def pixelize(self, ndx):
        x_steps = self.img_width / self.pix_width
        y_steps = self.img_height / self.pix_height
        x_pos = 0
        y_pos = 0
        new_image = Image.new('RGB', (self.img_width, self.img_height))
        for y in range(y_steps):
            for x in range(x_steps):
                # Cut out subimage to be pixelized
                subimage = self.image.crop((x_pos, y_pos, x_pos + self.pix_width, y_pos + self.pix_height))
                # Generate pixel from subimage
                pixel_image = self.get_pixel(subimage)
                # Paste pixel to new image
                new_image.paste(pixel_image, (x_pos, y_pos))
                x_pos += self.pix_width
            x_pos = 0
            y_pos += self.pix_height
        output_file = (str(ndx) + ".").join(self.output_file.rsplit('.', 1))
        new_image.save(output_file)
                
    def get_pixel(self, image):
        # Calculate avarage color
        image_array = np.array(image)
        color_sum = np.full((3), 0, dtype=int)
        for y in range(self.pix_width):
            for x in range(self.pix_height):
                color_val = image_array[x, y]
                color_sum = np.add(color_val, color_sum)                
        color_avg = np.divide(color_sum, self.pix_width * self.pix_height)
        
        # Create new pixel image having avarage color
        pixel_img = Image.new('RGB', (self.pix_width, self.pix_height))
        draw = ImageDraw.Draw(pixel_img)
        draw.rectangle(((0,0),(self.pix_width, self.pix_height)), fill=tuple(color_avg))
        return pixel_img

''' ******************************************************
    *** Script parameters:                             ***
    *** --file: Input file                             ***
    *** --scale, to_scal: Pixel creation ratio         ***
    *** --out: Output file                             ***            
    ****************************************************** '''
def main():
    # create parser
    descStr = "This program converts an image into ASCII art."
    parser = argparse.ArgumentParser(description=descStr)
    # add expected arguments
    parser.add_argument('--file', dest='imgFile', required=True)
    parser.add_argument('--scale', dest='scale', required=True)
    parser.add_argument('--to_scale', dest='to_scale', required=False)
    parser.add_argument('--out', dest='outFile', required=True)
    args = parser.parse_args() 
     
    if args.to_scale == None:
        pixelizer = Pixelizer(args.imgFile, args.outFile, int(args.scale))
    else:
        pixelizer = Pixelizer(args.imgFile, args.outFile, int(args.scale), int(args.to_scale))

    pixelizer.execute()

if __name__ == '__main__':
    main()