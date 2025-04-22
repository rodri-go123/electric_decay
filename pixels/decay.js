let corrupting = false;
let fading = false;
let currentRow;
let lastUpdateTime = 0;
let interval = 50; // 1000 ms = 1 row per second
let intervals  = [1, 2, 3, 4, 5, 250]; // change intervals mechanism to random number of rows once i map it to voltage, keep refresh rate in mind

let img;
let ditherMatrix = [
  [0, 8, 2, 10],
  [12, 4, 14, 6],
  [3, 11, 1, 9],
  [15, 7, 13, 5]
];

let fadingRows = {}; // Track which rows are fading and how much they've faded
let fadingRow = 1600; //bottom row

function preload() {
  img = loadImage('../assets/delete.png');
}

function setup() {
    createCanvas(600, 400);
    image(img, 0, 0, width, height);
    dither();
}

function draw() {
    if (corrupting && currentRow >= 0 && millis() - lastUpdateTime > interval) {
      interval = random(intervals);
      loadPixels();
  
      corruptRow(currentRow);
      updatePixels();
  
      currentRow--;
      lastUpdateTime = millis();
  
      if (currentRow < 0) {
        corrupting = false;
      }
    }

    if (fading || currentRow <= 0) {
        fadeOutRow(fadingRow);
        fadingRow--;
        updatePixels();
      };
  }

function dither() {
  loadPixels();
  img.loadPixels();

  for (let y = 0; y < img.height; y++) {
    for (let x = 0; x < img.width; x++) {
      let index = (x + y * img.width) * 4;
      let r = img.pixels[index];
      let g = img.pixels[index + 1];
      let b = img.pixels[index + 2];

      // Convert to grayscale using the Luma formula
      let grayscale = 0.299 * r + 0.587 * g + 0.114 * b;

      // Get the corresponding value from the dither matrix
      let ditherValue = (grayscale / 255) * 65;

      // Apply dithering
        if (ditherValue > ditherMatrix[x % 4][y % 4]) {
            set(x, y, color(255)); // Set pixel to white
        } else {
            set(x, y, color(0)); // Set pixel to black
        }
    }
  }
  
  updatePixels();
}

function corruptRow(y) {
    let row = [];
    let scale = [1, 1, 1, 2, 4, 4, 4, 0];
  
    for (let x = 0; x < width; x++) {
      let rowIndex = random(scale) * (y * width + x);
      let r = pixels[rowIndex];
      let g = pixels[rowIndex + 1];
      let b = pixels[rowIndex + 2];
  
      let brightness = 0.299 * r + 0.587 * g + 0.114 * b;
      let shouldShuffle = brightness < 128 || random() < 0.3;
  
      row.push({ r, g, b, a: pixels[rowIndex + 3], x, shuffle: shouldShuffle });
    }
  
    let shuffled = row.filter(p => p.shuffle);
    shuffle(shuffled, true);
  
    let shuffledIndex = 0;
    for (let i = 0; i < row.length; i++) {
      let p = row[i];
      let idx = 4 * (y * width + i);
  
      let newPixel = p.shuffle ? shuffled[shuffledIndex++] : p;
  
      pixels[idx] = 255 - newPixel.r;
      pixels[idx + 1] = 255 - newPixel.g;
      pixels[idx + 2] = 255 - newPixel.b;
      pixels[idx + 3] = newPixel.a;
    }
  }

  function fadeOutRow(n) {
    console.log("Starting fade-out row");
    fadingRows[n] = getBlackPixelsInRow(n);

    for (let y in fadingRows) {
        let xList = fadingRows[y];
        y = int(y);
        for (let i = 0; i < 5 && xList.length > 0; i++) {
          let idx = floor(random(xList.length));
          let x = xList[idx];
          let pixelIndex = 4 * (y * width + x);

          pixels[pixelIndex] = 0;
          pixels[pixelIndex + 1] = 0;
          pixels[pixelIndex + 2] = 0;
          pixels[pixelIndex + 3] = 0;

          xList.splice(idx, 1);

        }

        if (xList.length === 0) {
          delete fadingRows[y];
        }

      }

      
  }
  
  function getBlackPixelsInRow(y) {
    let list = [];
    for (let x = 0; x < width; x++) {
      let idx = 4 * (y * width + x);
      let r = pixels[idx];
      let g = pixels[idx + 1];
      let b = pixels[idx + 2];
  
      let brightness = 0.299 * r + 0.587 * g + 0.114 * b;
      if (brightness < 128) {
        list.push(x);
      }
    }
    return list;
  }

  function keyPressed() {
    if (key === 'd' || key === 'D') {
      corrupting = true;
      currentRow = 400 * 4; // Start from the real bottom row based on the image size
      loadPixels();
      lastUpdateTime = millis(); // Reset the timer
      console.log("Starting corruption at row:", currentRow);
    }

    if (key === 'f' || key === 'F') {
        fading = true;
      }
  
    if (key === 'x' || key === 'X') {
      if (corrupting) {
        corrupting = false;
        console.log("Corruption stopped.");
      }
    }
  
    if (key === 's' || key === 'S') {
      saveCanvas('dithered_image', 'jpg');
    }
  }