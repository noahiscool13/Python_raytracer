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
