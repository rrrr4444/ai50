First, I started with an adapted form of the handwriting network from the source code.

My methodology was to change every variable of my program one by one and see if it got me a better accuracy.
I tried to read some articles on tf, and I found that batch normalization could improve the speed of the training. So I tried putting in a layer, and that worked.
Then I added a second conv2 and maxpool. I a 2x2 kernel and  64 filters.

I had 3 hidden layers in my final config (1028, 512, 64) and then tried a lower dropout value because I read that batch norm. acted sort of like dropout. That worked pretty well and I consistenly got an accuracy of about 98%.

I also downloaded cuda and tensorflow-gpu to speed up the training.