def blend(images, weights = None):
    if weights == None:
        weights = [1 for _ in range(len(images))]
    else:
        first_weight = weights[0]
        weights = [w/first_weight for w in weights]

    final = images[0]

    for ind, img in enumerate(images[1:]):
        for y in range(len(img)):
            for x in range(len(img[0])):
                for col in range(3):
                    final[y][x][col] += weights[ind+1] * img[y][x][col]

    total_weight = sum(weights)

    for ind, img in enumerate(images[1:]):
        for y in range(len(img)):
            for x in range(len(img[0])):
                for col in range(3):
                    final[y][x][col] /= total_weight

    return final


def gen_kernel(size):
    normalized = 1/size**2
    return [[normalized for _ in range(size)] for _ in range(size)]


def pix_blur(img,x,y,kernel):
    k_size = len(kernel)
    k_half = k_size//2

    value = [0,0,0]

    for x_pos in range(k_size):
        for y_pos in range(k_size):
            if 0 <= x+x_pos-k_half < len(img[0]) and 0 <= y+y_pos-k_half < len(img):
                for col in range(3):
                    value[col] += img[y+y_pos-k_half][x+x_pos-k_half][col] * kernel[y_pos][x_pos]

    return value


def blur(img,kernel_size):
    kernel = gen_kernel(kernel_size)

    new_img = []

    for y in range(len(img)):
        row = []

        for x in range(len(img[0])):
            row.append(pix_blur(img,x,y,kernel))

        new_img.append(row)

    return new_img
