PImage img;
int yy = 0;

void setup() {
  size(400, 400);
  img = loadImage("armes_de_Paris.png");
}

void draw() {
  background(#FF0000);
  fill(#0000FF);
  stroke(#FFFFFF);
  rect(0, 0, 50, 100);
  image(img, 0, yy);
  yy = yy + 1;
  if (x != -1) {
    rect(min(x, mouseX), min(y, mouseY), abs(mouseX-x), abs(mouseY-y));
  }
}

int x = -1;
int y = -1;

void mousePressed() {
  x = mouseX;
  y = mouseY;
}

void mouseReleased() {
  rect(min(x, mouseX), min(y, mouseY), abs(mouseX - x), abs(mouseY - y));
  println(min(x, mouseX), min(y, mouseY), abs(mouseX - x), abs(mouseY - y));
  x = -1;
  y = -1;
}
