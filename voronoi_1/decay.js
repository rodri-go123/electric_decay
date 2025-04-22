// Coding Train / Daniel Shiffman
// Weighted Voronoi Stippling
// https://thecodingtrain.com/challenges/181-image-stippling

let points = [];

let delaunay, voronoi;

let gloria;

function preload() {
  gloria = loadImage("../assets/delete.png");
}

function setup() {
  createCanvas(gloria.width, gloria.height);
  for (let i = 0; i < 2500; i++) {
    let x = random(width);
    let y = random(height);
    let col = gloria.get(x, y);
    if (random(100) > brightness(col)) {
      points.push(createVector(x, y));
    } else {
      i--;
    }
  }

  delaunay = calculateDelaunay(points);
  voronoi = delaunay.voronoi([0, 0, width, height]);
  //noLoop();
}

function draw() {
  background(255);

  let polygons = voronoi.cellPolygons();
  let cells = Array.from(polygons);

  let centroids = new Array(cells.length);
  let weights = new Array(cells.length).fill(0);
  let counts = new Array(cells.length).fill(0);
  let avgWeights = new Array(cells.length).fill(0);
  for (let i = 0; i < centroids.length; i++) {
    centroids[i] = createVector(0, 0);
  }

  gloria.loadPixels();
  let delaunayIndex = 0;
  for (let i = 0; i < width; i++) {
    for (let j = 0; j < height; j++) {
      let index = (i + j * width) * 4;
      let r = gloria.pixels[index + 0];
      let g = gloria.pixels[index + 1];
      let b = gloria.pixels[index + 2];
      let bright = (r + g + b) / 3;
      let weight = 1 - bright / 255;
      delaunayIndex = delaunay.find(i, j, delaunayIndex);
      centroids[delaunayIndex].x += i * weight;
      centroids[delaunayIndex].y += j * weight;
      weights[delaunayIndex] += weight;
      counts[delaunayIndex]++;
    }
  }

  let maxWeight = 0;
  for (let i = 0; i < centroids.length; i++) {
    if (weights[i] > 0) {
      centroids[i].div(weights[i]);
      avgWeights[i] = weights[i] / (counts[i] || 1);
      if (avgWeights[i] > maxWeight) {
        maxWeight = avgWeights[i];
      }
    } else {
      centroids[i] = points[i].copy();
    }
  }

  for (let i = 0; i < points.length; i++) {
    points[i].lerp(centroids[i], 0.2);
  }

  // for (let i = 0; i < cells.length; i++) {
  //   let poly = cells[i];
  //   let centroid = centroids[i];
  //   let col =gloria.get(centroid.x, centroid.y)
  //   stroke(0);
  //   strokeWeight(0.5);
  //   beginShape();
  //   for (let i = 0; i < poly.length; i++) {
  //     vertex(poly[i][0], poly[i][1]);
  //   }
  //   endShape();
  // }

  for (let i = 0; i < points.length; i++) {
    let v = points[i];
    let col = gloria.get(v.x, v.y);
    stroke(col);
    stroke(0);
    let sw = map(avgWeights[i], 0, maxWeight, 1, 10, true);
    //sw = 4;
    strokeWeight(sw);
    point(v.x, v.y);
  }

  delaunay = calculateDelaunay(points);
  voronoi = delaunay.voronoi([0, 0, width, height]);
}

function calculateDelaunay(points) {
  let pointsArray = [];
  for (let v of points) {
    pointsArray.push(v.x, v.y);
  }
  return new d3.Delaunay(pointsArray);
}
