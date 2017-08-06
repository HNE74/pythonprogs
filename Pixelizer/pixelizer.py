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
    poster_cols = 0
    output_scale_from = None
    output_scale_to = None
    delta_scale = None
    
    image = None
    poster_image_names = None
    img_width = None
    img_height = None
    pix_width = None
    pix_height = None
    old_pix_width = 0
    old_pix_height = 0

    def __init__(self, input_file, output_file, poster_cols, output_scale, output_scale_to=-1, \
                 delta_scale=1):
        # initialize variables
        self.input_file = input_file
        self.output_file = output_file
        self.poster_cols = poster_cols
        self.output_scale_from = output_scale
        self.delta_scale = delta_scale
        if output_scale_to == -1:
            self.output_scale_to = output_scale+1
        else:
            self.output_scale_to = output_scale_to
        self.poster_image_names = []    
        
        # Read source image    
        self.image = Image.open(self.input_file)            
        self.img_width, self.img_height = self.image.size[0], self.image.size[1] 

        
    def execute(self): 
        # Execute pixelization
        ndx = 0
        for output_scale in range(self.output_scale_from, self.output_scale_to, self.delta_scale):
            self.pix_width = int(self.img_width / output_scale)
            self.pix_height = int(self.img_height / output_scale)
            if self.old_pix_width == self.pix_width and self.old_pix_height == self.pix_height:
                continue
            print("Input image dims: %d x %d" % (self.img_width, self.img_height))
            print("Output pixel dims: %d x %d" % (self.pix_width, self.pix_height))
        
            if self.pix_width == 0 or self.pix_height == 0:
                print("Pixel width and pixel height must be at least 1, please decrease scale.")
                break
            else:
                print("Start pixelizing image.")
            self.pixelize(ndx)
            print("Finished pixelizing image.")
            self.old_pix_width = self.pix_width
            self.old_pix_height = self.pix_height
            ndx += 1
        
        if self.poster_cols > 0:
            self.create_poster()
        
    def create_poster(self):
        # Create empty poster that contains all generated images
        # and original image at the end
        poster_width = self.img_width * self.poster_cols
        height_factor = (len(self.poster_image_names) + 1) / self.poster_cols
        if (len(self.poster_image_names) + 1) % self.poster_cols > 0:
            height_factor += 1
        poster_height = self.img_height * height_factor 
        poster_image = Image.new('RGB', (poster_width, poster_height))
        
        # Fill poster with previously created pictures
        col = 0
        row = 0
        print("Creating post with width " + str(poster_width) + " and height " + str(poster_height) + ".")
        for name in self.poster_image_names:
            tile_image = Image.open(name)
            xpos_tile = col * self.img_width
            ypos_tile = row * self.img_height
            poster_image.paste(tile_image, (xpos_tile, ypos_tile))
            tile_image.close()
            col += 1
            if col >= self.poster_cols:
                col = 0
                row +=1
                
        # Add original picture at end of poster
        xpos_tile = col * self.img_width
        ypos_tile = row * self.img_height
        orig_image = Image.open(self.input_file)
        poster_image.paste(orig_image, (xpos_tile, ypos_tile))
        poster_image.save(self.output_file)
        print("Finished creating poster.")
        
    
    def pixelize(self, ndx):
        # Calculate pixel size
        x_steps = self.img_width / self.pix_width
        if self.img_width % self.pix_width > 0:
            x_steps += 1
        y_steps = self.img_height / self.pix_height
        if self.img_height % self.pix_height > 0:
            y_steps += 1        
        
        # Create pixels
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
        self.save_new_image(new_image, ndx)

    
    def save_new_image(self, image, ndx):
        # Save single image
        output_file = (str(ndx) + ".").join(self.output_file.rsplit('.', 1))
        image.save(output_file)
        # Append filename to list of poster images
        self.poster_image_names.append(output_file)       
                
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
    *** --scale, to_scale: Pixel creation ratio        ***
    *** --delta_scale: Scale change per iteration      ***
    *** --poster_cols: Number of poster picture cols   ***
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
    parser.add_argument('--delta_scale', dest='delta_scale', required=False) 
    parser.add_argument('--poster_cols', dest='poster_cols', required=False)
    parser.add_argument('--out', dest='outFile', required=True)
    args = parser.parse_args() 
     
    poster_cols = 0
    if args.poster_cols <> None:
        poster_cols = int(args.poster_cols)
     
    if args.to_scale == None:
        pixelizer = Pixelizer(args.imgFile, args.outFile, poster_cols, int(args.scale))
    elif args.to_scale <> None and args.delta_scale == None:
        pixelizer = Pixelizer(args.imgFile, args.outFile, poster_cols, int(args.scale), int(args.to_scale))
    else:
        pixelizer = Pixelizer(args.imgFile, args.outFile, poster_cols, int(args.scale), int(args.to_scale), \
                              int(args.delta_scale))

    pixelizer.execute()

if __name__ == '__main__':
    main()