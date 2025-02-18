# What is this?

"This algorithm was inspired by [javidx9](https://www.youtube.com/@javidx9) from [Arbitrary Rectangle Collision Detection & Resolution - Complete!](https://www.youtube.com/watch?v=8JJ-4JgR7Dg&t=1278s)."

Slight changes have been made from the original algo to work in python, images are also from said video above

You use this to check 1 moving things against many non moving things (must be tiles, like rock tiles or floor tiles)

## The following is how it works

How the algo works is after this

### 1. You need 1 moving things against many non moving things (tiles and axis aligned)

![Must be axis aligned okay](./doc_images/1.png)

### 2. Then in 1 frame, do not move it yet but use vel to see starting and ending position

![Move with velocity](./doc_images/2.png)

### 3. The world is finite but big so we have to take sample for most likely collision check

![Find candidates](./doc_images/3.png)
![Find candidates another illustration](./doc_images/19.png)

### 4. Then iterate each candidate, this process will determine a new velocity that prevent overlap

This process transform the initial vel to a vel that will not cause overlap, the algo explanation is after this section

Note that how you iterate matters, otherwise transformed vel is wrong and move and slide will not work

![Iter candidate](./doc_images/4.png)

### 5. This is the end result

With this it is impossible for moving tile to overlap in a solid tile in any frame

![Final result](./doc_images/5.png)

## How the algo works

Imagine a ray, ray is the obj vel btw, starts P ends Q, its a function of time t, goal is to find t that results in the right vel that we want to prevent collision

![Algo intro](./doc_images/6.png)

It is observed that there is a pattern that defines what a collision is, this is by projecting the near and far x and y axis on a horizontal line, imagine a horizontal line above the image top side, if you line in up you can tell which ones are cloes and far, take the most bottom line for example, its clear that ny is smaller than fx since its closer to the left side of the pic, you need to satisfy both condition in order for a collision to be valid, nx < fy and ny < fx. To know which near is x or y, x is when the ray hit the vertical dotted lines, the y is the horizontal dotten lines collision

![Collision definition](./doc_images/7.png)

Note that where near and far is dynamic, its based on where the ray is from, for instance look at this

![The axis are dynamic](./doc_images/8.png)

Here are what happens when you deal with infinity

![Perfect horizontal](./doc_images/9.png)

Another infinity but light misses the box, no collision!

![Perfect horizontal misses](./doc_images/10.png)

We are interested in the time where vel hits closest, this is how, there is a pattern that we observe, take the max from both axis

![Get near time](./doc_images/11.png)

Computing for normal, just use conditions for this

![Get normal](./doc_images/12.png)

Finally in order for this to work, we have to expand the text solid tile, so that resulting vel dest is right on it, we want to rest flushed on

![Expand solid tile](./doc_images/13.png)

This is how velocity resolution works, we know the normal, then just minus total with the near time, that gets you the remaining from total that you use to push it out

![How to resolve vel](./doc_images/14.png)

Btw this is why we have iterate the candidate based on movement direction

Say you are moving to the right, and iterating from 1 2 3 and so on

![Proper order iterating candidate](./doc_images/15.png)

Then when you check 3, its alr not colliding so its all good

![Proper order iterating candidate second iter](./doc_images/16.png)

Say you are moving left this time, but you still iter in the same order from 1 2 3 4 like here, then on first iter you would be pushed to left

![Wrong candidate iter order](./doc_images/17.png)

Then on next iter, you just get pushed upward, and had lost the vel left from prev iter

![Wrong candidate iter order second iter](./doc_images/18.png)

## So when do you wanna use this?

Use this for moving player against static world tiles, make sure that world is made out of tiles, axis aligned too like chessboard
